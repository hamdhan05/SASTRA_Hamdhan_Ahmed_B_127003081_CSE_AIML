import re
from typing import List, Dict, Any, Set, Tuple
from sqlalchemy.orm import Session
from backend.models import domain as models

def sanitize_mermaid_id(name: str) -> str:
    """Replaces non-alphanumeric characters with underscores for safe Mermaid IDs."""
    return re.sub(r'[^a-zA-Z0-9_]', '_', name)

def sanitize_mermaid_label(label: str) -> str:
    """Escapes problematic characters in Mermaid node labels."""
    cleaned = label.replace('"', "'").replace('[', '(').replace(']', ')')
    return cleaned[:40]

def build_mermaid_topology(
    entities: List[models.ArchitectureEntity],
    relationships: List[models.ArchitectureRelationship]
) -> str:
    """
    Generates Mermaid graph markdown from real stored entities and relationships.
    Groups SWCs, Ports, and Interfaces into a clean, readable automotive topology.
    """
    if not entities and not relationships:
        return "graph TD\n    empty[\"No architectural entities available for this selection\"]"

    lines = ["graph LR"]
    lines.append("    classDef swc fill:#EFF6FF,stroke:#2563EB,stroke-width:2px,color:#1E3A8A;")
    lines.append("    classDef iface fill:#ECFDF5,stroke:#059669,stroke-width:2px,color:#065F46;")
    lines.append("    classDef port fill:#FEF3C7,stroke:#D97706,stroke-width:1px,color:#92400E;")

    entity_map = {e.id: e for e in entities}
    rendered_nodes: Set[str] = set()

    # Render entities
    for e in entities:
        nid = sanitize_mermaid_id(f"ent_{e.id}_{e.name}")
        lbl = sanitize_mermaid_label(e.name)
        
        if e.entity_type == "Software Component":
            lines.append(f'    {nid}["🧩 {lbl}"]:::swc')
            rendered_nodes.add(nid)
        elif e.entity_type == "Interface":
            lines.append(f'    {nid}["⚡ {lbl}"]:::iface')
            rendered_nodes.add(nid)
        elif e.entity_type == "Port":
            p_kind = e.port_kind or "Port"
            lines.append(f'    {nid}["🚪 {lbl} ({p_kind})"]:::port')
            rendered_nodes.add(nid)

    # Render edges
    for rel in relationships:
        src = entity_map.get(rel.source_entity_id)
        tgt = entity_map.get(rel.target_entity_id)
        if not src or not tgt:
            continue

        src_id = sanitize_mermaid_id(f"ent_{src.id}_{src.name}")
        tgt_id = sanitize_mermaid_id(f"ent_{tgt.id}_{tgt.name}")

        rel_type = rel.relationship_type.upper()
        if rel_type == "PROVIDES":
            lines.append(f'    {src_id} -->|PROVIDES| {tgt_id}')
        elif rel_type == "REQUIRES":
            lines.append(f'    {src_id} -.->|REQUIRES| {tgt_id}')
        elif rel_type == "DEPENDS_ON":
            lines.append(f'    {src_id} ==>|DEPENDS_ON| {tgt_id}')
        else:
            lines.append(f'    {src_id} -->|{rel_type}| {tgt_id}')

    return "\n".join(lines)

def analyze_dependency_impact(
    db: Session,
    project_id: int,
    root_entity_name: str
) -> Dict[str, Any]:
    """
    Performs BFS graph traversal with cycle protection to compute direct and
    transitive downstream dependents for a modified component.
    """
    all_entities = db.query(models.ArchitectureEntity).filter(
        models.ArchitectureEntity.project_id == project_id
    ).all()
    all_relationships = db.query(models.ArchitectureRelationship).filter(
        models.ArchitectureRelationship.project_id == project_id
    ).all()

    name_to_entity = {e.name: e for e in all_entities}
    id_to_entity = {e.id: e for e in all_entities}

    root_ent = name_to_entity.get(root_entity_name)
    if not root_ent:
        return {
            "root_component": root_entity_name,
            "direct_dependents": [],
            "transitive_dependents": [],
            "impact_paths": [],
            "cycle_detected": False,
            "message": f"Component '{root_entity_name}' not found in project entities."
        }

    # Build adjacency list: target -> list of sources (who depends on target)
    # E.g. If A -> B (A depends on B), then changing B impacts A!
    reverse_adj: Dict[int, List[Tuple[int, str]]] = {}
    for r in all_relationships:
        tgt_id = r.target_entity_id
        src_id = r.source_entity_id
        if tgt_id not in reverse_adj:
            reverse_adj[tgt_id] = []
        reverse_adj[tgt_id].append((src_id, r.relationship_type))

    # BFS Traversal
    queue = [(root_ent.id, [root_ent.name])]
    visited: Set[int] = {root_ent.id}
    direct_dependents: Set[str] = set()
    transitive_dependents: Set[str] = set()
    impact_paths: List[str] = []
    cycle_detected = False

    while queue:
        curr_id, curr_path = queue.pop(0)
        neighbors = reverse_adj.get(curr_id, [])

        for nbr_id, rel_type in neighbors:
            nbr_ent = id_to_entity.get(nbr_id)
            if not nbr_ent:
                continue

            path_str = " -> ".join(curr_path + [f"[{rel_type}]", nbr_ent.name])

            if nbr_id in visited:
                cycle_detected = True
                continue

            visited.add(nbr_id)
            if len(curr_path) == 1:
                direct_dependents.add(nbr_ent.name)
            else:
                transitive_dependents.add(nbr_ent.name)

            impact_paths.append(path_str)
            queue.append((nbr_id, curr_path + [nbr_ent.name]))

    return {
        "root_component": root_ent.name,
        "direct_dependents": list(direct_dependents),
        "transitive_dependents": list(transitive_dependents),
        "total_impacted_count": len(direct_dependents) + len(transitive_dependents),
        "impact_paths": impact_paths,
        "cycle_detected": cycle_detected
    }

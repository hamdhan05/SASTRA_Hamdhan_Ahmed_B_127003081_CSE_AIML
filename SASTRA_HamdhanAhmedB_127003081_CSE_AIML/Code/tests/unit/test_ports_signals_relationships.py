import pytest
from backend.services.document_service import extract_entities_from_text
from backend.services.graph_service import build_mermaid_topology, analyze_dependency_impact
from backend.database.connection import SessionLocal
from backend.models import domain as models

def test_ports_and_signals_extraction():
    sample_text = """
    Software Component PowertrainManager_SWC implements engine controls.
    It provides PPort_MotorTorque of interface MotorTorque_IF carrying signal Signal_EngineTorque.
    It requires RPort_VehicleSpeed of interface VehicleSpeed_IF.
    VehicleSpeed: float32 represents actual ground velocity.
    Signal_BatterySOC is represented as uint16.
    """
    entities = extract_entities_from_text(sample_text, page_num=3)
    
    types = [e["type"] for e in entities]
    names = [e["name"] for e in entities]

    # Verify entity types extracted
    assert "Software Component" in types
    assert "Port" in types
    assert "Signal" in types

    # Verify specific ports and attributes
    ports = [e for e in entities if e["type"] == "Port"]
    port_names = [p["name"] for p in ports]
    assert "PPort_MotorTorque" in port_names
    assert "RPort_VehicleSpeed" in port_names

    p_torque = next(p for p in ports if p["name"] == "PPort_MotorTorque")
    assert p_torque["port_kind"] == "PPort"
    assert p_torque["port_direction"] == "Output"

    p_speed = next(p for p in ports if p["name"] == "RPort_VehicleSpeed")
    assert p_speed["port_kind"] == "RPort"
    assert p_speed["port_direction"] == "Input"

    # Verify signals and data types
    signals = [e for e in entities if e["type"] == "Signal"]
    sig_names = [s["name"] for s in signals]
    assert any("EngineTorque" in n for n in sig_names)
    assert any("VehicleSpeed" in n for n in sig_names)

    sig_speed = next(s for s in signals if "VehicleSpeed" in s["name"])
    assert sig_speed["signal_data_type"] == "float32"

def test_mermaid_generation_and_dependency_traversal():
    db = SessionLocal()
    try:
        # Create project with SWCs and relationships
        proj = models.Project(name="Topology Test Project")
        db.add(proj)
        db.commit()
        db.refresh(proj)

        swc_a = models.ArchitectureEntity(
            project_id=proj.id,
            entity_type="Software Component",
            name="SensorManager_SWC"
        )
        swc_b = models.ArchitectureEntity(
            project_id=proj.id,
            entity_type="Software Component",
            name="VehicleController_SWC"
        )
        swc_c = models.ArchitectureEntity(
            project_id=proj.id,
            entity_type="Software Component",
            name="ActuatorDriver_SWC"
        )
        db.add_all([swc_a, swc_b, swc_c])
        db.commit()
        db.refresh(swc_a)
        db.refresh(swc_b)
        db.refresh(swc_c)

        # VehicleController depends on SensorManager (SensorManager is target)
        rel1 = models.ArchitectureRelationship(
            project_id=proj.id,
            source_entity_id=swc_b.id,
            target_entity_id=swc_a.id,
            relationship_type="DEPENDS_ON"
        )
        # ActuatorDriver depends on VehicleController
        rel2 = models.ArchitectureRelationship(
            project_id=proj.id,
            source_entity_id=swc_c.id,
            target_entity_id=swc_b.id,
            relationship_type="DEPENDS_ON"
        )
        db.add_all([rel1, rel2])
        db.commit()

        # 1. Test Mermaid Topology Generation
        mermaid_out = build_mermaid_topology([swc_a, swc_b, swc_c], [rel1, rel2])
        assert "graph LR" in mermaid_out
        assert "SensorManager_SWC" in mermaid_out
        assert "DEPENDS_ON" in mermaid_out

        # 2. Test Dependency Impact Traversal (Modifying SensorManager impacts VehicleController and ActuatorDriver)
        impact = analyze_dependency_impact(db, proj.id, "SensorManager_SWC")
        assert impact["total_impacted_count"] == 2
        assert "VehicleController_SWC" in impact["direct_dependents"]
        assert "ActuatorDriver_SWC" in impact["transitive_dependents"]
        assert impact["cycle_detected"] is False

    finally:
        db.close()

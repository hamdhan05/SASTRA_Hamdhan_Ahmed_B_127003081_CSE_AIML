import os
import time
from typing import Any, Dict, List, Optional
import pymupdf

def sanitize_pdf_text(text: Any) -> str:
    """Sanitizes text for standard PDF Latin/Helvetica encoding without missing glyphs."""
    if text is None:
        return ""
    s = str(text)
    replacements = {
        "—": "-",
        "–": "-",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "•": "*",
        "…": "...",
        "\xa0": " ",
        "≥": ">=",
        "≤": "<=",
        "≠": "!=",
        "→": "->",
        "←": "<-"
    }
    for old, new in replacements.items():
        s = s.replace(old, new)
    # Filter non-ascii characters to avoid font encoding errors in standard helvetica
    return s.encode("ascii", "replace").decode("ascii")

def validate_pdf_file(filepath: str) -> bool:
    """
    Validates that a generated file exists, is non-empty, begins with
    a valid PDF signature (%PDF-), and can be parsed by PyMuPDF.
    """
    if not os.path.exists(filepath):
        return False
    if os.path.getsize(filepath) < 100:
        return False
    
    try:
        with open(filepath, "rb") as f:
            header = f.read(5)
            if header != b"%PDF-":
                return False
        
        doc = pymupdf.open(filepath)
        valid = doc.page_count >= 1
        doc.close()
        return valid
    except Exception:
        return False

def generate_markdown_report(report_type: str, project_id: int, project_name: str, data: Dict[str, Any]) -> str:
    """Generates a structured, professional Markdown report from actual project data."""
    ts = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    lines: List[str] = []

    if report_type == "Component Specification Report":
        c_name = data.get("component_name", "Unknown")
        ver = data.get("version_label", "Unspecified")
        ports = data.get("ports", [])
        findings = data.get("related_findings", [])
        impact = data.get("downstream_impact", {})
        summary = data.get("summary", "No description available.")
        page_num = data.get("source_page", "N/A")

        lines.append(f"# AUTOSAR AI — Component Specification Report\n")
        lines.append(f"**Project:** {project_name} (ID: `{project_id}`)  ")
        lines.append(f"**Target Software Component:** `{c_name}`  ")
        lines.append(f"**Specification Version:** `{ver}`  ")
        lines.append(f"**Report Generated:** {ts}  ")
        lines.append(f"**Classification:** Confirmed Engineering Specification\n")
        lines.append("---\n")

        lines.append("## 1. Executive Summary")
        lines.append(f"{summary}\n")
        lines.append(f"- **Source Specification Page:** {page_num}")
        lines.append(f"- **Total Associated Ports:** {len(ports)}")
        lines.append(f"- **Total Direct/Indirect Impacted Dependents:** {impact.get('total_impacted_count', 0)}\n")

        lines.append("## 2. Ports & Interfaces Specification")
        if ports:
            lines.append("| Port Name | Kind | Direction | Associated Interface | Carried Signals |")
            lines.append("| :--- | :--- | :--- | :--- | :--- |")
            for p in ports:
                p_name = p.get("name", "N/A")
                p_kind = p.get("kind") or "Port"
                p_dir = p.get("direction") or "InOut"
                p_if = p.get("interface") or "N/A"
                p_sig = p.get("carried_signals") or "None"
                lines.append(f"| `{p_name}` | {p_kind} | {p_dir} | `{p_if}` | {p_sig} |")
        else:
            lines.append("> [!NOTE]\n> No dedicated ports extracted for this component in the current document scope.")
        lines.append("")

        lines.append("## 3. Architectural Validation & Compliance Findings")
        if findings:
            lines.append("| Finding ID | Severity | Finding Type | Description | Status |")
            lines.append("| :--- | :--- | :--- | :--- | :--- |")
            for f in findings:
                f_id = f.get("id", "N/A")
                f_sev = f.get("severity", "Low")
                f_type = f.get("type", "Rule Finding")
                f_desc = (f.get("description") or "").replace("|", "\\|")
                f_stat = f.get("status", "open")
                lines.append(f"| `{f_id}` | **{f_sev}** | {f_type} | {f_desc} | `{f_stat}` |")
        else:
            lines.append("No active rule violations or compliance findings associated with this component.")
        lines.append("")

        lines.append("## 4. Downstream Dependency Impact Analysis")
        imp_cnt = impact.get("total_impacted_count", 0)
        lines.append(f"- **Total Impacted Software Components:** {imp_cnt}")
        if imp_cnt > 0:
            lines.append(f"- **Direct Dependents:** {', '.join(f'`{c}`' for c in impact.get('direct_dependents', [])) or 'None'}")
            lines.append(f"- **Transitive Dependents:** {', '.join(f'`{c}`' for c in impact.get('transitive_dependents', [])) or 'None'}")
            lines.append("\n### Dependency Propagation Paths:")
            for path in impact.get("impact_paths", []):
                lines.append(f"- {path}")
        else:
            lines.append("This component has no recorded downstream dependents in the current graph.")
        lines.append("")

        lines.append("## 5. Traceability & Known Limitations")
        lines.append("- All relationships and interfaces reflect persisted data in the project database.")
        lines.append("- Heuristic port associations are confirmed via extracted AUTOSAR software component declarations.")
        lines.append("\n---\n*Report generated by AUTOSAR AI Intelligence Platform.*")

    elif report_type == "Architecture Summary":
        entities = data.get("entities", [])
        lines.append(f"# AUTOSAR AI — Architecture Summary Report\n")
        lines.append(f"**Project:** {project_name} (ID: `{project_id}`)  ")
        lines.append(f"**Generated:** {ts}  ")
        lines.append(f"**Total Extracted Entities:** {len(entities)}\n")
        lines.append("---\n")

        lines.append("## 1. Extracted Entities Inventory")
        if entities:
            lines.append("| ID | Entity Type | Name | Status | Page | Description |")
            lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
            for e in entities:
                desc = (e.get("description") or "").replace("|", "\\|")[:80]
                lines.append(f"| {e.get('id')} | {e.get('type')} | `{e.get('name')}` | {e.get('review_status')} | {e.get('source_page', 'N/A')} | {desc} |")
        else:
            lines.append("No entities extracted yet for this project.")
        lines.append("\n---\n*Report generated by AUTOSAR AI Intelligence Platform.*")

    elif report_type == "Findings Report":
        findings = data.get("findings", [])
        high_cnt = sum(1 for f in findings if (f.get("severity") or "").lower() == "high")
        med_cnt = sum(1 for f in findings if (f.get("severity") or "").lower() == "medium")
        low_cnt = sum(1 for f in findings if (f.get("severity") or "").lower() == "low")

        lines.append(f"# AUTOSAR AI — Architectural Validation Findings Report\n")
        lines.append(f"**Project:** {project_name} (ID: `{project_id}`)  ")
        lines.append(f"**Generated:** {ts}  ")
        lines.append(f"**Total Findings:** {len(findings)} (High: {high_cnt}, Medium: {med_cnt}, Low: {low_cnt})\n")
        lines.append("---\n")

        lines.append("## 1. Validation Findings Detail")
        if findings:
            lines.append("| ID | Severity | Finding Type | Status | Description | Reviewer Comments |")
            lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
            for f in findings:
                desc = (f.get("description") or "").replace("|", "\\|")
                comm = (f.get("comments") or "None").replace("|", "\\|")
                lines.append(f"| {f.get('id')} | **{f.get('severity')}** | {f.get('type')} | `{f.get('status')}` | {desc} | {comm} |")
        else:
            lines.append("No architectural rule violations identified.")
        lines.append("\n---\n*Report generated by AUTOSAR AI Intelligence Platform.*")

    else: # Dependency Matrix
        rels = data.get("relationships", [])
        lines.append(f"# AUTOSAR AI — Architecture Dependency Matrix\n")
        lines.append(f"**Project:** {project_name} (ID: `{project_id}`)  ")
        lines.append(f"**Generated:** {ts}  ")
        lines.append(f"**Total Directed Relationships:** {len(rels)}\n")
        lines.append("---\n")

        lines.append("## 1. Topology Relationships")
        if rels:
            lines.append("| ID | Source Entity | Relationship Type | Target Entity | Status |")
            lines.append("| :--- | :--- | :--- | :--- | :--- |")
            for r in rels:
                lines.append(f"| {r.get('id')} | `{r.get('source', 'N/A')}` | `{r.get('type')}` | `{r.get('target', 'N/A')}` | {r.get('status')} |")
        else:
            lines.append("No dependency relationships extracted yet.")
        lines.append("\n---\n*Report generated by AUTOSAR AI Intelligence Platform.*")

    return "\n".join(lines)

def generate_pdf_report(report_type: str, project_id: int, project_name: str, data: Dict[str, Any], output_path: str) -> None:
    """
    Generates a valid, multi-page, beautifully formatted PDF report using PyMuPDF.
    Ensures PDF headers, margins, page wrapping, tables, headers, and footers.
    Validates output before completion.
    """
    doc = pymupdf.open()
    ts = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())

    # Page dimensions (A4: 595.3 x 841.9 points)
    PAGE_WIDTH = 595.3
    PAGE_HEIGHT = 841.9
    MARGIN = 40.0
    CONTENT_WIDTH = PAGE_WIDTH - (MARGIN * 2)

    # Color palette
    COLOR_PRIMARY = (0.145, 0.388, 0.922)    # Brand Blue #2563EB
    COLOR_DARK = (0.067, 0.094, 0.153)       # Dark Navy #111827
    COLOR_MUTED = (0.420, 0.447, 0.502)      # Gray #6B7280
    COLOR_BG_LIGHT = (0.973, 0.980, 0.988)   # Light Gray #F8FAFC
    COLOR_BORDER = (0.898, 0.906, 0.922)     # Border #E5E7EB
    COLOR_RED = (0.863, 0.149, 0.149)        # Severity Red
    COLOR_AMBER = (0.851, 0.467, 0.024)      # Severity Amber

    current_page = doc.new_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)
    y = MARGIN

    def add_page_header(page, title_text, is_cover=False):
        nonlocal y
        if is_cover:
            # Blue banner
            banner_rect = pymupdf.Rect(MARGIN, MARGIN, PAGE_WIDTH - MARGIN, MARGIN + 55)
            page.draw_rect(banner_rect, color=None, fill=COLOR_PRIMARY)
            page.insert_text(
                pymupdf.Point(MARGIN + 15, MARGIN + 28),
                sanitize_pdf_text(f"AUTOSAR AI -- {title_text}"),
                fontsize=15,
                color=(1, 1, 1),
                fontname="helv"
            )
            page.insert_text(
                pymupdf.Point(MARGIN + 15, MARGIN + 45),
                sanitize_pdf_text(f"Project: {project_name} (ID: {project_id}) | Generated: {ts}"),
                fontsize=9,
                color=(0.9, 0.93, 1.0),
                fontname="helv"
            )
            y = MARGIN + 70
        else:
            # Simple running header
            page.insert_text(
                pymupdf.Point(MARGIN, MARGIN + 12),
                sanitize_pdf_text(f"AUTOSAR AI -- {title_text} (Continued)"),
                fontsize=8,
                color=COLOR_MUTED,
                fontname="helv"
            )
            page.draw_line(
                pymupdf.Point(MARGIN, MARGIN + 18),
                pymupdf.Point(PAGE_WIDTH - MARGIN, MARGIN + 18),
                color=COLOR_BORDER,
                width=0.5
            )
            y = MARGIN + 35

    def check_page_break(needed_height=40.0):
        nonlocal current_page, y
        if y + needed_height > (PAGE_HEIGHT - MARGIN - 30):
            current_page = doc.new_page(width=PAGE_WIDTH, height=PAGE_HEIGHT)
            add_page_header(current_page, report_type, is_cover=False)

    # Initial cover header
    add_page_header(current_page, report_type, is_cover=True)

    # Section generator helper
    def draw_section_heading(title: str):
        nonlocal y, current_page
        check_page_break(35)
        y += 10
        current_page.insert_text(
            pymupdf.Point(MARGIN, y),
            sanitize_pdf_text(title),
            fontsize=12,
            color=COLOR_PRIMARY,
            fontname="helv"
        )
        y += 4
        current_page.draw_line(
            pymupdf.Point(MARGIN, y),
            pymupdf.Point(PAGE_WIDTH - MARGIN, y),
            color=COLOR_PRIMARY,
            width=1.0
        )
        y += 14

    def draw_paragraph(text: str, fontsize=9.0):
        nonlocal y, current_page
        text_sanitized = sanitize_pdf_text(text)
        # Approximate line wrapping
        words = text_sanitized.split()
        cur_line = []
        for w in words:
            cur_line.append(w)
            if len(" ".join(cur_line)) > 85:
                check_page_break(14)
                current_page.insert_text(
                    pymupdf.Point(MARGIN, y),
                    " ".join(cur_line),
                    fontsize=fontsize,
                    color=COLOR_DARK,
                    fontname="helv"
                )
                y += 13
                cur_line = []
        if cur_line:
            check_page_break(14)
            current_page.insert_text(
                pymupdf.Point(MARGIN, y),
                " ".join(cur_line),
                fontsize=fontsize,
                color=COLOR_DARK,
                fontname="helv"
            )
            y += 13

    def draw_table(headers: List[str], rows: List[List[str]], col_widths: List[float]):
        nonlocal y, current_page
        row_height = 20.0
        header_height = 22.0

        check_page_break(header_height + 15)

        # Draw header row
        h_rect = pymupdf.Rect(MARGIN, y, MARGIN + CONTENT_WIDTH, y + header_height)
        current_page.draw_rect(h_rect, color=COLOR_BORDER, fill=COLOR_PRIMARY)
        
        cur_x = MARGIN
        for idx, (h, w) in enumerate(zip(headers, col_widths)):
            current_page.insert_text(
                pymupdf.Point(cur_x + 6, y + 15),
                sanitize_pdf_text(h)[:25],
                fontsize=9,
                color=(1, 1, 1),
                fontname="helv"
            )
            cur_x += w
        y += header_height

        # Draw rows
        for r_idx, row in enumerate(rows):
            check_page_break(row_height)
            bg = COLOR_BG_LIGHT if r_idx % 2 == 1 else (1, 1, 1)
            r_rect = pymupdf.Rect(MARGIN, y, MARGIN + CONTENT_WIDTH, y + row_height)
            current_page.draw_rect(r_rect, color=COLOR_BORDER, fill=bg)

            cur_x = MARGIN
            for cell, w in zip(row, col_widths):
                current_page.insert_text(
                    pymupdf.Point(cur_x + 6, y + 14),
                    sanitize_pdf_text(cell)[:35],
                    fontsize=8.5,
                    color=COLOR_DARK,
                    fontname="helv"
                )
                cur_x += w
            y += row_height

    # Populate Content based on report_type
    if report_type == "Component Specification Report":
        c_name = data.get("component_name", "Unknown")
        ver = data.get("version_label", "Unspecified")
        ports = data.get("ports", [])
        findings = data.get("related_findings", [])
        impact = data.get("downstream_impact", {})

        draw_section_heading("1. Target Component Overview")
        draw_paragraph(f"Component Name: {c_name}")
        draw_paragraph(f"Specification Version: {ver}")
        draw_paragraph(f"Summary: {data.get('summary', 'No description available.')}")
        draw_paragraph(f"Specification Source Page: {data.get('source_page', 'N/A')}")

        draw_section_heading("2. Extracted Ports & Interfaces")
        if ports:
            headers = ["Port Name", "Kind", "Direction", "Interface", "Signals"]
            col_widths = [120.0, 75.0, 75.0, 125.0, 120.0]
            rows = []
            for p in ports:
                rows.append([
                    p.get("name", "N/A"),
                    p.get("kind") or "Port",
                    p.get("direction") or "InOut",
                    p.get("interface") or "N/A",
                    p.get("carried_signals") or "None"
                ])
            draw_table(headers, rows, col_widths)
        else:
            draw_paragraph("No ports explicitly defined for this component in the current document scope.")

        draw_section_heading("3. Validation & Compliance Findings")
        if findings:
            headers = ["ID", "Severity", "Finding Type", "Description"]
            col_widths = [50.0, 75.0, 140.0, 250.0]
            rows = []
            for f in findings:
                rows.append([
                    str(f.get("id", "N/A")),
                    str(f.get("severity", "Low")),
                    str(f.get("type", "Rule Finding")),
                    str(f.get("description", ""))[:45]
                ])
            draw_table(headers, rows, col_widths)
        else:
            draw_paragraph("No active architectural rule violations or compliance findings associated with this component.")

        draw_section_heading("4. Downstream Dependency Impact Analysis")
        imp_cnt = impact.get("total_impacted_count", 0)
        draw_paragraph(f"Total Impacted Software Components: {imp_cnt}")
        if imp_cnt > 0:
            direct_str = ", ".join(impact.get("direct_dependents", [])) or "None"
            draw_paragraph(f"Direct Dependents: {direct_str}")
            trans_str = ", ".join(impact.get("transitive_dependents", [])) or "None"
            draw_paragraph(f"Transitive Dependents: {trans_str}")
            draw_paragraph("Impact Propagation Paths:")
            for pth in impact.get("impact_paths", [])[:5]:
                draw_paragraph(f"  * {pth}")
        else:
            draw_paragraph("This software component has zero recorded downstream dependents.")

    elif report_type == "Architecture Summary":
        entities = data.get("entities", [])
        draw_section_heading("1. Architecture Entities Inventory")
        draw_paragraph(f"Total Extracted Entities: {len(entities)}")

        if entities:
            headers = ["ID", "Type", "Name", "Status", "Page"]
            col_widths = [50.0, 120.0, 175.0, 100.0, 70.0]
            rows = []
            for e in entities:
                rows.append([
                    str(e.get("id", "")),
                    str(e.get("type", "")),
                    str(e.get("name", "")),
                    str(e.get("review_status", "")),
                    str(e.get("source_page", "N/A"))
                ])
            draw_table(headers, rows, col_widths)
        else:
            draw_paragraph("No architecture entities found in this project.")

    elif report_type == "Findings Report":
        findings = data.get("findings", [])
        draw_section_heading("1. Architectural Findings & Rule Violations")
        draw_paragraph(f"Total Findings Count: {len(findings)}")

        if findings:
            headers = ["ID", "Severity", "Finding Type", "Status", "Description"]
            col_widths = [45.0, 70.0, 120.0, 80.0, 200.0]
            rows = []
            for f in findings:
                rows.append([
                    str(f.get("id", "")),
                    str(f.get("severity", "")),
                    str(f.get("type", "")),
                    str(f.get("status", "")),
                    str(f.get("description", ""))[:35]
                ])
            draw_table(headers, rows, col_widths)
        else:
            draw_paragraph("No architectural findings or safety violations identified.")

    else: # Dependency Matrix
        rels = data.get("relationships", [])
        draw_section_heading("1. Architecture Dependency Relationships")
        draw_paragraph(f"Total Directed Edges: {len(rels)}")

        if rels:
            headers = ["ID", "Source Entity", "Relationship Type", "Target Entity", "Status"]
            col_widths = [45.0, 130.0, 110.0, 130.0, 100.0]
            rows = []
            for r in rels:
                rows.append([
                    str(r.get("id", "")),
                    str(r.get("source", "N/A")),
                    str(r.get("type", "")),
                    str(r.get("target", "N/A")),
                    str(r.get("status", ""))
                ])
            draw_table(headers, rows, col_widths)
        else:
            draw_paragraph("No relationships extracted.")

    # Add page footers on all pages
    total_pages = doc.page_count
    for p_idx in range(total_pages):
        page = doc[p_idx]
        page.draw_line(
            pymupdf.Point(MARGIN, PAGE_HEIGHT - MARGIN - 15),
            pymupdf.Point(PAGE_WIDTH - MARGIN, PAGE_HEIGHT - MARGIN - 15),
            color=COLOR_BORDER,
            width=0.5
        )
        page.insert_text(
            pymupdf.Point(MARGIN, PAGE_HEIGHT - MARGIN - 4),
            sanitize_pdf_text("AUTOSAR AI Engineering Platform -- Confidential & Proprietary"),
            fontsize=8,
            color=COLOR_MUTED,
            fontname="helv"
        )
        page.insert_text(
            pymupdf.Point(PAGE_WIDTH - MARGIN - 60, PAGE_HEIGHT - MARGIN - 4),
            sanitize_pdf_text(f"Page {p_idx + 1} of {total_pages}"),
            fontsize=8,
            color=COLOR_MUTED,
            fontname="helv"
        )

    # Save to disk
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    doc.save(output_path)
    doc.close()

    # Validate generated PDF before registering success
    if not validate_pdf_file(output_path):
        if os.path.exists(output_path):
            os.remove(output_path)
        raise RuntimeError("Generated PDF failed standard PDF structure validation.")

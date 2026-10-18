# Demonstration Video & Defense Materials (`Video/`)

This directory contains the video demonstration assets, spoken oral defense scripts, live interactive demonstration scene guides, and recording specifications for **AUTOSAR AI**.

---

## 1. Directory Inventory

| File | Type | Purpose & Scope |
| :--- | :---: | :--- |
| [`Presentation_Script.md`](Presentation_Script.md) | Markdown | Word-for-word spoken script for the 8-slide presentation deck. Timed for an 8 to 10 minute oral defense with clear pauses and emphasis guidelines. |
| [`Demo_Scenes.md`](Demo_Scenes.md) | Markdown | Comprehensive live software demonstration script detailing 4 structured scenes: System Health Diagnostic, Ingestion & Architecture Explorer, Grounded AI Assistant, and Findings/Comparisons. |
| `README.md` | Markdown | This guide outlining video recording instructions, hosting options, and demonstration guidelines. |

---

## 2. Video Demonstration Structure (Target: ~8 to 10 Minutes)

### Phase 1: Presentation Deck Overview (Minutes 0:00 – 4:00)
- Follows [`Presentation_Script.md`](Presentation_Script.md) matching [`Presentation/AUTOSAR_AI_Hamdhan_Ahmed_B_Presentation.pdf`](../Presentation/AUTOSAR_AI_Hamdhan_Ahmed_B_Presentation.pdf).
- Introduces candidate, problem statement, automotive constraints (ISO 26262 / ISO 21434), 8-layer architecture, hybrid RAG pipeline, and evaluation results.

### Phase 2: Live Software Demonstration (Minutes 4:00 – 9:00)
- Follows [`Demo_Scenes.md`](Demo_Scenes.md) in the live Streamlit UI running on `http://localhost:8501`.
- **Scene 1 (Settings & Diagnostics):** Runs one-click diagnostic probe validating all 6 core subsystems.
- **Scene 2 (Documents & Explorer):** Ingests an HLD PDF (`AUTOSAR_Adaptive_Powertrain_HLD.pdf`) and explores extracted SWCs, Runnables, Ports, Signals, and dynamic Mermaid topology graphs.
- **Scene 3 (Grounded AI Assistant):** Submits technical query demonstrating exact page citations (`[Page 4]`) and high Grounding Score (`0.95`). Demonstrates adversarial query with 100% honest abstention.
- **Scene 4 (Findings & Comparisons):** Reviews detected circular dependencies and demonstrates cross-version document diff highlighting added/removed components and signal type alterations.

---

## 3. Video Submission Links

For university portal and competition uploads where file size limits apply:
- **Video Format:** MP4 (1080p Full HD, 30/60 fps, H.264 video codec, AAC audio).
- **Google Drive / YouTube (Unlisted) Link:** *(Upload your recorded MP4 to Google Drive or YouTube unlisted and paste the shareable link below for remote evaluation)*
  ```text
  Video Demo Link: https://drive.google.com/file/d/your-video-link-here/view?usp=sharing
  ```
- **Local Video:** When placing an MP4 locally in this directory for offline USB submission, name it:
  `AUTOSAR_AI_Demonstration_Hamdhan_Ahmed_B.mp4`

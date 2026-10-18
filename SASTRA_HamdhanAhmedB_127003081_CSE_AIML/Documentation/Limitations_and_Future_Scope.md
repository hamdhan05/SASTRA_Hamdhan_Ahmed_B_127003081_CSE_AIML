# AUTOSAR AI — Limitations and Future Scope

## 1. Implemented Capabilities vs. Future Enhancements

To maintain complete academic honesty during university evaluation, the table below clearly separates what is fully implemented in the current codebase from what is planned for future work:

| Capability / Area | Implemented Status | Future Scope / Planned Roadmap |
| :--- | :--- | :--- |
| **PDF Text Extraction** | **Implemented**: PyMuPDF extracts text, preserves page ranges and section titles. | **Future**: OCR integration (Tesseract) for scanned raster PDFs; structured table cell parser. |
| **Architectural Entity Extraction** | **Implemented**: Heuristic regex rules identify SWCs, Runnables, Interfaces, Ports, Signals. | **Future**: Fine-tuned Named Entity Recognition (NER) model and formal ARXML AST parsing. |
| **Vector Search & Hybrid Fusion** | **Implemented**: Dense cosine search (`all-MiniLM-L6-v2`) + BM25 keyword search + RRF. | **Future**: Cross-encoder re-ranking and adaptive query expansion. |
| **Local LLM Inference** | **Implemented**: Ollama `llama3.2:3b` executing on-premises with grounded system prompt. | **Future**: Multi-model routing and quantizations optimized for low-power edge platforms. |
| **Answer Grounding & Verification** | **Implemented**: Claim decomposition, citation matching, numerical Grounding Score. | **Future**: Automated NLI (Natural Language Inference) entailment classifier. |
| **Architectural Validation Rules** | **Implemented**: Circular dependency detection, insecure IPC flags, missing port bindings. | **Future**: Full ISO 26262 ASIL hazard analysis and formal AUTOSAR schema compliance checker. |
| **Revision Comparison** | **Implemented**: Entity set diffing, component rename detection, signal type comparisons. | **Future**: Visual PDF side-by-side highlighting and git-style interactive visual merge tools. |
| **Reporting & Exporting** | **Implemented**: CSV findings report with formula injection sanitization. | **Future**: Native PDF report compilation with embedded diagrams and digital signatures. |

---

## 2. Technical Limitations of Current Implementation

### 2.1 Heuristic Regex-Based Entity Extraction
- **Limitation**: Extraction depends on standard automotive naming conventions (e.g., `_SWC`, `Runnable_`, `_IF`). If an HLD document uses unconventional formatting or omits standard prefixes, heuristic extraction may miss entities (false negatives) or extract arbitrary capitalized strings (false positives).
- **Academic Answer**: In a production environment, this heuristic layer would be paired with a deterministic ARXML schema parser and fine-tuned domain NER.

### 2.2 Scanned and Non-Searchable PDFs
- **Limitation**: The current PyMuPDF pipeline expects text-searchable PDFs. Scanned bitmap images of documents without OCR layers produce empty text extractions.

### 2.3 Complex Tables and Architecture Diagrams
- **Limitation**: Complex multi-column signal matrices and embedded vector block diagrams are extracted as linear text streams. Detailed visual topology in diagrams cannot be interpreted without vision-language models.

### 2.4 Generative LLM Hallucination Risk
- **Limitation**: While grounded system prompts and claim decomposition significantly mitigate unsupported statements, generative language models cannot mathematically guarantee 100% zero-hallucination.
- **Safety Control**: The platform explicitly marks claims as **Unverified** or **Needs Review** and forbids the LLM from making formal safety certifications.

---

## 3. Future Scope & Engineering Roadmap
1. **ARXML Round-Tripping**: Bi-directional synchronization between human-readable HLD PDFs and formal AUTOSAR ARXML XML files.
2. **Automotive Bus Timing Simulation**: Integration with CAN/LIN/Ethernet bus timing simulators to evaluate communication latency.
3. **Domain Fine-Tuning**: Parameter-Efficient Fine-Tuning (PEFT/LoRA) of local models on open AUTOSAR specifications.
4. **ISO 26262 Safety Compliance Automation**: Automated generation of Functional Safety Concepts (FSC) and Technical Safety Concepts (TSC).

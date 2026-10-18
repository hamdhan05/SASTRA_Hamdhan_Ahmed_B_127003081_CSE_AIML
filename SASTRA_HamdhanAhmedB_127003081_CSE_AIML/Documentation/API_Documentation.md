# AUTOSAR AI — REST API Documentation

## 1. Overview
The **AUTOSAR AI** backend is implemented using **FastAPI** running on port 8000. All routes are prefixed with `/api/v1/` and return typed JSON responses with standard HTTP status codes.

---

## 2. API Endpoint Catalog

| HTTP Method | Route Path | Subsystem | Description | Request Body / Parameters | Response Code |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/health` | Core | System health probe | None | `200 OK` |
| `GET` | `/api/v1/health` | Core | API v1 version health probe | None | `200 OK` |
| `POST` | `/api/v1/projects/` | Projects | Create new project workspace | `ProjectCreate` (name, description) | `201 Created` |
| `GET` | `/api/v1/projects/` | Projects | List all projects | `skip`, `limit` query params | `200 OK` |
| `GET` | `/api/v1/projects/{id}` | Projects | Get project details by ID | `id` path param | `200 OK` / `404` |
| `POST` | `/api/v1/documents/upload` | Documents | Upload HLD PDF document | Form-data: `file` (.pdf), `project_id`, `version_label` | `200 OK` / `400` |
| `GET` | `/api/v1/documents/project/{id}` | Documents | List documents in project | `id` path param | `200 OK` |
| `DELETE` | `/api/v1/documents/{id}` | Documents | Delete document and cascade vectors | `id` path param | `200 OK` / `404` |
| `PATCH` | `/api/v1/documents/{id}/governance`| Documents | Update governance state | `governance_state` (DRAFT, IN_REVIEW, APPROVED) | `200 OK` |
| `POST` | `/api/v1/sessions/` | Sessions | Create analysis chat session | `SessionCreate` (project_id, title) | `201 Created` |
| `GET` | `/api/v1/sessions/project/{id}` | Sessions | List sessions in project | `id` path param | `200 OK` |
| `GET` | `/api/v1/sessions/{id}/messages`| Sessions | Get message history in session | `id` path param | `200 OK` |
| `POST` | `/api/v1/sessions/{id}/query` | Sessions / RAG | Submit grounded engineering query | `QueryRequest` (query, top_k, strategy) | `200 OK` |
| `POST` | `/api/v1/sessions/messages/{id}/review` | Sessions / Review | Submit engineer review of answer | `review_decision`, `review_feedback` | `200 OK` |
| `GET` | `/api/v1/entities/project/{id}` | Entities | List extracted architecture entities| `id` path param, `entity_type` filter | `200 OK` |
| `GET` | `/api/v1/entities/project/{id}/graph` | Entities / Topology | Get Mermaid architecture graph | `id` path param | `200 OK` |
| `PATCH` | `/api/v1/entities/{id}/review` | Entities | Update entity review status | `review_status` (confirmed, rejected) | `200 OK` |
| `GET` | `/api/v1/findings/project/{id}` | Findings | List rule violation findings | `id` path param, `severity` filter | `200 OK` |
| `PATCH` | `/api/v1/findings/{id}` | Findings | Update finding review status | `review_status`, `reviewer_comments` | `200 OK` |
| `POST` | `/api/v1/comparisons/` | Comparisons | Compare baseline vs revision HLD | `ComparisonCreate` (baseline_id, revision_id) | `200 OK` / `400` |
| `GET` | `/api/v1/comparisons/{id}` | Comparisons | Retrieve comparison diff results | `id` path param | `200 OK` |
| `POST` | `/api/v1/reports/findings` | Reports | Generate sanitized CSV findings report | `ReportGenerateRequest` (project_id) | `200 OK` |
| `GET` | `/api/v1/reports/download/{id}`| Reports | Download generated report file | `id` path param | `200 OK` / `404` |
| `GET` | `/api/v1/settings/` | Settings | Get active system settings | None | `200 OK` |
| `PUT` | `/api/v1/settings/` | Settings | Update system settings | `chunk_size`, `chunk_overlap`, `top_k` | `200 OK` / `400` |
| `GET` | `/api/v1/diagnostics/` | Diagnostics | Run 6-subsystem health diagnostic | None | `200 OK` |
| `POST` | `/api/v1/evaluation/run` | Evaluation | Execute 35-query benchmark | `BenchmarkRequest` (strategy, top_k, max_queries) | `200 OK` |
| `GET` | `/api/v1/evaluation/history/{id}`| Evaluation | Get historical benchmark runs | `id` path param | `200 OK` |

---

## 3. Representative JSON Schemas

### 3.1 Grounded Query Request & Response
**Request** (`POST /api/v1/sessions/{id}/query`):
```json
{
  "query": "Which software component manages engine operations and torque arbitration?",
  "top_k": 5,
  "retrieval_strategy": "hybrid",
  "version_label": "1.0"
}
```

**Response** (`200 OK`):
```json
{
  "query": "Which software component manages engine operations and torque arbitration?",
  "answer": "According to Section 3.2 (Page 4) of the Powertrain HLD, the PowertrainManager component manages engine operations and torque arbitration.",
  "citations": [
    {
      "citation_id": 1,
      "document_id": 1,
      "document_name": "AUTOSAR_Adaptive_Powertrain_HLD.pdf",
      "page_start": 4,
      "page_end": 4,
      "excerpt": "The PowertrainManager SWC performs supervisory control and torque arbitration..."
    }
  ],
  "claims": [
    {
      "claim_text": "The PowertrainManager component manages engine operations and torque arbitration.",
      "status": "Grounded",
      "matched_citations": [1]
    }
  ],
  "grounding_score": 0.95,
  "confidence_level": "High",
  "latency_ms": 3178.2
}
```

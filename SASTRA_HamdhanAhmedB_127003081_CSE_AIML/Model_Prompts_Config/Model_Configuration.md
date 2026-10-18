# Model Configuration & Local Inference Architecture

## 1. Active Large Language Model (LLM) Configuration
- **Provider**: Ollama Local Runtime
- **Model Name**: `llama3.2:3b`
- **Model Architecture**: Llama 3.2 family, 3.21 Billion parameters, 16-bit quantized (Q4_K_M GGUF format)
- **Context Window**: 8,192 tokens
- **Inference Service Endpoint**: `http://localhost:11434/api/generate`
- **Streaming Mode**: `False` (Full response returned with JSON payload)
- **Timeout**: Connect timeout 10 seconds, Read timeout 120 seconds
- **Local Weight Storage**: `H:\OllamaModels` (Managed natively by Ollama service)

## 2. Provider Selection Rationale
| Feature | Local Ollama (`llama3.2:3b`) | Hosted Cloud APIs (e.g., Gemini / OpenAI) |
| :--- | :--- | :--- |
| **Data Privacy & IP Protection** | **100% On-Premises**: Proprietary automotive HLDs never leave the workstation. | Documents transmitted over external internet to 3rd-party servers. |
| **Operational Cost** | **Zero API Costs**: Runs entirely on local CPU/GPU compute. | Recurring token-based cost per query. |
| **Network Reliability** | **Offline Operation**: Works in isolated automotive engineering labs. | Requires continuous high-bandwidth internet connectivity. |
| **Inference Latency** | ~2.5s – 4.5s on modern hardware. | ~1.5s – 3.0s dependent on network latency. |
| **Standardization** | Deterministic configuration reproducible across academic evaluations. | Potential model version drift over time. |

## 3. Alternative Provider Fallback Support
The platform maintains modular support for hosted Google Gemini (`gemini-1.5-pro-latest`) via `backend/services/llm_service.py` when configured with `LLM_PROVIDER=gemini` and a valid `LLM_API_KEY`. However, by default, Ollama is enforced to guarantee academic reproducibility without requiring API keys.

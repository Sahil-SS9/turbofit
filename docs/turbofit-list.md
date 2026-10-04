# TurboFit List

The **TurboFit List** is made only from benchmark winners at each physical hardware level. **TurboFit Check** is the system scan-to-configuration process that matches a user's machine to this evidence; it is not a model leaderboard.

| Hardware level | Winner | Context | Intelligence | TPS | Balanced | Status |
|---:|---|---:|---:|---:|---:|---|
| 8 GB | — | — | — | — | — | pending benchmarks |
| 16 GB | — | — | — | — | — | pending benchmarks |
| 24 GB | — | — | — | — | — | pending benchmarks |
| 32 GB | — | — | — | — | — | pending benchmarks |
| 48 GB | `Qwen 3.8 27B Unleashed UD-Q3_K_XL + Route auxiliary tasks to main` | 262144 | 46.875 | 39.39215795117914 | 58.778 | winner |
| 64 GB | — | — | — | — | — | pending benchmarks |
| 96 GB | — | — | — | — | — | pending benchmarks |
| 128 GB | — | — | — | — | — | pending benchmarks |
| 192 GB | — | — | — | — | — | pending benchmarks |
| 256 GB | — | — | — | — | — | pending benchmarks |
| 384 GB | — | — | — | — | — | pending benchmarks |

A blank level is honest: no current-recipe winner has completed the exact physical and intelligence campaigns for that hardware class yet. Legacy aliases: 200 GB → 192 GB, 300 GB → 256 GB.

## Candidates (pending benchmarks)

| Hardware | Model | Size | Quant | Note |
|---|---|---|---|---|
| 16 GB | Qwen 3.8 27B GSQ-RCO IQ3_XXS | 10.1 GB | GSQ-RCO-IQ3_XXS | Strong all-round operating point; 3.0 bpw |
| 16 GB | Tiel Coder 35B-A3B UD-IQ3_XXS | 13.2 GB | UD-IQ3_XXS | Code specialist MoE; 3-bit with context headroom |
| 24 GB | Qwen 3.8 27B GSQ-RCO IQ3_S | 11.8 GB | GSQ-RCO-IQ3_S | Task-lossless; 3.5 bpw; recommended operating point |
| 24 GB | Qwen 3.8 27B Unleashed UD-Q3_K_XL | 13.0 GB | UD-Q3_K_XL | Current 24GB profile rung; evidence-backed |
| 32 GB | Qwen 3.8 27B GSQ-RCO IQ3_S | 11.8 GB | GSQ-RCO-IQ3_S | Task-lossless; fits with KV room |
| 32 GB | Tiel Coder 35B-A3B UD-Q5_K_XL | 26.6 GB | UD-Q5_K_XL | Code specialist MoE; 5-bit for 32GB |
| 64 GB | Qwen 3.8 27B GSQ-RCO IQ3_S | 11.8 GB | GSQ-RCO-IQ3_S | Task-lossless; fits with KV room |
| 64 GB | Tiel Coder 35B-A3B UD-Q6_K_XL | 31.8 GB | UD-Q6_K_XL | Near-lossless code MoE; 6-bit |
| 96 GB | Qwen 3.8 27B GSQ-RCO IQ3_S | 11.8 GB | GSQ-RCO-IQ3_S | Task-lossless; fits with KV room |
| 96 GB | Tiel Coder 35B-A3B UD-Q8_K_XL | 38.5 GB | UD-Q8_K_XL | Reference 8-bit code MoE |
| 128 GB | Qwen 3.8 27B GSQ-RCO IQ3_S | 11.8 GB | GSQ-RCO-IQ3_S | Task-lossless; fits with KV room |
| 128 GB | Tiel Coder 35B-A3B UD-Q8_K_XL | 38.5 GB | UD-Q8_K_XL | Reference 8-bit code MoE |
| 192 GB | Qwen 3.8 27B GSQ-RCO IQ3_S | 11.8 GB | GSQ-RCO-IQ3_S | Task-lossless; fits with KV room |
| 192 GB | Tiel Coder 35B-A3B UD-Q8_K_XL | 38.5 GB | UD-Q8_K_XL | Reference 8-bit code MoE |
| 256 GB | Qwen 3.8 27B GSQ-RCO IQ3_S | 11.8 GB | GSQ-RCO-IQ3_S | Task-lossless; fits with KV room |
| 256 GB | Tiel Coder 35B-A3B UD-Q8_K_XL | 38.5 GB | UD-Q8_K_XL | Reference 8-bit code MoE |
| 384 GB | Qwen 3.8 27B GSQ-RCO IQ3_S | 11.8 GB | GSQ-RCO-IQ3_S | Task-lossless; fits with KV room |
| 384 GB | Tiel Coder 35B-A3B UD-Q8_K_XL | 38.5 GB | UD-Q8_K_XL | Reference 8-bit code MoE |

## New engines

| Engine | Model | Requirements | Note |
|---|---|---|---|
| Strata | Qwen 3.8 Flash Next (125B MoE) | 12-24 GB VRAM + 64 GB RAM | Expert tiering: hot experts on GPU, all in RAM, n-gram on SSD. 60-95 tok/s on RTX 5070. IQ2_XS recommended. |


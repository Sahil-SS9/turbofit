# Turbofit

![Turbofit — unified backend, amber and mint aesthetic](assets/turbofit-hero.png)

**One model provider. Every machine. The best local configuration the hardware can safely sustain.**

Turbofit is a first-class [Hermes Agent](https://github.com/NousResearch/hermes-agent) provider and adaptive local-inference runtime. It inventories physical compute and total usable memory, recommends an evidence-backed ladder, launches a native backend, and exposes one OpenAI-compatible endpoint.

![Turbofit settings in Hermes Desktop, including fallback routing, multimodal model selection, and hardware-fit recommendations](assets/hermes-desktop-turbofit-settings.png)

```text
provider: custom:turbofit
model: auto
```

**TurboFit Check** scans the machine — dedicated VRAM, unified/integrated memory, or RAM-only — and applies Auto or a selected compatible lane.

> **Wiki:** [Full Turbofit Wiki](https://github.com/SouthpawIN/turbofit/wiki) — Model Zoo, benchmarks, hardware tiers, and more.

---

## Agentic Model Lineup (TurboFit List)

> 5 models suitable for running Hermes Agent locally. Ordered by capability.

| Order | Model | Type | Parameters | Optimal Quant | Size | AIME26 | GPQA-D | DeepSWE | LCBv6 | TB4.0 |
|-------|-------|------|------------|---------------|------|--------|--------|---------|-------|-------|
| 1 | **Maple Preview** | Ternary MoE | 20B-A1B | TQ2_0-head-Q4_K | 5.5 GiB | 87.5% | 73.5% | — | 75.1% | — |
| 2 | **Cyber Tiel Coder** | Code LLM (MoE) | 35B-A3B | UD-Q4_K_XL | 22.4 GiB | — | — | — | — | — |
| 3 | **Qwen 3.8 27B GSQ-RCO** | LLM (Quantized) | 27B | IQ3_S | 11.8 GiB | — | 89.2% | 42.2% | 90.3% | — |
| 4 | **Ornith 1.5 35A3B** | LLM (MoE) | 35B-A3B | Q4_K_M | ~11 GiB | — | — | — | — | — |
| 4 | **Qwen 3.8 Flash Next** | MoE (Qwen4 Preview) | 180B / 6B | IQ3_XXS | 47 GiB | — | 91.7% | 58.7% | 91.9% | — |
| 5 | **DeepSeek V4.1 Flash** | MoE | 763B / 16B | FP8 / UD-Q4_K_XL | 160 / ~40 GiB | — | 90.9% | 74.2% | — | 31.2% |

> **Fit rule:** model_size + KV cache ≤ tier size. KV cache ≈ 2-4GB at 262K context. GSQ-RCO IQ3_S is near-lossless and the default for all GPU tiers.

---

## Model Zoo

| Model | Type | System | Parameters | AIME26 | GPQA-D | DeepSWE | LCBv6 | TB4.0 |
|-------|------|--------|------------|--------|--------|---------|-------|-------|
| **Maple Preview** ★ | Ternary MoE | Omarchy | 20B-A1B | 87.5% | 73.5% | — | 75.1% | — |
| **Cyber Tiel Coder** ★ | Code LLM (MoE) | Omarchy, MacBook | 35B-A3B | — | — | — | — | — |
| **Qwen 3.8 GSQ-RCO** ★ | LLM (Quantized) | Omarchy | 27B | — | 89.2% | 42.2% | 90.3% | — |
| **Qwen 3.8 Flash Next** ★ | MoE (Qwen4 Preview) | Omarchy | 180B / 6B | — | 91.7% | 58.7% | 91.9% | — |
| **DeepSeek V4.1 Flash** ★ | MoE | Omarchy | 763B / 16B | — | 90.9% | 74.2% | — | 31.2% |
| **Ace Step 1.5** | Music Generation | Omarchy | 4B | — | — | — | — | — |
| **Bonsai 27B** | LLM (Ternary) | Omarchy | 27B | — | — | — | — | — |
| **Cosmos 37B** | LLM | Omarchy | 37B | — | — | — | — | — |
| **NVIDIA Nemotron 3.5** | Enterprise LLM (MoE) | Omarchy | 30B-A3B | — | — | — | — | — |
| **Qwen 2.5 Omni** | Multimodal VLM | Omarchy | 3B | — | — | — | — | — |
| **Soprano** | Creative Micro | Omarchy | 80M | — | — | — | — | — |

> ★ = on TurboFit List. For full model research, see the [wiki](https://github.com/SouthpawIN/turbofit/wiki).

---

## Two Fit Lists

Two separate lists, kept clean by memory model. **Dense models stay on the Dedicated
list** (a real GPU can run dense); the **Unified/CPU list uses MoE stand-ins**, because a
dense 27B crawls on CPU no matter what. Both lists converge on Qwen 3.8 Flash Next.

### Dedicated (GPU / VRAM) — dense is fine on a real GPU

| Band (VRAM) | Model | Quant | Class | Notes |
|------|-------|-------|-------|-------|
| 8–11 | Bonsai 2 | PTQ1_0 / PQ2_0 | dense (ternary) | lowest-VRAM rung |
| 12–15 | Underdog 27B | PQ2_0 | dense (ternary) | |
| 16–23 | Qwen 3.8 GSQ-RCO | IQ3_S | dense | 131K context |
| 24–63 | Qwen 3.8 GSQ-RCO | IQ3_S | dense | 262K context |
| 64+ | Qwen 3.8 Flash Next | IQ2_XS (Strata) | MoE | converges |

### Unified (CPU / RAM) — MoE stand-ins, never dense

| Band (RAM) | Model | Quant | Class | Stands in for |
|------|-------|-------|-------|---------------|
| 8–15 | Maple Preview | TQ2_0 | MoE | Bonsai 2 / Underdog (dense) |
| 16–23 | Cyber-Tiel Coder | IQ3_XXS | MoE | GSQ-RCO 27B (dense) |
| 24–31 | Cyber-Tiel Coder | Q4_K_XL | MoE | GSQ-RCO 27B (dense) |
| 32–47 | Cyber-Tiel Coder | Q5_K_XL | MoE | GSQ-RCO 27B (dense) |
| 48–63 | Cyber-Tiel Coder | Q6_K_XL | MoE | GSQ-RCO 27B (dense) |
| 64+ | Qwen 3.8 Flash Next | IQ2_XS (Strata) | MoE | converges |

> **Correspondence:** Maple is the MoE replacement for Bonsai 2 + Underdog (the low dense
> rungs); Cyber-Tiel is the MoE replacement for GSQ-RCO 27B (the mid dense rung). Dense never
> appears on the Unified list — it's too slow on CPU. Both lists converge on Flash Next. On
> Apple silicon the 64 GB+ Flash Next rung is candidate-only (no released macOS engine yet).

---

## Integrations

| Repo | Description |
|------|-------------|
| [SouthpawIN/TurboFit](https://github.com/SouthpawIN/turbofit) | Main Turbofit runtime |
| [deepgrove-ai/mlx-lm-deepgrove](https://github.com/deepgrove-ai/mlx-lm-deepgrove) | Maple MLX runtime |
| [RasoulNik/ssdmoe](https://github.com/RasoulNik/ssdmoe) | SSD MoE streaming |
| [tayoun/flash-moe](https://github.com/tayoun/flash-moe) | MoE streaming from SSD |
| [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) | Hermes Agent runtime |

---

## Rules

1. **Dense stays on the Dedicated list; CPU/Unified uses MoE stand-ins** — Maple for the low rungs, Cyber-Tiel for the mid rungs; both converge on Flash Next. Never put a dense model (GSQ-RCO) on the Unified list — it's too slow on CPU.
2. **IQ3_S is the default** — near-lossless, lower power, faster inference
3. **Only 5 TurboFit candidates** — Maple, Cyber-Tiel, GSQ-RCO, Flash Next, DeepSeek V4.1 Flash
4. **Math must be correct** — model size + KV cache ≤ tier size

---

## License

MIT

## Supported Models

- **Maple Preview 20B-A1B**
- **Qwen 3.8 27B GSQ-RCO**
- **Ornith 1.5 35A3B**
- **MiniMax Music 3**
- **NVIDIA Parakeet TDT 0.6B v3**
- **Soprano TTS**

## TurboSouth

TurboSouth installs TurboFit when it is missing. Install TurboSouth — reciprocal install: `hermes profile install https://github.com/SouthpawIN/turbosouth.git`

## Hermes messaging gateway

TurboFit integrates with the Hermes messaging gateway on 127.0.0.1:8091. On Windows, a connection refused (WinError 10061) means the gateway is not running. See docs/windows-native-install.md for details.

## Tailscale

Expose your local TurboFit gateway over Tailscale for remote access. Run `/turbofit serve` to start, `/turbofit smoke` to verify. Funnel is never used — Tailscale Serve only. TurboSouth handles install of missing components.

# Turbofit

![Turbofit — unified backend, amber and mint aesthetic](assets/turbofit-hero.png)

**One model provider. Every machine. The best local configuration the hardware can safely sustain.**

Turbofit is a first-class [Hermes Agent](https://github.com/NousResearch/hermes-agent) provider and adaptive local-inference runtime. It inventories physical compute and total usable memory, recommends an evidence-backed ladder, launches a native backend, and exposes one OpenAI-compatible endpoint. The client-facing name stays `auto` while the backing model, context, and auxiliary mode change.

```text
provider: custom:turbofit
model: auto
```

> Catalog entries are **candidates** until the physical campaign passes. Compile, download, or estimated fit is not a winner.

## Install

One command installs the plugin, the Desktop surface, **TurboSouth** (customer service, below), and its mascot pet:

```bash
hermes plugins install --enable https://github.com/SouthpawIN/Turbofit.git
```

Setup then downloads the recommended models for this machine if they are missing and starts the local stack:

| Layer | What | Starts when |
|---|---|---|
| Turbofit provider gateway | OpenAI `/v1` on **`127.0.0.1:8091`** | Setup / Apply / `/turbofit shift` / native service |
| Native model server | llama-server / backend | Turbofit selection after artifacts land |
| Tailscale Serve | Private HTTPS to other tailnet devices | `/turbofit serve` |

The easiest path: ask **TurboSouth**. It installs Turbofit, downloads recommended models, and verifies a real local completion.

Health check — JSON with `auto` means healthy. Connection refused means the Turbofit stack is not running (not a firewall miss, and not the Hermes messaging gateway):

```bash
curl -fsS http://127.0.0.1:8091/v1/models
```

## TurboSouth — TurboFit Customer Service

![TurboSouth mascot — the Sovthpaw pet](https://raw.githubusercontent.com/SouthpawIN/turbosouth/main/assets/turbosouth-hero.png)

**TurboFit is the whole project. TurboSouth is the dedicated bot that assists with installing, configuring, and sending fixes upstream to TurboFit.**

TurboSouth handles install, setup, Q&A with source/commit citations, machine-fit comparison, troubleshooting, and tested upstream pull requests. **TurboSouth installs TurboFit when it is missing.**

Installing TurboFit installs TurboSouth **with its mascot pet** — the Sovthpaw petdex skin (long auburn hair, black sunglasses, sleeveless black vest, pink strap). The pet (`s0uthpaw`) is installed and selected automatically for the default home and the TurboSouth profile; no extra steps.

Manual bootstrap (reciprocal — TurboSouth's installer pulls TurboFit first when missing):

```bash
git clone https://github.com/SouthpawIN/turbosouth.git
cd turbosouth
scripts/install
```

Pet only: `hermes pets install s0uthpaw --select` (gallery slug `s0uthpaw`, alias `turbofit`).

## Slash commands

```text
/turbofit                 # scan + intelligence / balanced / speed
/turbofit setup           # refresh Desktop → Turbofit
/turbofit update          # plugin + Desktop surface + TurboSouth + pet
/turbofit shift up|down   # next smarter / lighter measured combo
/turbofit shift maple     # recommended combo for that model
/turbofit serve           # publish :8091 on your tailnet (private Serve, never Funnel)
/turbofit smoke           # loopback health of the current local runtime
```

## How it adapts

```text
quality-main + auxiliary + 262K
              │ pressure
              ▼
smaller context / shared aux / smaller model
              │
              ▼
keyless Nous free fallback
```

Pressure drops fast; healing is slower and hysteretic. Transitions lock, fail closed, and roll back. Stable routes: `auto` · `active:main` · `active:aux`.

## Model lineup (2.4)

**Dedicated VRAM is not the same as total RAM.**

| Capacity | Main path |
|---|---|
| 96 GB+ dedicated | Qwen 3.8 27B 16-bit until Unleashed FP16 GGUF exists |
| 24–95 GB | Unleashed UD-Q3_K_XL + DFlash2 |
| 16 GB | Unleashed UD-IQ3_XXS + DFlash2 |
| 8 GB dedicated | Maple Preview TQ2_0; Ornith if host RAM holds offloaded experts |
| 24 GB+ shared | Unleashed UD-Q3_K_XL |
| 16–23 GB shared | Ornith 1.5 35A3B |
| 8–15 GB shared | Maple Preview TQ2_0 |

Below 8 GB dedicated: portable-fit only until benched. Never a 9B. Auxiliary is Ornith, optional Carwin Nano, or auto. FreeToken is a pinned NVIDIA MoE **candidate**, never Auto.

Supports **Maple Preview 20B-A1B** (TQ2_0), **Qwen 3.8 27B Unleashed** (UD-IQ3_XXS, UD-Q3_K_XL) + **Ornith 1.5 35A3B**, **MiniMax Music 3**, **NVIDIA Parakeet TDT 0.6B v3**, **Soprano TTS** — full matrix in `docs/model-matrix.md`.

## Hermes configuration

```yaml
model:
  provider: custom:turbofit
  default: auto

providers:
  turbofit:
    base_url: http://127.0.0.1:8091/v1
    api_key: not-needed
    model: auto
    model_name: auto
    provider: turbofit
    tool_format: hermes
```

Tailnet devices use `https://<this-machine>.<tailnet>.ts.net:9443/v1` — check `/turbofit serve status`. Public binds stay rejected.

## Tailscale

Private Serve publishes `127.0.0.1:8091` on your tailnet — Funnel is never used. A `WinError 10061` on Windows means TurboFit isn't listening on `127.0.0.1:8091` (try `/turbofit smoke`), not the Hermes messaging gateway. Native Windows details: `docs/windows-native-install.md` — the `TurbofitGateway` scheduled task.

## Desktop

Hermes Desktop **Turbofit** is the setup surface: hardware, score bars, shift, update, Tailscale serve, fallbacks, runtimes, TurboSouth, multimodal. When Check recommends a new main model, the page offers **Keep both / Archive / Delete** for old weights.

## More detail

| Topic | Doc |
|---|---|
| Evidence-only winners / Check vs List | [`docs/turbofit-list.md`](docs/turbofit-list.md) · [`docs/turbofit-check.md`](docs/turbofit-check.md) |
| Engine serve matrix | [`references/engine-serve-matrix.json`](references/engine-serve-matrix.json) |
| Models, campaigns, multimodal | [`docs/model-matrix.md`](docs/model-matrix.md) · [`docs/campaigns.md`](docs/campaigns.md) · [`docs/multimodal.md`](docs/multimodal.md) |
| Windows native install | [`docs/windows-native-install.md`](docs/windows-native-install.md) |

## Developer verification

```bash
PYTHONPATH=src:. python3 -m pytest -q
node --check desktop/plugin.js
scripts/release-check
```

## License

See [`LICENSE`](LICENSE).

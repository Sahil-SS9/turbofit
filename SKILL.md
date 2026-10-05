---
name: turbofit-runtime
description: "Hardware-aware adaptive Hermes runtime using portable Turbofiles, total usable memory, owned native llama.cpp residency, stable auto/active:main/active:aux routes, and evidence-backed promotion. Use for recommending, activating, inspecting, testing, or troubleshooting Turbofit runtimes."
version: 2.3.1
author: SouthpawIN + Nous Girl
license: MIT
tags: [hermes-agent, llama-cpp, llm, accelerator, cpu, adaptive-runtime, turbofile]
adoption_status: provisional
---

# Turbofit

## 2.3 model authority

Fit List keeps dedicated VRAM separate from integrated/RAM-only total memory. Dedicated: Maple Preview TQ2_0 at 8GB, Qwen 3.8 27B Unleashed UD-IQ3_XXS at 16GB, UD-Q3_K_XL at 24–95GB, and Qwen 3.8 27B 16-bit at 96GB+ until an Unleashed FP16 GGUF is published. Shared total memory: Maple at 8–15GB, Ornith 1.5 35A3B at 16–23GB, and Unleashed UD-Q3_K_XL at 24GB+. An 8GB GPU may also use Ornith when host RAM can hold offloaded experts. Maple remains Auto on dedicated 8GB at native 64K/128K. Auxiliary is Ornith, optional Carwin Nano, or auto.

## Use when

- Selecting an evidence-backed main/aux runtime for physical hardware
- Activating or inspecting a Turbofile profile
- Diagnosing pressure, contraction, expansion, routing, or native residency
- Benchmarking or promoting a model pair
- Updating candidate intelligence or generated wiki views

## Canonical workflow
1. Call `turbofit_status` to inspect provider registration, gateway health, selected hardware profile, active rung, and stable routes.
2. Call `turbofit_configure` with `profile: auto` for hardware selection. Manual `hardware-*gb` profiles are accepted only when physical topology fits.
3. Set `primary: true` to use `custom:turbofit` with model `auto` as the main Hermes provider.
4. Set `fallback: true` to append Turbofit to the canonical `fallback_providers` chain; set it false to remove only Turbofit while preserving other fallbacks.
5. Set `publish_tailnet: true` to create private Tailscale Serve routes for the provider and dashboard; the returned HTTPS provider URL is registered automatically.
6. Set `install_sirvir: true` (alias `install_turbosouth: true`) to install or update the canonical `SouthpawIN/turbosouth` GitHub-current profile without replacing its memories or user state — TurboSouth sends tested pull requests upstream to TurboFit.
7. Set `install_freetoken: true` only on Linux x86_64 + NVIDIA driver 580+ + CUDA toolkit 13+ to install pinned FreeToken 0.1.2 as a text-only MoE **candidate**. It never changes Auto until exact on-box campaigns promote a supported model recipe.
8. Start a new Hermes session after provider changes.

Work from the Git repository, not an installed copy.

```bash
scripts/turbofit-runtime list
scripts/turbofit-runtime set auto
scripts/turbofit-runtime set <profile-id>
scripts/turbofit-runtime status
scripts/turbofit-controller --once
curl -fsS http://127.0.0.1:8091/v1/models
```

`set auto` chooses a canonical profile from immutable physical topology. `set
<profile-id>` validates a measured, natively resolvable manual combination.
Both begin at API safety and use the same adaptive controller to contract and
heal; manual selection changes only the healing ceiling.

- `scripts/turbofit-catalog-campaign` proves native runtime fit and TPS; it does not produce intelligence scores.
- `scripts/turbofit-intelligence-campaign` runs the exact successful quantized production recipe through pinned DeepSWE and the Turbofit agentic main/auxiliary pair harness.
- Use `status`, `run-one`, or `run --limit N`; state is resumable in `references/intelligence-campaign-state.json`.
- Scores require both benchmark suites and immutable raw evidence. Never replace missing scores with catalog tiers, parameter counts, or vendor benchmark claims.
- `/turbofit tiers` and `scripts/turbofit-hardware-tiers` show every 8/16/24/32/48/64/96/128/192/256/384 GB class with pending versus measured intelligence and TPS.
- `scripts/turbofit-intelligence-campaign` benchmarks only the current machine's TurboFit List tournament candidates. `rebuild-scores` recomputes derived composites from raw suite counts; zero-call/token trials remain invalid infrastructure.
- `scripts/turbofit-promote-list-winner` promotes only an exact-tier candidate with current physical evidence, positive intelligence/TPS/balanced values, and matching recipe hashes. `scripts/turbofit-list` renders the global evidence-only List.
- Qwen 3.8 DFlash2 is a separate candidate runtime/artifact pair (`dflash2-llama.cpp`, `Qwen3.8-27B-DFlash2-Q4_K_M.gguf`). Never attach that drafter to Bonsai. Bonsai uses its own released DSpark sidecar and Prism runtime until a dedicated Bonsai DFlash checkpoint exists.

## Portable memory allocation

Hardware fingerprints classify memory as `dedicated`, `unified`, or `cpu`. Turbofit reserves 5% of host RAM, bounded to 1–8 GiB, and never double-counts unified memory. Dedicated systems can combine VRAM and host RAM through llama.cpp offload; contexts beyond the model's native window move KV cache pressure to host RAM when at least 32 GiB is usable. Unified-memory systems suppress discrete split flags. CPU-only systems use pinned CPU runtimes with both model and draft GPU layers set to zero.

Backend order is CUDA → ROCm → Vulkan → CPU on Linux/Windows and Metal on macOS. Build or verify the current machine's pinned backend with `scripts/install-native-runtimes --backend cuda|rocm|metal|vulkan|cpu`.

## Non-negotiable safety

- Never kill or signal external accelerator/model processes.
- Signal only PID-and-command-verified processes owned by Turbofit.
- Count external memory as unavailable and managed residency as reclaimable.
- A temporary auxiliary admission redirect may precede drain; never publish a
  new target rung before verification.
- Restore and verify the previous rung after any failed transition.
- Never place paths, secrets, credentials, provider keys, or device indices in Turbofiles.
- Never treat research candidates or generated wiki text as production authority.
- Never mark benchmark success without a canonical promotion record.

## Profile/recommendation checks

```bash
PYTHONPATH=src python3 scripts/turbofit-runtime-recommend --fit-only --json
PYTHONPATH=src:. python3 -m pytest tests/test_runtime_profile.py tests/test_profile_io.py tests/test_hardware.py tests/test_recommend.py -q -o 'addopts='
```

Topology matters: `1x48` and `2x24` are different classes. Unmeasured classes keep API as the Auto safety rung while setup may expose separately labeled portable-fit local candidates for on-box validation.

**TurboFit Check** means the system scan-to-configuration process. **TurboFit List** means only the exact physical hardware-level winners generated by `scripts/turbofit-list`. Intelligence campaigns run only the current tier's tournament candidates; zero-call/token DeepSWE trials are invalid, and suite composites are rebuilt from real hash-bound pass counts rather than stale stored zeros.

Qwen 3.8 DFlash2 is a separate candidate using the pinned Inco Q4_K_M drafter and pinned z-lab llama.cpp PR runtime. Never reuse it for Bonsai. Bonsai keeps its own Prism DSpark sidecar/runtime until a dedicated Bonsai DFlash checkpoint exists.

## Pressure and adaptation checks

```bash
PYTHONPATH=src:. python3 -m pytest tests/test_pressure.py tests/test_pressure_probe.py tests/test_policy.py tests/test_reconciler.py tests/test_controller.py tests/test_runtime_service.py tests/integration -q -o 'addopts='
```

Expected contraction:

```text
dedicated aux → shared-main → smaller context/model → terminal API
```

Expected recovery walks one rung at a time toward the recommendation after margin and dwell.

## Engine pin/build provenance

For vendored engines, verify the owning repository's full commit and engine subtree Git tree separately from a synthetic standalone snapshot commit. Probe anonymous remote fetchability rather than assuming that a local fix is unavailable; GitHub fork-network commit lookup does not establish default-branch inclusion. Keep engine fixes in the engine, and manager code limited to source/build/recipe binding.

When testing copied engine installations, use a tiny shared-library fixture without fixture-supplied RPATH, preserve/rename the build tree, and execute the installed binary. Supply relative loader paths in the installer and inspect ELF RUNPATH plus actual dependency resolution: hashing copied libraries alone can pass while the loader still depends on an unbound build directory.

For fresh CUDA validation beside a live inference service, keep compiler jobs and CPU affinity bounded at low scheduling/I/O priority; deny GPU device access and live-home writes before executing source. Permit trusted Git fetch networking separately, then seal TCP and datagram creation before CMake so build descendants cannot inherit fetch access. Resolve `/etc/resolv.conf` symlinks explicitly in the read-only allowlist rather than opening all of `/run`.

Preserve the build tree under a new name before testing the copied installation; require every package-owned library to resolve inside the installed sibling directory. Run pristine model-dependent regressions with exact weight hashes and a positive execution marker because a zero exit may mean a non-hybrid skip. Small-context CPU checks do not close CUDA or production-context acceptance.

Do not use an intentionally missing model as a supposedly nonbinding server parser test: the server may bind its listener before loading weights. Keep binding denied, preserve that refusal, and use an explicitly labelled `--help` parsing probe when only argument compatibility is required. Pass the absolute interpreter path as `execv` argv[0] as well as the executable argument; otherwise Python may report an empty `sys.executable`, weakening runtime evidence.

Hash the complete deployed shared-library set and verify symlinks, not only the server executable. Preserve exact recipe and model hashes. Label those hashes as deployment references rather than predicted rebuild outputs: compiler versions, native CPU tuning, paths and embedded Git metadata can prevent byte-for-byte reproduction. Record dirty test-only source changes separately from the pristine tree and prior test receipts.

## Release gates

```bash
scripts/release-check
scripts/release-check --real
```

The first command validates syntax, tests, profiles, links, and simulated transitions. The second additionally requires working accelerator telemetry, stable live routes, and controlled real pressure/recovery evidence. Do not claim release readiness if `--real` is blocked.

Acceptance evidence: `references/results/adaptive-runtime-acceptance.json`.

## Candidate intelligence

Collectors write only `research/candidates.json`:

```bash
PYTHONPATH=. python3 research/discover_huggingface.py
PYTHONPATH=. python3 research/discover_model_news.py --url <public-feed>
PYTHONPATH=. python3 research/discover_api_models.py --provider <name> --url <public-model-list>
```

No collector may modify runtime profiles, routes, or credentials. Live cron schedules/delivery require explicit user approval.

## Troubleshooting order

1. `scripts/turbofit-runtime status` and the hardware fingerprint in Dashboard/Desktop
2. The platform's available native inventory probe (CUDA, ROCm, Metal, Vulkan, or CPU)
3. Native runtime `/health`, `/v1/models`, and `/metrics`
4. Gateway `/v1/models`
5. Route-state freshness and stable IDs
6. Acceptance record blockers
7. Focused tests, then full `scripts/release-check`

If `http://127.0.0.1:8091/v1/models` is connection-refused, the Turbofit provider gateway is not running. That is setup missing. Do not restart the Hermes messaging gateway, do not start with a firewall hunt when nothing listens, and do not invoke Sirvir until the endpoint answers.

If the platform reports a driver/runtime mismatch, stop the real pressure test. Do not attempt blind driver reloads or disruptive accelerator work.

Full architecture and schema: `README.md`.

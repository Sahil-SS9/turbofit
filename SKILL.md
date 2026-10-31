---
name: turbofit-runtime
description: "Hardware-aware adaptive Hermes runtime using portable Turbofiles, total usable memory, owned native llama.cpp residency, stable auto/active:main/active:aux routes, and evidence-backed promotion. Use for recommending, activating, inspecting, testing, or troubleshooting Turbofit runtimes."
version: 2.4.0
author: SouthpawIN + Nous Girl
license: MIT
tags: [hermes-agent, llama-cpp, llm, accelerator, cpu, adaptive-runtime, turbofile]
adoption_status: provisional
---

# Turbofit

## 2.4 model authority

Two ladders converge on Qwen 3.8 Flash Next. Ladder 1 — dedicated VRAM (dense is fine): Bonsai 2 27B PTQ1_0/PQ2_0 at 8–11 GB → Underdog 27B PQ2_0 at 12–15 GB → Qwen 3.8 27B GSQ-RCO IQ3_S at 16–48 GB (262K from 24 GB) → Flash Next IQ3_XXS at 64 GB+. Ladder 2 — unified/CPU (MoE only): Maple Preview 20B-A1B at 8–15 GB → Cyber-Tiel Coder 35B-A3B UD-Q4_K_XL at 16 GB+ → Flash Next → DeepSeek V4.1 (1017) as the top rung (native engine pending). Fit math: model + KV ≤ tier. Cross-cutting: MTP on at every rung; IQ3_S is lossless — do not push a heavier quant past it for the power bill. `serve auto` builds the fit chain from these ladders and walks down on OOM/timeout — the Fit List IS the fallback chain.

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
6. Set `install_turbosouth: true` (alias `install_turbosouth: true`) to install or update the canonical `SouthpawIN/turbosouth` GitHub-current profile without replacing its memories or user state — TurboSouth sends tested pull requests upstream to TurboFit.
7. Set `install_freetoken: true` only on Linux x86_64 + NVIDIA driver 580+ + CUDA toolkit 13+ to install pinned FreeToken 0.1.2 as a text-only MoE **candidate**. It never changes Auto until exact on-box campaigns promote a supported model recipe.
8. Start a new Hermes session after provider changes.

Work from the Git repository, not an installed copy.

`/turbofit setup` refreshes Hermes Desktop. A refused `http://127.0.0.1:8091/v1/models` means the Turbofit runtime is down — not the Hermes messaging gateway. Diagnose that from TurboSouth or Desktop with `turbofit_status`. Setup downloads recommended models if they are missing.

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

## Selectable models in the Hermes `/model` picker

Treat stable route IDs and selectable model IDs as different contracts. Keep
`auto`, `active:main`, and `active:aux` stable, then advertise friendly model
IDs only from an operator-owned selector map that resolves each ID to an
approved runtime profile. Add matching entries to Hermes provider config so
the picker shows useful labels.

Switch through the canonical runtime CLI rather than a second launcher:

1. Reject the transition while lifecycle leases show an active request; never
   restart or unload a model mid-response.
2. Resolve the friendly ID to a measured profile, write the normal selection,
   and let the controller retire the old main before loading the new one.
3. Wait until route state reports the requested profile as active before
   proxying the caller. Size this timeout for cold model startup, not a normal
   HTTP request; large local runtimes can need several minutes.
4. Rewrite the friendly picker ID to the selected backend's real model ID when
   forwarding the request.
5. Verify the catalog and a real `A → B → A` inference sequence, leaving the
   declared default active. Catalog visibility alone does not prove switching.

Leases and residency gate every mutation and admission. Wait (bounded re-check
loop) for lifecycle leases to drain before switching or deploying — a live
fleet request holds a lease for seconds to minutes, and an instant empty-check
must never disturb an active response. Read fleet readiness from `/v1/models`
plus the services' active state, not `/health`, which legitimately degrades
while wake-on-demand roles sit idle-released. The ownership proof for a
resident native process is its creation identity plus command line: require
`--alias` in that line only when the launcher actually passes it — config-
driven backends whose alias is fixed by their config omit it and otherwise
report residency `error`, which refuses every lease and makes the wake path
euthanize and relaunch a perfectly healthy model. Treat the lifecycle endpoint
as ephemeral: its real port and token live in a state-dir endpoint file that
every controller start rewrites; port tables are intent, not address.

Store one runtime profile document per YAML file. Discover a bounded naming
pattern such as `manual-profile*.yaml`; do not concatenate profiles into a
multi-document file unless every profile loader is explicitly multi-document
aware. Validate the profile catalog, runtime resolutions, and rung
requirements together before restart so every advertised selector is
loadable.

When a non-llama backend is a runtime flavor, branch before constructing the
launch command and do not append llama.cpp-only flags afterward. Backend
selection is not complete until the exact launch path has passed a real
controller-style startup probe — same user and same working directory as the
daemon. A probe run from the repo checkout can pass while the daemon's spawn
fails, because recipe paths and the invoker's home resolve differently.

When the gateway — not a human shell — invokes the runtime CLI, it inherits the
service user's home: pass `TURBOFIT_CONFIG_DIR` and `TURBOFIT_SELECTION_STATE`
so profile lookup and the selection write land on the controller's config
directory. The same envs matter from an operator shell whenever the controller's
config lives outside the default `~/.config/turbofit`: without them `status`
answers `configured: false` beside a perfectly healthy controller. Without them the CLI reports `unknown profile` for valid profiles
and the picker answers 400 even though the same command succeeds in a shell.
Make the watched selection file's directory writable by the gateway user: the
selection write is a tempfile-plus-rename inside that directory, so a
root-owned directory fails every activation even when the file itself is
readable. When a gateway-invoked helper fails only inside the service, log its captured
stdout/stderr into the service journal with one bounded retry, and make the
helper self-report (its interpreter, config dir, profile files, catalog ids)
on non-zero exit — a spawn-only failure that cannot be reproduced outside the
gateway must confess its own view. Reproduce such spawns from the running
service's `/proc/<pid>/environ` and exact argv before concluding anything.
Pin service-run Python dependencies in a stable venv outside directories a
tool manager refreshes: the interactive PATH often resolves a different
interpreter than the daemon's spawn, and a refreshed shared interpreter
silently loses packages between runs while a shell probe still passes.

Deploy picker changes as one rollback-capable unit: back up controller,
gateway, recipe resolver, Turbofit config, selector map, and Hermes provider
config; syntax/parse-check staged files; apply; restart only the Turbofit
control plane; verify `/health`, `/v1/models`, both switch directions, and the
final active profile. Restore the whole unit on any failed gate rather than
leaving picker entries that point to an unavailable runtime.

When iterating an apply script, every verification failure rolls back to the
PREVIOUS run's state, which can predate your newest fix: install the complete
shadow code set — every module the switch path executes — on every attempt,
and mirror each installed artifact in both the backup and rollback sets
(an artifact absent from the backup cannot be restored). Verify the restore
explicitly on every failure path: an ERR trap does not catch `set -u`
unbound-variable errors inside functions, and `local` names shadow shell
builtins. Reuse an expensive standalone smoke test across attempts with a
one-use marker file that only the verified success writes and the next run
consumes. Three one-line traps worth an hour each: capture HTTP error bodies
without curl's `-f` (it suppresses the body exactly when you need it); poll
the process that actually runs, not a `setsid`/`exec` wrapper whose PID dies
instantly and whose death then triggers cleanup on the just-started server;
accept `reasoning_content` when asserting a chat reply, because thinking
models can return empty `content`.
For operator-facing summaries, lead with four plain facts: default model,
alternative model, context/speed, and the exact action required. Keep internal
implementation detail behind those outcomes unless requested.

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

## Switching a live profile on this rig

- Measure the target's weights on disk before writing a selection. A profile
  resolution's `expected_vram_mb` can sit far below the real artifact: a 125B
  IQ3_XXS pack is ~76 GB of shards behind a 21.5 GB expectation, so the load
  fills the card, aborts, and restarts. Sum `source_shards[].size` in the
  pack's `conversions.json` (or stat the gguf) and compare against
  `nvidia-smi` free: weights above the largest single pool mean the profile is
  not runnable on this box whatever the resolution advertises.
- A transition that dies mid-load parks the controller inside its
  `--verification-timeout` wait (900 s by default) with no journal lines and a
  frozen route state. It is not dead: at expiry it reconciles to whatever
  `selection.json` holds at that moment, so an edit made during the stall
  applies late. Poll the state file boundedly and do not signal the unit — a
  clean stop exits successfully and `Restart=on-failure` never brings it back.
- The dedicated aux rung needs the aux card free. Reclaim it from a
  co-resident service through that service's own API rather than stopping the
  service (ComfyUI: `POST /free {"unload_models":true,"free_memory":true}`
  after `GET /queue` shows nothing running), then say the cost plainly: that
  service has no headroom while the aux owns the card.
- Prove a switch on both roles — one real chat completion to `active:main` and
  one to `active:aux` — before reporting it active; the aux's first call may
  include model load time.

Exact selection/rung procedure, rollback and recovery sequence:
`references/switch-and-recovery.md`.

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

After a controller restart `/v1/models` reports `residency=unknown` until the first request loads the model (about 20-40 s). That is normal on a quiet service, not a fault: send one small chat request, then re-check residency before diagnosing.

If the platform reports a driver/runtime mismatch, stop the real pressure test. Do not attempt blind driver reloads or disruptive accelerator work.

Full architecture and schema: `README.md`.

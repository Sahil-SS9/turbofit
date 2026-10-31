# Switching the live model, and recovering a failed switch

Control plane on this rig: `/srv/kensei-ai/turbofit/{app,config,state}`.

| File | What it holds |
|---|---|
| `config/selection.json` | `profile_id`, `requested`, `initial_rung_index`, `target_ceiling_index`, `mode` |
| `config/manual-profile*.yaml` | one document per `profile_id`; roles and `rungs[]` |
| `config/manual-runtime-resolutions.json` | per profile per rung: main/aux `model_tag`, `expected_vram_mb`, `gpu` |
| `config/model-recipes.json` | model name → alias, port, gguf path |
| `state/runtime-state.json` | live truth: `active`, `rung_id`, `rung_index`, `routes.main`, `routes.aux` |

Rung semantics: `shared-main` means the aux IS the main model — no second
process is loaded, so nothing small runs. `dedicated-exact` gives the aux its
own backend and port (e.g. main 18081, aux 18082).

## Switch procedure

1. Copy `selection.json` and `state/runtime-state.json` beside themselves with
a dated `.bak` — rollback is restoring that file.
2. Size the target before writing anything: sum `source_shards[].size` in the
pack's `conversions.json`, or `stat` the gguf. Compare with `nvidia-smi`
`memory.free` per card and with the resolution's `expected_vram_mb`. If the
weights exceed the largest single pool, stop — the profile is not loadable
here and the attempt costs the fleet its local model for several minutes.
3. Patch `profile_id` (and `requested`) in `selection.json`. Keep
`target_ceiling_index` at the rung you actually want; a ceiling above what fits
makes the controller retry an impossible expansion every tick.
4. Poll `state/runtime-state.json` for `rung_id`, `routes.main`, `routes.aux`.
The controller ticks about every 2 s but goes silent during a transition, so
the journal is not the progress signal.
5. Prove it: `POST /v1/chat/completions` with `"model":"active:main"` and again
with `"active:aux"`, then read `residency` from `/v1/models`.

```bash
curl -s -X POST http://127.0.0.1:8091/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"active:aux","messages":[{"role":"user","content":"Reply: ok"}],"max_tokens":8,"temperature":0}'
```

Thinking models can answer in `reasoning_content` with empty `content` — accept
either when asserting a reply.

## Failed transition

A model that dies during load leaves the controller inside its verification
wait (`--verification-timeout`, 900 s default): no new journal lines, route
state frozen at the previous rung. At expiry it reconciles to whatever
`selection.json` holds then. Consequences:

- A rollback written during the stall sits unapplied until the wait expires.
  Bound the wait with a poll loop (15 s ticks against the state file), not a
  kill.
- Do not signal the unit. `Restart=on-failure` plus a clean SIGTERM exit means
  the service stays down until someone with privilege starts it.
- No kernel or driver entry is expected; absence of an Xid/OOM line does not
  mean the load succeeded.

## Enabling the dedicated aux

1. `nvidia-smi --query-compute-apps=pid,used_memory` and resolve each PID to a
service to learn who holds the aux card.
2. Free it through the holder's own API where one exists — ComfyUI accepts
`POST /free {"unload_models":true,"free_memory":true}` and keeps serving; check
`GET /queue` first so a running job is not interrupted.
3. Write `initial_rung_index: 0` with `target_ceiling_index: 0`, then poll for
`routes.aux.kind == "local"`.
4. Verify the aux with a real completion, and tell the user the trade: the
freed service now reloads on demand with no reserved headroom.

## Rollback

`cp selection.json.bak-<date> selection.json`, poll until `rung_id` returns to
the previous value, then confirm with one real completion — a restored file is
not proof of a restored service.

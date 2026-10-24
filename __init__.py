"""Turbofit — adaptive local inference provider plugin for Hermes Agent."""
from __future__ import annotations

import json
from pathlib import Path
import sys

_PLUGIN_SRC = Path(__file__).resolve().parent / "src"
if str(_PLUGIN_SRC) not in sys.path:
    sys.path.insert(0, str(_PLUGIN_SRC))

from . import schemas
from . import plugin_tools
from .plugin_tools import (
    handle_configure,
    handle_status,
    hardware_tier_snapshot,
    launch_setup_screen,
    recommendation_snapshot,
)
from .product_ops import _apply, _ladder, serve_status, serve_tailnet, shift_configuration, smoke_local_runtime, update_products

USAGE = "usage: /turbofit [scan|status|tiers|update|shift up|shift down|shift <model>|serve|smoke|intelligence|balanced|speed|setup|aux <model>]"


def check_available() -> bool:
    return True


def _slash_turbofit(raw_args: str) -> str:
    action = str(raw_args or "").strip()
    lowered = action.lower()
    if lowered == "status":
        return handle_status({})
    if lowered in {"", "scan", "rescan", "recommend"}:
        try:
            snapshot = recommendation_snapshot()
        except Exception as exc:
            return json.dumps({"ok": False, "error": str(exc)})
        try:
            ladder = _ladder("intelligence")
            if ladder:
                applied = _apply(
                    str(ladder[0]["profile"]),
                    reason="auto-apply top intelligence recommendation from /turbofit",
                    extra={"snapshot": snapshot},
                )
                return json.dumps(applied)
        except Exception as exc:
            return json.dumps({"ok": False, "error": str(exc), "snapshot": snapshot})
        return json.dumps({"ok": True, "snapshot": snapshot, "message": "no evidence-backed configuration fits this machine"})
    if lowered in {"intelligence", "quality", "balanced", "context", "speed"}:
        try:
            return json.dumps(recommendation_snapshot(lowered))
        except Exception as exc:
            return json.dumps({"ok": False, "error": str(exc)})
    if lowered in {"tiers", "hardware", "hardware-tiers"}:
        try:
            return json.dumps(hardware_tier_snapshot())
        except Exception as exc:
            return json.dumps({"ok": False, "error": str(exc)})
    if lowered == "update":
        try:
            return json.dumps(update_products())
        except Exception as exc:
            return json.dumps({"ok": False, "error": str(exc)})
    if lowered in {"serve", "tailscale", "tailnet"}:
        try:
            return json.dumps(serve_tailnet())
        except Exception as exc:
            return json.dumps({"ok": False, "error": str(exc)})
    if lowered in {"serve status", "tailscale status", "tailnet status"}:
        try:
            return json.dumps(serve_status())
        except Exception as exc:
            return json.dumps({"ok": False, "error": str(exc)})
    if lowered in {"smoke", "check"}:
        try:
            return json.dumps(smoke_local_runtime())
        except Exception as exc:
            return json.dumps({"ok": False, "error": str(exc)})
    if lowered == "shift" or lowered.startswith("shift "):
        target = action[5:].strip() if lowered.startswith("shift") else ""
        try:
            return json.dumps(shift_configuration(target))
        except Exception as exc:
            return json.dumps({"ok": False, "error": str(exc)})
    if lowered in {"setup", "configure"}:
        try:
            return json.dumps({
                "ok": True,
                "setup": launch_setup_screen(),
                "message": "Open Hermes Desktop → Turbofit. Dashboard is deprecated.",
            })
        except Exception as exc:
            return json.dumps({"ok": False, "error": str(exc)})
    if lowered.startswith("aux "):
        model = action[3:].strip()
        if not model:
            return json.dumps({"ok": False, "error": "usage: /turbofit aux <model>"})
        try:
            from turbofit_runtime.allowed_lineup import ALLOWED_AUX
        except Exception as exc:
            return json.dumps({"ok": False, "error": str(exc)})
        if model.lower() not in {m.lower() for m in ALLOWED_AUX}:
            return json.dumps({"ok": False, "error": f"unknown aux model {model!r}; allowed: {ALLOWED_AUX}"})
        try:
            from turbofit_runtime.allowed_lineup import local_aux_for_host
            default_aux = local_aux_for_host(vram_gb=32.0, host_ram_gb=32.0)
        except Exception:
            default_aux = None
        try:
            from hermes_cli.config import load_config
            config = load_config()
            result = plugin_tools.configure_aux_model(config, aux_model=model)
            from hermes_cli.config import save_config
            save_config(result, merge_existing=False)
            return json.dumps({
                "ok": True,
                "aux_model": model,
                "default_aux": default_aux,
                "message": f"Auxiliary model set to {model}. Restart Hermes to apply.",
            })
        except Exception as exc:
            return json.dumps({"ok": False, "error": str(exc)})
    return json.dumps({"ok": False, "error": USAGE})


def register(ctx) -> None:
    """Register Turbofit tools, slash command, and bundled operator skill."""
    ctx.register_tool(
        name="turbofit_status",
        toolset="turbofit",
        schema=schemas.TURBOFIT_STATUS,
        handler=handle_status,
        check_fn=check_available,
        emoji="⚡",
    )
    ctx.register_tool(
        name="turbofit_configure",
        toolset="turbofit",
        schema=schemas.TURBOFIT_CONFIGURE,
        handler=handle_configure,
        check_fn=check_available,
        emoji="⚡",
    )
    ctx.register_command(
        "turbofit",
        _slash_turbofit,
        description="Scan, shift, serve, smoke, or update Turbofit on this machine",
        args_hint="[scan|status|tiers|update|shift up|shift down|shift <model>|serve|smoke|setup]",
    )
    ctx.register_skill("turbofit", Path(__file__).parent / "SKILL.md")
    try:
        from .plugin_tools import activate_slash_commands, ensure_provider_registered

        activate_slash_commands()
        # Fresh-profile heal — ensures every home (including newly created
        # ones like turbosovth/turbosouth) has providers.turbofit so
        # custom:turbofit never fails with Unknown provider on first use.
        try:
            ensure_provider_registered()
        except Exception:
            pass
    except Exception:
        pass


__all__ = ["register"]

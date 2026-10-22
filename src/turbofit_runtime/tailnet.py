"""Tailscale Serve integration for private Turbofit endpoints and dashboard."""
from __future__ import annotations

import json
import subprocess
from collections.abc import Callable
from typing import Any

CommandRunner = Callable[[list[str]], subprocess.CompletedProcess[str]]


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    # Run the tailscale command directly. Tailscale Serve may require elevated
    # privileges on some hosts; in that case the caller receives the (clear)
    # permission error and can re-run with elevation manually.
    # We deliberately do NOT auto-escalate privileges here: an automatic
    # privilege escalation call trips the plugin security scanner and blocks
    # install of the whole plugin. Escalation, when needed, is left to the
    # operator.
    return subprocess.run(command, text=True, capture_output=True, timeout=30, check=False)


def _execute_json(command: list[str], runner: CommandRunner) -> dict[str, Any]:
    result = runner(command)
    if result.returncode:
        message = (result.stderr or result.stdout or "Tailscale command failed").strip()
        raise RuntimeError(message)
    try:
        value = json.loads(result.stdout or "{}")
    except ValueError as exc:
        raise RuntimeError("Tailscale returned invalid JSON") from exc
    if not isinstance(value, dict):
        raise RuntimeError("Tailscale returned a non-object response")
    return value


def tailnet_status(*, command_runner: CommandRunner | None = None) -> dict[str, Any]:
    runner = command_runner or _run
    try:
        status = _execute_json(["tailscale", "status", "--json"], runner)
        serve = _execute_json(["tailscale", "serve", "status", "--json"], runner)
    except (FileNotFoundError, OSError, subprocess.SubprocessError, RuntimeError) as exc:
        return {"available": False, "connected": False, "dns_name": None, "serve": {}, "error": str(exc)}
    raw_self = status.get("Self")
    own: dict[str, Any] = raw_self if isinstance(raw_self, dict) else {}
    dns_name = str(own.get("DNSName") or "").strip().rstrip(".") or None
    connected = status.get("BackendState") == "Running" and dns_name is not None
    return {
        "available": True,
        "connected": connected,
        "dns_name": dns_name,
        "serve": serve,
        "error": None,
    }


def _port(value: int, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 65535:
        raise ValueError(f"{name} must be an integer from 1 to 65535")
    return value


def build_serve_commands(
    *,
    dashboard_local_port: int = 9127,
    provider_local_port: int = 8091,
    dashboard_https_port: int = 9444,
    provider_https_port: int = 9443,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    dashboard_local_port = _port(dashboard_local_port, "dashboard_local_port")
    provider_local_port = _port(provider_local_port, "provider_local_port")
    dashboard_https_port = _port(dashboard_https_port, "dashboard_https_port")
    provider_https_port = _port(provider_https_port, "provider_https_port")
    if dashboard_https_port == provider_https_port:
        raise ValueError("dashboard and provider HTTPS ports must differ")
    return (
        (
            "tailscale", "serve", "--bg", "--yes", f"--https={dashboard_https_port}",
            f"http://127.0.0.1:{dashboard_local_port}",
        ),
        (
            "tailscale", "serve", "--bg", "--yes", f"--https={provider_https_port}",
            f"http://127.0.0.1:{provider_local_port}",
        ),
    )


def publish_tailnet(
    *,
    dashboard_local_port: int = 9127,
    provider_local_port: int = 8091,
    dashboard_https_port: int = 9444,
    provider_https_port: int = 9443,
    command_runner: CommandRunner | None = None,
) -> dict[str, Any]:
    runner = command_runner or _run
    status = tailnet_status(command_runner=runner)
    if not status["connected"]:
        raise RuntimeError(status.get("error") or "Tailscale is not connected")
    commands = build_serve_commands(
        dashboard_local_port=dashboard_local_port,
        provider_local_port=provider_local_port,
        dashboard_https_port=dashboard_https_port,
        provider_https_port=provider_https_port,
    )
    dns_name = status["dns_name"]
    existing_web = status.get("serve", {}).get("Web", {})
    if not isinstance(existing_web, dict):
        existing_web = {}
    intended = {
        dashboard_https_port: f"http://127.0.0.1:{dashboard_local_port}",
        provider_https_port: f"http://127.0.0.1:{provider_local_port}",
    }
    for https_port, proxy in intended.items():
        route = existing_web.get(f"{dns_name}:{https_port}")
        if route is None:
            continue
        expected_route = {"Handlers": {"/": {"Proxy": proxy}}}
        if route != expected_route:
            raise RuntimeError(
                f"Tailscale Serve port {https_port} is already configured; refusing to overwrite it"
            )
    for command in commands:
        result = runner(list(command))
        if result.returncode:
            message = (result.stderr or result.stdout or "tailscale serve failed").strip()
            raise RuntimeError(message)
    return {
        "ok": True,
        "dns_name": dns_name,
        "dashboard_url": f"https://{dns_name}:{dashboard_https_port}/",
        "provider_base_url": f"https://{dns_name}:{provider_https_port}/v1",
        "commands": [list(command) for command in commands],
    }


def ensure_tailnet(
    *,
    dashboard_local_port: int = 9127,
    provider_local_port: int = 8091,
    dashboard_https_port: int = 9444,
    provider_https_port: int = 9443,
    command_runner: CommandRunner | None = None,
) -> dict[str, Any]:
    """Auto-configure Tailscale Serve if available.

    Returns a dict with:
    - available: bool — tailscale binary found
    - connected: bool — tailscale backend running
    - published: bool — serve routes were published
    - dns_name: str | None — tailnet DNS name
    - dashboard_url: str | None — HTTPS dashboard URL
    - provider_base_url: str | None — HTTPS provider URL
    - error: str | None — error message if not available/connected
    """
    runner = command_runner or _run
    status = tailnet_status(command_runner=runner)
    if not status["available"]:
        return {
            "available": False,
            "connected": False,
            "published": False,
            "dns_name": None,
            "dashboard_url": None,
            "provider_base_url": None,
            "error": status.get("error") or "Tailscale is not installed",
        }
    if not status["connected"]:
        return {
            "available": True,
            "connected": False,
            "published": False,
            "dns_name": None,
            "dashboard_url": None,
            "provider_base_url": None,
            "error": "Tailscale is not connected (run: tailscale up)",
        }
    try:
        publication = publish_tailnet(
            dashboard_local_port=dashboard_local_port,
            provider_local_port=provider_local_port,
            dashboard_https_port=dashboard_https_port,
            provider_https_port=provider_https_port,
            command_runner=runner,
        )
        return {
            "available": True,
            "connected": True,
            "published": True,
            "dns_name": publication["dns_name"],
            "dashboard_url": publication["dashboard_url"],
            "provider_base_url": publication["provider_base_url"],
            "error": None,
        }
    except Exception as exc:
        return {
            "available": True,
            "connected": True,
            "published": False,
            "dns_name": status.get("dns_name"),
            "dashboard_url": None,
            "provider_base_url": None,
            "error": str(exc),
        }


def discover_turbofit_peers(
    *,
    provider_port: int = 8091,
    timeout_s: float = 2.0,
    command_runner: CommandRunner | None = None,
    probe: Callable[[str, float], bool] | None = None,
) -> list[dict[str, Any]]:
    """Discover TurboFit gateways running on other machines in the tailnet.

    Enumerates online Tailscale peers and probes each for a TurboFit
    gateway on ``provider_port``. Returns a list of peers that answered,
    each with ``host`` (MagicDNS name), ``port`` and ``url``.

    This is what lets the model picker show models from the user's other
    machines without any manual peer configuration.
    """
    import socket

    runner = command_runner or _run

    def default_probe(host: str, timeout: float) -> bool:
        try:
            with socket.create_connection((host, provider_port), timeout=timeout):
                return True
        except OSError:
            return False

    probe_fn = probe or default_probe

    try:
        status = _execute_json(["tailscale", "status", "--json"], runner)
    except (FileNotFoundError, OSError, subprocess.SubprocessError, RuntimeError):
        return []

    peers: list[dict[str, Any]] = []
    raw_peer_map = status.get("Peer") or {}
    if not isinstance(raw_peer_map, dict):
        return []
    for _key, raw_peer in raw_peer_map.items():
        if not isinstance(raw_peer, dict):
            continue
        if raw_peer.get("Online") is not True:
            continue
        dns_name = str(raw_peer.get("DNSName") or "").strip().rstrip(".")
        if not dns_name:
            continue
        if not probe_fn(dns_name, timeout_s):
            continue
        peers.append({
            "host": dns_name,
            "port": provider_port,
            "url": f"http://{dns_name}:{provider_port}",
            "os": raw_peer.get("OS"),
        })
    return peers

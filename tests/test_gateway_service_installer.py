"""Gateway service installation across platforms.

The gateway must be reachable on the tailnet for federated model
discovery, and on macOS the LaunchAgent must carry an explicit PATH or
the tailscale CLI is invisible and discovery silently returns nothing.
"""
from __future__ import annotations

import importlib.util
import plistlib
from importlib.machinery import SourceFileLoader
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _module():
    path = ROOT / "scripts/install-controller-service"
    loader = SourceFileLoader("install_controller_service", str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    assert spec
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def test_gateway_unit_binds_for_tailnet_reachability() -> None:
    unit = _module().gateway_unit_text()
    # Without this no peer can ever discover the gateway.
    assert "TURBOFIT_GATEWAY_HOST=0.0.0.0" in unit
    assert "Restart=on-failure" in unit


def test_launchd_plist_sets_path_for_tailscale_cli() -> None:
    plist = _module().gateway_launchd_plist()
    env = plist["EnvironmentVariables"]
    # launchd's default PATH omits /usr/local/bin, where tailscale lives.
    assert "/usr/local/bin" in env["PATH"]
    assert env["TURBOFIT_PEER_DISCOVERY"] == "1"
    assert plist["RunAtLoad"] is True
    assert plist["KeepAlive"] is True


def test_launchd_plist_is_serializable_and_targets_the_gateway() -> None:
    plist = _module().gateway_launchd_plist()
    dumped = plistlib.dumps(plist)
    assert plistlib.loads(dumped)["Label"] == "com.hermes.turbofit-gateway"
    assert any("turbofit-gateway.py" in part for part in plist["ProgramArguments"])

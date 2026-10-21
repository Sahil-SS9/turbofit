from __future__ import annotations

import json
import subprocess

import pytest

from turbofit_runtime.tailnet import build_serve_commands, publish_tailnet, tailnet_status


def completed(command: list[str], stdout: str = "", returncode: int = 0, stderr: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(command, returncode, stdout=stdout, stderr=stderr)


def test_tailnet_status_reports_dns_and_existing_serve_routes() -> None:
    calls: list[list[str]] = []

    def run(command: list[str]) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        if command == ["tailscale", "status", "--json"]:
            return completed(command, json.dumps({"BackendState": "Running", "Self": {"DNSName": "host.example.ts.net."}}))
        return completed(command, json.dumps({"TCP": {"443": {"HTTPS": True}}, "Web": {}}))

    status = tailnet_status(command_runner=run)

    assert status["available"] is True
    assert status["connected"] is True
    assert status["dns_name"] == "host.example.ts.net"
    assert status["serve"]["TCP"]["443"]["HTTPS"] is True
    assert calls == [["tailscale", "status", "--json"], ["tailscale", "serve", "status", "--json"]]


def test_build_serve_commands_uses_distinct_https_ports_without_shell() -> None:
    commands = build_serve_commands(
        dashboard_local_port=9127,
        provider_local_port=8091,
        dashboard_https_port=9444,
        provider_https_port=9443,
    )

    assert commands == (
        ("tailscale", "serve", "--bg", "--yes", "--https=9444", "http://127.0.0.1:9127"),
        ("tailscale", "serve", "--bg", "--yes", "--https=9443", "http://127.0.0.1:8091"),
    )


def test_publish_refuses_to_overwrite_an_unrelated_existing_serve_route() -> None:
    calls: list[list[str]] = []

    def run(command: list[str]) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        if command == ["tailscale", "status", "--json"]:
            return completed(command, json.dumps({"BackendState": "Running", "Self": {"DNSName": "host.example.ts.net."}}))
        if command == ["tailscale", "serve", "status", "--json"]:
            return completed(command, json.dumps({
                "Web": {"host.example.ts.net:9444": {"Handlers": {"/": {"Proxy": "http://127.0.0.1:3000"}}}}
            }))
        return completed(command)

    with pytest.raises(RuntimeError, match="refusing to overwrite"):
        publish_tailnet(command_runner=run)

    assert len(calls) == 2


def test_run_escalates_via_noninteractive_sudo_only_when_available(monkeypatch) -> None:
    import turbofit_runtime.tailnet as tn

    calls: list[list[str]] = []
    sudo_available = {"value": True}

    def fake_run(command, **kwargs):
        calls.append(list(command))
        if command[:2] == ["sudo", "-n"]:
            # sudo -n true succeeds when sudo is available
            return completed(command, returncode=0)
        if command[:1] == ["sudo"]:
            return completed(command, stdout="ok")
        return completed(command, returncode=1, stderr="permission denied (root required)")

    monkeypatch.setattr(tn.subprocess, "run", fake_run)
    result = tn._run(["tailscale", "serve", "--bg", "--yes", "--https=9443", "http://127.0.0.1:8091"])
    assert result.returncode == 0
    # plain attempt -> probe -> sudo attempt
    assert calls[0][0] == "tailscale"
    assert calls[1] == ["sudo", "-n", "true"]
    assert calls[2][:2] == ["sudo", "-n"]
    assert calls[2][2:] == ["tailscale", "serve", "--bg", "--yes", "--https=9443", "http://127.0.0.1:8091"]

    # Without sudo (probe fails) the original failure is returned untouched.
    calls.clear()
    def fake_run_no_sudo(command, **kwargs):
        calls.append(list(command))
        if command[:2] == ["sudo", "-n"]:
            return completed(command, returncode=1, stderr="sudo: a password is required")
        return completed(command, returncode=1, stderr="permission denied")
    monkeypatch.setattr(tn.subprocess, "run", fake_run_no_sudo)
    result = tn._run(["tailscale", "serve", "--bg", "--yes", "--https=9443", "http://127.0.0.1:8091"])
    assert result.returncode == 1
    assert calls == [
        ["tailscale", "serve", "--bg", "--yes", "--https=9443", "http://127.0.0.1:8091"],
        ["sudo", "-n", "true"],
    ]


def test_publish_tailnet_returns_shareable_dashboard_and_provider_urls() -> None:
    calls: list[list[str]] = []

    def run(command: list[str]) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        if command == ["tailscale", "status", "--json"]:
            return completed(command, json.dumps({"BackendState": "Running", "Self": {"DNSName": "host.example.ts.net."}}))
        if command == ["tailscale", "serve", "status", "--json"]:
            return completed(command, "{}")
        return completed(command)

    result = publish_tailnet(command_runner=run)

    assert result["dashboard_url"] == "https://host.example.ts.net:9444/"
    assert result["provider_base_url"] == "https://host.example.ts.net:9443/v1"
    assert calls[-2:] == [
        ["tailscale", "serve", "--bg", "--yes", "--https=9444", "http://127.0.0.1:9127"],
        ["tailscale", "serve", "--bg", "--yes", "--https=9443", "http://127.0.0.1:8091"],
    ]

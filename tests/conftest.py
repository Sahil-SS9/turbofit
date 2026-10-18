"""Shared pytest configuration.

Disables live Tailscale peer discovery for the whole test session so the
suite is hermetic: tests must never depend on which machines happen to be
reachable on the developer's tailnet. Individual tests that exercise peer
discovery monkeypatch the probe directly.
"""
import os

os.environ.setdefault("TURBOFIT_PEER_DISCOVERY", "0")

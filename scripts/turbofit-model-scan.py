#!/usr/bin/env python3
"""Scan Nous for available free models and write a validated fallback list.

Reads the Hermes metadata cache (updated by every Hermes session), cross-references
against known-free model IDs, and writes a Turbofit-consumable fallback manifest.
Safe to run repeatedly — stale entries are dropped, new ones are appended.
"""
import json
import os
import sys
import time
from pathlib import Path

HOME = os.path.expanduser("~")
CATALOG_PATH = os.environ.get("TURBOFIT_CATALOG", f"{HOME}/.config/turbofit/models.yaml")
FALLBACK_PATH = os.environ.get(
    "TURBOFIT_FALLBACK_MANIFEST",
    f"{HOME}/.config/turbofit/fallback-models.yaml",
)
NOUS_CACHE = f"{HOME}/.hermes/cache/endpoint_model_metadata.json"
NOUS_CONFIG = f"{HOME}/.hermes/providers/nous/config.yaml"
FREE_TAGS = {":free"}

# Hard exclusion list — models known to be dead or unsuitable for aux fallback
BLOCKLIST = {
    "stealth/ox-alpha",  # retired
    "tencent/hy3:free",  # 404
}


def _load_json_safe(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return {}


def _load_yaml_safe(path):
    try:
        import yaml
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def discover_free_models(metadata_cache):
    """Extract free models from the Nous metadata cache."""
    free = {}
    for ep, meta in metadata_cache.items():
        if "nous" not in ep:
            continue
        for model_id, model_meta in (meta.get("models") or {}).items():
            if model_id in BLOCKLIST:
                continue
            tags = model_meta.get("tags") or []
            desc = (model_meta.get("description") or "").lower()
            is_free = any(t in model_id.lower() for t in [":free"]) or "free" in desc
            if not is_free:
                continue
            free[model_id] = {
                "context_length": model_meta.get("context_length", 0),
                "description": (model_meta.get("description") or "").strip()[:120],
                "free": True,
            }
    return free


def main():
    # Load Nous metadata cache
    metadata = _load_json_safe(NOUS_CACHE)
    if not metadata:
        print("FAIL: Nous metadata cache not found", file=sys.stderr)
        sys.exit(1)

    free_models = discover_free_models(metadata)
    if not free_models:
        print("FAIL: No free models found in Nous cache", file=sys.stderr)
        sys.exit(1)

    # Build manifest
    manifest = {
        "schema": "turbofit.fallback-manifest/v1",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "provider": "nous",
        "models": {
            mid: {
                "context_length": info["context_length"],
                "description": info["description"],
                "role": "aux",  # free models are fallback aux, never main
                "source": "nous-scan",
            }
            for mid, info in sorted(free_models.items())
        },
    }

    # Write
    Path(FALLBACK_PATH).parent.mkdir(parents=True, exist_ok=True)
    import yaml
    with open(FALLBACK_PATH, "w") as f:
        yaml.dump(manifest, f, default_flow_style=False, sort_keys=False)

    # Print summary
    count = len(manifest["models"])
    print(f"OK: {count} free models → {FALLBACK_PATH}")
    for mid in list(manifest["models"].keys())[:5]:
        ctx = manifest["models"][mid]["context_length"]
        print(f"  {mid} (ctx={ctx})")
    if count > 5:
        print(f"  ... and {count - 5} more")

    return manifest


if __name__ == "__main__":
    main()

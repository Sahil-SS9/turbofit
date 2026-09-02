# Verification procedure — turbofit

Status: NO AUTOMATED TESTS YET. Honest baseline created by the Foundry
estate remediation (2026-08-23).

What must be tested before any maturity claim is made:
1. Trigger routing: should-fire prompts fire; near-miss prompts stay silent.
2. Outcome: golden cases pass against a deterministic verifier.
3. Regression: previously correct behaviours remain green after edits.

Until tests land here, any maturity language in this skill is UNSUPPORTED.

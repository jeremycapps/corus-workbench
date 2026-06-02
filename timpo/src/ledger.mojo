# Minimal ledger-related primitives that support Timpo retention.
# Full Corus ledger bundles live in fs/ and Legacy, not in this wire engine.

def ledger_entry_key(entry_id: String) -> String:
    return entry_id

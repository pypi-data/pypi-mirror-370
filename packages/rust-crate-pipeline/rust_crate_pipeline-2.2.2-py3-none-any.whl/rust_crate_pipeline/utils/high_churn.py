from __future__ import annotations

from typing import Set


HIGH_CHURN_CRATES: Set[str] = {
    # Core ecosystem with frequent minor releases
    "tokio",
    "axum",
    "serde",
    "serde_json",
    "regex",
    "rustls",
    "hyper",
    "tower",
    "reqwest",
    "openssl",
    "clap",
    "tracing",
    "thiserror",
}


def is_high_churn(crate_name: str) -> bool:
    return crate_name in HIGH_CHURN_CRATES

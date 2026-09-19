"""Runtime configuration. Everything is overridable via environment variables."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


@dataclass
class Config:
    # LLM backend: "anthropic" (Anthropic SDK, needs ANTHROPIC_API_KEY) or "claude_cli" (`claude -p`, uses your Claude Code login)
    backend: str = os.environ.get("LEAN_AGENT_BACKEND", "anthropic")
    base_url: str | None = os.environ.get("LEAN_AGENT_BASE_URL") or None  # optional Anthropic-compatible proxy
    model: str = os.environ.get("LEAN_AGENT_MODEL", "claude-opus-4-8")
    critic_model: str = os.environ.get("LEAN_AGENT_CRITIC_MODEL", "") or os.environ.get(
        "LEAN_AGENT_MODEL", "claude-opus-4-8"
    )
    max_tokens: int = 4096

    # Loop budgets
    max_attempts: int = int(os.environ.get("LEAN_AGENT_MAX_ATTEMPTS", "16"))
    stall_after: int = int(os.environ.get("LEAN_AGENT_STALL_AFTER", "4"))  # 0 disables
    probes_per_attempt: int = int(os.environ.get("LEAN_AGENT_PROBES", "6"))  # 0 disables the probe tool
    explain_project: bool = os.environ.get("LEAN_AGENT_EXPLAIN_PROJECT", "1") != "0"  # EXPLANATION.md at project completion
    explain: bool = os.environ.get("LEAN_AGENT_EXPLAIN", "1") != "0"
    lean_timeout_s: int = int(os.environ.get("LEAN_AGENT_LEAN_TIMEOUT", "300"))

    # Paths
    lean_project: Path = ROOT / "lean_env"
    lean_src_dir: Path = ROOT / "lean_env" / "LeanEnv"
    runs_dir: Path = ROOT / "runs"
    elan_bin: Path = Path.home() / ".elan" / "bin"

    # Proof text that is never acceptable, regardless of what Lean says.
    banned_tokens: tuple[str, ...] = ("sorry", "admit", "native_decide", "axiom ", "opaque ", "unsafe ", "implemented_by", "extern ", "partial def")

    extra_env: dict = field(default_factory=dict)

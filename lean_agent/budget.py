"""Dollar budget enforcement. Prices are list prices per million tokens; matched by substring on model id."""
from __future__ import annotations

PRICES_PER_M = [  # (substring, input $/M, output $/M) -- first match wins
    ("opus-4-8", 5.0, 25.0), ("opus-4-7", 5.0, 25.0), ("opus-4-6", 5.0, 25.0), ("opus-5", 5.0, 25.0),
    ("sonnet-5", 2.0, 10.0), ("sonnet-4-6", 3.0, 15.0), ("haiku-4-5", 1.0, 5.0),
    ("fable", 10.0, 50.0), ("best_coding", 5.0, 25.0),
]
DEFAULT_PRICE = (5.0, 25.0)


def price_for(model: str) -> tuple[float, float]:
    m = (model or "").lower()
    for sub, i, o in PRICES_PER_M:
        if sub in m:
            return i, o
    return DEFAULT_PRICE


def call_cost(call: dict) -> float:
    i, o = price_for(call.get("model", ""))
    return call.get("input_tokens", 0) * i / 1e6 + call.get("output_tokens", 0) * o / 1e6


class BudgetExceeded(RuntimeError):
    pass


class BudgetTracker:
    """Attach to an LLMClient via `llm.on_call = tracker.on_call`. Raises once the cap is hit."""

    def __init__(self, cap_usd: float, spent_usd: float = 0.0):
        self.cap = cap_usd
        self.spent = spent_usd
        self.calls = 0

    def on_call(self, call: dict):
        self.spent += call_cost(call)
        self.calls += 1
        if self.spent >= self.cap:
            raise BudgetExceeded(f"budget cap ${self.cap:.2f} reached (spent ${self.spent:.2f} over {self.calls} calls)")

    def remaining(self) -> float:
        return max(0.0, self.cap - self.spent)

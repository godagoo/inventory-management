"""Restocking recommendations and submitted restock orders.

Restock orders are purchases from suppliers, not customer sales, so they are
kept apart from the orders in mock_data. They live in memory and reset when
the server restarts.
"""

from datetime import datetime, timedelta, timezone

LEAD_TIME_DAYS = 10
TREND_PRIORITY = {"increasing": 0, "stable": 1}

restock_orders: list[dict] = []


def _shortfall(forecast: dict) -> int:
    return forecast["forecasted_demand"] - forecast["current_demand"]


def _restock_candidates(forecasts: list[dict]) -> list[dict]:
    """Return forecasts worth restocking, in the order budget is spent on them."""
    candidates = [
        forecast for forecast in forecasts
        if _shortfall(forecast) > 0 and forecast["trend"] in TREND_PRIORITY
    ]
    return sorted(candidates, key=lambda forecast: (
        TREND_PRIORITY[forecast["trend"]],
        -_shortfall(forecast),
        forecast["item_sku"],
    ))


def _to_cents(amount: float) -> int:
    return round(amount * 100)


def _cost(quantity: int, unit_cost: float) -> float:
    return round(quantity * unit_cost, 2)


def recommend_restock(forecasts: list[dict], budget: float) -> dict:
    """Spend the budget on the forecast items that need restocking most."""
    candidates = _restock_candidates(forecasts)
    remaining = budget
    items = []

    for forecast in candidates:
        unit_cost = forecast["unit_cost"]
        # An item that doesn't fit doesn't end the walk: a cheaper item further
        # down the list may still be affordable with what's left. Whole cents
        # keep float division from leaving an exact budget one unit short.
        affordable = _to_cents(remaining) // _to_cents(unit_cost)
        quantity = min(_shortfall(forecast), affordable)
        if quantity == 0:
            continue

        line_total = _cost(quantity, unit_cost)
        remaining = round(remaining - line_total, 2)
        items.append({
            "sku": forecast["item_sku"],
            "name": forecast["item_name"],
            "trend": forecast["trend"],
            "quantity": quantity,
            "quantity_needed": _shortfall(forecast),
            "unit_cost": unit_cost,
            "line_total": line_total,
        })

    return {
        "budget": budget,
        "items": items,
        "total_cost": round(budget - remaining, 2),
        "remaining_budget": remaining,
        "full_cost": round(sum(
            _cost(_shortfall(forecast), forecast["unit_cost"])
            for forecast in candidates
        ), 2),
    }


def create_restock_order(recommendation: dict) -> dict:
    """Record a recommendation as a submitted order."""
    ordered_at = datetime.now(timezone.utc)
    order = {
        "id": str(len(restock_orders) + 1),
        "order_number": f"RST-{ordered_at.year}-{len(restock_orders) + 1:04d}",
        "items": [
            {
                "sku": item["sku"],
                "name": item["name"],
                "quantity": item["quantity"],
                "unit_price": item["unit_cost"],
            }
            for item in recommendation["items"]
        ],
        "status": "Submitted",
        "order_date": ordered_at.isoformat(timespec="seconds"),
        "lead_time_days": LEAD_TIME_DAYS,
        "expected_delivery": (
            ordered_at + timedelta(days=LEAD_TIME_DAYS)
        ).isoformat(timespec="seconds"),
        "total_value": recommendation["total_cost"],
    }
    restock_orders.append(order)
    return order

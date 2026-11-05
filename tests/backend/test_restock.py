"""
Tests for restocking API endpoints.
"""
from datetime import datetime, timedelta

import pytest

from restock import recommend_restock, restock_orders


RECOMMENDATIONS_URL = "/api/restock/recommendations"
ORDERS_URL = "/api/restock-orders"


def forecast(sku, current, forecasted, trend, unit_cost):
    """Build a forecast row with only the fields the logic reads."""
    return {
        "item_sku": sku,
        "item_name": f"Item {sku}",
        "current_demand": current,
        "forecasted_demand": forecasted,
        "trend": trend,
        "unit_cost": unit_cost,
    }


@pytest.fixture(autouse=True)
def clear_restock_orders():
    """Orders are module-level state, so reset them around each test."""
    restock_orders.clear()
    yield
    restock_orders.clear()


class TestRecommendRestock:
    """Test suite for the recommendation logic."""

    def test_increasing_items_rank_before_stable(self):
        """Test that rising demand is bought first, whatever the gap size."""
        result = recommend_restock([
            forecast("STABLE", 0, 500, "stable", 1.0),
            forecast("RISING", 0, 10, "increasing", 1.0),
        ], 1000)

        assert [item["sku"] for item in result["items"]] == ["RISING", "STABLE"]

    def test_larger_gap_ranks_first_within_a_trend(self):
        """Test the tie-break inside one trend."""
        result = recommend_restock([
            forecast("SMALL", 0, 10, "increasing", 1.0),
            forecast("LARGE", 0, 20, "increasing", 1.0),
        ], 1000)

        assert [item["sku"] for item in result["items"]] == ["LARGE", "SMALL"]

    def test_excludes_items_without_a_shortfall(self):
        """Test that falling or flat demand is never recommended."""
        result = recommend_restock([
            forecast("FALLING", 50, 35, "decreasing", 1.0),
            forecast("FLAT", 50, 50, "stable", 1.0),
            forecast("ODD", 10, 20, "decreasing", 1.0),
        ], 1000)

        assert result["items"] == []
        assert result["full_cost"] == 0

    def test_partial_quantity_when_budget_runs_out(self):
        """Test that an item is bought in part when it doesn't fully fit."""
        result = recommend_restock([forecast("A", 0, 10, "increasing", 3.0)], 10)

        assert result["items"][0]["quantity"] == 3
        assert result["total_cost"] == 9
        assert result["remaining_budget"] == 1

    def test_budget_too_small_for_first_item_still_buys_cheaper_one(self):
        """Test that the walk continues past an unaffordable item."""
        result = recommend_restock([
            forecast("COSTLY", 0, 10, "increasing", 100.0),
            forecast("CHEAP", 0, 5, "stable", 2.0),
        ], 10)

        assert [item["sku"] for item in result["items"]] == ["CHEAP"]
        assert result["items"][0]["quantity"] == 5

    def test_exact_budget_is_not_lost_to_float_division(self):
        """Test a price and budget that divide inexactly as floats."""
        result = recommend_restock([forecast("A", 0, 3, "increasing", 24.99)], 74.97)

        assert result["items"][0]["quantity"] == 3
        assert result["remaining_budget"] == 0


class TestRecommendationEndpoint:
    """Test suite for the recommendations endpoint."""

    def test_total_never_exceeds_budget(self, client):
        """Test a spread of budgets against the real forecast data."""
        for budget in [1, 50, 500, 1234.56, 5000]:
            data = client.get(RECOMMENDATIONS_URL, params={"budget": budget}).json()

            assert data["total_cost"] <= budget
            assert data["remaining_budget"] == pytest.approx(budget - data["total_cost"])

    def test_zero_budget_recommends_nothing(self, client):
        """Test the bottom of the slider."""
        response = client.get(RECOMMENDATIONS_URL, params={"budget": 0})

        assert response.status_code == 200
        assert response.json()["items"] == []
        assert response.json()["full_cost"] > 0

    def test_full_cost_budget_buys_everything(self, client):
        """Test the top of the slider against the real forecast data."""
        full_cost = client.get(RECOMMENDATIONS_URL, params={"budget": 0}).json()["full_cost"]
        data = client.get(RECOMMENDATIONS_URL, params={"budget": full_cost}).json()

        assert data["total_cost"] == full_cost
        assert data["remaining_budget"] == 0
        assert all(item["quantity"] == item["quantity_needed"] for item in data["items"])

    def test_negative_budget_is_rejected(self, client):
        """Test budget validation."""
        response = client.get(RECOMMENDATIONS_URL, params={"budget": -1})

        assert response.status_code == 422

    def test_missing_budget_is_rejected(self, client):
        """Test that budget is required."""
        assert client.get(RECOMMENDATIONS_URL).status_code == 422


class TestRestockOrderEndpoints:
    """Test suite for submitting and listing restock orders."""

    def test_create_order(self, client):
        """Test the fields of a submitted order."""
        response = client.post(ORDERS_URL, json={"budget": 2000})

        assert response.status_code == 201
        order = response.json()
        assert order["status"] == "Submitted"
        assert order["lead_time_days"] == 10
        assert order["order_number"].startswith("RST-")
        assert order["items"]
        assert order["total_value"] <= 2000

    def test_delivery_is_ten_days_after_order(self, client):
        """Test the delivery date calculation."""
        order = client.post(ORDERS_URL, json={"budget": 2000}).json()

        ordered_at = datetime.fromisoformat(order["order_date"])
        expected = datetime.fromisoformat(order["expected_delivery"])
        assert expected - ordered_at == timedelta(days=10)

    def test_order_matches_recommendation(self, client):
        """Test that the server places what it recommended."""
        recommendation = client.get(RECOMMENDATIONS_URL, params={"budget": 2000}).json()
        order = client.post(ORDERS_URL, json={"budget": 2000}).json()

        assert order["total_value"] == recommendation["total_cost"]
        assert [item["sku"] for item in order["items"]] == [
            item["sku"] for item in recommendation["items"]
        ]

    def test_orders_list_newest_first(self, client):
        """Test listing order and unique order numbers."""
        first = client.post(ORDERS_URL, json={"budget": 1000}).json()
        second = client.post(ORDERS_URL, json={"budget": 2000}).json()

        listed = client.get(ORDERS_URL).json()

        assert [order["id"] for order in listed] == [second["id"], first["id"]]
        assert first["order_number"] != second["order_number"]

    def test_orders_start_empty(self, client):
        """Test the list before any order is placed."""
        response = client.get(ORDERS_URL)

        assert response.status_code == 200
        assert response.json() == []

    def test_budget_that_buys_nothing_is_rejected(self, client):
        """Test that an empty order can't be placed."""
        response = client.post(ORDERS_URL, json={"budget": 0})

        assert response.status_code == 400
        assert client.get(ORDERS_URL).json() == []

    def test_negative_budget_is_rejected(self, client):
        """Test request validation."""
        assert client.post(ORDERS_URL, json={"budget": -5}).status_code == 422

    def test_customer_orders_are_unchanged(self, client):
        """Test that restock orders stay out of customer orders."""
        before = client.get("/api/orders").json()

        client.post(ORDERS_URL, json={"budget": 2000})

        assert client.get("/api/orders").json() == before


class TestDemandUnitCost:
    """Test suite for the price added to demand forecasts."""

    def test_every_forecast_has_a_positive_unit_cost(self, client):
        """Test that the recommendation logic can price every forecast."""
        data = client.get("/api/demand").json()

        assert data
        assert all(item["unit_cost"] > 0 for item in data)

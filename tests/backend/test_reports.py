"""
Tests for the report endpoints and their filters.
"""
import pytest

from main import orders


def orders_matching(**fields):
    return [o for o in orders if all(o.get(k) == v for k, v in fields.items())]


class TestQuarterlyReports:
    """Test suite for /api/reports/quarterly."""

    def test_unfiltered_covers_every_order(self, client):
        data = client.get("/api/reports/quarterly").json()

        assert [q["quarter"] for q in data] == sorted(q["quarter"] for q in data)
        assert sum(q["total_orders"] for q in data) == len(orders)

    def test_warehouse_filter(self, client):
        data = client.get("/api/reports/quarterly", params={"warehouse": "Tokyo"}).json()

        assert sum(q["total_orders"] for q in data) == len(orders_matching(warehouse="Tokyo"))

    def test_month_filter_returns_only_that_quarter(self, client):
        data = client.get("/api/reports/quarterly", params={"month": "2025-01"}).json()

        assert [q["quarter"] for q in data] == ["Q1-2025"]

    def test_status_filter_gives_full_fulfillment(self, client):
        data = client.get("/api/reports/quarterly", params={"status": "Delivered"}).json()

        assert data
        assert all(q["fulfillment_rate"] == 100.0 for q in data)

    def test_all_means_no_filter(self, client):
        unfiltered = client.get("/api/reports/quarterly").json()
        filtered = client.get(
            "/api/reports/quarterly",
            params={"warehouse": "all", "category": "all", "status": "all", "month": "all"},
        ).json()

        assert filtered == unfiltered

    def test_no_matches_returns_empty_list(self, client):
        response = client.get("/api/reports/quarterly", params={"warehouse": "Nowhere"})

        assert response.status_code == 200
        assert response.json() == []


class TestMonthlyTrends:
    """Test suite for /api/reports/monthly-trends."""

    def test_unfiltered_covers_every_order(self, client):
        data = client.get("/api/reports/monthly-trends").json()

        assert [m["month"] for m in data] == sorted(m["month"] for m in data)
        assert sum(m["order_count"] for m in data) == len(orders)

    def test_month_filter_returns_one_month(self, client):
        data = client.get("/api/reports/monthly-trends", params={"month": "2025-03"}).json()
        expected = [o for o in orders if o["order_date"].startswith("2025-03")]

        assert [m["month"] for m in data] == ["2025-03"]
        assert data[0]["order_count"] == len(expected)
        assert data[0]["revenue"] == pytest.approx(sum(o["total_value"] for o in expected))

    def test_filters_combine(self, client):
        params = {"warehouse": "London", "category": orders[0]["category"], "status": "Shipped"}
        data = client.get("/api/reports/monthly-trends", params=params).json()
        expected = [
            o for o in orders_matching(warehouse="London", status="Shipped")
            if o["category"].lower() == params["category"].lower()
        ]

        assert sum(m["order_count"] for m in data) == len(expected)

    def test_no_matches_returns_empty_list(self, client):
        response = client.get("/api/reports/monthly-trends", params={"category": "Nothing"})

        assert response.status_code == 200
        assert response.json() == []

from decimal import Decimal

import pytest
from django.db import IntegrityError, transaction
from django.urls import reverse

from .models import Instrument


@pytest.fixture
def instruments(db):
    return [
        Instrument.objects.create(
            symbol="NVDA",
            name="NVIDIA Corporation",
            exchange="NASDAQ",
            sector="Technology",
            industry="Semiconductors",
            market_cap=Decimal("3000000000000.00"),
        ),
        Instrument.objects.create(
            symbol="JPM",
            name="JPMorgan Chase & Co.",
            exchange="NYSE",
            sector="Financial Services",
            industry="Banks",
            is_active=False,
        ),
    ]


@pytest.mark.django_db
def test_health_endpoints(client):
    assert client.get(reverse("health-live")).json() == {"status": "ok"}
    response = client.get(reverse("health-ready"))
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


def test_openapi_schema(client):
    assert client.get(reverse("schema")).status_code == 200


@pytest.mark.django_db
def test_duplicate_symbol_exchange_is_rejected():
    Instrument.objects.create(symbol="AMD", name="AMD", exchange="NASDAQ")
    with pytest.raises(IntegrityError), transaction.atomic():
        Instrument.objects.create(symbol="AMD", name="Duplicate", exchange="NASDAQ")


@pytest.mark.django_db
def test_instrument_api_is_paginated_filterable_and_read_only(client, instruments):
    response = client.get(reverse("instrument-list"), {"sector": "technology", "active": "true"})
    assert response.status_code == 200
    assert response.json()["count"] == 1
    assert response.json()["results"][0]["symbol"] == "NVDA"
    assert client.get(reverse("instrument-detail", args=[instruments[0].pk])).status_code == 200
    assert client.post(reverse("instrument-list"), {"symbol": "ARM"}).status_code == 405

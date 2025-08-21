from unittest.mock import Mock

import pytest
import requests

from sepp.scripts import geocoding as mut


@pytest.fixture(autouse=True)
def fake_logger(monkeypatch: Mock) -> Mock:
    fake = Mock()
    monkeypatch.setattr(mut, "logger", fake)
    return fake


@pytest.fixture
def fake_client(monkeypatch: Mock) -> Mock:
    client = Mock()

    monkeypatch.setattr(mut.googlemaps, "Client", lambda key: client)
    return client


def test_geocode_with_nominatim_city() -> None:
    """Test Nominatim geocoding with a valid address."""
    cues = ["Reutlingen"]
    result = mut.geocode_with_nominatim(cues)
    assert isinstance(result, dict)
    assert "city" in result
    assert "country" in result
    assert "zip" in result
    assert result["city"] == "Reutlingen"
    assert result["country"] == "Germany"
    assert result["zip"] is not None  # Zip code may vary


def test_geocode_with_nominatim_zip() -> None:
    """Test Nominatim geocoding with a valid address including zip code."""
    cues = ["72072"]
    result = mut.geocode_with_nominatim(cues)
    assert isinstance(result, dict)
    assert "city" in result
    assert "country" in result
    assert "zip" in result
    assert result["city"] == "Tübingen"
    assert result["country"] == "Germany"
    assert result["zip"] == "72072"


def test_geocode_with_nominatim_invalid() -> None:
    """Test Nominatim geocoding with an invalid address."""
    cues = ["Invalid Address"]
    result = mut.geocode_with_nominatim(cues)
    assert isinstance(result, dict)
    assert not result  # Expecting an empty dictionary for no match
    assert "city" not in result
    assert "country" not in result
    assert "zip" not in result
    assert result == {}


def test_geocode_with_nominatim_no_cues(fake_logger: Mock) -> None:
    """Test Nominatim geocoding with no available location cues."""
    cues: list[str] = []
    result = mut.geocode_with_nominatim(cues)
    assert isinstance(result, dict)
    assert not result  # Expecting an empty dictionary for no cues
    fake_logger.error.assert_called_once_with("No address information provided.")


def test_geocode_with_nominatim_request_error(
    monkeypatch: Mock, fake_logger: Mock
) -> None:
    fake_request = Mock()
    fake_request.get = Mock(side_effect=requests.exceptions.RequestException)
    monkeypatch.setattr(mut.requests, "get", fake_request.get)

    cues = ["Reutlingen"]
    # 3) It should catch & return {} (not raise)
    result = mut.geocode_with_nominatim(cues)

    assert result == {}

    # 4) And it should have logged the exception
    fake_logger.exception.assert_called_once_with("Network error")


def test_successful_geocode_returns_all_fields(fake_client: Mock) -> None:
    fake_client.places.return_value = {
        "status": "OK",
        "results": [{"place_id": "pid123"}],
    }
    fake_client.place.return_value = {
        "result": {
            "address_components": [
                {"long_name": "Berlin", "types": ["locality"]},
                {"long_name": "Germany", "types": ["country"]},
                {"long_name": "10115", "types": ["postal_code"]},
            ]
        }
    }

    # Act
    out = mut.geocode_with_google("Some Company", api="APIKEY")

    # Assert
    assert out == {"city": "Berlin", "country": "Germany", "zip": "10115"}
    fake_client.places.assert_called_once_with(query="Some Company", language="en")
    fake_client.place.assert_called_once_with(
        place_id="pid123", fields=["address_component"]
    )


def test_status_not_ok_returns_empty(fake_client: Mock) -> None:
    fake_client.places.return_value = {"status": "ZERO_RESULTS", "results": []}
    out = mut.geocode_with_google("NoSuchPlace", api="KEY")
    assert out == {}
    # no call to place() when status != OK
    fake_client.place.assert_not_called()


def test_empty_results_list_returns_empty(fake_client: Mock) -> None:
    fake_client.places.return_value = {"status": "OK", "results": []}
    out = mut.geocode_with_google("NoResultsHere", api="KEY")
    assert out == {}
    fake_client.place.assert_not_called()


def test_missing_components_populates_none(fake_client: Mock) -> None:
    fake_client.places.return_value = {
        "status": "OK",
        "results": [{"place_id": "pid456"}],
    }
    # Only return country, omit locality and postal_code
    fake_client.place.return_value = {
        "result": {"address_components": [{"long_name": "USA", "types": ["country"]}]}
    }
    out = mut.geocode_with_google("SomePlace", api="KEY")
    assert out == {"city": None, "country": "USA", "zip": None}


def test_exception_during_api_logs_and_returns_empty(
    fake_client: Mock, fake_logger: Mock
) -> None:
    # Arrange: have places() throw
    fake_client.places.side_effect = RuntimeError("boom")
    # Act
    out = mut.geocode_with_google("BadCall", api="KEY")
    # Assert
    assert out == {}
    fake_logger.exception.assert_called_once_with("Error during Google geocoding")

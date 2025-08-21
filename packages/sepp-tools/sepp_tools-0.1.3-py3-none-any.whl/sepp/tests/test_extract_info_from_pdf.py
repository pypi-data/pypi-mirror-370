from pathlib import Path
from unittest.mock import Mock

import pytest
from microsoft.connectors.api import MSGraphAPI

from sepp import extract_info_from_pdf as mut
from sepp.exceptions import LLMResponseIncompleteError


@pytest.fixture
def fake_msgraph(monkeypatch: Mock) -> Mock:
    fake = Mock(spec=MSGraphAPI)
    monkeypatch.setattr(mut, "msgraph", fake)
    return fake


@pytest.fixture
def fake_logger(monkeypatch: Mock) -> Mock:
    fake = Mock()
    monkeypatch.setattr(mut, "logger", fake)
    return fake


@pytest.fixture
def fake_send_error(monkeypatch: Mock) -> Mock:
    fake = Mock()
    monkeypatch.setattr(mut, "send_error_email", fake)
    return fake


@pytest.fixture
def fake_send_failed_email(monkeypatch: Mock) -> Mock:
    fake = Mock()
    monkeypatch.setattr(mut, "send_failed_email", fake)
    return fake


@pytest.fixture
def pdf_path(tmp_path: Path) -> Path:
    p = tmp_path / "test.pdf"
    p.write_bytes(b"%PDF-1.4 dummy")
    return p


@pytest.fixture
def fake_final_sanity_check(monkeypatch: Mock) -> Mock:
    fake = Mock()
    monkeypatch.setattr(mut, "_final_sanity_check", fake)
    return fake


def test_get_llm_response_incomplete_response(
    monkeypatch: Mock, pdf_path: Path
) -> None:
    incomplete_response = {"key": "incomplete_value"}

    # Mock pdf_to_json to return an incomplete response
    fake_pdf_to_json = Mock(return_value=(incomplete_response, "dummy_text"))
    monkeypatch.setattr(mut, "pdf_to_json", fake_pdf_to_json)

    with pytest.raises(LLMResponseIncompleteError):
        mut.get_llm_response(pdf_path)


def test_get_llm_response_success_on_first_attempt(
    monkeypatch: Mock, tmp_path: Path
) -> None:
    # Arrange
    pdf_path = tmp_path / "dummy.pdf"
    expected = {"foo": "bar"}
    monkeypatch.setattr(mut, "pdf_to_json", Mock(return_value=(expected, "raw")))
    monkeypatch.setattr(mut, "_check_transports", Mock(return_value=[]))
    monkeypatch.setattr(mut, "_check_client_fields", Mock(return_value=([], [])))

    # Act
    cleaned, raw = mut.get_llm_response(pdf_path)

    # Assert
    assert cleaned == expected
    assert raw == "raw"


def test_get_llm_response_success_after_retry(
    monkeypatch: Mock, tmp_path: Path, fake_final_sanity_check: Mock
) -> None:
    # Arrange
    pdf_path = tmp_path / "dummy.pdf"
    incomplete = {"incomplete": True}
    complete = {"complete": True}

    # pdf_to_json returns only once, then retries come via _handle_incomplete_response
    monkeypatch.setattr(mut, "pdf_to_json", Mock(return_value=(incomplete, "text1")))

    # First pass: both transports and client missing → retry
    # Second pass: both empty → success
    fake_check_transports = Mock(side_effect=[["t_missing"], []])
    fake_check_client = Mock(side_effect=[(["c_missing"], ["avail"]), ([], [])])
    monkeypatch.setattr(mut, "_check_transports", fake_check_transports)
    monkeypatch.setattr(mut, "_check_client_fields", fake_check_client)

    # Simulate the LLM retry populating a complete response
    monkeypatch.setattr(
        mut, "_handle_incomplete_response", Mock(return_value=(complete, "text2"))
    )

    # Act
    cleaned, raw = mut.get_llm_response(pdf_path)
    fake_final_sanity_check.assert_called_once_with(complete)
    # Assert
    assert cleaned == complete
    assert raw == "text2"


def test_get_llm_response_incomplete_raises_after_max_retries(
    monkeypatch: Mock,
    tmp_path: Path,
) -> None:
    # Arrange
    pdf_path = tmp_path / "dummy.pdf"
    incomplete = {"still": "bad"}

    monkeypatch.setattr(mut, "pdf_to_json", Mock(return_value=(incomplete, "raw")))

    # Always report missing so we exhaust retries
    always_missing = ["x"]
    fake_check_transports = Mock(side_effect=[always_missing] * 3)
    fake_check_client = Mock(side_effect=[(always_missing, [])] * 3)
    monkeypatch.setattr(mut, "_check_transports", fake_check_transports)
    monkeypatch.setattr(mut, "_check_client_fields", fake_check_client)

    # _handle_incomplete_response yields the same incomplete dict each retry
    monkeypatch.setattr(
        mut, "_handle_incomplete_response", Mock(side_effect=[(incomplete, "raw")] * 2)
    )

    # Act & Assert
    with pytest.raises(LLMResponseIncompleteError) as exc:
        mut.get_llm_response(pdf_path, max_retries=2)

    msg = str(exc.value)
    assert "LLM response is still incomplete after 2 attempts" in msg
    assert "Missing fields" in msg


@pytest.mark.parametrize(
    ("llm_response", "expected_missing"),
    [
        ({"transports": []}, ["transports"]),
        ({"transports": None}, ["transports"]),
    ],
)
def test_items_missing_in_llm_response_transport(
    llm_response: dict, expected_missing: list
) -> None:
    missing_items = mut._check_transports(llm_response)
    assert missing_items == expected_missing


@pytest.mark.parametrize(
    ("transport", "expected_missing"),
    [
        (
            # missing receiver_name and receiver_city
            {
                "sender": {"name": "Alice", "city": "Berlin"},
                "receiver": {"name": "", "city": ""},
                "loadingDate": "2023-10-02",
                "deliveryDate": "2023-10-06",
            },
            ["transport[1].receiver_name", "transport[1].receiver_city"],
        ),
        (
            # missing sender_name only
            {
                "sender": {"name": "", "city": "Munich"},
                "receiver": {"name": "Bob", "city": "Hamburg"},
                "loadingDate": "2023-10-02",
                "deliveryDate": "2023-10-06",
            },
            ["transport[1].sender_name"],
        ),
        (
            # missing sender_city and receiver_city
            {
                "sender": {"name": "Alice", "city": ""},
                "receiver": {"name": "Bob", "city": ""},
                "loadingDate": "2023-10-02",
                "deliveryDate": "2023-10-06",
            },
            ["transport[1].sender_city", "transport[1].receiver_city"],
        ),
        (
            # missing all four fields
            {
                "sender": {"name": "", "city": ""},
                "receiver": {"name": "", "city": ""},
                "loadingDate": "",
            },
            [
                "transport[1].sender_name",
                "transport[1].sender_city",
                "transport[1].receiver_name",
                "transport[1].receiver_city",
                "transport[1].loading_date",
                "transport[1].delivery_date",
            ],
        ),
    ],
)
def test_check_transports_for_each_missing_field(
    transport: dict, expected_missing: list
) -> None:
    llm_response = {"transports": [transport]}

    missing_items = mut._check_transports(llm_response)
    assert missing_items == expected_missing


def test_check_transports_all_fields_present() -> None:
    llm_response = {
        "transports": [
            {
                "sender": {"name": "Alice", "city": "Berlin"},
                "receiver": {
                    "name": "Bob",
                    "city": "Hamburg",
                },
                "loadingDate": "2023-10-02",
                "deliveryDate": "2023-10-06",
            },
        ]
    }
    # Should not raise
    assert mut._check_transports(llm_response) == []


@pytest.mark.parametrize(
    ("client", "expected_missing", "expected_available"),
    [
        # 1) nothing provided → all mandatory missing, none available
        ({}, {"name", "zip", "city", "country"}, []),
        # 2) all fields present → no missing, all five cues available in order
        (
            {
                "name": "Alice",
                "street": "Main St",
                "houseNumber": "42",
                "zip": "12345",
                "city": "Metropolis",
                "country": "Freedonia",
            },
            set(),
            ["street", "houseNumber", "zip", "city", "country"],
        ),
        # 3) some optional present, some mandatory missing
        (
            {
                "name": "Bob",
                "zip": "54321",
                "city": "Smallville",
                # country missing
                "street": "1st Ave",
                # houseNumber missing
            },
            {"country"},
            ["street", "zip", "city"],
        ),
        # 4) name is empty string (falsey) → treated as missing
        (
            {
                "name": "",
                "zip": "00000",
                "city": "Gotham",
                "country": "USA",
            },
            {"name"},
            ["zip", "city", "country"],
        ),
    ],
)
def test_check_client_fields(
    client: dict, expected_missing: set[str], expected_available: list[str]
) -> None:
    missing, available = mut._check_client_fields(client)
    assert set(missing) == expected_missing
    assert available == expected_available


def test_final_sanity_check_fail(monkeypatch: Mock) -> None:
    fake_check_transport = Mock(return_value=["a"])
    monkeypatch.setattr(mut, "_check_transports", fake_check_transport)
    fake_check_client_fields = Mock(return_value=(["b"], ["c"]))
    monkeypatch.setattr(mut, "_check_client_fields", fake_check_client_fields)

    with pytest.raises(LLMResponseIncompleteError):
        mut._final_sanity_check(llm_response={})


def test_final_sanity_check_pass(monkeypatch: Mock) -> None:
    fake_check_transport = Mock(return_value=[])
    monkeypatch.setattr(mut, "_check_transports", fake_check_transport)
    fake_check_client_fields = Mock(return_value=([], []))
    monkeypatch.setattr(mut, "_check_client_fields", fake_check_client_fields)

    # Should not raise
    mut._final_sanity_check(llm_response={})


def test_get_llm_response_oppel(monkeypatch: Mock, pdf_path: Path) -> None:
    llm_response = {"client": {"name": "OPPEL Spedition"}}

    fake_handle_oppel = Mock(return_value=(llm_response, "dummy_text"))
    monkeypatch.setattr(mut, "_handle_oppel", fake_handle_oppel)

    fake_pdf_to_json = Mock(return_value=(llm_response, "dummy_text"))
    monkeypatch.setattr(mut, "pdf_to_json", fake_pdf_to_json)

    with pytest.raises(LLMResponseIncompleteError):
        mut.get_llm_response(pdf_path)
    fake_handle_oppel.assert_called_once_with(pdf_path)


def test_get_llm_response_missing_raw_text(
    monkeypatch: Mock, pdf_path: Path, fake_logger: Mock
) -> None:
    llm_response = {"a": "b", "c": "d"}
    raw_text = ""
    fake_pdf_to_json = Mock(return_value=(llm_response, raw_text))
    monkeypatch.setattr(mut, "pdf_to_json", fake_pdf_to_json)
    fake_check_transports = Mock(return_value=[])
    monkeypatch.setattr(mut, "_check_transports", fake_check_transports)
    fake_check_client_fields = Mock(return_value=([], []))
    monkeypatch.setattr(mut, "_check_client_fields", fake_check_client_fields)
    fake_final_sanity_check = Mock()
    monkeypatch.setattr(mut, "_final_sanity_check", fake_final_sanity_check)

    # Act
    response_dict, response_raw_text = mut.get_llm_response(pdf_path)
    # Assert
    assert response_dict == llm_response
    fake_logger.warning.assert_called_once_with(
        "Raw text is empty, trying to fill it with the LLM response."
    )
    assert response_raw_text == str(list(llm_response.values()))


@pytest.fixture
def client() -> dict:
    return {
        "name": "Test Company",
        "zip": "12345",
        "city": "Test City",
        "street": "Test Street",
        "houseNumber": "1",
        "country": "Test Country",
    }


@pytest.fixture
def fake_geocode_nominatim(monkeypatch: Mock) -> Mock:
    fake = Mock(
        return_value={
            "city": "Fake City",
            "country": "Fake Country",
            "zip": "Fake Zip",
        }
    )
    monkeypatch.setattr(mut, "geocode_with_nominatim", fake)
    return fake


@pytest.fixture
def fake_geocode_google(monkeypatch: Mock) -> Mock:
    fake = Mock(
        return_value={
            "city": "Fake City",
            "country": "Fake Country",
            "zip": "Fake Zip",
        }
    )
    monkeypatch.setattr(mut, "geocode_with_google", fake)
    return fake


def test_geocode_client_zip(
    fake_geocode_nominatim: Mock,
    fake_logger: Mock,
    client: dict,
) -> None:
    # Mock the geocode function to return a fixed response
    result = mut._geocode_client(client, available_fields=["zip"])
    fake_geocode_nominatim.assert_called_once_with(available_location_cues=["12345"])
    fake_logger.info.assert_called_with("Geocoding via Nominatim using %s", ["12345"])
    assert result == {
        "city": "Fake City",
        "country": "Fake Country",
    }


def test_geocode_client_city(
    fake_geocode_nominatim: Mock,
    fake_logger: Mock,
    client: dict,
) -> None:
    # Mock the geocode function to return a fixed response
    result = mut._geocode_client(client, available_fields=["city"])
    fake_geocode_nominatim.assert_called_once_with(
        available_location_cues=["Test City"]
    )
    fake_logger.info.assert_called_with(
        "Geocoding via Nominatim using %s", ["Test City"]
    )
    assert result == {
        "zip": "Fake Zip",
        "country": "Fake Country",
    }


def test_geocode_nominatim_fail(
    fake_geocode_nominatim: Mock,
    fake_geocode_google: Mock,
    fake_logger: Mock,
    client: dict,
) -> None:
    # Simulate a failure in geocoding
    fake_geocode_nominatim.return_value = {}
    result = mut._geocode_client(client, available_fields=["zip", "city"])
    fake_geocode_nominatim.assert_called_with(
        available_location_cues=["12345", "Test City"]
    )
    fake_logger.info.assert_called_with(
        "Geocoding via Nominatim using %s", ["12345", "Test City"]
    )
    fake_logger.warning.assert_called_with(
        "Nominatim geocoding failed, trying Google Maps API."
    )
    fake_geocode_google.assert_called_with(
        query="Test Company 12345 Test City", api=mut.GOOGLE_API
    )
    assert result == {
        "country": "Fake Country",
    }


def test_geocode_no_zip_or_city(
    fake_geocode_google: Mock,
    fake_logger: Mock,
    client: dict,
) -> None:
    # Test when neither zip nor city is available
    result = mut._geocode_client(client, available_fields=["street", "houseNumber"])
    name = client["name"]
    cues = ["Test Street", "1"]

    fake_logger.info.assert_called_with(
        "No city or zip available, using Google for %s: %s", name, cues
    )
    fake_geocode_google.assert_called_with(
        query=" ".join([name, *cues]), api=mut.GOOGLE_API
    )
    assert result == {
        "city": "Fake City",
        "country": "Fake Country",
        "zip": "Fake Zip",
    }


def test_check_and_fill_raw_text_not_empty(fake_logger: Mock) -> None:
    llm_dict = {"a": 1, "b": 2}
    raw_text = "some text"
    result = mut._check_and_fill_raw_text(llm_dict, raw_text)
    assert result == raw_text
    fake_logger.warning.assert_not_called()


def test_fills_when_empty_and_logs_warning(fake_logger: Mock) -> None:
    # Order of values in list is insertion order from dict
    llm_dict = {"transport": "T1", "client": "C1"}
    raw_text = ""
    result = mut._check_and_fill_raw_text(llm_dict, raw_text)
    # It should be the string representation of the list of values
    assert result == "['T1', 'C1']"
    fake_logger.warning.assert_called_once_with(
        "Raw text is empty, trying to fill it with the LLM response."
    )

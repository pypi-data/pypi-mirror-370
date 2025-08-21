from datetime import datetime
from unittest.mock import Mock
from zoneinfo import ZoneInfo

import pytest

import sepp.scripts.llm_response_hardcoded_cases as mut  # <-- replace with your actual module name


@pytest.fixture(autouse=True)
def fake_logger(monkeypatch: Mock) -> Mock:
    mock_logger = Mock()
    monkeypatch.setattr(mut, "logger", mock_logger)
    return mock_logger


def test_apply_hardcoded_cases_hermes(monkeypatch: Mock, fake_logger: Mock) -> None:
    mock_hermes = Mock()
    mock_lutz = Mock()
    monkeypatch.setattr(mut, "swap_sender_receiver_for_hermes", mock_hermes)
    monkeypatch.setattr(mut, "add_return_transport_for_xxxlutz", mock_lutz)
    llm = {"client": {"name": "Hermes Express"}, "transports": []}

    mut.apply_hardcoded_cases(llm)

    mock_hermes.assert_called_once_with(llm)
    mock_lutz.assert_not_called()
    fake_logger.info.assert_any_call("Client is 'Hermes', exceptions might apply...")


def test_apply_hardcoded_cases_xxxlutz(monkeypatch: Mock, fake_logger: Mock) -> None:
    mock_hermes = Mock()
    mock_lutz = Mock()
    monkeypatch.setattr(
        mut,
        "swap_sender_receiver_for_hermes",
        mock_hermes,
    )
    monkeypatch.setattr(
        mut,
        "add_return_transport_for_xxxlutz",
        mock_lutz,
    )
    llm = {"client": {"name": "XXXLutz GmbH"}, "transports": []}

    mut.apply_hardcoded_cases(llm)

    mock_hermes.assert_not_called()
    mock_lutz.assert_called_once_with(llm)
    fake_logger.info.assert_any_call(
        "Client name is 'XXXLutz', exceptions might apply..."
    )


def test_apply_hardcoded_cases_none(fake_logger: Mock) -> None:
    llm = {"client": {"name": "Other Co."}, "transports": []}

    mut.apply_hardcoded_cases(llm)

    fake_logger.info.assert_any_call("No hardcoded exceptions found.")


def test_swap_sender_receiver_for_hermes_swaps_and_logs(fake_logger: Mock) -> None:
    llm = {
        "transports": [
            {
                "sender": {"city": "Mülheim an der Ruhr"},
                "receiver": {"city": "Ansbach"},
            }
        ]
    }
    mut.swap_sender_receiver_for_hermes(llm)
    t = llm["transports"][0]
    assert t["sender"]["city"] == "Ansbach"
    assert t["receiver"]["city"] == "Mülheim an der Ruhr"
    fake_logger.info.assert_any_call(
        "Swapped sender and receiver for Hermes transport (now: %s -> %s)",
        "mülheim an der ruhr",
        "ansbach",
    )


def test_swap_sender_receiver_for_hermes_no_swap(fake_logger: Mock) -> None:
    llm = {
        "transports": [{"sender": {"city": "Berlin"}, "receiver": {"city": "Ansbach"}}]
    }
    mut.swap_sender_receiver_for_hermes(llm)
    t = llm["transports"][0]
    assert t["sender"]["city"] == "Berlin"
    # No log for swap
    fake_logger.info.assert_not_called()


def test_add_return_transport_for_xxxlutz_success(fake_logger: Mock) -> None:
    loading = "2025-07-01 08:00:00"
    delivery = "2025-07-01 12:00:00"
    llm = {
        "transports": [
            {
                "loadingDate": [loading],
                "deliveryDate": [delivery],
                "sender": {"city": "A"},
                "receiver": {"city": "B"},
                "carrier": {"name": "CarrierX"},
            }
        ]
    }
    mut.add_return_transport_for_xxxlutz(llm)

    transports = llm["transports"]
    expected_len_transports = 2
    assert len(transports) == expected_len_transports
    orig, ret = transports
    # Return transport should swap sender/receiver
    assert ret["sender"] == orig["receiver"]
    assert ret["receiver"] == orig["sender"]

    dt_del = datetime.strptime(delivery, "%Y-%m-%d %H:%M:%S").replace(
        tzinfo=ZoneInfo("Europe/Berlin")
    )

    # The return's deliveryDate should be original delivery + delta
    expected_ret_delivery = (dt_del).strftime("%Y-%m-%d %H:%M:%S")
    assert next(iter(ret["deliveryDate"])) == expected_ret_delivery

    # And loadingDate of return equals original delivery
    assert next(iter(ret["loadingDate"])) == delivery

    fake_logger.info.assert_any_call("Added return transport for XXXLutz.")


def test_add_return_transport_for_xxxlutz_error(fake_logger: Mock) -> None:
    # Malformed dates cause exception
    llm = {"transports": [{"loadingDate": ["bad"], "deliveryDate": ["bad"]}]}
    original = llm["transports"].copy()

    mut.add_return_transport_for_xxxlutz(llm)

    # Should remain unchanged
    assert llm["transports"] == original
    fake_logger.exception.assert_called_once_with(
        "Failed to add return transport for XXXLutz."
    )

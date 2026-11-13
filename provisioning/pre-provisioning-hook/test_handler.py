"""
Quick unit tests for the pre-provisioning hook. Run with: python -m pytest
(or just: python test_handler.py)
"""

from handler import handler


def _event(serial, group):
    return {"parameters": {"SerialNumber": serial, "FleetGroup": group}}


def test_valid_device_is_allowed():
    res = handler(_event("DEVICE-0001", "fleet-a"), None)
    assert res["allowProvisioning"] is True


def test_bad_serial_is_rejected():
    res = handler(_event("laptop-123", "fleet-a"), None)
    assert res["allowProvisioning"] is False


def test_unknown_fleet_group_is_rejected():
    res = handler(_event("DEVICE-0001", "fleet-unknown"), None)
    assert res["allowProvisioning"] is False


if __name__ == "__main__":
    test_valid_device_is_allowed()
    test_bad_serial_is_rejected()
    test_unknown_fleet_group_is_rejected()
    print("all tests passed")

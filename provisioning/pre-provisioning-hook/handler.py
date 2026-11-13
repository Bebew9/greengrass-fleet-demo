"""
Pre-provisioning hook for AWS IoT fleet provisioning.

AWS IoT invokes this Lambda SYNCHRONOUSLY during fleet provisioning, before it
creates a Thing or issues a permanent certificate. It is the gatekeeper: it
decides whether a device that showed up with the shared "claim" certificate is
actually allowed to join the fleet.

Returning allowProvisioning=False stops the whole provisioning flow, so a leaked
claim certificate on its own is not enough to register a rogue device.

This is a generic, educational example — adapt the validation rules to your own
serial-number scheme and fleet groups.
"""

import re

# Only serials matching these patterns are allowed to provision.
SERIAL_PATTERNS = [
    re.compile(r"^DEVICE-[A-Z0-9]{4,12}$"),
]

# Only these fleet groups are accepted.
ALLOWED_FLEET_GROUPS = {"fleet-a", "fleet-b"}


def _is_valid_serial(serial: str) -> bool:
    return any(p.match(serial) for p in SERIAL_PATTERNS)


def handler(event, context):
    """
    event looks like:
    {
      "parameters": {
        "SerialNumber": "DEVICE-0001",
        "FleetGroup": "fleet-a"
      },
      "certificateId": "...",
      "clientId": "..."
    }
    """
    params = event.get("parameters", {})
    serial = params.get("SerialNumber", "")
    fleet_group = params.get("FleetGroup", "")

    allow = _is_valid_serial(serial) and fleet_group in ALLOWED_FLEET_GROUPS

    if allow:
        # parameterOverrides are passed on to the provisioning template.
        return {
            "allowProvisioning": True,
            "parameterOverrides": {
                "SerialNumber": serial,
                "FleetGroup": fleet_group,
            },
        }

    # Reject: no Thing is created, no permanent certificate is issued.
    return {"allowProvisioning": False, "parameterOverrides": {}}

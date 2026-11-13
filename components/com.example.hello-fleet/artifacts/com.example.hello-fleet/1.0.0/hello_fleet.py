#!/usr/bin/env python3
"""
Minimal Greengrass component. In a real fleet this would be your application —
vision, inference, telemetry, a command handler. Here it just prints a heartbeat
so you can watch the component run and get redeployed across the fleet.

Greengrass runs this via the recipe's Lifecycle.Run. It's expected to stay alive
(long-running), so it loops instead of exiting — a component that exits cleanly
would be restarted again and again (the classic edge version of a crash loop).
"""

import os
import time

COMPONENT = os.environ.get("AWS_IOT_THING_NAME", "unknown-device")
VERSION = "1.0.0"


def main():
    print(f"hello-fleet {VERSION} starting on {COMPONENT}", flush=True)
    while True:
        print(f"[{COMPONENT}] heartbeat — running {VERSION}", flush=True)
        time.sleep(30)


if __name__ == "__main__":
    main()

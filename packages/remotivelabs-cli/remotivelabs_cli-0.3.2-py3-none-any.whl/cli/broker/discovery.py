from __future__ import annotations

from time import sleep

from zeroconf import IPVersion, ServiceBrowser, ServiceStateChange, Zeroconf

from cli.utils.console import print_generic_message, print_newline


def discover() -> None:
    zeroconf = Zeroconf(ip_version=IPVersion.V4Only)
    services = ["_remotivebroker._tcp.local."]

    print_generic_message("Looking for RemotiveBrokers on your network, press Ctrl-C to exit...")
    ServiceBrowser(zeroconf, services, handlers=[on_service_state_change])

    try:
        while True:
            sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        zeroconf.close()


def on_service_state_change(zeroconf: Zeroconf, service_type: str, name: str, state_change: ServiceStateChange) -> None:
    """TODO: use log instead of print for debug information?"""
    if state_change is ServiceStateChange.Removed:
        print_generic_message(f"Service {name} was removed")

    if state_change is ServiceStateChange.Updated:
        print_generic_message(f"Service {name} was updated")

    if state_change is ServiceStateChange.Added:
        print_generic_message(f"[ {name} ]")
        info = zeroconf.get_service_info(service_type, name)
        if info:
            for addr in info.parsed_scoped_addresses():
                print_generic_message(f"RemotiveBrokerApp: http://{addr}:8080")
                print_generic_message(f"RemotiveBroker http://{addr}:50051")
        else:
            print_generic_message("  No info")
        print_newline()

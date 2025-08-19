import subprocess


def normalize_service_name(service_name: str) -> str:
    """Append .service to a systemd service name, if it isn't already there."""
    return (
        f"{service_name}.service"
        if not service_name.endswith(".service")
        else service_name
    )


def get_service_status(service_name: str) -> bool:
    """Get the systemd service status."""
    # Check needs to be false because services that aren't running return non-0 codes
    result = subprocess.call(
        ["systemctl", "is-active", "--quiet", normalize_service_name(service_name)]
    )
    return True if result == 0 else False

import os
import signal
from typing import Annotated

from unpage.cli.graph._app import graph_app
from unpage.cli.graph._background import cleanup_pid_file, get_pid_file, is_process_running
from unpage.cli.options import DEFAULT_PROFILE, ProfileParameter
from unpage.telemetry import client as telemetry
from unpage.telemetry import prepare_profile_for_telemetry


@graph_app.command
async def stop(*, profile: Annotated[str, ProfileParameter] = DEFAULT_PROFILE) -> None:
    """Stop running graph build

    Parameters
    ----------
    profile
        The profile to use
    """
    await telemetry.send_event(
        {
            "command": "graph stop",
            **prepare_profile_for_telemetry(profile),
        }
    )

    pid_file = get_pid_file(profile)

    if not pid_file.exists():
        print(f"No graph build running for profile '{profile}'")
        return

    try:
        pid = int(pid_file.read_text().strip())
        if is_process_running(pid):
            print(f"Stopping graph build for profile '{profile}' (PID: {pid})...")
            os.kill(pid, signal.SIGTERM)
            print("Graph build stopped successfully")
        else:
            print(f"Process not found for profile '{profile}', cleaning up stale PID file...")
        cleanup_pid_file(profile)
    except (ValueError, ProcessLookupError):
        cleanup_pid_file(profile)
        print(f"No running process found for profile '{profile}', cleaned up stale PID file")

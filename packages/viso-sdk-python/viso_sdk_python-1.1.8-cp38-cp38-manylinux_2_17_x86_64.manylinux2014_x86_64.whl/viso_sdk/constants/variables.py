
"""
Environment Values

Note that NODE_ID and NODE_TYPE environment variables are passed from the SolutionManager.

Use these constant values in your containers to make your code simple!

"""

import os

# Viso directory where all Viso containers are using.
VISO_DIR: str = "/viso"


def get_node_id():
    # Node ID in the flow.
    # Use `SLIM_SIMULATION` value if set, otherwise, use correct value
    NODE_ID: str = os.environ.get("SLIM_SIMULATION", os.environ.get("NODE_ID", ""))
    return NODE_ID


def get_node_type():
    # Node type in the flow
    NODE_TYPE: str = os.environ.get("NODE_TYPE", "unknown")
    return NODE_TYPE


def get_container_dir():
    NODE_ID = get_node_id()
    NODE_TYPE = get_node_type()
    # Root directory where all log files, model files, etc are located.
    container_dir: str = os.path.join(VISO_DIR, f"{NODE_TYPE}_{NODE_ID}")
    os.makedirs(container_dir, exist_ok=True)
    return container_dir


def get_viso_dir():
    return VISO_DIR


def get_log_dir():
    # Log file directory
    container_dir = get_container_dir()
    log_dir: str = os.path.join(container_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    return log_dir

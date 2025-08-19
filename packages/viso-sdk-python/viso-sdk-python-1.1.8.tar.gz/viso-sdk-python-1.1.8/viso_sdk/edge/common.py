import os
import platform
import signal
import subprocess
import time


from viso_sdk.logging import get_logger

logger = get_logger(name=__name__)


def get_mem() -> dict:
    """
    Get memory usage
    """
    pipe = os.popen("free -tm | grep 'Total' | awk '{print $2,$3,$4}'")
    data = pipe.read().strip().split()
    pipe.close()

    all_mem = int(data[0])
    used_mem = int(data[1])
    free_mem = int(data[2])

    percent = round(used_mem * 100.0 / all_mem, 1)

    return {"used": used_mem, "total": all_mem, "free": free_mem, "percent": percent}


def check_running_proc(proc_name: str) -> bool:
    """Check if a process is running or not

    Args:
        proc_name(str): Target process name
    """
    try:
        cmd = f"ps -aef | grep -i '{proc_name}' | grep -v 'grep' | awk '{{ print $3 }}'"
        if len(os.popen(cmd).read().strip().splitlines()) > 0:
            return True
    except Exception as err:
        logger.error(f"Failed to get status of the process({proc_name}) - {err}")
    return False


def kill_process_by_name(proc_name: str) -> None:
    """Kill process by its name

    Args:
        proc_name(str): Target process name
    """
    with subprocess.Popen(["ps", "-A"], stdout=subprocess.PIPE) as proc:
        out, _ = proc.communicate()
    for line in out.decode().splitlines():
        if proc_name in line:
            pid = int(line.split(None, 1)[0])
            logger.debug(f"Found PID({pid}) of `{proc_name}`, killing...")
            os.kill(pid, getattr(signal, "SIGKILL"))


def get_up_time() -> str:
    """Get uptime in string format"""
    pipe = os.popen("uptime")
    data = pipe.read().strip().split(",")[0]
    pipe.close()
    return " ".join(data.split()[-2:])


def get_username() -> str:
    """Get current user name"""
    return os.getlogin()


def get_cpu_architecture() -> str:
    """Get CPU architecture"""
    machine = platform.machine()
    return 'amd64' if machine == 'x86_64' else machine

def get_integrated_gpu_info() -> str:
    """Get integrated GPU information"""
    return os.popen("lspci -nn -s 0:002.0").readline().strip()


def reset_usb(sleep_t: int = 10) -> None:
    """Reset USB and then sleep for the given duration"""
    logger.debug(f"Calling usb-reset and sleeping {sleep_t} sec")
    os.system("usb-reset -a")
    time.sleep(sleep_t)

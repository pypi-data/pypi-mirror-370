import platform
import psutil
import GPUtil
import cpuinfo
import subprocess
import json


def get_gpu_info():
    try:
        gpus = GPUtil.getGPUs()
        return [
            {
                "name": gpu.name,
                "memory_total_GB": round(gpu.memoryTotal / 1024, 2),
                "driver": gpu.driver,
                "id": gpu.id,
            }
            for gpu in gpus
        ]
    except Exception as e:
        return [{"error": f"Could not retrieve GPU info: {e}"}]


def get_cpu_info():
    try:
        return {
            "name": cpuinfo.get_cpu_info().get("brand_raw", "unknown"),
            "count_physical": psutil.cpu_count(logical=False),
            "count_logical": psutil.cpu_count(),
        }
    except Exception as e:
        return {"error": f"Could not retrieve system info: {e}"}


def get_ram_info():
    try:
        return {
            "memory_total_GB": round(psutil.virtual_memory().total / 1e9, 2),
        }
    except Exception as e:
        return {"error": f"Could not retrieve system info: {e}"}


def get_system_info():
    try:
        return {
            "os": f"{platform.system()} {platform.release()}",
            "arch": platform.machine(),
            "python_version": platform.python_version(),
        }
    except Exception as e:
        return {"error": f"Could not retrieve system info: {e}"}


def get_cuda_info():
    try:
        result = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=driver_version,cuda_version",
                "--format=csv,noheader",
            ],
            stderr=subprocess.DEVNULL,
        )
        driver, cuda = result.decode().strip().split(",")
        return {"nvidia_driver_version": driver.strip(), "cuda_version": cuda.strip()}
    except Exception:
        return {"warning": "nvidia-smi not available or failed to parse"}


def get_info():
    return {
        "gpu": get_gpu_info(),
        "cpu": get_cpu_info(),
        "ram": get_ram_info(),
        "system": get_system_info(),
        "cuda": get_cuda_info(),
    }


info = json.dumps(get_info(), indent=2)
print(info)

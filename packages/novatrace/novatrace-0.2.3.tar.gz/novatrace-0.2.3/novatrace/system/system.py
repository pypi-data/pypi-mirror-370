import psutil
import platform
from datetime import datetime
from pynvml import *

# Sistema de informacion de sistema como uso de RAM y CPU para feature de consumo de recursos del proyecto y estado del servidor

# Información del sistema operativo
def get_os_info():
    uname = platform.uname()
    return {
        "Sistema": uname.system,
        "Nombre del nodo": uname.node,
        "Versión": uname.version,
        "Release": uname.release,
        "Arquitectura": platform.machine(),
        "Procesador": uname.processor
    }

# Información de CPU
def get_cpu_info():
    return {
        "Cores físicos": psutil.cpu_count(logical=False),
        "Cores lógicos": psutil.cpu_count(logical=True),
        "Uso de CPU (%)": psutil.cpu_percent(interval=1)
    }

# Información de memoria RAM
def get_memory_info():
    mem = psutil.virtual_memory()
    return {
        "Total (GB)": round(mem.total / (1024 ** 3), 2),
        "Disponible (GB)": round(mem.available / (1024 ** 3), 2),
        "Uso (%)": mem.percent
    }

# Información del disco
def get_disk_info():
    disk = psutil.disk_usage('/')
    return {
        "Total (GB)": round(disk.total / (1024 ** 3), 2),
        "Usado (GB)": round(disk.used / (1024 ** 3), 2),
        "Libre (GB)": round(disk.free / (1024 ** 3), 2),
        "Uso (%)": disk.percent
    }

def get_gpu_info():
    try:
        nvmlInit()
        device_count = nvmlDeviceGetCount()
        gpus = []
        for i in range(device_count):
            handle = nvmlDeviceGetHandleByIndex(i)
            mem_info = nvmlDeviceGetMemoryInfo(handle)
            util = nvmlDeviceGetUtilizationRates(handle)
            gpus.append({
                "Nombre": nvmlDeviceGetName(handle).decode(),
                "Memoria Total (MB)": mem_info.total // (1024 ** 2),
                "Memoria Usada (MB)": mem_info.used // (1024 ** 2),
                "Memoria Libre (MB)": mem_info.free // (1024 ** 2),
                "Uso (%)": util.gpu
            })
        nvmlShutdown()
        return gpus
    except Exception as e:
        return [f"No se pudo obtener información de GPU: {e}"]

def info_sistema_stream():
    yield "🖥️ Información del Sistema Operativo:"
    yield get_os_info()

    yield "\n⚙️ Información de la CPU:"
    yield get_cpu_info()

    yield "\n💾 Información de la Memoria RAM:"
    yield get_memory_info()

    yield "\n🗂️ Información del Disco:"
    yield get_disk_info()

    yield "\n🎮 Información de la GPU:"
    gpus = get_gpu_info()
    if gpus:
        for i, gpu in enumerate(gpus):
            yield f"GPU {i + 1}: {gpu}"
    else:
        yield "No se detectó GPU o no es compatible."
        
for bloque in info_sistema_stream():
    print(bloque)

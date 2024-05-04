import subprocess
from prometheus_client import Gauge

def get_pi_cpu_temperature():
    with open('/sys/class/thermal/thermal_zone0/temp') as f:
        temp = f.read()
    return round(float(temp) / 1000, 2)

def get_pi_cpu_usage():
    with open('/proc/stat', 'r') as f:
        line = f.readline()
    stats = line.split()
    total = sum(int(i) for i in stats[1:])
    idle = int(stats[4])
    usage = ((total - idle) / total) * 100
    return round(usage, 2)

def get_pi_memory_usage():
    mem = subprocess.check_output(['cat', '/proc/meminfo']).decode()
    total_memory = int(mem.split('\n')[0].split()[1]) / 1024  # Convert from KB to MB
    available_memory = int(mem.split('\n')[2].split()[1]) / 1024  # Convert from KB to MB
    memory_usage_percentage = ((total_memory - available_memory) / total_memory) * 100
    return round(memory_usage_percentage, 2)

def get_pi_disk_usage():
    disk = subprocess.check_output(['df', '-h', '/']).decode()
    disk_usage_percentage = disk.split('\n')[1].split()[4]
    return float(disk_usage_percentage.rstrip('%'))

def get_all_pi_stats():
    return {
        "cpu_temperature": get_pi_cpu_temperature(),
        "cpu_usage": get_pi_cpu_usage(),
        "memory_usage": get_pi_memory_usage(),
        "disk_usage": get_pi_disk_usage()
    }


# Create a Gauge object for each metric we want to expose to Prometheus
cpu_temp_gauge = Gauge('cpu_temperature', 'CPU Temperature')
cpu_usage_gauge = Gauge('cpu_usage', 'CPU Usage')
memory_usage_gauge = Gauge('memory_usage', 'Memory Usage')

def create_and_set_pi_gauges():
    # Set the value of each gauge
    cpu_temp_gauge.set(get_pi_cpu_temperature())
    cpu_usage_gauge.set(get_pi_cpu_usage())
    memory_usage_gauge.set(get_pi_memory_usage())

    return cpu_temp_gauge, cpu_usage_gauge, memory_usage_gauge



import subprocess

def get_pi_cpu_temperature():
    """
    Gets the current CPU temperature of the Raspberry Pi.

    Returns:
        float: The current CPU temperature in degrees Celsius.
    """
    with open('/sys/class/thermal/thermal_zone0/temp') as f:
        temp = f.read()
    return round(float(temp) / 1000, 2)

def get_pi_cpu_usage():
    """
    Calculates the current CPU usage of the Raspberry Pi.

    Returns:
        float: The current CPU usage as a percentage.
    """
    with open('/proc/stat', 'r') as f:
        line = f.readline()
    stats = line.split()
    total = sum(int(i) for i in stats[1:])
    idle = int(stats[4])
    usage = ((total - idle) / total) * 100
    return round(usage, 2)

def get_pi_memory_usage():
    """
    Calculates the current memory usage of the Raspberry Pi.

    Returns:
        float: The current memory usage as a percentage of total memory.
    """
    mem = subprocess.check_output(['cat', '/proc/meminfo']).decode()
    total_memory = int(mem.split('\n')[0].split()[1]) / 1024  # Convert from KB to MB
    available_memory = int(mem.split('\n')[2].split()[1]) / 1024  # Convert from KB to MB
    memory_usage_percentage = ((total_memory - available_memory) / total_memory) * 100
    return round(memory_usage_percentage, 2)

def get_pi_disk_usage():
    """
    Calculates the current disk usage of the Raspberry Pi.

    Returns:
        float: The current disk usage as a percentage of total disk space.
    """
    disk = subprocess.check_output(['df', '-h', '/']).decode()
    disk_usage_percentage = disk.split('\n')[1].split()[4]
    return float(disk_usage_percentage.rstrip('%'))

def get_all_pi_stats():
    """
    Gathers all Raspberry Pi statistics including CPU temperature, CPU usage, memory usage, and disk usage.

    Returns:
        dict: A dictionary containing all the Raspberry Pi statistics.
    """
    return {
        "cpu_temperature": get_pi_cpu_temperature(),
        "cpu_usage": get_pi_cpu_usage(),
        "memory_usage": get_pi_memory_usage(),
        "disk_usage": get_pi_disk_usage()
    }

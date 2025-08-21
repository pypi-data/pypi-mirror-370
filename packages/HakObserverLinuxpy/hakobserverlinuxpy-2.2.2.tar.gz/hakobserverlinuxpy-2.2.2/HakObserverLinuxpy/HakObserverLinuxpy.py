import os
import platform
import psutil
import socket
import subprocess
import requests
import uuid
import pwd

# ------------------------------
# Helper: Send data to API
# ------------------------------
def send_data_to_api(url):
    try:
        response = requests.get(url)
        return response.status_code
    except Exception as e:
        return str(e)

# ------------------------------
# Status Logger
# ------------------------------
def StatusLogginfo(HWDeviceID, Task, Message, Status):
    url = f"https://api.hakware.com/HakObserver/callLog/{HWDeviceID}/{Task}/{Message}/{Status}"
    send_data_to_api(url)

# ------------------------------
# System Resource Info
# ------------------------------
def get_system_usage(HWDeviceID, ObserverVersion):
    device_name = socket.gethostname()
    processor = platform.processor() or ''
    device_id = str(uuid.uuid4())
    system_type = platform.system()
    os = str(platform.version())
    os_version = os.replace('~','').replace('#','')

    total_memory_gb = round(psutil.virtual_memory().total / (1024 ** 3), 2)
    total_cpus = psutil.cpu_count(logical=True)
    total_cores = psutil.cpu_count(logical=False) or total_cpus



#'https://api.hakware.com/HakObserver/Device/66998FDE-098D-4466-A22D-597A65F88B2B/0.0.0/UbuntuVM1/x86_64/e3f6ff54-c054-4639-b520-8d304c23ec12/Linux/#36~22.04.1-Ubuntu%20SMP%20Tue%20Jul%20%201%2003:54:01%20UTC%202025/3.78/2/2'


    url = f"https://api.hakware.com/HakObserver/Device/{HWDeviceID}/{ObserverVersion}/{device_name}/{processor}/{device_id}/{system_type}/{os_version}/{total_memory_gb}/{total_cpus}/{total_cores}"
    send_data_to_api(url)

# ------------------------------
# Installed Applications
# ------------------------------
def get_installed_applications(HWDeviceID):
    try:
        output = subprocess.check_output(['dpkg-query', '-W', '-f=${Package}\t${Version}\n']).decode()
        apps = [line.split('\t') for line in output.strip().split('\n') if '\t' in line]
    except Exception:
        apps = []

    for app in apps:
        name = app[0].strip()
        version = app[1].strip()
        url = f"https://api.hakware.com/HakObserver/DeviceApps/{HWDeviceID}/{name}/{version}"
        send_data_to_api(url)

# ------------------------------
# Users
# ------------------------------
import subprocess
import pwd

def get_users(HWDeviceID):
    for user in pwd.getpwall():
        username = user.pw_name
        uid = user.pw_uid
        shell = user.pw_shell
        comment = user.pw_gecos.replace('/', '_') or "''"

        # Only allow login-capable users
        if (uid == 0 or uid >= 1000) and shell not in ('/usr/sbin/nologin', '/bin/false', ''):
            try:
                output = subprocess.check_output(['chage', '-l', username]).decode()
                for line in output.splitlines():
                    if line.startswith("Password last changed"):
                        last_changed = line.split(":", 1)[-1].strip()
                        if last_changed.lower() == "never":
                            password_age = 0
                        else:
                            from datetime import datetime
                            try:
                                changed_date = datetime.strptime(last_changed, "%b %d, %Y")
                                password_age = (datetime.today() - changed_date).days
                            except:
                                password_age = 0
                        break
                else:
                    password_age = 0
            except:
                password_age = 0

            url = f"https://api.hakware.com/HakObserver/InsertUsers/{HWDeviceID}/{username}/{password_age}/{comment}"
            send_data_to_api(url)

# ------------------------------
# Disk Info
# ------------------------------
def monitor_disk_space(DeviceID):
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
            Disk = "root" if part.mountpoint == "/" else part.mountpoint.replace('/', '_') or "unknown"
            fstype = part.fstype or "unknown"
            Total = usage.total
            Free = usage.free
            Used = usage.used
            Usage = usage.percent

            url = f"https://api.hakware.com/HakObserver/InsertDisks/{DeviceID}/{Disk}/{fstype}/{Usage}/{Used}/{Free}/{Total}"
            send_data_to_api(url)
        except Exception:
            continue

# ------------------------------
# CPU/MEM/NET Info
# ------------------------------
def system_usage(HWDeviceID):
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    url = f"https://api.hakware.com/HakObserver/InsertSystemUsage/{HWDeviceID}/{cpu}/{memory}/{disk}"
    send_data_to_api(url)

# ------------------------------
# Running Services (systemctl)
# ------------------------------
import subprocess
import psutil
import os

def list_services(DeviceID):
    try:
        # Get all running service names via systemctl
        output = subprocess.check_output(['systemctl', 'list-units', '--type=service', '--no-pager', '--all']).decode()
        lines = output.strip().split('\n')

        for line in lines:
            if ".service" in line:
                columns = line.split()
                service_name = columns[0]

                # Attempt to get status using systemctl is-active
                try:
                    status = subprocess.check_output(['systemctl', 'is-active', service_name]).decode().strip()
                except subprocess.CalledProcessError:
                    status = "unknown"

                # Attempt to get ExecStart path (binpath)
                try:
                    show_output = subprocess.check_output(['systemctl', 'show', service_name, '-p', 'ExecStart']).decode()
                    binpath = show_output.strip().split('=')[1].strip().split()[0] if '=' in show_output else '-'
                except:
                    binpath = "-"

                # Default fields for Linux
                pid = "-"
                username = "-"
                start_type = "-"
                description = "-"
                display_name = service_name

                # Try to find PID and username from psutil
                for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'username']):
                    try:
                        if service_name.replace(".service", "") in ' '.join(proc.info.get('cmdline', [])):
                            pid = str(proc.info['pid'])
                            username = proc.info['username'] or "-"
                            break
                    except:
                        continue

                # Construct final URL
                url = f"https://api.hakware.com/HakObserver/InsertServices/{DeviceID}/{pid}/{service_name}/{display_name}/{binpath}/{username}/{start_type}/{description}/{status}"
                send_data_to_api(url)

    except Exception as e:
        print(f"Error in list_services: {e}")
# ------------------------------
# Top processes using CPU/Memory
# ------------------------------
def list_Device_Usage(HWDeviceID):
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            pid = proc.info['pid']
            name = proc.info['name']
            cpu = proc.info['cpu_percent']
            mem = proc.info['memory_percent']
            url = f"https://api.hakware.com/HakObserver/DeviceUsage/{HWDeviceID}/{pid}/{name}/{cpu}/{mem}"
            send_data_to_api(url)
        except Exception as e:
            print(e)
            continue

# ------------------------------
# System Logs (/var/log/syslog)
# ------------------------------
def get_system_events(DeviceID):
    log_type = "System"
    path = "/var/log/syslog"

    try:
        output = subprocess.check_output(['tail', '-n', '50', path]).decode()
        lines = output.strip().split('\n')

        for idx, line in enumerate(lines):
            RecordNumber = str(idx)
            EventID = f"{RecordNumber}"
            EventDescription = line.strip().replace('/', '_')[:250]
            Source = 'syslog'
            EventTime = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            strEventTypeID = "-"
            EventTypeDescription = "-"
            EventCategoryID = "-"
            category_text = "-"
            EventData = EventDescription

            url = (
                f"https://api.hakware.com/HakObserver/InsertEvents/"
                f"{DeviceID}/{RecordNumber}/{log_type}/{EventID}/{EventDescription}/"
                f"{Source}/{EventTime}/{strEventTypeID}/{EventTypeDescription}/"
                f"{EventCategoryID}/{category_text}/{EventData}"
            )
            send_data_to_api(url)

    except Exception as e:
        StatusLogginfo(DeviceID, "System Events", str(e), "Error")


# ------------------------------
# Auth Logs (as Security Events)
# ------------------------------
from datetime import datetime
import hashlib

def get_Security_events(HWDeviceID):
    try:
        with open('/var/log/auth.log', 'r') as file:
            lines = file.readlines()

        for i, line in enumerate(lines[-50:]):  # last 50 entries
            RecordNumber = str(i + 1)
            log_type = "Security"

            # Use a hash of the line as a pseudo EventID
            EventID = str(int(hashlib.sha1(line.encode()).hexdigest(), 16) % (10 ** 8))

            EventDescription = line.strip().replace('/', '_')[:150]
            Source = "auth.log"

            try:
                # Parse timestamp (format: "Aug 18 06:25:01")
                parts = line.split()
                if len(parts) >= 3:
                    dt = datetime.strptime(' '.join(parts[:3]), "%b %d %H:%M:%S")
                    dt = dt.replace(year=datetime.now().year)
                    EventTime = dt.strftime('%Y-%m-%dT%H:%M:%S')
                else:
                    EventTime = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            except:
                EventTime = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

            strEventTypeID = "1"
            EventTypeDescription = "Logon Event"
            EventCategoryID = "10"
            category_text = "Authentication"
            EventData = EventDescription

            url = f"https://api.hakware.com/HakObserver/InsertEvents/{HWDeviceID}/{RecordNumber}/{log_type}/{EventID}/{EventDescription}/{Source}/{EventTime}/{strEventTypeID}/{EventTypeDescription}/{EventCategoryID}/{category_text}/{EventData}"
            send_data_to_api(url)

    except Exception as e:
        StatusLogginfo(HWDeviceID, 'Security Events', str(e), 'Error')

# ------------------------------
# IIS Alternative: Placeholder
# ------------------------------
def get_iis_sites(HWDeviceID):
    url = f"https://api.hakware.com/HakObserver/IIS/{HWDeviceID}/''/''"
    send_data_to_api(url)

# ------------------------------
# MAIN EXECUTION FUNCTION
# ------------------------------
def InitiateCollection(HWDeviceID, ObserverVersion): 
    StatusLogginfo(HWDeviceID, 'Starting HakObserver Scan', 'Starting','Completed')

    try:
        get_system_usage(HWDeviceID, ObserverVersion)
        StatusLogginfo(HWDeviceID, 'System Details', 'Gathering System Resource Information','Completed')
    except Exception as e:
        StatusLogginfo(HWDeviceID, 'System Details', str(e),'Error')

    try:
        #get_installed_applications(HWDeviceID)
        StatusLogginfo(HWDeviceID, 'Installed Applications', 'Get Installed Apps','Completed')
    except Exception as e:
        StatusLogginfo(HWDeviceID, 'Installed Applications', str(e),'Error')

    try:
        #get_users(HWDeviceID)
        StatusLogginfo(HWDeviceID, 'System Users', 'Get active Users','Completed')
    except Exception as e:
        StatusLogginfo(HWDeviceID, 'System Users', str(e),'Error')

    try:
        #monitor_disk_space(HWDeviceID)
        StatusLogginfo(HWDeviceID, 'Disks', 'Get allocated disks','Completed')
    except Exception as e:
        StatusLogginfo(HWDeviceID, 'Disks', str(e),'Error')

    try:
        list_Device_Usage(HWDeviceID)
        StatusLogginfo(HWDeviceID, 'Resource Usage', 'List of apps using resources','Completed')
    except Exception as e:
        StatusLogginfo(HWDeviceID, 'Resource Usage', str(e),'Error')

    try:
        #list_services(HWDeviceID)
        StatusLogginfo(HWDeviceID, 'Services', 'List of running services','Completed')
    except Exception as e:
        StatusLogginfo(HWDeviceID, 'Services', str(e),'Error')

    try:
        system_usage(HWDeviceID)
        StatusLogginfo(HWDeviceID, 'Resources', 'CPU, memory, and disk usage','Completed')
    except Exception as e:
        StatusLogginfo(HWDeviceID, 'Resources', str(e),'Error')

    try:
        #get_Security_events(HWDeviceID)
        StatusLogginfo(HWDeviceID, 'Security Events', 'Security Event Logs','Completed')
    except Exception as e:
        StatusLogginfo(HWDeviceID, 'Security Events', str(e),'Error')

    try:
        get_system_events(HWDeviceID)
        StatusLogginfo(HWDeviceID, 'System Logs', 'System Logs','Completed')
    except Exception as e:
        StatusLogginfo(HWDeviceID, 'System Logs', str(e),'Error')

    try:
        get_iis_sites(HWDeviceID)
        StatusLogginfo(HWDeviceID, 'IIS Sites', 'Placeholder for IIS Bindings','Completed')
    except Exception as e:
        StatusLogginfo(HWDeviceID, 'IIS Sites', str(e),'Error')

# Example usage
# InitiateCollection('12345-abc', 'v1.0.0')
#HWDeviceID = '66998FDE-098D-4466-A22D-597A65F88B2B' 
#ObserverVersion = '0.0.0'

#InitiateCollection(HWDeviceID, ObserverVersion)
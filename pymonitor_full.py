#!/usr/bin/env python3
import os
import sys
import time
import json
import csv
import subprocess
import socket
from datetime import datetime
from pathlib import Path

try:
    import psutil
except ImportError:
    print("\n[!] Error: 'psutil' module එක නැත. කරුණාකර 'pip install psutil' run කරන්න.\n")
    sys.exit(1)

# =====================================================
# CONFIGURATION
# =====================================================
LOG_FILE = os.path.expanduser("~/system-monitor.log")
JSON_LOG_FILE = os.path.expanduser("~/system-monitor.json")
CSV_LOG_FILE = os.path.expanduser("~/system-monitor.csv")
INTERVAL = 3
MAX_LOG_ENTRIES = 1000

# Color Codes
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"
RESET = "\033[0m"
GRAY = "\033[90m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"

# =====================================================
# UTILITY FUNCTIONS
# =====================================================

def get_size(bytes, suffix="B"):
    """Convert bytes to human readable format"""
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < 1024.0:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= 1024.0

def make_bar(percent, width=20):
    """Create a progress bar"""
    percent = min(100, max(0, percent))
    filled_width = int(width * percent / 100)
    bar = "█" * filled_width + "░" * (width - filled_width)
    return f"[{bar}] {percent:.1f}%"

def get_net_speed():
    """Get network upload/download speed safely"""
    try:
        net_start = psutil.net_io_counters()
        time.sleep(0.5)
        net_end = psutil.net_io_counters()
        upload = (net_end.bytes_sent - net_start.bytes_sent) * 2
        download = (net_end.bytes_recv - net_start.bytes_recv) * 2
        return get_size(upload, "/s"), get_size(download, "/s")
    except (PermissionError, Exception):
        return None, None

def get_cpu_temperature():
    """Get CPU temperature (if available)"""
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            if 'coretemp' in temps:
                return temps['coretemp'][0].current
            elif 'k10temp' in temps:
                return temps['k10temp'][0].current
            else:
                for temp_type, temp_list in temps.items():
                    if temp_list:
                        return temp_list[0].current
        return None
    except Exception:
        return None

def get_disk_io():
    """Get disk read/write speed"""
    try:
        io_start = psutil.disk_io_counters()
        time.sleep(0.5)
        io_end = psutil.disk_io_counters()
        read_speed = (io_end.read_bytes - io_start.read_bytes) * 2
        write_speed = (io_end.write_bytes - io_start.write_bytes) * 2
        return get_size(read_speed, "/s"), get_size(write_speed, "/s")
    except Exception:
        return None, None

def get_system_uptime():
    """Get system uptime"""
    try:
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{days}d {hours}h {minutes}m"
    except Exception:
        return "N/A"

def get_active_connections():
    """Get active network connections count"""
    try:
        connections = psutil.net_connections()
        return len(connections)
    except (PermissionError, Exception):
        return 0

def get_logged_in_users():
    """Get currently logged in users"""
    try:
        users = psutil.users()
        return len(users)
    except Exception:
        return 0

def get_gpu_info():
    """Try to get GPU information (if nvidia-smi available)"""
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=utilization.gpu,memory.used,memory.total', 
             '--format=csv,noheader,nounits'],
            capture_output=True, text=True, timeout=2
        )
        if result.returncode == 0:
            gpu_util, gpu_mem_used, gpu_mem_total = result.stdout.strip().split(',')
            return float(gpu_util.strip()), float(gpu_mem_used.strip()), float(gpu_mem_total.strip())
    except Exception:
        pass
    return None, None, None

def create_ascii_graph(data, width=20, height=5):
    """Create a simple ASCII graph from recent data"""
    if len(data) < 2:
        return ""
    
    max_val = max(data[-width:]) if data else 100
    if max_val == 0:
        max_val = 100
    
    graph = ""
    for h in range(height, 0, -1):
        threshold = (h / height) * max_val
        line = ""
        for val in data[-width:]:
            line += "█" if val >= threshold else " "
        graph += f"{line}\n"
    
    return graph

def kill_process(pid):
    """Kill a process by PID"""
    try:
        p = psutil.Process(pid)
        p.terminate()
        return True, f"Process {pid} terminated successfully"
    except psutil.NoSuchProcess:
        return False, f"Process {pid} not found"
    except psutil.AccessDenied:
        return False, f"Permission denied to terminate process {pid}"
    except Exception as e:
        return False, str(e)

def search_process(name):
    """Search for processes by name"""
    results = []
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                if name.lower() in proc.info['name'].lower():
                    results.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except Exception:
        pass
    return results

def export_to_json(data):
    """Export monitoring data to JSON"""
    try:
        json_data = {
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        with open(JSON_LOG_FILE, "a") as f:
            f.write(json.dumps(json_data) + "\n")
        return True
    except Exception as e:
        return False

def export_to_csv(data):
    """Export monitoring data to CSV"""
    try:
        file_exists = os.path.exists(CSV_LOG_FILE)
        with open(CSV_LOG_FILE, "a", newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['Timestamp', 'CPU%', 'MEM%', 'DISK%', 'TEMP°C'])
            writer.writerow([
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                data.get('cpu', 0),
                data.get('mem', 0),
                data.get('disk', 0),
                data.get('temp', 'N/A')
            ])
        return True
    except Exception:
        return False

def play_alert_sound():
    """Play alert sound"""
    try:
        if sys.platform == 'darwin':  # macOS
            os.system('afplay /System/Library/Sounds/Alarm.aiff')
        elif sys.platform == 'linux':  # Linux
            os.system('paplay /usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga 2>/dev/null || beep')
        elif sys.platform == 'win32':  # Windows
            import winsound
            winsound.Beep(1000, 500)
    except Exception:
        pass

def play_notification_sound():
    """Play notification sound"""
    try:
        if sys.platform == 'linux':
            os.system('paplay /usr/share/sounds/freedesktop/stereo/complete.oga 2>/dev/null || true')
    except Exception:
        pass

def get_memory_info():
    """Get detailed memory information"""
    try:
        mem = psutil.virtual_memory()
        return {
            'total': get_size(mem.total),
            'available': get_size(mem.available),
            'used': get_size(mem.used),
            'percent': mem.percent
        }
    except Exception:
        return {}

def get_all_disks():
    """Get information for all mounted disks"""
    disks = []
    try:
        partitions = psutil.disk_partitions(all=False)
        for partition in partitions:
            try:
                disk = psutil.disk_usage(partition.mountpoint)
                disks.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'total': get_size(disk.total),
                    'used': get_size(disk.used),
                    'free': get_size(disk.free),
                    'percent': disk.percent
                })
            except PermissionError:
                pass
    except Exception:
        pass
    return disks

# =====================================================
# MAIN MONITORING FUNCTION
# =====================================================

def monitor():
    """Main monitoring loop"""
    psutil.cpu_percent(interval=None)
    
    cpu_history = []
    mem_history = []
    disk_history = []
    
    try:
        while True:
            os.system('clear' if os.name == 'posix' else 'cls')
            
            # Header
            print(f"{GREEN}{BOLD}╔══════════════════════════════════════════════════════════════════╗{RESET}")
            print(f"{GREEN}{BOLD}║           🔥 MATRIX SYSTEM MONITOR v3.0 (Full Edition) 🔥         ║{RESET}")
            print(f"{GREEN}{BOLD}╚══════════════════════════════════════════════════════════════════╝{RESET}")
            print(f"{GRAY}Commands: (S)earch Process | (K)ill Process | (E)xport | (H)elp | Ctrl+C to Exit{RESET}\n")

            # =====================================================
            # SYSTEM OVERVIEW SECTION
            # =====================================================
            now = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
            print(f"{GREEN}{now} - SYSTEM OVERVIEW{RESET}")
            print(f"{GRAY}{'─' * 70}{RESET}")

            # CPU Usage
            cpu_usage = psutil.cpu_percent(interval=None)
            cpu_history.append(cpu_usage)
            if len(cpu_history) > 100:
                cpu_history.pop(0)
            
            cpu_color = RED if cpu_usage > 80 else YELLOW if cpu_usage > 50 else GREEN
            cpu_count = psutil.cpu_count()
            print(f"{CYAN}CPU Usage{RESET:>20} : {cpu_color}{make_bar(cpu_usage)}{RESET}  ({cpu_count} cores)")

            # Temperature
            temp = get_cpu_temperature()
            if temp:
                temp_color = RED if temp > 80 else YELLOW if temp > 60 else GREEN
                print(f"{CYAN}CPU Temperature{RESET:>20} : {temp_color}{temp:.1f}°C{RESET}")

            # Memory
            mem = psutil.virtual_memory()
            mem_history.append(mem.percent)
            if len(mem_history) > 100:
                mem_history.pop(0)
            
            mem_color = RED if mem.percent > 85 else YELLOW if mem.percent > 70 else GREEN
            mem_used = get_size(mem.used)
            mem_total = get_size(mem.total)
            print(f"{CYAN}Memory Usage{RESET:>20} : {mem_color}{make_bar(mem.percent)}{RESET}  ({mem_used}/{mem_total})")

            # Disk
            disk = psutil.disk_usage('/')
            disk_history.append(disk.percent)
            if len(disk_history) > 100:
                disk_history.pop(0)
            
            disk_color = RED if disk.percent > 90 else YELLOW if disk.percent > 80 else GREEN
            disk_used = get_size(disk.used)
            disk_total = get_size(disk.total)
            print(f"{CYAN}Disk Usage{RESET:>20} : {disk_color}{make_bar(disk.percent)}{RESET}  ({disk_used}/{disk_total})")

            # Load Average
            try:
                load_1, load_5, load_15 = os.getloadavg()
                print(f"{CYAN}Load Average{RESET:>20} : {load_1:.2f}, {load_5:.2f}, {load_15:.2f}")
            except (AttributeError, OSError):
                pass

            # System Uptime
            uptime = get_system_uptime()
            print(f"{CYAN}System Uptime{RESET:>20} : {uptime}")

            print(f"{GRAY}{'─' * 70}{RESET}")

            # =====================================================
            # HARDWARE & NETWORK SECTION
            # =====================================================
            print(f"{GREEN}HARDWARE & NETWORK STATUS{RESET}")
            print(f"{GRAY}{'─' * 70}{RESET}")

            # Network Speed
            up_speed, down_speed = get_net_speed()
            if up_speed and down_speed:
                print(f"{MAGENTA}🌐 Network Speed{RESET:>19} : ⬇️  {down_speed}   ⬆️  {up_speed}")
            else:
                print(f"{MAGENTA}🌐 Network Speed{RESET:>19} : {RED}N/A (Permission Denied){RESET}")

            # Active Connections
            connections = get_active_connections()
            print(f"{MAGENTA}🔗 Active Connections{RESET:>13} : {connections}")

            # Logged in Users
            users = get_logged_in_users()
            print(f"{MAGENTA}👥 Logged In Users{RESET:>15} : {users}")

            # Disk I/O
            read_speed, write_speed = get_disk_io()
            if read_speed and write_speed:
                print(f"{MAGENTA}💾 Disk I/O{RESET:>23} : Read: {read_speed}  Write: {write_speed}")
            else:
                print(f"{MAGENTA}💾 Disk I/O{RESET:>23} : {RED}N/A{RESET}")

            # Battery Status
            try:
                battery = psutil.sensors_battery()
                if battery:
                    plugged = "Charging 🔌" if battery.power_plugged else "Discharging 🔋"
                    batt_color = RED if battery.percent < 20 else YELLOW if battery.percent < 50 else GREEN
                    print(f"{MAGENTA}🔋 Battery{RESET:>24} : {batt_color}{battery.percent}%{RESET} [{plugged}]")
                else:
                    print(f"{MAGENTA}🔋 Battery{RESET:>24} : N/A (No battery detected)")
            except Exception:
                print(f"{MAGENTA}🔋 Battery{RESET:>24} : N/A")

            # GPU Info
            gpu_util, gpu_mem_used, gpu_mem_total = get_gpu_info()
            if gpu_util is not None:
                gpu_color = RED if gpu_util > 80 else YELLOW if gpu_util > 50 else GREEN
                print(f"{MAGENTA}🎮 GPU Utilization{RESET:>15} : {gpu_color}{gpu_util:.1f}%{RESET} ({get_size(gpu_mem_used*1024*1024)}/{get_size(gpu_mem_total*1024*1024)})")

            print(f"{GRAY}{'─' * 70}{RESET}")

            # =====================================================
            # TOP PROCESSES SECTION
            # =====================================================
            print(f"{YELLOW}🔥 TOP PROCESSES (BY CPU USAGE){RESET}")
            print(f"{GRAY}{'─' * 70}{RESET}")
            print(f"{GRAY}{'PID':<8}{'NAME':<25}{'CPU %':<10}{'MEM %':<10}{RESET}")

            processes = []
            try:
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                    try:
                        processes.append(proc.info)
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass
            except Exception:
                pass

            top_cpu = sorted(processes, key=lambda x: x['cpu_percent'] if x['cpu_percent'] is not None else 0, reverse=True)[:3]
            
            for p in top_cpu:
                p_name = p['name'][:23] if p['name'] else "Unknown"
                p_cpu = p['cpu_percent'] if p['cpu_percent'] is not None else 0.0
                p_mem = p['memory_percent'] if p['memory_percent'] is not None else 0.0
                cpu_col = RED if p_cpu > 50 else YELLOW if p_cpu > 20 else GREEN
                print(f"{p['pid']:<8}{p_name:<25}{cpu_col}{p_cpu:<10.1f}{RESET}{p_mem:<10.1f}")

            print(f"{GRAY}{'─' * 70}{RESET}")

            print(f"{YELLOW}💾 TOP PROCESSES (BY MEMORY USAGE){RESET}")
            print(f"{GRAY}{'─' * 70}{RESET}")
            print(f"{GRAY}{'PID':<8}{'NAME':<25}{'MEM %':<10}{'MEM':<15}{RESET}")

            top_mem = sorted(processes, key=lambda x: x['memory_percent'] if x['memory_percent'] is not None else 0, reverse=True)[:3]
            
            for p in top_mem:
                p_name = p['name'][:23] if p['name'] else "Unknown"
                p_mem = p['memory_percent'] if p['memory_percent'] is not None else 0.0
                try:
                    proc = psutil.Process(p['pid'])
                    mem_usage = get_size(proc.memory_info().rss)
                except:
                    mem_usage = "N/A"
                mem_col = RED if p_mem > 50 else YELLOW if p_mem > 20 else GREEN
                print(f"{p['pid']:<8}{p_name:<25}{mem_col}{p_mem:<10.1f}{RESET}{mem_usage:<15}")

            print(f"{GRAY}{'─' * 70}{RESET}")

            # =====================================================
            # ALERTS SECTION
            # =====================================================
            alerts = []
            if cpu_usage > 80:
                alerts.append(f"{RED}⚠️  HIGH CPU USAGE: {cpu_usage:.1f}%{RESET}")
            if mem.percent > 85:
                alerts.append(f"{RED}⚠️  HIGH MEMORY USAGE: {mem.percent:.1f}%{RESET}")
            if disk.percent > 90:
                alerts.append(f"{RED}⚠️  DISK SPACE CRITICAL: {disk.percent:.1f}%{RESET}")
            if temp and temp > 90:
                alerts.append(f"{RED}⚠️  CRITICAL CPU TEMPERATURE: {temp:.1f}°C{RESET}")
                play_alert_sound()
            
            if alerts:
                print(f"{YELLOW}ACTIVE ALERTS:{RESET}")
                for alert in alerts:
                    print(alert)
                print(f"{GRAY}{'─' * 70}{RESET}")

            # Status
            print(f"{GREEN}[√] Monitoring Active... | Data being logged to {LOG_FILE}{RESET}")

            # =====================================================
            # LOGGING
            # =====================================================
            try:
                log_data = {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'cpu': cpu_usage,
                    'mem': mem.percent,
                    'disk': disk.percent,
                    'temp': temp if temp else 'N/A'
                }
                
                # Log to TXT
                with open(LOG_FILE, "a") as f:
                    f.write(f"{log_data['timestamp']} | CPU:{log_data['cpu']:.1f}% | MEM:{log_data['mem']:.1f}% | DISK:{log_data['disk']:.1f}%\n")
                
                # Export to JSON and CSV
                export_to_json(log_data)
                export_to_csv(log_data)
                
            except Exception:
                pass

            time.sleep(INTERVAL)

    except KeyboardInterrupt:
        print(f"\n{GREEN}Matrix Monitor Stopped. Exiting safely...{RESET}\n")
        print(f"{CYAN}📊 Log files saved:{RESET}")
        print(f"   • Text: {LOG_FILE}")
        print(f"   • JSON: {JSON_LOG_FILE}")
        print(f"   • CSV: {CSV_LOG_FILE}\n")
        sys.exit(0)

# =====================================================
# INTERACTIVE MENU
# =====================================================

def show_menu():
    """Show interactive menu"""
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        print(f"{GREEN}{BOLD}╔══════════════════════════════════════════════════════════════╗{RESET}")
        print(f"{GREEN}{BOLD}║     🔥 MATRIX SYSTEM MONITOR - INTERACTIVE MENU 🔥           ║{RESET}")
        print(f"{GREEN}{BOLD}╚══════════════════════════════════════════════════════════════╝{RESET}\n")
        
        print(f"{CYAN}1{RESET}. Start Monitoring")
        print(f"{CYAN}2{RESET}. Search Process")
        print(f"{CYAN}3{RESET}. Kill Process")
        print(f"{CYAN}4{RESET}. View System Information")
        print(f"{CYAN}5{RESET}. Export Logs")
        print(f"{CYAN}6{RESET}. View Help")
        print(f"{CYAN}0{RESET}. Exit")
        
        choice = input(f"\n{MAGENTA}Enter your choice: {RESET}").strip()
        
        if choice == '1':
            monitor()
        elif choice == '2':
            search_menu()
        elif choice == '3':
            kill_menu()
        elif choice == '4':
            system_info()
        elif choice == '5':
            export_menu()
        elif choice == '6':
            show_help()
        elif choice == '0':
            print(f"{GREEN}Goodbye!{RESET}\n")
            sys.exit(0)
        else:
            print(f"{RED}Invalid choice. Please try again.{RESET}")
            time.sleep(2)

def search_menu():
    """Search for processes"""
    os.system('clear' if os.name == 'posix' else 'cls')
    process_name = input(f"{CYAN}Enter process name to search: {RESET}").strip()
    
    if not process_name:
        print(f"{RED}No process name provided.{RESET}")
        time.sleep(2)
        return
    
    results = search_process(process_name)
    
    os.system('clear' if os.name == 'posix' else 'cls')
    print(f"{GREEN}Search Results for '{process_name}':{RESET}\n")
    
    if results:
        print(f"{GRAY}{'PID':<8}{'NAME':<30}{'CPU %':<10}{'MEM %':<10}{RESET}")
        print(f"{GRAY}{'─' * 60}{RESET}")
        for p in results:
            p_name = p['name'][:28] if p['name'] else "Unknown"
            p_cpu = p['cpu_percent'] if p['cpu_percent'] is not None else 0.0
            p_mem = p['memory_percent'] if p['memory_percent'] is not None else 0.0
            print(f"{p['pid']:<8}{p_name:<30}{p_cpu:<10.1f}{p_mem:<10.1f}")
    else:
        print(f"{YELLOW}No processes found matching '{process_name}'.{RESET}")
    
    input(f"\n{CYAN}Press Enter to continue...{RESET}")

def kill_menu():
    """Kill a process"""
    os.system('clear' if os.name == 'posix' else 'cls')
    
    try:
        pid = int(input(f"{MAGENTA}Enter PID to kill: {RESET}").strip())
        success, message = kill_process(pid)
        
        if success:
            print(f"{GREEN}✓ {message}{RESET}")
            play_notification_sound()
        else:
            print(f"{RED}✗ {message}{RESET}")
    except ValueError:
        print(f"{RED}Invalid PID provided.{RESET}")
    
    time.sleep(2)

def system_info():
    """Display detailed system information"""
    os.system('clear' if os.name == 'posix' else 'cls')
    
    print(f"{GREEN}{BOLD}DETAILED SYSTEM INFORMATION{RESET}\n")
    
    # CPU Info
    print(f"{CYAN}CPU Information:{RESET}")
    print(f"  Cores: {psutil.cpu_count()}")
    print(f"  Max Frequency: {psutil.cpu_freq().max:.2f} MHz")
    print(f"  Current Frequency: {psutil.cpu_freq().current:.2f} MHz\n")
    
    # Memory Info
    mem_info = get_memory_info()
    print(f"{CYAN}Memory Information:{RESET}")
    for key, value in mem_info.items():
        if key != 'percent':
            print(f"  {key.capitalize()}: {value}")
    print()
    
    # Disk Info
    print(f"{CYAN}Disk Information:{RESET}")
    disks = get_all_disks()
    for disk in disks:
        print(f"  {disk['device']} ({disk['mountpoint']})")
        print(f"    Total: {disk['total']} | Used: {disk['used']} | Free: {disk['free']} | {disk['percent']:.1f}%")
    print()
    
    # Network Info
    print(f"{CYAN}Network Information:{RESET}")
    try:
        net_if = psutil.net_if_addrs()
        for interface, addrs in net_if.items():
            print(f"  {interface}:")
            for addr in addrs:
                print(f"    {addr.family.name}: {addr.address}")
    except Exception:
        print("  Unable to retrieve network info")
    
    input(f"\n{CYAN}Press Enter to continue...{RESET}")

def export_menu():
    """Export monitoring data"""
    os.system('clear' if os.name == 'posix' else 'cls')
    
    print(f"{GREEN}Exporting monitoring data...{RESET}\n")
    
    files = {
        'Text': LOG_FILE,
        'JSON': JSON_LOG_FILE,
        'CSV': CSV_LOG_FILE
    }
    
    for name, path in files.items():
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"{GREEN}✓{RESET} {name}: {path} ({get_size(size)})")
        else:
            print(f"{YELLOW}○{RESET} {name}: No data yet")
    
    input(f"\n{CYAN}Press Enter to continue...{RESET}")

def show_help():
    """Show help information"""
    os.system('clear' if os.name == 'posix' else 'cls')
    
    print(f"{GREEN}{BOLD}MATRIX SYSTEM MONITOR - HELP{RESET}\n")
    
    help_text = """
{CYAN}Features:{RESET}
  • Real-time CPU, Memory, and Disk monitoring
  • CPU Temperature monitoring
  • Network speed tracking
  • Active connections monitoring
  • Top processes by CPU and Memory usage
  • Disk I/O speed measurement
  • GPU utilization (if NVIDIA GPU detected)
  • Battery status tracking
  • System uptime display
  • Process search and kill functionality
  • Automatic data logging (TXT, JSON, CSV)
  • Alert system for high resource usage

{CYAN}Interactive Menu Options:{RESET}
  1. Start Monitoring - Begin real-time monitoring
  2. Search Process - Find processes by name
  3. Kill Process - Terminate a process by PID
  4. View System Info - Detailed system information
  5. Export Logs - View exported log files
  6. Help - Show this help message
  0. Exit - Close the application

{CYAN}Keyboard Shortcuts (During Monitoring):{RESET}
  Ctrl+C - Stop monitoring and exit safely

{CYAN}Log Files:{RESET}
  Text: ~/system-monitor.log
  JSON: ~/system-monitor.json
  CSV: ~/system-monitor.csv

{CYAN}Requirements:{RESET}
  • Python 3.6+
  • psutil module (pip install psutil)
  • For GPU monitoring: nvidia-smi (NVIDIA drivers)

{CYAN}Tips:{RESET}
  • Run with elevated privileges (sudo) for full data access
  • Monitor runs every 3 seconds by default
  • All data is automatically exported while monitoring
  • Search is case-insensitive
    """.format(CYAN=CYAN, RESET=RESET)
    
    print(help_text)
    input(f"{CYAN}Press Enter to continue...{RESET}")

# =====================================================
# MAIN ENTRY POINT FOR TERMINAL COMMAND
# =====================================================

def main():
    """GitHub Actions සහ Terminal Command එක සඳහා ප්‍රධාන Entry Point එක"""
    if len(sys.argv) > 1:
        if sys.argv[1] == '--monitor':
            monitor()
        elif sys.argv[1] == '--help':
            show_help()
        else:
            print(f"Usage: {sys.argv[0]} [--monitor|--help]")
            sys.exit(1)
    else:
        show_menu()

if __name__ == "__main__":
    main()
    

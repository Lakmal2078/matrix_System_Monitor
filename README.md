# 🔥 MATRIX SYSTEM MONITOR v3.0 - Full Documentation

## Overview

MATRIX System Monitor යනු Python-ට ලියැවුණු advanced system monitoring tool එකයි. Real-time data එක tracking කරනවා සහ beautiful UI එක display කරනවා with comprehensive features.

---

## ✨ Features

### Core Monitoring
- ✅ **CPU Usage Tracking** - Real-time CPU percentage සහ cores info
- ✅ **Memory Monitoring** - Available, used, total memory tracking
- ✅ **Disk Space** - Monitor root partition සහ all mounted drives
- ✅ **System Uptime** - Show කරනවා system කොපි කාලයක් on තිබේද
- ✅ **Load Average** - 1, 5, 15 minute load averages
- ✅ **Temperature Monitoring** - CPU temperature tracking (if available)

### Advanced Features
- 🌐 **Network Monitoring**
  - Real-time upload/download speeds
  - Active network connections count
  - Per-interface IP information
  
- 💾 **Disk I/O**
  - Read/Write speed tracking
  - All mounted partitions monitoring
  
- 🎮 **GPU Monitoring**
  - NVIDIA GPU utilization
  - GPU memory usage (if nvidia-smi available)
  
- 🔋 **Battery Status**
  - Battery percentage
  - Charging/Discharging status
  
- 👥 **User Management**
  - Currently logged-in users count
  - Active session information

### Process Management
- 🔍 **Process Search** - Case-insensitive process search
- ⚙️ **Top Processes** - Top 3 by CPU and Memory usage
- 🛑 **Process Killing** - Terminate processes safely by PID
- 📊 **Process Details** - PID, name, CPU%, Memory%

### Data Export
- 📄 **Text Logging** - `~/.system-monitor.log`
- 📋 **JSON Export** - `~/.system-monitor.json`
- 📊 **CSV Export** - `~/.system-monitor.csv`

### Alert System
- ⚠️ **High CPU Alert** - CPU > 80%
- ⚠️ **High Memory Alert** - Memory > 85%
- ⚠️ **Low Disk Space Alert** - Disk > 90%
- ⚠️ **Critical Temperature Alert** - Temp > 90°C (with sound)

---

## 📦 Installation

### Prerequisites
- Python 3.6 or higher
- pip (Python package manager)
- Linux or macOS (Windows සඳහා modifications සෙවිය යුතු)

### Automatic Installation (Recommended)

```bash
# Download the installation script
chmod +x install_monitor.sh
./install_monitor.sh
```

### Manual Installation

```bash
# Install psutil
pip3 install psutil

# Copy script to bin
sudo cp pymonitor_full.py /usr/local/bin/pymonitor
sudo chmod +x /usr/local/bin/pymonitor

# Add to ~/.bashrc or ~/.zshrc
echo "alias pymonitor='python3 /usr/local/bin/pymonitor'" >> ~/.bashrc
```

---

## 🚀 Usage

### Basic Commands

```bash
# Start interactive menu
pymonitor

# Start monitoring directly (no menu)
pymonitor --monitor

# Show help
pymonitor --help

# Run with full permissions
sudo pymonitor
```

### Interactive Menu

When you run `pymonitor` without arguments, you'll see the menu:

```
🔥 MATRIX SYSTEM MONITOR - INTERACTIVE MENU 🔥

1. Start Monitoring    - Begin real-time monitoring
2. Search Process      - Find processes by name
3. Kill Process        - Terminate a process by PID
4. View System Info    - Detailed system information
5. Export Logs         - View exported log files
6. Help                - Show help information
0. Exit                - Close the application
```

### During Monitoring

- **Ctrl+C** - Stop monitoring safely
- **Monitor runs every 3 seconds** - Data is logged automatically
- **Real-time updates** - All metrics update in real-time

---

## 💡 Examples

### Example 1: Basic Monitoring

```bash
$ pymonitor --monitor
```

This starts the monitoring dashboard immediately.

### Example 2: Search for Firefox Process

```bash
$ pymonitor
# Choose option 2
Enter process name to search: firefox
```

Output:
```
Search Results for 'firefox':

PID     NAME                      CPU %     MEM %
----    ----                      -----     -----
1234    firefox                   5.2       12.3
1245    firefox-esr               2.1       8.5
```

### Example 3: Kill a Process

```bash
$ pymonitor
# Choose option 3
Enter PID to kill: 1234
✓ Process 1234 terminated successfully
```

### Example 4: View Logs

```bash
$ cat ~/.system-monitor.log
2024-01-15 10:30:45 | CPU:25.3% | MEM:45.2% | DISK:60.5%
2024-01-15 10:30:48 | CPU:28.1% | MEM:46.1% | DISK:60.5%
2024-01-15 10:30:51 | CPU:26.5% | MEM:45.8% | DISK:60.5%
```

---

## 📊 Output Explanation

### Main Dashboard

```
╔══════════════════════════════════════════════════════════════════╗
║           🔥 MATRIX SYSTEM MONITOR v3.0 (Full Edition) 🔥         ║
╚══════════════════════════════════════════════════════════════════╝

SYSTEM OVERVIEW
─────────────────────────────────────────────────────────────────

CPU Usage        : [████████░░░░░░░░░░] 40.0%  (8 cores)
CPU Temperature  : 55.2°C
Memory Usage     : [██████░░░░░░░░░░░░░] 30.0%  (8.00GB/32.00GB)
Disk Usage       : [█████████████░░░░░░] 65.0%  (325.50GB/500.00GB)
Load Average     : 0.45, 0.52, 0.48
System Uptime    : 5d 12h 45m

HARDWARE & NETWORK STATUS
─────────────────────────────────────────────────────────────────

🌐 Network Speed         : ⬇️  2.50MB/s   ⬆️  1.20MB/s
🔗 Active Connections    : 45
👥 Logged In Users       : 2
💾 Disk I/O              : Read: 15.23MB/s  Write: 8.45MB/s
🔋 Battery               : 95% [Charging 🔌]
🎮 GPU Utilization       : 35.2% (4.50GB/8.00GB)

🔥 TOP PROCESSES (BY CPU USAGE)
─────────────────────────────────────────────────────────────────

PID     NAME                  CPU %     MEM %
1234    chrome                12.5      8.3
5678    python3               8.2       5.1
9012    firefox               6.1       10.5
```

---

## 📝 Log Files

### Text Format (~/system-monitor.log)

```
2024-01-15 10:30:45 | CPU:25.3% | MEM:45.2% | DISK:60.5%
2024-01-15 10:30:48 | CPU:28.1% | MEM:46.1% | DISK:60.5%
2024-01-15 10:30:51 | CPU:26.5% | MEM:45.8% | DISK:60.5%
```

### JSON Format (~/system-monitor.json)

```json
{"timestamp": "2024-01-15T10:30:45", "data": {"cpu": 25.3, "mem": 45.2, "disk": 60.5, "temp": 55.2}}
{"timestamp": "2024-01-15T10:30:48", "data": {"cpu": 28.1, "mem": 46.1, "disk": 60.5, "temp": 54.8}}
```

### CSV Format (~/system-monitor.csv)

```
Timestamp,CPU%,MEM%,DISK%,TEMP°C
2024-01-15 10:30:45,25.3,45.2,60.5,55.2
2024-01-15 10:30:48,28.1,46.1,60.5,54.8
2024-01-15 10:30:51,26.5,45.8,60.5,55.1
```

---

## 🎨 Color Coding

| Color | Meaning |
|-------|---------|
| 🟢 Green | Normal/Good (< 50%) |
| 🟡 Yellow | Warning (50-80%) |
| 🔴 Red | Critical (> 80%) |
| 🔵 Cyan | Information |
| 🟣 Magenta | Hardware/Network |

---

## ⚡ System Requirements

### Minimum
- Python 3.6+
- 50 MB free disk space
- Linux or macOS

### Recommended
- Python 3.8+
- 100 MB free disk space
- 4+ core CPU
- Elevated privileges (sudo)

### Optional
- NVIDIA drivers + nvidia-smi (GPU monitoring)
- Sound card (for alerts)

---

## 🔒 Permissions

For full functionality, run with `sudo`:

```bash
sudo pymonitor
```

This allows access to:
- Network interface details
- System temperature sensors
- All process information
- Battery status

---

## 🐛 Troubleshooting

### psutil not found
```bash
pip3 install psutil
# or
pip install psutil --break-system-packages
```

### Permission Denied Errors
```bash
# Run with sudo for full access
sudo pymonitor

# Or give execute permissions
chmod +x /usr/local/bin/pymonitor
```

### GPU Monitoring Not Working
```bash
# Install NVIDIA drivers
# Check nvidia-smi is available
nvidia-smi
```

### No Temperature Data
- Temperature sensors may not be available
- Some CPUs don't expose temperature
- Check: `sensors` command (if available)

### Network Speed Shows N/A
- Run with sudo for full access
- Check network interface permissions

---

## 📋 Configuration

Default settings in the script:

```python
LOG_FILE = os.path.expanduser("~/system-monitor.log")      # Log file location
JSON_LOG_FILE = os.path.expanduser("~/system-monitor.json") # JSON export
CSV_LOG_FILE = os.path.expanduser("~/system-monitor.csv")   # CSV export
INTERVAL = 3                                                  # Update interval (seconds)
MAX_LOG_ENTRIES = 1000                                       # Max log entries
```

To modify, edit `/usr/local/bin/pymonitor` and change the configuration section.

---

## 🚀 Advanced Usage

### Export logs to analyze

```bash
# View latest 100 entries
tail -n 100 ~/.system-monitor.log

# Parse JSON logs
python3 << 'EOF'
import json
with open(os.path.expanduser('~/.system-monitor.json')) as f:
    for line in f:
        data = json.loads(line)
        print(data['timestamp'], data['data']['cpu'])
EOF

# Analyze CSV with pandas
python3 << 'EOF'
import pandas as pd
df = pd.read_csv(os.path.expanduser('~/.system-monitor.csv'))
print(df.describe())
EOF
```

### Run in background

```bash
# Run monitoring in background
nohup pymonitor --monitor > /dev/null 2>&1 &

# Or with screen
screen -S monitor
pymonitor --monitor
# Detach with Ctrl+A then D
```

### Cron Job Integration

```bash
# Monitor every hour
0 * * * * /usr/local/bin/pymonitor --monitor > /dev/null 2>&1

# Or specific monitoring
0 9 * * * sudo /usr/local/bin/pymonitor --monitor > ~/monitor_$(date +\%Y\%m\%d_\%H\%M\%S).log 2>&1
```

---

## 📞 Support & Issues

- **Check the Help Menu**: `pymonitor` → Option 6
- **View Logs**: `~/.system-monitor.log`
- **Common Issues**: See Troubleshooting section
- **Feature Requests**: Modify the script as needed

---

## 📄 License

This tool is provided as-is for system monitoring purposes.

---

## 🎯 Version History

### v3.0 (Current)
- ✅ Full-featured system monitoring
- ✅ Interactive menu system
- ✅ Process search and kill
- ✅ JSON/CSV export
- ✅ GPU monitoring
- ✅ Temperature tracking
- ✅ Alert system

### v2.1
- CPU, Memory, Disk monitoring
- Network speed tracking
- Top processes display

### v1.0
- Basic monitoring

---

**Happy Monitoring! 🔥**

For updates and improvements, keep the script handy and modify as needed!

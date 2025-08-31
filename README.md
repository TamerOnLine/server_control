# server_control

`server_control` is a lightweight **server monitoring and control tool** built in Python.  
It lets you connect to any remote Linux server (via SSH) and launch a live monitoring dashboard powered by `tmux`.

## 🔹 What it does

- 📜 Stream **cloud-init logs** (`/var/log/cloud-init-output.log`)  
- 📝 Follow **system/service logs** (e.g., `journalctl -fu peertube`)  
- 📊 View **CPU, memory, and process usage** with `htop`  
- 🔄 Auto-fix SSH host key issues (`fix_known_hosts.py`)  

This project starts as a monitoring tool but is designed to expand into **full server management**: service control, updates, firewall, database management, and more.

---

## 🚀 Features

- One-command setup (`tmux` + `htop` installation if missing)
- Multi-pane `tmux` monitoring:
  - Top → cloud-init logs  
  - Bottom-left → journalctl logs  
  - Bottom-right → htop  
- Works with any Linux server (tested on Ubuntu 22.04/24.04)  
- Self-healing SSH connections (host key reset automation)

---

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/TamerOnLine/server_control.git
cd server_control
```

(Optional) create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows PowerShell
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 📡 Usage

### Fix SSH host key (if IP changed):

```bash
python -m fix_known_hosts --host <IP> --user root
```

### Start monitoring session:

```bash
python monitor.py --host <IP> --user root --install
```

**Arguments:**
- `--host` → server IP or domain  
- `--user` → SSH username (default: root)  
- `--install` → auto-install `tmux` + `htop` on the server  

**Example:**
```bash
python monitor.py --host 159.69.122.193 --user root --install
```

---

## 🛠 Roadmap

- [x] Basic monitoring with tmux  
- [x] SSH host key auto-fix  
- [ ] Service management (start/stop/restart)  
- [ ] Firewall management (ufw/iptables)  
- [ ] Database management (Postgres/MySQL)  
- [ ] File transfer integration (scp/rsync)  
- [ ] Web UI dashboard (Flask/FastAPI + React/Vue)  
- [ ] Multi-server monitoring  

---

## 📄 License

[MIT](LICENSE) © 2025 [TamerOnLine](https://github.com/TamerOnLine)  

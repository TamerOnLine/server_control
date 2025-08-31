#!/usr/bin/env python3
import argparse, os, shlex, subprocess, sys
from datetime import datetime

def run(cmd, check=True):
    print(f"$ {cmd}")
    return subprocess.run(cmd, shell=True, check=check)

def ssh_wrap(cmd, host=None, user="root", force_tty=False):
    if not host or host in ("localhost", "127.0.0.1"):
        return cmd
    # -t لإجبار TTY لبعض الأوامر التفاعلية (htop, journalctl -f)
    tflag = "-t" if force_tty else ""
    return f"ssh {tflag} {shlex.quote(f'{user}@{host}')} {shlex.quote(cmd)}"

def ensure_tools(host=None, user="root", install=False):
    # تثبيت tmux و htop محليًا أو على الخادوم البعيد إذا طلبت --install
    if not install:
        return
    cmd = "apt-get update -y && apt-get install -y tmux htop"
    run(ssh_wrap(cmd, host, user))

def tmux(cmd):
    return run(f"tmux {cmd}")

def main():
    p = argparse.ArgumentParser(description="Server live monitor (cloud-init + service logs + htop) locally or via SSH.")
    p.add_argument("--host", help="Server IP/hostname (omit or 'localhost' for local).", default=None)
    p.add_argument("--user", help="SSH user (when --host is used).", default="root")
    p.add_argument("--service", help="Primary service to follow with journalctl.", default="peertube")
    p.add_argument("--extra-service", action="append", default=[], help="Extra service(s) to follow (can repeat).")
    p.add_argument("--session", help="tmux session name (auto if not set).")
    p.add_argument("--no-cloudinit", action="store_true", help="Hide cloud-init pane.")
    p.add_argument("--no-htop", action="store_true", help="Hide htop pane.")
    p.add_argument("--add-nginx", action="store_true", help="Add nginx logs pane.")
    p.add_argument("--install", action="store_true", help="Install tmux/htop before starting.")
    args = p.parse_args()

    # اسم الجلسة
    default_session = f"mon-{(args.host or 'local').replace('.', '-')}-{args.service}-{datetime.now().strftime('%H%M%S')}"
    session = args.session or default_session

    # تأكد من الأدوات
    ensure_tools(args.host, args.user, install=args.install)

    # اغلق جلسة قديمة بنفس الاسم (إن وجدت)
    subprocess.run(f"tmux kill-session -t {shlex.quote(session)}", shell=True)

    # أنشئ جلسة tmux
    tmux(f"new-session -d -s {shlex.quote(session)}")

    # نبني لستة الأوامر لكل نافذة
    panes = []

    # 1) cloud-init (اختياري)
    if not args.no_cloudinit:
        cmd = "tail -f /var/log/cloud-init-output.log"
        panes.append(ssh_wrap(cmd, args.host, args.user, force_tty=True))

    # 2) الخدمة الأساسية
    svc_cmd = f"journalctl -fu {shlex.quote(args.service)}"
    panes.append(ssh_wrap(svc_cmd, args.host, args.user, force_tty=True))

    # 3) htop (اختياري)
    if not args.no-htop if False else not args.no_htop:  # guard for hyphen var
        cmd = "htop"
        panes.append(ssh_wrap(cmd, args.host, args.user, force_tty=True))

    # 4) nginx (اختياري)
    if args.add_nginx:
        cmd = "journalctl -fu nginx"
        panes.append(ssh_wrap(cmd, args.host, args.user, force_tty=True))

    # 5) خدمات إضافية
    for extra in args.extra_service:
        cmd = f"journalctl -fu {shlex.quote(extra)}"
        panes.append(ssh_wrap(cmd, args.host, args.user, force_tty=True))

    if not panes:
        print("No panes to show. Enable at least one (e.g. remove --no-cloudinit or set --service).")
        sys.exit(1)

    # ارسل أول أمر في النافذة الأولى
    first = panes[0]
    tmux(f"send-keys -t {shlex.quote(session)} {shlex.quote(first)} C-m")

    # افتح بقية الأوامر في نوافذ مقسّمة
    for cmd in panes[1:]:
        tmux(f"split-window -t {shlex.quote(session)}")
        tmux(f"send-keys -t {shlex.quote(session)} {shlex.quote(cmd)} C-m")

    # ترتيب ممتاز
    tmux(f"select-layout -t {shlex.quote(session)} tiled")

    print(f"\n[+] Attached to tmux session: {session}")
    os.execvp("tmux", ["tmux", "attach", "-t", session])

if __name__ == "__main__":
    main()

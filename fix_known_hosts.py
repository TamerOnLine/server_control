#!/usr/bin/env python3
import subprocess
import os
import pexpect

IP = "159.69.122.193"
USER = "root"

# غيّر هذه القيم حسب ما عندك
OLD_PASS = "كلمة_المرور_الحالية"
NEW_PASS = "كلمة_المرور_الجديدة"

def run(cmd):
    print(f"$ {cmd}")
    return subprocess.run(cmd, shell=True)

def ssh_change_password():
    print("\n[+] Trying to login and change password...")
    child = pexpect.spawn(f"ssh {USER}@{IP}", timeout=30)

    try:
        # أول طلب كلمة المرور
        child.expect("password:")
        child.sendline(OLD_PASS)

        # رسالة إلزام تغيير الباسورد
        i = child.expect([
            "Current password:",
            "You are required to change your password immediately",
            pexpect.EOF,
            pexpect.TIMEOUT
        ], timeout=20)

        if i == 0 or i == 1:
            child.sendline(OLD_PASS)
            child.expect("New password:")
            child.sendline(NEW_PASS)
            child.expect("Retype new password:")
            child.sendline(NEW_PASS)
            print("[+] Password changed successfully!")

        child.expect(["#", ">", "\\$"], timeout=20)
        child.sendline("exit")
        child.close()

    except pexpect.ExceptionPexpect as e:
        print(f"[!] Failed to change password automatically: {e}")
        child.close()

def main():
    # 1) امسح البصمات القديمة
    run(f"ssh-keygen -R {IP}")
    run(f"ssh-keygen -R '[{IP}]:22'")

    # 2) اجبر ssh يضيف البصمة الجديدة
    print("\n[+] تثبيت البصمة الجديدة...")
    run(f"ssh -o StrictHostKeyChecking=accept-new {USER}@{IP} exit")

    # 3) جرّب تغيير الباسورد إن لزم
    ssh_change_password()

    # 4) شغّل monitor.py
    print("\n[+] تشغيل المونيتور...")
    run(f"python monitor.py --host {IP} --user {USER} --install")

if __name__ == "__main__":
    main()

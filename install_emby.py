#!/usr/bin/env python3
"""
install_emby.py

Connects to a remote Linux server over SSH and installs Emby Server.

Requires:
    pip install paramiko

The remote SSH account you log in with must have sudo privileges
(passwordless sudo, or you'll be prompted to adjust the sudo calls below).

This script:
  1. Prompts for the server IP, SSH login credentials, and the Emby
     download URL (.deb package).
  2. Downloads the package on the remote host.
  3. Installs it (and any missing dependencies).
  4. Creates a local Linux user "emby" with password "go".
  5. Starts and enables the emby-server service.
  6. Prints a success message once everything completes without error.
"""

import sys
import getpass

try:
    import paramiko
except ImportError:
    sys.exit("Missing dependency. Install it with: pip install paramiko")


def run_remote_command(ssh_client, command, sudo_password=None, description=""):
    """Run a command over SSH, stream output, and check the exit status."""
    if description:
        print(f"\n--- {description} ---")

    stdin, stdout, stderr = ssh_client.exec_command(command, get_pty=True)

    # If the command uses sudo -S, feed the sudo password in.
    if sudo_password and command.strip().startswith("sudo"):
        stdin.write(sudo_password + "\n")
        stdin.flush()

    out = stdout.read().decode(errors="ignore")
    err = stderr.read().decode(errors="ignore")
    exit_status = stdout.channel.recv_exit_status()

    if out.strip():
        print(out.strip())
    if err.strip():
        print(err.strip())

    if exit_status != 0:
        raise RuntimeError(f"Command failed (exit {exit_status}): {command}")

    return out


def main():
    print("=== Emby Server Remote Installer ===\n")

    server_ip = input("Enter the server IP address: ").strip()
    ssh_user = input("Enter the SSH username: ").strip()
    ssh_password = getpass.getpass("Enter the SSH password: ")
    download_url = input("Enter the URL for the latest Emby .deb package: ").strip()

    if not server_ip or not ssh_user or not download_url:
        sys.exit("Server IP, SSH username, and download URL are all required.")

    remote_deb_path = "/tmp/emby-server.deb"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"\nConnecting to {server_ip} as {ssh_user}...")
        ssh.connect(hostname=server_ip, username=ssh_user, password=ssh_password)

        # 1. Download the Emby package
        run_remote_command(
            ssh,
            f"wget -O {remote_deb_path} '{download_url}'",
            description="Downloading Emby Server package",
        )

        # 2. Install the package
        run_remote_command(
            ssh,
            f"sudo -S dpkg -i {remote_deb_path}",
            sudo_password=ssh_password,
            description="Installing Emby Server package",
        )

        # 3. Fix any missing dependencies
        run_remote_command(
            ssh,
            "sudo -S apt-get install -f -y",
            sudo_password=ssh_password,
            description="Resolving dependencies",
        )

        # 4. Create the "emby" user with password "go"
        run_remote_command(
            ssh,
            "sudo -S useradd -m emby || true",
            sudo_password=ssh_password,
            description="Creating user 'emby'",
        )
        run_remote_command(
            ssh,
            "echo 'emby:go' | sudo -S chpasswd",
            sudo_password=ssh_password,
            description="Setting password for user 'emby'",
        )

        # 5. Enable and start the Emby service
        run_remote_command(
            ssh,
            "sudo -S systemctl enable --now emby-server",
            sudo_password=ssh_password,
            description="Starting Emby Server service",
        )

        print("\nEmby server installed and ready for use")

    except Exception as e:
        print(f"\nInstallation failed: {e}")
        sys.exit(1)

    finally:
        ssh.close()


if __name__ == "__main__":
    main()

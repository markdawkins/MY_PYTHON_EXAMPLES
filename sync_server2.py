!/usr/bin/env python3
"""
sync_srv.py
 
One-way sync tool for a "srv/" folder between two Ubuntu workstations
connected over SSH/network.
 
What it does:
  1. Prompts for connection details (IP, username, password) for a
     PRIMARY and a SECONDARY server.
  2. Connects to both over SSH/SFTP and recursively lists the contents
     of each server's srv/ directory.
  3. Compares the two file listings (by relative path + size).
  4. Copies any file that exists on PRIMARY but NOT on SECONDARY
     (by relative path) from PRIMARY -> SECONDARY. Existing files on
     the secondary are left untouched (never overwritten).
  5. Re-checks the two directories after copying and, if they match,
     prints a "File Sync Complete" banner.
 
Requirements:
  pip install paramiko
 
IMPORTANT NOTE ON PASSWORDS + CRON:
  This script prompts interactively for passwords (via getpass), which
  is fine when you run it manually. A cron job has no terminal to type
  a password into, so an interactive password prompt will hang/fail
  when run unattended. For cron use, either:
    - Switch to SSH key-based auth (recommended) and modify this script
      to use `key_filename=` instead of `password=` in the connect()
      calls, or
    - Store credentials securely (e.g. environment variables read by
      cron, or a secrets manager) and adapt the credential-gathering
      function accordingly.
  This script is written so that swapping the auth method only
  requires changing the `get_ssh_client()` function.
 
Usage:
  python3 sync_srv.py
  (or from cron, once adapted for non-interactive auth):
  */30 * * * * /usr/bin/python3 /path/to/sync_srv.py >> /var/log/srv_sync.log 2>&1
"""
 
import sys
import os
import posixpath
import getpass
import stat
import logging
from dataclasses import dataclass
 
try:
    import paramiko
except ImportError:
    print("ERROR: paramiko is required. Install it with:")
    print("    pip install paramiko")
    sys.exit(1)
 
 
# --------------------------------------------------------------------------
# Configuration / constants
# --------------------------------------------------------------------------
 
REMOTE_SRV_DIR = "srv"  # relative path used on both servers; change if needed
SSH_PORT = 22
SSH_TIMEOUT = 15  # seconds
 
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("sync_srv")
 
 
@dataclass
class ServerInfo:
    role: str  # "PRIMARY" or "SECONDARY"
    host: str
    username: str
    password: str
    srv_path: str  # absolute path to the srv/ dir on that server
 
 
# --------------------------------------------------------------------------
# Credential gathering
# --------------------------------------------------------------------------
 
def prompt_for_server(role: str) -> ServerInfo:
    """
    Interactively prompt the user for connection details for one server.
    Replace this function (or branch inside it) if you need non-interactive
    credential loading for cron.
    """
    print(f"\n--- {role} server details ---")
    host = input(f"{role} server IP address / hostname: ").strip()
    username = input(f"{role} server username: ").strip()
    password = getpass.getpass(f"{role} server password: ")
    srv_path = input(
        f"Absolute path to srv/ on {role} server "
        f"[default: /home/{username}/srv]: "
    ).strip()
    if not srv_path:
        srv_path = f"/home/{username}/srv"
 
    return ServerInfo(
        role=role,
        host=host,
        username=username,
        password=password,
        srv_path=srv_path,
    )
 
 
# --------------------------------------------------------------------------
# SSH / SFTP helpers
# --------------------------------------------------------------------------
 
def get_ssh_client(server: ServerInfo) -> paramiko.SSHClient:
    """
    Establish an SSH connection to a server using password auth.
    To switch to key-based auth for cron use, replace `password=server.password`
    with `key_filename="/path/to/key"` (and remove password prompting above).
    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            hostname=server.host,
            port=SSH_PORT,
            username=server.username,
            password=server.password,
            timeout=SSH_TIMEOUT,
        )
    except Exception as e:
        log.error(f"Failed to connect to {server.role} ({server.host}): {e}")
        sys.exit(1)
    return client
 
 
def list_remote_files(sftp: paramiko.SFTPClient, base_path: str) -> dict:
    """
    Recursively list all files under base_path on a remote server.
    Returns a dict mapping: relative_path -> size_in_bytes
    Directories are traversed but not included as entries themselves.
    """
    files = {}
 
    def _walk(remote_dir: str, rel_prefix: str):
        try:
            entries = sftp.listdir_attr(remote_dir)
        except IOError as e:
            log.error(f"Cannot list remote directory '{remote_dir}': {e}")
            sys.exit(1)
 
        for entry in entries:
            remote_path = posixpath.join(remote_dir, entry.filename)
            rel_path = posixpath.join(rel_prefix, entry.filename) if rel_prefix else entry.filename
 
            if stat.S_ISDIR(entry.st_mode):
                _walk(remote_path, rel_path)
            else:
                files[rel_path] = entry.st_size
 
    _walk(base_path, "")
    return files
 
 
def ensure_remote_dirs(sftp: paramiko.SFTPClient, remote_dir: str):
    """
    Ensure all directories in remote_dir exist on the remote server,
    creating any that are missing (like `mkdir -p`).
    """
    parts = remote_dir.strip("/").split("/")
    current = ""
    for part in parts:
        current = f"{current}/{part}" if current else f"/{part}"
        try:
            sftp.stat(current)
        except FileNotFoundError:
            sftp.mkdir(current)
 
 
def copy_file_between_servers(
    primary_sftp: paramiko.SFTPClient,
    secondary_sftp: paramiko.SFTPClient,
    primary_full_path: str,
    secondary_full_path: str,
):
    """
    Copy a single file from primary server to secondary server by
    streaming it through the local machine (download then upload).
    """
    tmp_local = f"/tmp/_sync_srv_tmp_{os.path.basename(secondary_full_path)}"
    try:
        primary_sftp.get(primary_full_path, tmp_local)
        remote_dir = posixpath.dirname(secondary_full_path)
        ensure_remote_dirs(secondary_sftp, remote_dir)
        secondary_sftp.put(tmp_local, secondary_full_path)
    finally:
        if os.path.exists(tmp_local):
            os.remove(tmp_local)
 
 
# --------------------------------------------------------------------------
# Main sync logic
# --------------------------------------------------------------------------
 
def main():
    print("=" * 60)
    print(" srv/ Directory Sync Tool (one-way: PRIMARY -> SECONDARY) ")
    print("=" * 60)
 
    primary = prompt_for_server("PRIMARY")
    secondary = prompt_for_server("SECONDARY")
 
    log.info(f"Connecting to PRIMARY server {primary.host} ...")
    primary_client = get_ssh_client(primary)
    primary_sftp = primary_client.open_sftp()
 
    log.info(f"Connecting to SECONDARY server {secondary.host} ...")
    secondary_client = get_ssh_client(secondary)
    secondary_sftp = secondary_client.open_sftp()
 
    try:
        # Step 1: list files on both sides
        log.info(f"Scanning PRIMARY srv/ directory: {primary.srv_path}")
        primary_files = list_remote_files(primary_sftp, primary.srv_path)
        log.info(f"Found {len(primary_files)} file(s) on PRIMARY.")
 
        log.info(f"Scanning SECONDARY srv/ directory: {secondary.srv_path}")
        secondary_files = list_remote_files(secondary_sftp, secondary.srv_path)
        log.info(f"Found {len(secondary_files)} file(s) on SECONDARY.")
 
        # Step 2: determine which files are missing on secondary
        missing_on_secondary = [
            rel_path for rel_path in primary_files
            if rel_path not in secondary_files
        ]
 
        if not missing_on_secondary:
            log.info("No missing files. Secondary already has everything primary has.")
        else:
            log.info(f"{len(missing_on_secondary)} file(s) need to be copied to SECONDARY:")
            for rel_path in missing_on_secondary:
                print(f"    -> {rel_path}")
 
            # Step 3: copy each missing file (never overwrite existing ones)
            for rel_path in missing_on_secondary:
                primary_full_path = posixpath.join(primary.srv_path, rel_path)
                secondary_full_path = posixpath.join(secondary.srv_path, rel_path)
 
                log.info(f"Copying: {rel_path}")
                copy_file_between_servers(
                    primary_sftp, secondary_sftp,
                    primary_full_path, secondary_full_path,
                )
 
        # Step 4: re-verify sync status after copying
        log.info("Re-checking directories after sync ...")
        primary_files_after = list_remote_files(primary_sftp, primary.srv_path)
        secondary_files_after = list_remote_files(secondary_sftp, secondary.srv_path)
 
        still_missing = [
            rel_path for rel_path in primary_files_after
            if rel_path not in secondary_files_after
        ]
 
        # Optional sanity check: warn (don't fail) if sizes differ for
        # files that exist on both sides -- this does not block the sync
        # since we never overwrite existing files by design.
        size_mismatches = [
            rel_path for rel_path in primary_files_after
            if rel_path in secondary_files_after
            and primary_files_after[rel_path] != secondary_files_after[rel_path]
        ]
        if size_mismatches:
            log.warning(
                f"{len(size_mismatches)} file(s) exist on both servers but differ "
                f"in size (not overwritten, since existing files are skipped):"
            )
            for rel_path in size_mismatches:
                print(f"    ~ {rel_path}")
 
        if still_missing:
            log.error(
                f"Sync incomplete: {len(still_missing)} file(s) still missing on SECONDARY "
                f"after copy attempt."
            )
            for rel_path in still_missing:
                print(f"    ! {rel_path}")
            sys.exit(1)
        else:
            print_banner("File Sync Complete")
 
    finally:
        primary_sftp.close()
        secondary_sftp.close()
        primary_client.close()
        secondary_client.close()
 
 
def print_banner(message: str):
    line = "*" * (len(message) + 8)
    print()
    print(line)
    print(f"*   {message}   *")
    print(line)
    print()
 
 
if __name__ == "__main__":
    main()
 

import paramiko
import getpass
import time

def get_virtual_server_status(hostname, username, password, virtual_name):
    try:
        # SSH setup
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print(f"Connecting to {hostname}...")
        client.connect(hostname, username=username, password=password, timeout=10)

        # Open shell
        shell = client.invoke_shell()
        time.sleep(1)
        shell.recv(1000)  # Clear banner

        # Enter bash
        shell.send("run /util bash\n")
        time.sleep(1)
        shell.recv(1000)

        # Run the tmsh command from within bash
        tmsh_command = f"tmsh show ltm virtual {virtual_name}\n"
        shell.send(tmsh_command)
        time.sleep(2)
        output = shell.recv(5000).decode()

        # Check if not found or error
        if "was not found" in output:
            print(f"❌ Virtual server '{virtual_name}' not found.")
            return

        # Parse and print status
        print(f"\n✅ Status for virtual server '{virtual_name}':\n")
        for line in output.splitlines():
            if "Availability" in line or "State" in line:
                print(line.strip())

    except Exception as e:
        print(f"⚠️ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    hostname = input("Enter F5 hostname or IP: ")
    username = input("Enter your username: ")
    password = getpass.getpass("Enter your password: ")
    virtual_name = input("Enter the virtual server name: ")

    get_virtual_server_status(hostname, username, password, virtual_name)

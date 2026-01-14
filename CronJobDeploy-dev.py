import paramiko
import getpass
import time 

#time.sleep(10)
def connect_and_show_ltm(host, username, password):
    try:
        # Initialize the SSH client
        client = paramiko.SSHClient()

        # Automatically add the host key if not already in the known hosts
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the F5 load balancer
        print(f"Connecting to {host}...")
        client.connect(hostname=host, username=username, password=password)
        print("Connected successfully.")

        # Execute the command
        stdin, stdout, stderr = client.exec_command(
           """
           bash -c '
           ls -l &&
           curl -o /shared/backup.py https://librenms.sys.testsite.com/f5/backup.py &&
           chmod +x /shared/backup.py &&
           crontab -l | tee /shared/crontab.backup &&
           (crontab -l | sed -e "/backup\\.[sh|py]/ s/^#*/#/" 2>/dev/null; 
           echo "30 1 * * Mon,Thu,Sat /shared/backup.py >/dev/null 2>&1") | crontab - &&
           crontab -l
           '
           """
    )

        
        # Read and print the output of the command
        output = stdout.read().decode()
        error = stderr.read().decode()

        if output:
            print("\n--- Bash Command Output ---\n")
            print(output)
        if error:
            print("\n--- Errors ---\n")
            print(error)

    except paramiko.AuthenticationException:
        print("Authentication failed, please verify your credentials.")
    except paramiko.SSHException as ssh_exception:
        print(f"SSH connection error: {ssh_exception}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the connection
        client.close()
        print("Connection closed.")

if __name__ == "__main__":
    # Prompt user for F5 host IP or hostname
    f5_host = input("Enter the F5 host IP or hostname: ")
    
    # Prompt user for username
    
    f5_username = input("Enter your username: ")

    # Prompt user for password (hidden input)
    
    f5_password = getpass.getpass("Enter your password: ")

    # Connect to the F5 and show LTM configuration
    connect_and_show_ltm(f5_host, f5_username, f5_password)       

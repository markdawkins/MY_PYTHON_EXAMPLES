import os
import time
import ftplib
import smtplib
from email.message import EmailMessage
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configuration
SOURCE_FOLDER = "/home/mark/Downloads/qbitdownloads"
FTP_SERVER = "192.168.1.142"
FTP_FOLDER = "/media/mark/vids3"
FTP_USER = "anonymous"
FTP_PASSWORD = "password"
CHECK_INTERVAL = 150
CHUNK_SIZE = 65536
MAX_RETRIES = 5
RETRY_DELAY = 30
MIN_STABLE_TIME = 60
MAX_WAIT_TIME = 3600

# Email Configuration
EMAIL_SENDER = "code.lab.072025@gmail.com"
EMAIL_RECEIVER = "username@gmail.com"
EMAIL_SUBJECT = "FTP Upload Script Completion"
EMAIL_BODY = "All file uploads completed"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "code.lab.072025@gmail.com"
SMTP_PASSWORD = "your_app_password_here"  # Use an App Password if 2FA is enabled

class FTPUploader:
    def __init__(self):
        self.ftp = None
        self.connect()
        
    def connect(self):
        try:
            if self.ftp:
                try:
                    self.ftp.quit()
                except:
                    pass
            self.ftp = ftplib.FTP(FTP_SERVER, timeout=120)
            self.ftp.login(FTP_USER, FTP_PASSWORD)
            self.ftp.set_pasv(True)
            self._ensure_ftp_folder()
            return True
        except Exception as e:
            print(f"FTP connection failed: {str(e)}")
            return False
    
    def _ensure_ftp_folder(self):
        try:
            self.ftp.cwd(FTP_FOLDER)
        except ftplib.error_perm:
            try:
                path_parts = [p for p in FTP_FOLDER.split('/') if p]
                current_path = ""
                for part in path_parts:
                    current_path += f"/{part}"
                    try:
                        self.ftp.cwd(current_path)
                    except ftplib.error_perm:
                        self.ftp.mkd(current_path)
                        print(f"Created directory: {current_path}")
                self.ftp.cwd(FTP_FOLDER)
            except Exception as e:
                print(f"Failed to create FTP folder: {str(e)}")
                raise
    
    def upload_file(self, file_path):
        file_name = os.path.basename(file_path)
        
        for attempt in range(MAX_RETRIES):
            try:
                if not os.path.exists(file_path):
                    print(f"File not found: {file_path}")
                    return False
                
                print(f"Attempt {attempt + 1}/{MAX_RETRIES} for {file_name}")
                
                if not self.ftp and not self.connect():
                    time.sleep(RETRY_DELAY)
                    continue
                
                self.ftp.cwd(FTP_FOLDER)
                file_size = os.path.getsize(file_path)
                print(f"Uploading {file_name} ({file_size/1024/1024:.2f} MB)...")
                
                with open(file_path, 'rb') as f:
                    self.ftp.storbinary(f'STOR {file_name}', f, blocksize=CHUNK_SIZE)
                
                print(f"Successfully uploaded {file_name}")
                return True
                
            except (ftplib.error_temp, ftplib.error_reply, ConnectionError) as e:
                print(f"Temporary error: {str(e)}")
                time.sleep(RETRY_DELAY)
                self.connect()
            except Exception as e:
                print(f"Fatal error: {str(e)}")
                break
                
        print(f"Failed to upload {file_name} after {MAX_RETRIES} attempts")
        return False
    
    def is_file_stable(self, file_path):
        try:
            stat1 = os.stat(file_path)
            size1 = stat1.st_size
            mtime1 = stat1.st_mtime
            
            time.sleep(MIN_STABLE_TIME/2)
            stat2 = os.stat(file_path)
            
            return (size1 == stat2.st_size and 
                   mtime1 == stat2.st_mtime and
                   (time.time() - stat2.st_mtime) >= MIN_STABLE_TIME/2)
        except Exception as e:
            print(f"Error checking file stability: {str(e)}")
            return False
        
    def close(self):
        if self.ftp:
            try:
                self.ftp.quit()
            except:
                pass

class FolderMonitor(FileSystemEventHandler):
    def __init__(self, uploader):
        self.uploader = uploader
        self.pending_files = {}
        
    def on_created(self, event):
        if not event.is_directory:
            self._handle_new_file(event.src_path)
            
    def _handle_new_file(self, file_path):
        if file_path not in self.pending_files:
            print(f"Tracking new file: {os.path.basename(file_path)}")
            self.pending_files[file_path] = {
                'first_seen': time.time(),
                'last_checked': 0,
                'stable': False
            }
    
    def check_pending_files(self):
        for file_path, file_info in list(self.pending_files.items()):
            try:
                if file_info['stable']:
                    continue
                
                if not os.path.exists(file_path):
                    print(f"File disappeared: {os.path.basename(file_path)}")
                    self.pending_files.pop(file_path)
                    continue
                
                if time.time() - file_info['first_seen'] > MAX_WAIT_TIME:
                    print(f"Timeout waiting for file: {os.path.basename(file_path)}")
                    self.pending_files.pop(file_path)
                    continue
                
                if self.uploader.is_file_stable(file_path):
                    print(f"File ready for upload: {os.path.basename(file_path)}")
                    if self.uploader.upload_file(file_path):
                        file_info['stable'] = True
                        self.pending_files.pop(file_path)
                else:
                    print(f"Still waiting for: {os.path.basename(file_path)}")
                    
            except Exception as e:
                print(f"Error checking file {os.path.basename(file_path)}: {str(e)}")

def send_completion_email():
    """Send email notification when script completes"""
    try:
        msg = EmailMessage()
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER
        msg['Subject'] = EMAIL_SUBJECT
        msg.set_content(EMAIL_BODY)
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        print("Completion email sent successfully")
    except Exception as e:
        print(f"Failed to send completion email: {str(e)}")

def main():
    uploader = FTPUploader()
    monitor = FolderMonitor(uploader)
    observer = Observer()
    
    try:
        observer.schedule(monitor, SOURCE_FOLDER, recursive=False)
        observer.start()
        
        print(f"Monitoring {SOURCE_FOLDER} for new files...")
        print(f"Destination: ftp://{FTP_SERVER}{FTP_FOLDER}")
        print(f"Will wait up to {MAX_WAIT_TIME//60} minutes for files to stabilize")
        
        while True:
            monitor.check_pending_files()
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        print("\nStopping monitor...")
    except Exception as e:
        print(f"Fatal error: {str(e)}")
    finally:
        observer.stop()
        observer.join()
        uploader.close()
        print("Cleanup complete. Exiting.")
        send_completion_email()  # Send email after cleanup

if __name__ == "__main__":
    main()

import os
import paramiko
from getpass import getpass
import fnmatch
import time
import datetime
from tsbuddy import parse_chassis, parse_system

first_dir_list = os.listdir()

def main():
    #Testing the new stuff
    hosts = collect_hosts()
    if hosts != []:
        # #Erase existing log files in the directory
        # for file in first_dir_list:
        #     if 'tech_support_complete' in file:
        #         os.remove(file)
        grab_tech_support(hosts)
        print("Finished")
        #Grab new dir_list

def collect_hosts():
	'''Collects device details from the user and returns a list of hosts.'''
	hosts = []
	print("\nEnter device details for the switch you want the logs from. Press Enter without an IP to exit")
	ip = input("Enter device IP [exit]: ").strip()
	if not ip:
		return hosts
	username = input(f"Enter username for {ip} [admin]: ") or "admin"
	password = getpass(f"Enter password for {ip} [switch]: ") or "switch"
	hosts.append({"ip": ip, "username": username, "password": password})
	#print(hosts)
	return hosts

def get_host_serial(host):
    """Connects to a host via SSH, runs tech support commands, and returns master serial."""
    ip = host["ip"]
    username = host["username"]
    password = host["password"]
    print(f"Getting SN of {ip}.")
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, 22, username, password, timeout=10)
        shell = client.invoke_shell()
        shell.send("show chassis\n")
        time.sleep(3)
        chas_info = shell.recv(16384).decode('utf-8')
        chassis_list = parse_chassis(chas_info)
        for chassis in chassis_list:
            if chassis.get("Role", "").lower() == "master":
                master_serial = chassis.get("Serial Number", None)
        # shell.send("show tech-support eng complete\n")
        # time.sleep(1)
        # shell.recv(1024)
        # print("Command sent to switch")
        client.close()
        return master_serial
    except Exception as e:
        print(f"[{ip}] SSH ERROR: {e}")
        exit()

def gen_tech_support(host):
    """Connects to a host via SSH, runs tech support commands."""
    ip = host["ip"]
    username = host["username"]
    password = host["password"]
    print(f"Connecting to {ip} via SSH to run the tech support command")
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, 22, username, password, timeout=10)
        shell = client.invoke_shell()
        shell.send("show tech-support eng complete\n")
        time.sleep(5)
        shell.recv(1024)
        #print(shell.recv(1024).decode('utf-8'))  # Print the output for debugging
        print("Command sent to switch")
        return client
    except Exception as e:
        print(f"[{ip}] SSH ERROR: {e}")
        client.close()

def grab_tech_support(hosts):
    paramiko.util.log_to_file("paramiko.log")
    master_serials = {}
    for host in hosts:
        ip = host["ip"]
        username = host["username"]
        password = host["password"]
        master_serial = get_host_serial(host)
        master_serials[host["ip"]] = master_serial
        master_serial = master_serials.get(ip)
        print("Backing up existing file for "+str(ip))
        try:
            transport = paramiko.Transport((ip,22))
            transport.connect(None,username,password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            # Try to download existing tech_support_complete.tar if present
            # Generate timestamp: e.g., 2025-08-05_153012
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
            existing_file = download_existing_tech_support(sftp, timestamp, master_serial)
            if existing_file:
                remove_existing_tech_support(sftp)
            sftp.close()
            transport.close()
            #
            # Add feature to get system space info & give warning if space is low
            #
            sshclient = gen_tech_support(host)
            # Reconnect to SFTP to get the new tech support file
            transport = paramiko.Transport((ip,22))
            transport.connect(None,username,password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            # Generate timestamp: e.g., 2025-08-05_153012
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
            size = get_new_tech_support(sftp, master_serial)
            print(f"Downloaded new tech support file of size {size} bytes for {ip}")
            # Remove the existing tech support file after it was downloaded
            remove_existing_tech_support(sftp)
            if sftp: sftp.close()
            if transport: transport.close()
        except Exception as e:
            print(f"[{ip}]SFTP ERROR: {e}")
        finally:
            sshclient.close()

def download_existing_tech_support(sftp, timestamp, master_serial):
    for file in sftp.listdir('/flash/'):
        if fnmatch.fnmatch(file, "tech_support_complete.tar"):
            filename_parts = file.rsplit('.', 1)
            if len(filename_parts) == 2:
                local_file = f"{filename_parts[0]}_{master_serial}_{timestamp}_old.{filename_parts[1]}"
            else:
                local_file = f"{file}_{master_serial}_{timestamp}_old"
            remote_path = f"/flash/{file}"
            file_size = sftp.stat(remote_path).st_size
            sftp.get(remote_path, local_file)
            print(f"Downloaded existing {file} as {local_file} (size: {file_size} bytes)")
            return file
    return None

def remove_existing_tech_support(sftp):
    for file in sftp.listdir('/flash/'):
        if fnmatch.fnmatch(file, "tech_support_complete.tar"):
            sftp.remove(f"/flash/{file}")
            print(f"Removed {file} from /flash/")
            return True
    return False

def get_new_tech_support(sftp, master_serial):
    filesize = 0
    finished = False
    while not finished:
        try:
            file_attributes = sftp.stat('/flash/tech_support_complete.tar')
        except FileNotFoundError:
            print("No new tech_support_complete.tar found yet. Please wait...")
            time.sleep(10)
            continue
        newfilesize = file_attributes.st_size
        if newfilesize == filesize:
            print("The tech support files is ready. Beginning download")
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
            local_file = f"tech_support_complete_{master_serial}_{timestamp}.tar"
            sftp.get("/flash/tech_support_complete.tar", local_file)
            finished = True
            return newfilesize
        else:
            print("The file is still generating. Please wait...")
            filesize = newfilesize
            time.sleep(10)
            continue

if __name__ == "__main__":
    main()
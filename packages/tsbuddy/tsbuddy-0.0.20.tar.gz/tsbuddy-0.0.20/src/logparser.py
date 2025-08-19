import csv
import json
import os
import paramiko
from getpass import getpass
import fnmatch
from . import logfinder

SwlogFiles1 = []
SwlogFiles2 = []
SwlogFiles3 = []
SwlogFiles4 = []
SwlogFiles5 = []
SwlogFiles6 = []
SwlogFiles7 = []
SwlogFiles8 = []
ConsoleFiles = []
dir_list = os.listdir()
first_dir_list = os.listdir()

def find_log_paths(root_dir=None):
	"""
	Finds all swlog & console files in the specified directory and its subdirectories.
	Returns a dictionary categorizing log files with file paths for processing.
	"""
	dir_list_recursive = logfinder.main()
	return dir_list_recursive





#Opens specified file, grabs the data, formats it, and exports it as a CSV
def ReadandParse(OutputFilePath,LogByLine):
	with open(OutputFilePath, 'w', newline='') as csvfile:
		OutputFile = csv.writer(csvfile)
		OutputFile.writerow(['Year', 'Month', 'Day', 'Time', 'SwitchName', 'Source', 'AppID', 'Subapp', 'Priority', 'LogMessage'])
		for line in LogByLine:
			line = line.replace("  ", " ")
			parts = line.split(" ")
			partsSize = len(parts)
			Year = parts[0]
			Month = parts[1]
			Date = parts[2]
			Time = parts[3]
			SwitchName = parts[4]
			Source = parts[5]
			#parser for different sources
			match Source:
				case "swlogd":
					if partsSize > 6:
						Appid = parts[6]
						if Appid == "^^":
							LogMessage = ""
							LogPartsCounter = 6
							while LogPartsCounter < partsSize:
								LogMessage += parts[LogPartsCounter]+" "
								LogPartsCounter += 1
							LogMessage = LogMessage.strip()
							OutputFile.writerow([Year, Month, Date, Time, SwitchName, Source, "", "", "", LogMessage])
							continue
					if partsSize > 7:
						Subapp = parts[7]
					if partsSize > 8:
						Priority = parts[8]
					LogMessage = ""
					if partsSize > 9:
						LogPartsCounter = 9
						while LogPartsCounter < partsSize:
							LogMessage += parts[LogPartsCounter]+" "
							LogPartsCounter += 1
						LogMessage = LogMessage.strip()
					OutputFile.writerow([Year, Month, Date, Time, SwitchName, Source, Appid, Subapp, Priority, LogMessage])
				case _:
					Model = parts[6]
					if Model == "ConsLog":
						LogMessage = ""
						LogPartsCounter = 7
						while LogPartsCounter < partsSize:
							LogMessage += parts[LogPartsCounter]+" "
							LogPartsCounter += 1
						LogMessage = LogMessage.strip()
						OutputFile.writerow([Year, Month, Date, Time, SwitchName, Source, Model, "", "", LogMessage])
					else:
						LogMessage = ""
						LogPartsCounter = 5
						while LogPartsCounter < partsSize:
							LogMessage += parts[LogPartsCounter]+" "
							LogPartsCounter += 1
						LogMessage = LogMessage.strip()
						OutputFile.writerow([Year, Month, Date, Time, SwitchName, Source, "", "", "", LogMessage])
					
def process_logs(log_files, csv_name, json_name):
    LogByLine = []
    if log_files:
        for logfile in log_files:
            with open(logfile, 'r', errors='ignore') as file:
                LogByLine += file.readlines()
        ReadandParse(csv_name, LogByLine)
        with open(csv_name, mode='r', newline='') as csvfile:
            data = list(csv.DictReader(csvfile))
        with open(json_name, mode='w') as jsonfile:
            json.dump(data, jsonfile, indent=4)

def main():
#Testing the new stuff
	hosts = collect_hosts()
	if hosts != []:
		#Erase existing log files in the directory
		for file in first_dir_list:
			if 'swlog_chassis' in file:
				os.remove(file)
			if 'swlog_localConsole' in file:
				os.remove(file)
		grab_logs(hosts)
		print("Grab logs finished")
		#Grab new dir_list
	dir_list = os.listdir()
#Find swlogs in current directory
	for file in dir_list:
		if 'swlog_chassis1' in file:
			SwlogFiles1.append(file)
		if 'swlog_chassis2' in file:
			SwlogFiles2.append(file)
		if 'swlog_chassis3' in file:
			SwlogFiles3.append(file)
		if 'swlog_chassis4' in file:
			SwlogFiles4.append(file)
		if 'swlog_chassis5' in file:
			SwlogFiles5.append(file)
		if 'swlog_chassis6' in file:
			SwlogFiles6.append(file)
		if 'swlog_chassis7' in file:
			SwlogFiles7.append(file)
		if 'swlog_chassis8' in file:
			SwlogFiles8.append(file)
		if 'swlog_localConsole' in file:
			ConsoleFiles.append(file)
	
	# # Group chassis files for easier iteration
	# chassis_files = [
    #     (SwlogFiles1, 'Chassis1SwlogsParsed-tsbuddy.csv', 'Chassis1SwlogsParsed-tsbuddy.json'),
    #     (SwlogFiles2, 'Chassis2SwlogsParsed-tsbuddy.csv', 'Chassis2SwlogsParsed-tsbuddy.json'),
    #     (SwlogFiles3, 'Chassis3SwlogsParsed-tsbuddy.csv', 'Chassis3SwlogsParsed-tsbuddy.json'),
    #     (SwlogFiles4, 'Chassis4SwlogsParsed-tsbuddy.csv', 'Chassis4SwlogsParsed-tsbuddy.json'),
    #     (SwlogFiles5, 'Chassis5SwlogsParsed-tsbuddy.csv', 'Chassis5SwlogsParsed-tsbuddy.json'),
    #     (SwlogFiles6, 'Chassis6SwlogsParsed-tsbuddy.csv', 'Chassis6SwlogsParsed-tsbuddy.json'),
    #     (SwlogFiles7, 'Chassis7SwlogsParsed-tsbuddy.csv', 'Chassis7SwlogsParsed-tsbuddy.json'),
    #     (SwlogFiles8, 'Chassis8SwlogsParsed-tsbuddy.csv', 'Chassis8SwlogsParsed-tsbuddy.json'),
    # ]

	# for files, csv_name, json_name in chassis_files:
	# 	process_logs(files, csv_name, json_name)

    # # Console logs
	# process_logs(ConsoleFiles, 'ConsoleLogsParsed-tsbuddy.csv', 'ConsoleLogsParsed-tsbuddy.json')


	#Combine all log files
	
	#SwlogChassis1
	LogByLine = []
	for logfile in SwlogFiles1:
		with open(logfile, 'r', errors='ignore') as file:
			LogByLine += file.readlines()
			#print("Reading "+str(logfile)+". Total line count is "+str(len(LogByLine))+" lines.")
	OutputFilePath = 'Chassis1SwlogsParsed-tsbuddy.csv'
	ReadandParse(OutputFilePath,LogByLine)
	#Convert to JSON
	#with open(OutputFilePath, mode='r', newline='') as csvfile:
	with open(OutputFilePath, mode='r', newline='') as csvfile:
		data = list(csv.DictReader(csvfile))
	with open('Chassis1SwlogsParsed-tsbuddy.json', mode='w') as jsonfile:
		json.dump(data, jsonfile, indent=4)
	
	#SwlogChassis2
	LogByLine = []
	if SwlogFiles2 != []:
		for logfile in SwlogFiles2:
			with open(logfile, 'r', errors='ignore') as file:
				LogByLine += file.readlines()
		OutputFilePath = 'Chassis2SwlogsParsed-tsbuddy.csv'
		ReadandParse(OutputFilePath,LogByLine)
	#Convert to JSON
		with open(OutputFilePath, mode='r', newline='') as csvfile:
			data = list(csv.DictReader(csvfile))
		with open('Chassis2SwlogsParsed-tsbuddy.json', mode='w') as jsonfile:
			json.dump(data, jsonfile, indent=4)
		
	#SwlogChassis3
	LogByLine = []
	if SwlogFiles3 != []:
		for logfile in SwlogFiles3:
			with open(logfile, 'r', errors='ignore') as file:
				LogByLine += file.readlines()
		OutputFilePath = 'Chassis3SwlogsParsed-tsbuddy.csv'
		ReadandParse(OutputFilePath,LogByLine)
	#Convert to JSON
		with open(OutputFilePath, mode='r', newline='') as csvfile:
			data = list(csv.DictReader(csvfile))
		with open('Chassis3SwlogsParsed-tsbuddy.json', mode='w') as jsonfile:
			json.dump(data, jsonfile, indent=4)
	
	#SwlogChassis4
	LogByLine = []
	if SwlogFiles4 != []:
		for logfile in SwlogFiles4:
			with open(logfile, 'r', errors='ignore') as file:
				LogByLine += file.readlines()
		OutputFilePath = 'Chassis4SwlogsParsed-tsbuddy.csv'
		ReadandParse(OutputFilePath,LogByLine)
	#Convert to JSON
		with open(OutputFilePath, mode='r', newline='') as csvfile:
			data = list(csv.DictReader(csvfile))
		with open('Chassis4SwlogsParsed-tsbuddy.json', mode='w') as jsonfile:
			json.dump(data, jsonfile, indent=4)
	
	#SwlogChassis5
	LogByLine = []
	if SwlogFiles5 != []:
		for logfile in SwlogFiles5:
			with open(logfile, 'r', errors='ignore') as file:
				LogByLine += file.readlines()
		OutputFilePath = 'Chassis5SwlogsParsed-tsbuddy.csv'
		ReadandParse(OutputFilePath,LogByLine)
	#Convert to JSON
		with open(OutputFilePath, mode='r', newline='') as csvfile:
			data = list(csv.DictReader(csvfile))
		with open('Chassis5SwlogsParsed-tsbuddy.json', mode='w') as jsonfile:
			json.dump(data, jsonfile, indent=4)
	
	#SwlogChassis6
	LogByLine = []
	if SwlogFiles6 != []:
		for logfile in SwlogFiles6:
			with open(logfile, 'r', errors='ignore') as file:
				LogByLine += file.readlines()
		OutputFilePath = 'Chassis6SwlogsParsed-tsbuddy.csv'
		ReadandParse(OutputFilePath,LogByLine)
	#Convert to JSON
		with open(OutputFilePath, mode='r', newline='') as csvfile:
			data = list(csv.DictReader(csvfile))
		with open('Chassis6SwlogsParsed-tsbuddy.json', mode='w') as jsonfile:
			json.dump(data, jsonfile, indent=4)
	
	#SwlogChassis7
	LogByLine = []
	if SwlogFiles7 != []:
		for logfile in SwlogFiles7:
			with open(logfile, 'r', errors='ignore') as file:
				LogByLine += file.readlines()
		OutputFilePath = 'Chassis7SwlogsParsed-tsbuddy.csv'
		ReadandParse(OutputFilePath,LogByLine)
	#Convert to JSON
		with open(OutputFilePath, mode='r', newline='') as csvfile:
			data = list(csv.DictReader(csvfile))
		with open('Chassis7SwlogsParsed-tsbuddy.json', mode='w') as jsonfile:
			json.dump(data, jsonfile, indent=4)
	
	#SwlogChassis8
	LogByLine = []
	if SwlogFiles8 != []:
		for logfile in SwlogFiles8:
			with open(logfile, 'r', errors='ignore') as file:
				LogByLine += file.readlines()
		OutputFilePath = 'Chassis8SwlogsParsed-tsbuddy.csv'
		ReadandParse(OutputFilePath,LogByLine)
	#Convert to JSON
		with open(OutputFilePath, mode='r', newline='') as csvfile:
			data = list(csv.DictReader(csvfile))
		with open('Chassis8SwlogsParsed-tsbuddy.json', mode='w') as jsonfile:
			json.dump(data, jsonfile, indent=4)
	
	#ConsoleFiles
	LogByLine = []
	if ConsoleFiles != []:
		for logfile in ConsoleFiles:
			with open(logfile, 'r', errors='ignore') as file:
				LogByLine += file.readlines()
		OutputFilePath = 'ConsoleLogsParsed-tsbuddy.csv'
		ReadandParse(OutputFilePath,LogByLine)
	#Convert to JSON
		with open(OutputFilePath, mode='r', newline='') as csvfile:
			data = list(csv.DictReader(csvfile))
		with open('ConsoleLogsParsed-tsbuddy.json', mode='w') as jsonfile:
			json.dump(data, jsonfile, indent=4)
	print("Logs parsed successfully!")
	
def collect_hosts():
	"""Collects device details from the user and returns a list of hosts."""
	hosts = []
	print("\nEnter device details for the switch you want the logs from. Press Enter without an IP to use logs in current directory")
	ip = input("Enter device IP: ").strip()
	if not ip:
		return hosts
	username = input(f"Enter username for {ip} [admin]: ") or "admin"
	password = getpass(f"Enter password for {ip} [switch]: ") or "switch"
	hosts.append({"ip": ip, "username": username, "password": password})
	#print(hosts)
	return hosts

def grab_logs(hosts):
	#paramiko.util.log_to_file("paramiko-tsbuddy.log")
	#print(hosts)
	for host in hosts:
		ip = host["ip"]
		username = host["username"]
		password = host["password"]
		print("Connecting to "+str(ip))
		try:
			transport = paramiko.Transport((ip,22))
			transport.connect(None,username,password)
			sftp = paramiko.SFTPClient.from_transport(transport)
			for file in sftp.listdir('/flash/'):
				#print(file)
				if fnmatch.fnmatch(file, "swlog_archive"):
					#print("Skipping swlog_archive")
					continue
				if fnmatch.fnmatch(file, "*swlog*.*"):
					#print(file+" is good")
					sftp.get("/flash/"+file, file)
					continue
				if fnmatch.fnmatch(file, "*swlog*"):
					#print(file+" is good")
					sftp.get("/flash/"+file, file)
					continue
			#filepath = "/flash/swlog_chassis1"
			#localpath = "swlog_chassis1"
			#sftp.get(filepath,localpath)
			if sftp: sftp.close()
			if transport: transport.close()
		except Exception as e:
			print(f"[{ip}] ERROR: {e}")

if __name__ == "__main__":
    main()
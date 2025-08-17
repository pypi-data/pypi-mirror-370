import re
import csv
import os
from typing import List, Dict
from datetime import datetime

# Column definitions
COLUMN_DEFINITIONS = {
    "show hardware-info": [
        "Chassis",
        "CPU Manufacturer",
        "CPU Model",
        "Flash Manufacturer",
        "Flash size",
        "RAM size",
        "FPGA version",
        "U-Boot Version",
        "Power Supplies Present",
        "NIs Present",
    ],
    "show chassis": [
        "Chassis ID",
        "Role",
        "Model Name",
        "Module Type",
        "Description",
        "Part Number",
        "Hardware Revision",
        "Serial Number",
        "Manufacture Date",
        "Admin Status",
        "Operational Status",
        "Number Of Resets",
        "MAC Address",
    ],
    "show module long": [
        "Module ID",
        "Slot",
        "Chassis",
        "Model Name",
        "Module Type",
        "Description",
        "Part Number",
        "Hardware Revision",
        "Serial Number",
        "Manufacture Date",
        "FPGA - Physical 1",
        "Admin Status",
        "Operational Status",
        "Max Power",
        "CPU Model Type",
        "MAC Address",
        "UBOOT Version",
        "POE-Software Version",
        "POE-Hardware Version",
    ],
    "show transceivers": [
        "Chassis ID",
        "Slot",
        "Port Number",
        "Manufacturer Name",
        "Part Number",
        "ALU Model Name",
        "ALU Model Number",
        "Hardware Revision",
        "Serial Number",
        "Manufacture Date",
        "Laser Wave Length",
        "Admin Status",
        "Operational Status",
    ],
    "show fan": [
        "Chassis/Tray",
        "Fan",
        "Functional",
        "Speed",
    ],
    "show powersupply": [
        "Chassis/PS",
        "Power",
        "PS Type",
        "Status",
        "Location",
    ],
    "show temperature": [
        "Chassis/Device",
        "Current",
        "Range",
        "Danger",
        "Thresh",
        "Status",
    ],
    "show system": [
        "Description",
        "Object ID",
        "Up Time",
        "Contact",
        "Name",
        "Location",
        "Services",
        "Date & Time",
        "Primary CMM - Available (bytes)",
        "Primary CMM - Comments",
        "Secondary CMM - Available (bytes)",
        "Secondary CMM - Comments",
    ],
    "show running-directory": [
        "Running CMM",
        "CMM Mode",
        "Current CMM Slot",
        "Running Directory",
        "Certify/Restore Status",
        "Flash Between CMMs",
        "Running Configuration",
    ],
    "show microcode": [
        "Location",
        "Directory",
        "Package",
        "Release",
        "Size",
        "Description",
    ],
    "show license-info": [
        "VC",
        "Device",
        "License",
        "Type",
        "Time Remaining (Days)",
        "Upgrade Status",
        "Expiration Date",
    ],
    "show lldp remote-system": [
        "Local Port",
        "Chassis IP",
        "Port",
        "Remote ID",
        "Chassis Subtype",
        "Port Subtype",
        "Port Description",
        "System Name",
        "System Description",
        "Capabilities Supported",
        "Capabilities Enabled",
        "Management IP Address",
        "MED Device Type",
        "MED Capabilities",
        "MED Extension TLVs Present",
        "MED Power Type",
        "MED Power Source",
        "MED Power Priority",
        "MED Power Value",
        "Remote port MAC/PHY AutoNeg",
        "Mau Type",
    ],
    "show aaa authentication": [
        "Service Type",
        "Authentication",
        "1st Authentication Server",
        "2nd Authentication Server",
        "3rd Authentication Server",
        "4th Authentication Server",
    ],
    "show health": [
        "Resource",
        "Current",
        "1 Min Avg",
        "1 Hr Avg",
        "1 Day Avg",
    ],
    "show health all cpu": [
        "CPU",
        "Current",
        "1 Min Avg",
        "1 Hr Avg",
        "1 Day Avg",
    ],
    "show vlan": [
        "VLAN",
        "Type",
        "Admin State",
        "Operational",
        "IP",
        "MTU",
        "Name",
    ],
    "show spantree": [
        "VLAN",
        "STP Status",
        "Protocol",
        "Priority",
        "Spanning Tree Path Cost Mode",
    ],
    "show spantree ports active": [
        "VLAN",
        "Port",
        "Oper Status",
        "Path Cost",
        "Role",
        "Loop Guard",
        "Note",
    ],
    "show interfaces status": [
        "Chas/Slot/Port",
        "Admin Status",
        "Auto Nego",
        "Detected Speed (Mbps)",
        "Detected Duplex",
        "Detected Pause",
        "Detected FEC",
        "Configured Speed (Mbps)",
        "Configured Duplex",
        "Configured Pause",
        "Configured FEC",
        "Link Trap",
        "EEE Status",
    ],
    "show interfaces counters": [
        "Interface",
        "InOctets",
        "OutOctets",
        "InUcastPkts",
        "OutUcastPkts",
        "InMcastPkts",
        "OutMcastPkts",
        "InBcastPkts",
        "OutBcastPkts",
        "InPauseFrames",
        "OutPauseFrames",
        "InPkts/s",
        "OutPkts/s",
        "InBits/s",
        "OutBits/s",
    ],
    "show ip interface": [
        "Name",
        "IP Address",
        "Subnet Mask",
        "Status",
        "Forward",
        "Device",
        "Flags",
    ],
    "show ip config": [
        "IP directed-broadcast",
        "IP default TTL",
        "Distributed ARP",
        "Anycast MAC",
        "Proxy-arp aging-time",
    ],
    "show ip protocols": [
        "RIP status",
        "OSPF status",
        "ISIS status",
        "BGP status",
        "PIM status",
        "DVMRP status",
        "RIPng status",
        "OSPF3 status",
        "LDP status",
        "VRRP status",
    ],
    "show ip dos statistics": [
        "port scan",
        "ping of death",
        "land",
        "loopback-src",
        "invalid-ip",
        "invalid-multicast",
        "unicast dest-ip/multicast-mac",
        "ping overload",
        "arp flood",
        "arp poison",
        "anti-spoof",
        "gratuitous-arp",
        "ip-options-filter",
    ],
    "show snmp statistics": [
        "snmpInPkts",
        "snmpOutPkts",
        "snmpInBadVersions",
        "snmpInBadCommunityNames",
        "snmpInBadCommunityUses",
        "snmpInASNParseErrs",
        "snmpEnableAuthenTraps",
        "snmpSilentDrop",
        "snmpProxyDrops",
        "snmpInTooBigs",
        "snmpInNoSuchNames",
        "snmpInBadValues",
        "snmpInReadOnlys",
        "snmpInGenErrs",
        "snmpInTotalReqVars",
        "snmpInTotalSetVars",
        "snmpInGetRequests",
        "snmpInGetNexts",
        "snmpInSetRequests",
        "snmpInGetResponses",
        "snmpInTraps",
        "snmpOutTooBigs",
        "snmpOutNoSuchNames",
        "snmpOutBadValues",
        "snmpOutGenErrs",
        "snmpOutGetRequests",
        "snmpOutGetNexts",
        "snmpOutSetRequests",
        "snmpOutGetResponses",
        "snmpOutTraps",
        "snmpUnknownSecurityModels",
        "snmpInvalidMsgs",
        "snmpUnknownPDUHandlers",
        "snmpUnavailableContexts",
        "snmpUnknownContexts",
        "usmStatsUnsupportedSecLevels",
        "usmStatsNotInTimeWindows",
        "usmStatsUnknownUserNames",
        "usmStatsUnknownEngineIDs",
        "usmStatsWrongDigests",
        "usmStatsDecryptionErrors",
        "snmpTsmInvalidCaches",
        "snmpTsmInadequateSecurityLevels",
        "snmpTsmUnknownPrefixes",
        "snmpTsmInvalidPrefixes",
        "snmpTlstmSessionOpens",
        "snmpTlstmSessionClientCloses",
        "snmpTlstmSessionOpenErrors",
        "snmpTlstmSessionAccepts",
        "snmpTlstmSessionServerCloses",
        "snmpTlstmSessionNoSessions",
        "snmpTlstmSessionInvalidClientCertificates",
        "snmpTlstmSessionUnknownServerCertificate",
        "snmpTlstmSessionInvalidServerCertificates",
        "snmpTlstmSessionInvalidCaches",
        "snmpEngineID",
        "snmpEngineBoots",
        "snmpEngineTime",
        "snmpEngineMaxMessageSize",
    ],
    "show virtual-chassis topology": [
        "Oper Chas",
        "Role",
        "Status",
        "Config Chas ID",
        "Oper Priority",
        "Group",
        "MAC-Address",
        "Local Chassis",
    ],
    "show virtual-chassis consistency": [
        "Chassis ID",
        "Config Chas ID",
        "Status",
        "Oper Type",
        "Oper Group",
        "Hello Interv",
        "Oper Control Vlan",
        "Config Control Vlan",
        "License",
    ],
    "show virtual-chassis vf-link member-port": [
        "Chassis/VFLink ID",
        "Chassis/Slot/Port",
        "Oper",
        "Is Primary",
        "VFLink Mode",
    ],
    "show virtual-chassis chassis-reset-list": [
        "Chas",
        "Chassis reset list",
    ],
    "show virtual-chassis slot-reset-list": [
        "Chas",
        "Slot",
        "Reset status",
    ],
    "show virtual-chassis vf-link": [
        "Chassis/VFLink ID",
        "Oper",
        "Primary Port",
        "Config Port",
        "Active Port",
        "Def Vlan",
        "Speed Type",
        "VFLink Mode",
    ],
    "show virtual-chassis auto-vf-link-port": [
        "Chassis/Slot/Port",
        "Chassis/VFLink ID",
        "VFLink member status",
    ],
    "show virtual-chassis neighbors": [
        "Chas ID",
        "VFL 0",
        "VFL 1",
    ],
    "debug show virtual-chassis topology": [
        "Oper Chas",
        "Role",
        "Status",
        "Config Chas ID",
        "Oper Priority",
        "Group",
        "MAC-Address",
        "System Ready",
        "Local Chassis",
    ],
    "debug show virtual-chassis status": [
        "ID",
        "Level",
        "Parameter",
        "Value",
        "Timestamp",
        "Status",
    ],
    "debug show virtual-chassis connection": [
        "Chas",
        "MAC-Address",
        "Local IP",
        "Remote IP",
        "Status",
    ],
    "show cloud-agent status": [
        "Admin State",
        "Activation Server State",
        "Device State",
        "Error State",
        "Cloud Group",
        "DHCP Address",
        "DHCP IP Address Mask",
        "Gateway",
        "Activation Server",
        "Network ID",
        "NTP Server",
        "DNS Server",
        "DNS Domain",
        "Proxy Server",
        "VPN Server",
        "Preprovision Server",
        "OV Tenant",
        "VPN DPD Time (sec)",
        "Image Server",
        "Image Download Retry Count",
        "Discovery Interval (min)",
        "Time to next Call Home (sec)",
        "Call Home Timer Status",
        "Discovery Retry Count",
        "Certificate Status",
        "Thin Client",
        "Retry Call-Home time remaining",
    ],
    "show pkgmgr": [
        "Name",
        "Version",
        "Status",
        "Install Script",
    ],
    "show appmgr": [
        "Application",
        "Status",
        "Package Name",
        "User",
        "Status Time Stamp",
    ],
    "show naas license": [
        "Chas ID",
        "Serial Number",
        "Device Mode",
        "Device State",
        "Call-home Period",
        "Grace Period",
        "Valid Licenses",
        "Expiry Day",
        "Expiry Time",
    ],
    "show naas-agent status": [
        "Proxy Server",
        "Activation Server",
        "DNS Server",
        "DNS Domain",
        "NTP Server",
        "Call Home Timer Status",
        "Time to next call-home (min)",
        "Grace Period (days)",
        "Grace Period (cause)",
    ],
    "debug show capability naas": [
        "Chas ID",
        "Naas",
        "Decided",
        "Esntial",
        "Advanced",
        "DC",
        "10G",
        "MACSEC",
        "MPLS",
        "GRACE",
        "DEGR",
        "MGMT",
        "UPGRADE",
        "GRC_MGMT",
        "GRCUPGRADE",
        "DEGMGMT",
        "DEGUPGRADE",
        "ADVROUTING",
    ],
    "show ntp server status": [
        "IP address",
        "Host mode",
        "Peer mode",
        "Prefer",
        "Version",
        "Key",
        "Stratum",
        "Minpoll",
        "Maxpoll",
        "Poll",
        "When",
        "Delay",
        "Offset",
        "Dispersion",
        "Root distance",
        "Precision",
        "Reference IP",
        "Status",
        "Uptime count",
        "Reachability",
        "Unreachable count",
        "Stats reset count",
        "Packets sent",
        "Packets received",
        "Duplicate packets",
        "Bogus origin",
        "Bad authentication",
        "Bad dispersion",
        "Last Event",
    ],
    "show ntp status": [
        "Current time",
        "Last NTP update",
        "Server reference",
        "Client mode",
        "Broadcast client mode",
        "Broadcast delay (microseconds)",
        "Clock status",
        "Stratum",
        "Maximum Associations Allowed",
        "Authentication",
        "Source IP Configured",
        "VRF Name",
    ],
    "show ntp keys": [
        "Key",
        "Status",
    ],
    "show capability profile": [
        "Configured Profile",
        "Active Profile",
        "Configured TCAM Mode",
        "Active TCAM mode",
    ],
}

# Parsers
def parse_hardware_info(output: str) -> List[Dict[str, str]]:
    columns = COLUMN_DEFINITIONS["show hardware-info"]
    data, current = [], {}
    for line in output.strip().splitlines():
        if match := re.match(r'^Chassis (\d+)', line):
            if current:
                data.append(current)
                current = {}
            current["Chassis"] = match.group(1)
        elif ':' in line:
            key, value = map(str.strip, line.split(':', 1))
            if key in columns:
                current[key] = value
    if current:
        data.append(current)
    return data


def parse_chassis(output: str) -> List[Dict[str, str]]:
    columns = COLUMN_DEFINITIONS["show chassis"]
    data, current = [], {}
    pattern = re.compile(r'^(Local|Remote) Chassis ID (\d+) \((\w+)\)')
    for line in output.strip().splitlines():
        match = pattern.match(line)
        if match:
            if current:
                data.append(current)
                current = {}
            _, chassis_id, role = match.groups()
            current["Chassis ID"] = chassis_id
            current["Role"] = role
        elif ':' in line:
            key, value = map(str.strip, line.split(':', 1))
            if key in columns:
                current[key] = value.strip(',')
    if current:
        data.append(current)
    return data


def parse_module_long(output: str) -> List[Dict[str, str]]:
    columns = COLUMN_DEFINITIONS["show module long"]
    data = []
    current = {}

    # Persistent context for Module ID, Chassis, Slot
    context = {
        "Module ID": None,
        "Chassis": None,
        "Slot": None
    }

    lines = output.strip().splitlines()

    module_id_pattern = re.compile(r'^Module ID (\d+)')
    slot_pattern = re.compile(r'^Module in slot ([\w-]+)')
    chassis_slot_pattern = re.compile(r'^Module in chassis (\d+) slot (\d+)')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Match and store Module ID context
        if module_id_match := module_id_pattern.match(line):
            context["Module ID"] = module_id_match.group(1)

        # Start new record: Module in chassis X slot Y
        elif chassis_slot_match := chassis_slot_pattern.match(line):
            if current:
                data.append(current)
            context["Chassis"] = chassis_slot_match.group(1)
            context["Slot"] = chassis_slot_match.group(2)
            current = {k: v for k, v in context.items() if v is not None}

        # Start new record: Module in slot CMM-A (no chassis)
        elif slot_match := slot_pattern.match(line):
            if current:
                data.append(current)
            context["Slot"] = slot_match.group(1)
            context["Chassis"] = None  # Clear chassis if not present
            current = {k: v for k, v in context.items() if v is not None}

        # Key-value fields
        elif ':' in line:
            key, value = map(str.strip, line.split(':', 1))
            key = key.rstrip(',')
            value = value.rstrip(',')
            if key in columns:
                current[key] = value

    if current:
        data.append(current)

    return data


def parse_transceivers(output: str) -> List[Dict[str, str]]:
    columns = COLUMN_DEFINITIONS["show transceivers"]
    data = []
    current = {}
    current_chassis_id = None

    lines = output.strip().splitlines()

    chassis_pattern = re.compile(r"^Chassis ID (\d+)")
    transceiver_pattern = re.compile(r"^Slot (\d+) Transceiver (\d+)")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        chassis_match = chassis_pattern.match(line)
        transceiver_match = transceiver_pattern.match(line)

        if chassis_match:
            current_chassis_id = chassis_match.group(1)

        elif transceiver_match:
            if current:
                data.append(current)
                current = {}

            slot, port_number = transceiver_match.groups()
            current["Chassis ID"] = current_chassis_id
            current["Slot"] = slot
            current["Port Number"] = port_number

        elif ':' in line:
            key, value = map(str.strip, line.split(":", 1))
            key = key.rstrip(',')
            value = value.rstrip(',')
            if key in columns:
                current[key] = value

    if current:
        data.append(current)

    return data


def parse_fan(output: str) -> List[Dict[str, str]]:
    columns = COLUMN_DEFINITIONS["show fan"]
    data = []

    lines = output.strip().splitlines()
    header_found = False

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Skip the header and separator
        if not header_found:
            if all(col in line for col in ["Chassis/Tray", "Fan", "Functional", "Speed"]):
                header_found = True  # Header line found
            continue
        elif set(line) <= set("-+| "):
            continue  # Skip the separator line

        # Split columns by whitespace assuming fixed-width format
        parts = re.split(r'\s{2,}', line)
        if len(parts) == 4:
            # Precede Chassis/Tray value with a single quote
            #parts[0] = "'" + parts[0]
            row = dict(zip(columns, parts))
            data.append(row)

    return data


def parse_powersupply(output: str) -> List[Dict[str, str]]:
    columns = COLUMN_DEFINITIONS["show powersupply"]
    data = []

    lines = output.strip().splitlines()
    header_found = False

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Skip header and separator lines
        if not header_found:
            if all(col in line for col in ["Chassis/PS", "Power", "Type", "Status", "Location"]):
                header_found = True
            continue
        elif set(line) <= set("-+ "):
            continue

        # Skip the total summary line
        if line.lower().startswith("total"):
            continue

        # Parse the data line
        parts = re.split(r'\s{2,}', line)
        if len(parts) == 5:
            row = dict(zip(columns, parts))
            data.append(row)

    return data


def parse_temperature(output: str) -> List[Dict[str, str]]:
    columns = COLUMN_DEFINITIONS["show temperature"]
    data = []

    lines = output.strip().splitlines()
    header_found = False

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Detect the header line
        if not header_found:
            if all(col in line for col in ["Chassis/Device", "Current", "Range", "Danger", "Thresh", "Status"]):
                header_found = True
            continue
        elif set(line) <= set("-+| "):
            continue  # Skip separator line

        # Split fixed-width fields by 2+ spaces
        parts = re.split(r'\s{2,}', line)
        if len(parts) == 6:
            row = dict(zip(columns, parts))

            # Ensure "Chassis/Device" is interpreted as text in Excel
            #if "/" in row["Chassis/Device"]:
            #    row["Chassis/Device"] = f"=\"{row['Chassis/Device']}\""

            data.append(row)

    return data


def parse_system(output: str) -> List[Dict[str, str]]:
    columns = COLUMN_DEFINITIONS["show system"]
    data = {}

    # General system fields
    general_pattern = re.compile(r"^(.*?):\s+(.*?),?$")
    for line in output.splitlines():
        line = line.strip()
        if not line or line.startswith("Flash Space:"):
            continue
        match = general_pattern.match(line)
        if match:
            key, value = match.groups()
            key = key.strip()
            value = value.strip()
            if key in columns:
                data[key] = value

    # Match Primary CMM block
    primary_match = re.search(r"Primary CMM:\s*(.*?)\s*(?:Secondary CMM:|$)", output, re.DOTALL)
    if primary_match:
        primary_block = primary_match.group(1)
        for line in primary_block.splitlines():
            if ':' in line:
                key, value = map(str.strip, line.split(":", 1))
                full_key = f"Primary CMM - {key}"
                if full_key in columns:
                    data[full_key] = value.strip(',')

    # Match Secondary CMM block
    secondary_match = re.search(r"Secondary CMM:\s*(.*)", output, re.DOTALL)
    if secondary_match:
        secondary_block = secondary_match.group(1)
        for line in secondary_block.splitlines():
            if ':' in line:
                key, value = map(str.strip, line.split(":", 1))
                full_key = f"Secondary CMM - {key}"
                if full_key in columns:
                    data[full_key] = value.strip(',')

    return [data] if data else []


def parse_running_directory(output: str) -> List[Dict[str, str]]:
    columns = COLUMN_DEFINITIONS["show running-directory"]
    data = {key: "" for key in columns}

    current_block = None
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue

        if line == "CONFIGURATION STATUS":
            current_block = "CONFIGURATION STATUS"
            continue
        elif line == "SYNCHRONIZATION STATUS":
            current_block = "SYNCHRONIZATION STATUS"
            continue

        if ':' in line:
            key, value = map(str.strip, line.split(":", 1))
            value = value.rstrip(',')

            if current_block == "CONFIGURATION STATUS":
                if key == "Running configuration":
                    data["Running Directory"] = value
                elif key in columns:
                    data[key] = value
            elif current_block == "SYNCHRONIZATION STATUS":
                if key == "Running Configuration":
                    data["Running Configuration"] = value
                elif key in columns:
                    data[key] = value

    return [data]


def parse_microcode(output: str, location: str) -> List[Dict[str, str]]:
    columns = COLUMN_DEFINITIONS["show microcode"]
    data = []

    lines = output.strip().splitlines()

    if not lines:
        return data

    # Step 1: Find the directory line
    directory = ""
    for line in lines:
        line = line.strip()
        if line:
            directory = line
            break

    # Step 2: Parse actual data lines after separator
    parsing = False
    for line in lines:
        line = line.strip()

        if not line:
            continue

        if re.match(r"^-+\+.*", line):
            parsing = True
            continue

        if not parsing:
            continue

        # Regex pattern to extract: Package, Release, Size, Description
        match = re.match(r'^(\S+)\s+(\S+)\s+(\d+)\s+(.+)$', line)
        if match:
            package, release, size, description = match.groups()
            row = {
                "Location": location,
                "Directory": f"=\"{directory}\"",  # Protect from Excel path parsing
                "Package": package,
                "Release": release,
                "Size": size,
                "Description": description
            }
            data.append(row)

    return data


def parse_license_info(output: str) -> List[Dict[str, str]]:
    columns = COLUMN_DEFINITIONS["show license-info"]
    data = []
    
    lines = output.strip().splitlines()
    header_found = False

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Skip the header and separator
        if not header_found:
            if all(col in line for col in ["VC", "device", "License", "Type", "Remaining", "Status", "Date"]):
                header_found = True  # Header line found
            continue
        elif set(line) <= set("-+| "):
            continue  # Skip the separator line

        # Split columns by whitespace (accounting for multiple spaces between columns)
        parts = re.split(r'\s{2,}', line)
        if len(parts) == 7:
            row = dict(zip(columns, parts))
            data.append(row)

    return data


def parse_lldp_remote_system(raw_text: str) -> List[Dict[str, str]]:
    """
    Parses the show lldp remote-system section.
    """
    entries = []
    entry_pattern = re.compile(
        r"Remote LLDP nearest-bridge Agents on Local Port (\S+):\s*"
        r"Chassis\s+([\w\.:]+),\s+Port\s+([\S]+):\s*"
        r"(.*?)\s*(?=(Remote LLDP nearest-bridge|$))",
        re.DOTALL
    )
    
    matches = entry_pattern.findall(raw_text)
    
    for match in matches:
        local_port = match[0]
        chassis_ip = match[1]
        port = match[2]
        details = match[3]
        
        # Extracting key-value pairs
        detail_pattern = re.compile(r"^\s*([\w\s]+)\s*=\s*([\w\.\:,\-\/\(\)]+)?", re.MULTILINE)
        detail_matches = detail_pattern.findall(details)
        
        data = {
            "Local Port": local_port,
            "Chassis IP": chassis_ip,
            "Port": port,
        }
        
        # Populating the dictionary with available data
        for key, value in detail_matches:
            # Clean up any leading or trailing whitespace
            key = key.strip()
            value = value.strip().rstrip(",.") if value else None
            data[key] = value
        
        entries.append(data)
    
    return entries
    

def parse_aaa_authentication(raw_text: str) -> List[Dict[str, str]]:
    """
    Parses the 'show aaa authentication' section with support for optional 'Authentication = Use Default' entries.
    """
    entries = []
    current_entry = {}
    lines = raw_text.strip().splitlines()

    for line in lines:
        line = line.strip()

        if line.startswith("Service type ="):
            # Save the previous entry if it exists
            if current_entry:
                entries.append(current_entry)
                current_entry = {}
            service_type = line.split("=", 1)[1].strip()
            current_entry["Service Type"] = service_type

        elif line.startswith("Authentication ="):
            value = line.split("=", 1)[1].strip().rstrip(',')
            current_entry["Authentication"] = value

        elif "authentication server" in line:
            match = re.match(r"(\d+)(?:st|nd|rd|th) authentication server\s*=\s*(.+?),?$", line)
            if match:
                index = int(match.group(1))
                server = match.group(2).strip()
                suffix = (
                    f"{index}st" if index == 1 else
                    f"{index}nd" if index == 2 else
                    f"{index}rd" if index == 3 else
                    f"{index}th"
                )
                key = f"{suffix} Authentication Server"
                current_entry[key] = server

    # Append the final entry
    if current_entry:
        entries.append(current_entry)

    return entries


def parse_health(raw_text: str) -> List[Dict[str, str]]:
    """
    Parses the 'show health' section of the log.
    """
    rows = []
    lines = raw_text.strip().splitlines()

    # Skip headers, look for lines with actual data (usually below the separator line)
    data_started = False
    for line in lines:
        if re.match(r"^-+\+.*-+$", line):  # separator line with dashes and pluses
            data_started = True
            continue
        if not data_started:
            continue

        parts = re.split(r"\s{2,}", line.strip())
        if len(parts) == 5:
            rows.append({
                "Resource": parts[0],
                "Current": parts[1],
                "1 Min Avg": parts[2],
                "1 Hr Avg": parts[3],
                "1 Day Avg": parts[4]
            })

    return rows


def parse_health_all_cpu(raw_text: str) -> List[Dict[str, str]]:
    """
    Parses the 'show health all cpu' section.
    """
    entries = []
    lines = raw_text.strip().splitlines()

    for line in lines:
        # Match lines that look like: "Slot  1/1    22    19    19    19"
        match = re.match(r'^(Slot\s+\S+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)', line)
        if match:
            entries.append({
                "CPU": match.group(1),
                "Current": match.group(2),
                "1 Min Avg": match.group(3),
                "1 Hr Avg": match.group(4),
                "1 Day Avg": match.group(5)
            })

    return entries


def parse_vlan(raw_text: str) -> List[Dict[str, str]]:
    """
    Parses the 'show vlan' section into a list of dictionaries.
    Handles space in the 'name' field.
    """
    entries = []
    lines = raw_text.strip().splitlines()
    data_started = False

    for line in lines:
        if re.match(r"-+\+-+", line):  # separator line
            data_started = True
            continue
        if not data_started or not line.strip():
            continue

        # Use regex to extract the first 6 fields; the rest is the name
        match = re.match(
            r'(\d+)\s+(\w+)\s+(\w+)\s+(\w+)\s+(\w+)\s+(\d+)\s+(.*)', line.strip()
        )
        if match:
            entry = {
                "VLAN": match.group(1),
                "Type": match.group(2),
                "Admin State": match.group(3),
                "Operational": match.group(4),
                "IP": match.group(5),
                "MTU": match.group(6),
                "Name": match.group(7).strip()
            }
            entries.append(entry)

    return entries


def parse_spantree(output: str) -> List[Dict[str, str]]:
    columns = COLUMN_DEFINITIONS["show spantree"]
    data = []
    spanning_tree_mode = ""

    lines = output.strip().splitlines()

    # Extract global config like Spanning Tree Path Cost Mode
    for idx, line in enumerate(lines):
        if "Spanning Tree Path Cost Mode" in line:
            match = re.search(r"Spanning Tree Path Cost Mode\s*:\s*(\S+)", line)
            if match:
                spanning_tree_mode = match.group(1)
            lines = lines[idx + 1:]  # Skip to table
            break

    header_found = False
    for line in lines:
        line = line.strip()
        if not line or set(line) <= set("-+ "):
            continue

        if not header_found:
            if all(keyword in line for keyword in ["Vlan", "STP", "Protocol", "Priority"]):
                header_found = True
            continue

        # Parse table rows
        parts = re.split(r'\s{2,}', line)
        if len(parts) == 4:
            row = {
                "VLAN": parts[0],
                "STP Status": parts[1],
                "Protocol": parts[2],
                "Priority": parts[3],
                "Spanning Tree Path Cost Mode": spanning_tree_mode
            }
            data.append(row)
    return data


def parse_spantree_ports_active(output: str) -> List[Dict[str, str]]:
    columns = COLUMN_DEFINITIONS["show spantree ports active"]
    data = []

    lines = output.strip().splitlines()
    header_found = False

    for line in lines:
        line = line.strip()
        if not line or set(line) <= set("-+ "):
            continue

        if not header_found:
            if all(keyword in line for keyword in ["Vlan", "Port", "Oper Status", "Path Cost", "Role", "Loop Guard"]):
                header_found = True
            continue

        # Split columns using 2+ spaces (assuming fixed-width formatting)
        parts = re.split(r'\s{2,}', line)
        if len(parts) >= 6:
            # Ensure 'Note' is included even if blank
            while len(parts) < 7:
                parts.append("")
            row = dict(zip(columns, parts))
            data.append(row)

    return data


def parse_interfaces_status(output):
    """
    Parses the 'show interfaces status' command output using regex-based splitting.
    Returns a list of dictionaries, one per interface.
    """
    data = []
    capture = False

    for line in output.splitlines():
        # Start capturing when data lines begin (match chassis/slot/port format)
        if re.match(r'^\s*\d+/\d+/\d+', line):
            capture = True

        if capture:
            # Skip separator lines
            if re.match(r"^\s*[-+]+\s*$", line):
                continue

            # Split line into tokens
            tokens = re.split(r'\s+', line.strip())

            # Defensive check to ensure expected number of fields
            if len(tokens) >= 13:
                entry = {
                    "Chas/Slot/Port": tokens[0],
                    "Admin Status": tokens[1],
                    "Auto Nego": tokens[2],
                    "Detected Speed (Mbps)": tokens[3],
                    "Detected Duplex": tokens[4],
                    "Detected Pause": tokens[5],
                    "Detected FEC": tokens[6],
                    "Configured Speed (Mbps)": tokens[7],
                    "Configured Duplex": tokens[8],
                    "Configured Pause": tokens[9],
                    "Configured FEC": tokens[10],
                    "Link Trap": tokens[11],
                    "EEE Status": tokens[12]
                }
                data.append(entry)

    return data


def parse_interfaces_counters(text):
    interfaces = []
    current_interface = None
    current_data = {}

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        # Match interface line (e.g., "3/1/47  ,")
        iface_match = re.match(r'^(\d+/\d+/\d+)\s*,', line)
        if iface_match:
            # Store previous interface data
            if current_interface and current_data:
                interfaces.append({"Interface": current_interface, **current_data})
            # Start new interface
            current_interface = iface_match.group(1)
            current_data = {}
            continue

        # Match all key=value pairs (including keys with slashes)
        for kv in re.findall(r'([\w/]+)\s*=\s*([\d]+)', line):
            key, value = kv
            current_data[key] = int(value)

    # Append last interface
    if current_interface and current_data:
        interfaces.append({"Interface": current_interface, **current_data})

    return interfaces


def parse_ip_interface(text):
    interfaces = []
    lines = text.strip().splitlines()
    header_found = False

    for line in lines:
        if re.match(r'^-+\+-+', line):
            header_found = True
            continue
        if not header_found or not line.strip():
            continue

        # Pattern for the fields
        match = re.match(
            r'^(.+?)\s+(\d{1,3}(?:\.\d{1,3}){3})\s+(\d{1,3}(?:\.\d{1,3}){3})\s+(UP|DOWN)\s+(YES|NO)\s+(.+?)(?:\s{2,}(.+))?$',
            line.strip()
        )

        if match:
            name, ip, mask, status, forward, device, flags = match.groups()
            interfaces.append({
                "Name": name.strip(),
                "IP Address": ip.strip(),
                "Subnet Mask": mask.strip(),
                "Status": status.strip(),
                "Forward": forward.strip(),
                "Device": device.strip(),
                "Flags": flags.strip() if flags else ""
            })

    return interfaces


def parse_ip_config(section_text: str) -> list[dict[str, str]]:
    """
    Parses the 'show ip config' section into a list of dictionaries.
    Filters only expected keys and removes trailing commas.
    """
    expected_keys = COLUMN_DEFINITIONS["show ip config"]
    result = {}

    for line in section_text.splitlines():
        line = line.strip()
        if not line or '=' not in line:
            continue  # skip empty lines or malformed lines
        key_part, value_part = line.split('=', 1)
        key = key_part.strip()
        value = value_part.strip().rstrip(',')  # Remove trailing commas
        if key in expected_keys:
            result[key] = value

    return [result] if result else []


def parse_ip_protocols(text):
    """
    Parses the 'show ip protocols' section and returns a list of dictionaries with column values.
    """
    result = []
    row = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().rstrip(",")
        row[key] = value
    if row:
        result.append(row)
    return result


def parse_ip_dos_statistics(section_text: str) -> list[dict[str, str]]:
    stats = {}
    for line in section_text.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("DoS type") or line.startswith("-"):
            continue
        if match := re.match(r"(.+?)\s{2,}(\d+)$", line):
            dos_type, attacks = match.groups()
            stats[dos_type.strip()] = attacks.strip()
    return [stats]


def parse_snmp_statistics(text: str) -> list[dict]:
    section_name = "show snmp statistics"
    columns = COLUMN_DEFINITIONS.get(section_name)
    if not columns:
        return []

    row = {}
    for line in text.splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().rstrip(",")
            if key in columns:
                row[key] = value

    # Ensure all columns are included even if not present in the output
    full_row = {col: row.get(col, "") for col in columns}

    return [full_row]  # return as a list[dict]


def parse_virtual_chassis_topology(text: str) -> list[dict]:
    section_name = "show virtual-chassis topology"
    columns = COLUMN_DEFINITIONS.get(section_name)
    if not columns:
        return []
    rows = []
    local_chassis = None
    # Extract the Local Chassis value
    for line in text.splitlines():
        match = re.match(r"Local Chassis:\s+(\d+)", line)
        if match:
            local_chassis = match.group(1)
            break
    # Regex pattern to match data lines
    pattern = re.compile(
        r"^\s*(\d+)\s+(\w+)\s+([\w+]+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([0-9a-f:]{17})",
        re.IGNORECASE
    )
    for line in text.splitlines():
        match = pattern.match(line)
        if match:
            row = dict(zip(columns[:-1], match.groups()))
            row[columns[-1]] = local_chassis  # Append Local Chassis column
            rows.append(row)
    return rows


def parse_virtual_chassis_consistency(data: str) -> list[dict]:
    # Define column headers based on the provided definitions
    column_headers = COLUMN_DEFINITIONS.get("show virtual-chassis consistency", [])
    
    # Prepare the output list
    results = []
    
    # Split the input data into lines
    lines = data.strip().split("\n")
    
    # Skip the first line as it contains the legend and is not needed for parsing
    lines = lines[1:]

    # Regex pattern to match each row of data
    line_pattern = re.compile(r"^\s*(\d+)\s+(\d+)\s+([A-Za-z]+)\s+([A-Za-z0-9]+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([A-Z]+)\s*$")

    for line in lines:
        # Match the line against the regex pattern
        match = line_pattern.match(line.strip())
        
        if match:
            # Extract the matched groups
            chas, config_chas_id, status, oper_type, oper_group, hello_interv, oper_vlan, config_vlan, license = match.groups()
            
            # Create a dictionary with the corresponding column names
            entry = {
                "Chassis ID": chas,
                "Config Chas ID": config_chas_id,
                "Status": status,
                "Oper Type": oper_type,
                "Oper Group": oper_group,
                "Hello Interv": hello_interv,
                "Oper Control Vlan": oper_vlan,
                "Config Control Vlan": config_vlan,
                "License": license
            }
            
            # Append the entry to the results list
            results.append(entry)

    # Return the results as a list of dictionaries
    
    return results


def parse_virtual_chassis_vf_link_member_port(output: str) -> List[Dict[str, str]]:
    lines = output.strip().splitlines()
    results = []
    vf_link_mode = ""

    # Extract VFLink mode
    for line in lines:
        mode_match = re.match(r"VFLink mode:\s*(\S+)", line)
        if mode_match:
            vf_link_mode = mode_match.group(1)
            break

    # Find the data section after the separator line
    data_started = False
    for line in lines:
        if re.match(r"^-+\+-+", line):
            data_started = True
            continue
        if not data_started or not line.strip():
            continue

        parts = re.split(r'\s{2,}', line.strip())
        if len(parts) == 4:
            results.append({
                "Chassis/VFLink ID": parts[0],
                "Chassis/Slot/Port": parts[1],
                "Oper": parts[2],
                "Is Primary": parts[3],
                "VFLink Mode": vf_link_mode
            })

    return results


def parse_virtual_chassis_chassis_reset_list(output: str) -> List[Dict[str, str]]:
    lines = output.strip().splitlines()
    results = []
    
    # Skip the header line
    data_started = False
    
    for line in lines:
        # Skip empty lines and the header line
        if not line.strip() or "Chas" in line:
            continue

        # Split by one or more spaces or tabs
        parts = re.split(r'\s{2,}', line.strip())
        if len(parts) == 2:
            # Remove trailing commas from the second column
            parts[1] = parts[1].rstrip(',')
            
            results.append({
                "Chas": parts[0],
                "Chassis reset list": parts[1]
            })

    return results


def parse_virtual_chassis_slot_reset_list(output: str) -> List[Dict[str, str]]:
    lines = output.strip().splitlines()
    results = []
    
    # Skip the header line
    for line in lines:
        # Skip empty lines and the header line
        if not line.strip() or "Chas" in line:
            continue

        # Split by one or more spaces or tabs
        parts = re.split(r'\s{2,}', line.strip())
        if len(parts) == 3:
            results.append({
                "Chas": parts[0],
                "Slot": parts[1],
                "Reset status": parts[2]
            })

    return results


def parse_virtual_chassis_vf_link(output: str) -> List[Dict[str, str]]:
    lines = output.strip().splitlines()
    results = []
    vf_link_mode = ""

    # Extract VFLink mode
    for line in lines:
        mode_match = re.match(r"VFLink mode:\s*(\S+)", line)
        if mode_match:
            vf_link_mode = mode_match.group(1)
            break

    # Find the data section after the separator line
    data_started = False
    for line in lines:
        if re.match(r"^-+\+-+", line):
            data_started = True
            continue
        if not data_started or not line.strip():
            continue

        # Split by two or more spaces
        parts = re.split(r'\s{2,}', line.strip())
        if len(parts) == 7:
            results.append({
                "Chassis/VFLink ID": parts[0],
                "Oper": parts[1],
                "Primary Port": parts[2],
                "Config Port": parts[3],
                "Active Port": parts[4],
                "Def Vlan": parts[5],
                "Speed Type": parts[6],
                "VFLink Mode": vf_link_mode
            })

    return results


def parse_virtual_chassis_auto_vf_link_port(output: str) -> List[Dict[str, str]]:
    lines = output.strip().splitlines()
    results = []

    # Process each line of output
    for line in lines:
        # Skip empty lines and the header line
        if not line.strip() or "Chassis/Slot/Port" in line:
            continue

        # Split by one or more spaces or tabs (to handle potential irregular spacing)
        parts = re.split(r'\s{2,}', line.strip())
        if len(parts) == 3:
            results.append({
                "Chassis/Slot/Port": parts[0],
                "Chassis/VFLink ID": parts[1],
                "VFLink member status": parts[2]
            })

    return results


def parse_virtual_chassis_neighbors(output: str) -> List[Dict[str, str]]:
    lines = output.strip().splitlines()
    results = []

    # Skip the first three lines: 2 header lines + separator
    data_lines = lines[3:]

    for line in data_lines:
        if not line.strip():
            continue

        parts = re.split(r'\s{2,}', line.strip())

        if len(parts) >= 2:
            result = {
                "Chas ID": parts[0],
                "VFL 0": parts[1],
                "VFL 1": parts[2] if len(parts) > 2 else ""
            }
            results.append(result)

    return results


def parse_debug_virtual_chassis_topology(text: str) -> List[Dict[str, str]]:
    section_name = "debug show virtual-chassis topology"
    columns = [
        "Oper Chas",
        "Role",
        "Status",
        "Config Chas ID",
        "Oper Priority",
        "Group",
        "MAC-Address",
        "System Ready",
        "Local Chassis"
    ]
    
    rows = []
    local_chassis = None

    # Extract the Local Chassis value
    for line in text.splitlines():
        match = re.match(r"Local Chassis:\s+(\d+)", line)
        if match:
            local_chassis = match.group(1)
            break

    # Regex pattern to match data lines
    pattern = re.compile(
        r"^\s*(\d+)\s+(\w+)\s+([\w+]+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([0-9a-f:]{17})\s+(\w+)",
        re.IGNORECASE
    )

    for line in text.splitlines():
        match = pattern.match(line)
        if match:
            row = dict(zip(columns[:-1], match.groups()))
            row["Local Chassis"] = local_chassis
            rows.append(row)

    return rows


def parse_debug_virtual_chassis_status(output: str) -> List[Dict[str, str]]:
    columns = COLUMN_DEFINITIONS["debug show virtual-chassis status"]

    rows = []

    # Regex pattern to capture the 6 fields, allowing for spacing in "Parameter"
    pattern = re.compile(
        r"^\s*(\d+)\s+(\w+)\s+(.+?)\s{2,}(\S+)\s+(\S+)\s+(\S+)\s*$"
    )

    for line in output.strip().splitlines():
        match = pattern.match(line)
        if match:
            row = dict(zip(columns, match.groups()))
            rows.append(row)

    return rows


def parse_debug_virtual_chassis_connection(output: str) -> List[Dict[str, str]]:
    columns = COLUMN_DEFINITIONS["debug show virtual-chassis connection"]

    rows = []

    # Regex to match the expected row format
    pattern = re.compile(
        r"^\s*(\d+)\s+([0-9a-f:]{17})\s+([\d.]+)\s+([\d.]+)\s+(\w+)\s*$",
        re.IGNORECASE
    )

    for line in output.strip().splitlines():
        match = pattern.match(line)
        if match:
            row = dict(zip(columns, match.groups()))
            rows.append(row)

    return rows


def parse_show_cloud_agent_status(output: str) -> List[Dict[str, str]]:
    result = {}
    
    # Match lines in the format: Key : Value (optionally ending with a comma)
    pattern = re.compile(r"^\s*(.+?)\s*:\s*(.+?)(?:,)?\s*$")
    
    for line in output.strip().splitlines():
        match = pattern.match(line)
        if match:
            key = match.group(1).strip()
            value = match.group(2).strip()
            result[key] = value

    return [result]


def parse_pkgmgr(output: str) -> List[Dict[str, str]]:
    columns = COLUMN_DEFINITIONS["show pkgmgr"]
    rows = []

    for line in output.strip().splitlines():
        # Skip legend, column header, and separator lines
        if "indicates" in line or "Name" in line or set(line.strip()) <= {"-", "+"}:
            continue

        parts = line.strip().split(None, 3)
        if len(parts) == 4:
            row = dict(zip(columns, parts))
            rows.append(row)

    return rows


def parse_appmgr(output: str) -> List[Dict[str, str]]:
    columns = COLUMN_DEFINITIONS["show appmgr"]    
    rows = []

    for line in output.strip().splitlines():
        # Skip legend, header, and separator lines
        if "indicates" in line or "Application" in line or set(line.strip()) <= {"-", "+"}:
            continue

        parts = line.strip().split(None, 4)  # Split into max 5 fields
        if len(parts) == 5:
            row = dict(zip(columns, parts))
            rows.append(row)

    return rows


def parse_naas_license(output: str) -> List[Dict[str, str]]:
    columns = COLUMN_DEFINITIONS["show naas license"]    
    rows: List[Dict[str, str]] = []

    for line in output.strip().splitlines():
        # Skip headers, separators, and legend lines
        if "Serial" in line or "VC" in line or set(line.strip()) <= {"-", "+"}:
            continue

        parts = line.strip().split(None, 8)  # maxsplit=8 for 9 columns
        if len(parts) == 9:
            row = dict(zip(columns, parts))
            rows.append(row)

    return rows


def parse_naas_agent_status(output: str) -> List[Dict[str, str]]:
    columns = COLUMN_DEFINITIONS["show naas-agent status"]    
    data: Dict[str, str] = {}

    for line in output.strip().splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().rstrip(",")
        if key in columns:
            data[key] = value

    return [data] if data else []


def parse_capability_naas(output: str) -> List[Dict[str, str]]:
    columns = COLUMN_DEFINITIONS["debug show capability naas"]    
    rows: List[Dict[str, str]] = []

    for line in output.strip().splitlines():
        # Skip legend, headers, and separators
        if line.strip().startswith("+") or "NAAS" in line:
            continue

        # Split line by pipe delimiter
        parts = [part.strip() for part in line.strip().strip('|').split('|')]
        if len(parts) == len(columns):
            row = dict(zip(columns, parts))
            rows.append(row)

    return rows


def parse_ntp_server_status(output: str) -> List[Dict[str, str]]:
    columns = COLUMN_DEFINITIONS["show ntp server status"]
    
    # Initialize a dictionary to store key-value pairs
    data = {}

    # Split the output by lines
    lines = output.strip().splitlines()

    # Iterate through each line
    for line in lines:
        # Skip lines that don't contain '=' or are empty
        if '=' not in line:
            continue
        
        # Split the line into key and value based on '='
        parts = line.split("=", 1)
        
        if len(parts) == 2:
            key = parts[0].strip()
            value = parts[1].strip().rstrip(',')  # Remove trailing commas
            
            # Only add to dictionary if the key is in the columns
            if key in columns:
                data[key] = value

    # Return the parsed data as a list of dictionaries
    return [data] if data else []


def parse_ntp_status(output: str) -> List[Dict[str, str]]:
    columns = COLUMN_DEFINITIONS["show ntp status"]    
    data = {}

    for line in output.strip().splitlines():
        if ':' not in line:
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().rstrip(',')

        if key in columns:
            data[key] = value

    return [data] if data else []


def parse_ntp_keys(output: str) -> List[Dict[str, str]]:
    columns = COLUMN_DEFINITIONS["show ntp keys"]    
    rows = []

    for line in output.strip().splitlines():
        # Skip header and separator lines
        if line.strip().startswith("Key") or "-" in line or "+" in line:
            continue

        parts = line.strip().split(None, 1)
        if len(parts) == 2:
            row = dict(zip(columns, parts))
            rows.append(row)

    return rows


def parse_capability_profile(output: str) -> List[Dict[str, str]]:
    columns = COLUMN_DEFINITIONS["show capability profile"]    

    data = {}

    for line in output.strip().splitlines():
        if ':' not in line:
            continue

        key, value = line.split(':', 1)
        key = key.strip().replace("  ", " ")  # Normalize spacing
        value = value.strip().rstrip(',')

        if key in columns:
            data[key] = value

    return [data] if data else []


PARSERS = {
    "show hardware-info": parse_hardware_info,
    "show chassis": parse_chassis,
    "show module long": parse_module_long,
    "show transceivers": parse_transceivers,
    "show fan": parse_fan,
    "show powersupply": parse_powersupply,
    "show temperature": parse_temperature,
    "show system": parse_system,
    "show running-directory": parse_running_directory,
    "show microcode": parse_microcode,
    "show license-info": parse_license_info,
    "show lldp remote-system": parse_lldp_remote_system,
    "show aaa authentication": parse_aaa_authentication,
    "show health": parse_health,
    "show health all cpu": parse_health_all_cpu,
    "show vlan": parse_vlan,
    "show spantree": parse_spantree,
    "show spantree ports active": parse_spantree_ports_active,
    "show interfaces status": parse_interfaces_status,
    "show interfaces counters": parse_interfaces_counters,
    "show ip interface": parse_ip_interface,
    "show ip config": parse_ip_config,
    "show ip protocols": parse_ip_protocols,
    "show ip dos statistics": parse_ip_dos_statistics,
    "show snmp statistics": parse_snmp_statistics,
    "show virtual-chassis topology": parse_virtual_chassis_topology,
    "show virtual-chassis consistency": parse_virtual_chassis_consistency,
    "show virtual-chassis vf-link member-port": parse_virtual_chassis_vf_link_member_port,
    "show virtual-chassis chassis-reset-list": parse_virtual_chassis_chassis_reset_list,
    "show virtual-chassis slot-reset-list": parse_virtual_chassis_slot_reset_list,
    "show virtual-chassis vf-link": parse_virtual_chassis_vf_link,
    "show virtual-chassis auto-vf-link-port": parse_virtual_chassis_auto_vf_link_port,
    "show virtual-chassis neighbors": parse_virtual_chassis_neighbors,
    "debug show virtual-chassis topology": parse_debug_virtual_chassis_topology,
    "debug show virtual-chassis status": parse_debug_virtual_chassis_status,
    "debug show virtual-chassis connection": parse_debug_virtual_chassis_connection,
    "show cloud-agent status": parse_show_cloud_agent_status,
    "show pkgmgr": parse_pkgmgr,
    "show appmgr": parse_appmgr,
    "show naas license": parse_naas_license,
    "show naas-agent status": parse_naas_agent_status,
    "debug show capability naas": parse_capability_naas,
    "show ntp server status": parse_ntp_server_status,
    "show ntp status": parse_ntp_status,
    "show ntp keys": parse_ntp_keys,
    "show capability profile": parse_capability_profile,
}

def extract_section(full_text: str, section_name: str) -> str:
    pattern = fr"#+\s*{re.escape(section_name)}\s*#+\n(.*?)(?=\n#+|\Z)"
    match = re.search(pattern, full_text, re.DOTALL)
    return match.group(1).strip() if match else ""


def parse_sections(full_text: str) -> Dict[str, List[Dict[str, str]]]:
    parsed_output = {}
    for section_name, parser in PARSERS.items():
        # Special handling for combined microcode sections
        if (section_name == "show microcode"):
            combined_microcode_data = []
            for location in ["certified", "working", "loaded"]:
                specific_section_name = f"show microcode {location}"
                raw_text = extract_section(full_text, specific_section_name)
                if raw_text:
                    parsed = parser(raw_text, location)
                    if parsed:
                        combined_microcode_data.extend(parsed)
            if combined_microcode_data:
                parsed_output["show microcode"] = combined_microcode_data
        else:
            raw_text = extract_section(full_text, section_name)
            if raw_text:
                parsed_output[section_name] = parser(raw_text)
    return parsed_output


def export_to_csv(parsed_data: Dict[str, List[Dict[str, str]]]):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = f"parsed_sections_{timestamp}.csv"
    
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        for idx, (section_name, rows) in enumerate(parsed_data.items()):
            if not rows:
                writer.writerow([f"{section_name}"])
                headers = COLUMN_DEFINITIONS.get(section_name)
                writer.writerow(headers)
                if idx < len(parsed_data) - 1:
                    writer.writerows([[]] * 2)
                continue

            writer.writerow([f"{section_name}"])

            headers = COLUMN_DEFINITIONS.get(section_name, list(rows[0].keys()))
            writer.writerow(headers)

            for row in rows:
                row_out = []
                for col in headers:
                    val = row.get(col, "")
                    # 🛡️ Protect any value with "/" (like 1/1) from Excel auto-formatting
                    if isinstance(val, str) and "/" in val and not val.startswith("=\""):
                        val = f"=\"{val}\""
                    row_out.append(val)
                writer.writerow(row_out)

            # Add 2 blank lines between sections
            if idx < len(parsed_data) - 1:
                writer.writerows([[]] * 2)

    print(f"✅ CSV exported to {filename}")


def main():
    log_file = "tech_support.log"
    if not os.path.isfile(log_file):
        print(f"❌ File not found: {log_file}")
        return

    with open(log_file, encoding='utf-8') as f:
        full_text = f.read()

    parsed = parse_sections(full_text)
    if not parsed:
        print("⚠️ No recognizable sections found.")
    else:
        export_to_csv(parsed)

if __name__ == "__main__":
    main()

import paramiko
from getpass import getpass
import time
import re
import json
import os

def wait_for_shell(shell, timeout=120):
    """Read output from shell until timeout or prompt returns."""
    shell.settimeout(2)
    output = ""
    start = time.time()
    while time.time() - start < timeout:
        try:
            chunk = shell.recv(4096).decode("utf-8")
            output += chunk
            # Break if we detect shell prompt (e.g., ending in # or $)
            if any(p in chunk for p in ["# ", "#->", "$ ", ">", "login: "]):
                break
        except Exception:
            time.sleep(1)
    return output

def prompt_initial_aos_version():
    """Prompts the user for the full AOS version string."""
    return input("\nEnter AOS version string (e.g., 8.9.221.R03): ").strip()

def parse_aos_version_string(version_string):
    """
    Parses the AOS version string into major, build, and release components.
    Returns a dictionary with 'major', 'build', and 'release' keys.
    Values can be None if not found in the string.
    """
    regex_pattern = r'^(\d+\.\d+)(?:\.(\d+))?(?:\.?([Rr]\d+))?$'
    match = re.match(regex_pattern, version_string)

    if match:
        major = match.group(1)
        build = match.group(2) if match.group(2) else None  # Can be None
        release_raw = match.group(3).upper() if match.group(3) else None # Can be None
        # Conditional formatting
        release = None
        if release_raw:
            if major.startswith("8."):
                # Convert to "R03" format
                number_part = release_raw[1:].zfill(2)  # Pad to 2 digits
                release = "R" + number_part
            else:
                release = release_raw
        return {"major": major, "build": build, "release": release}
    else:
        # If the basic major.minor pattern isn't found, return None for all
        return {"major": None, "build": None, "release": None}

def validate_and_complete_version_parts(parsed_parts):
    """
    Validates parsed version sections. If a section (build or release)
    is missing (None), prompts the user for it.
    Assumes 'major' will always be present if initial parsing was somewhat successful.
    """
    major = parsed_parts.get("major") # Should already be there from a successful parse
    build = parsed_parts.get("build")
    release = parsed_parts.get("release")

    if major is None:
        # This indicates a fundamental failure in parsing the initial string.
        # The main loop should handle this by re-prompting for the full string.
        # However, if we wanted to be extremely robust and prompt for major here:
        while not major:
            major = input("Enter AOS Major version (e.g., 8.9): ").strip()
        # For this exercise, we assume parse_aos_version_string got the major if input was valid.
        #pass # Major should be handled by the calling function based on parse_aos_version_string output

    if build is None:
        build = input("Enter AOS Build Number (e.g., 221): ").strip() or "221" # Default if empty

    if release is None:
        release = input("Enter AOS Release (e.g., R03): ").strip() or "R03" # Default if empty

    return {"major": major, "build": build, "release": release}

def get_aos_version_orchestrator():
    """Orchestrates prompting, parsing, and validation to get the full AOS version."""
    while True:
        initial_version_string = prompt_initial_aos_version()
        parsed_components = parse_aos_version_string(initial_version_string)

        if not parsed_components.get("major"):
            print("Invalid format. Major version (e.g., X.Y) could not be parsed. Please try again.")
            continue # Re-prompt for the full string

        # Now, parsed_components["major"] is guaranteed to be something.
        # Fill in any missing optional parts (build, release)
        completed_components = validate_and_complete_version_parts(parsed_components)

        aos_major = completed_components["major"]
        aos_build = completed_components["build"]
        aos_release = completed_components["release"]

        full_version = f"{aos_major}.{aos_build}.{aos_release}"
        confirm = input(f"Confirm full AOS version string [{full_version}] [y]/n: ").strip().lower() or "y"

        if confirm == "y":
            return aos_major, aos_build, aos_release
        # If not 'y', the loop will restart, prompting for the initial string again.


# Load GA index once at the module level
ga_index_path = os.path.join(os.path.dirname(__file__), "ga_index.json")
with open(ga_index_path) as f:
    ga_index = json.load(f)

def get_ga_build(version, family):
    try:
        build = ga_index[version][family]
        if build in ('', 'N/S', 'N/A', 'UNK'):
            raise ValueError(f"No GA build available for version {version} and family {family}. Build returned: {build}")
        return build
    except KeyError:
        raise ValueError(f"No GA build found for version {version} and family {family}")

def lookup_ga_build():
    """Allows the user to repeatedly look up GA builds until they provide a blank input."""
    print("Lookup the GA build by providing the AOS version & switch family...")
    while True:
        ga_prompt_fam = input("Enter the switch family name to lookup the GA build # (e.g., shasta) [exit]: ").strip().lower() or None
        if not ga_prompt_fam:
            print("Canceling GA build lookup...")
            break
        ga_prompt_ver = input("Provide the AOS version & Release for the lookup (e.g., 8.10R02) [exit]: ").strip().upper() or None
        if ga_prompt_ver:
            print("GA Build: ",get_ga_build(ga_prompt_ver, ga_prompt_fam))
        else:
            print("Lookup canceled.")

def main():
    #lookup_ga_build()
    aos_major, aos_build, aos_release = get_aos_version_orchestrator()

    print("\n--- AOS Version Parsed ---")
    print(f"Major Version: {aos_major}")
    print(f"Build Number:  {aos_build}")
    print(f"Release:       {aos_release}")
    print(f"Full Version:  {aos_major}.{aos_build}.{aos_release}")

    # Step 2: Get list of IPs with optional usernames and passwords
    hosts = []
    print("\nEnter device details. Press Enter without an IP to finish.")
    while True:
        ip = input("Enter device IP: ").strip()
        if not ip:
            break
        username = input(f"Enter username for {ip} [admin]: ") or "admin"
        password = getpass(f"Enter password for {ip} [switch]: ") or "switch"
        hosts.append({"ip": ip, "username": username, "password": password})
    
    
    # Image mapping
    image_map = {
        "nandi_sim": ["Nossim.img"],
        "everest": ["Uos.img"],
        "medora_sim64": ["Mossim.img", "Menisim.img"],
        "tor": ["Tos.img"],
        "vindhya": ["Nos.img"],
        "medora": ["Mos.img", "Meni.img", "Mhost.img"],
        "yukon": ["Yos.img"],
        "shasta": ["Uos.img"],
        "aravalli": ["Nosa.img"],
        "shasta_n": ["Uosn.img"],
        "whitney": ["Wos.img"],
        "nandi": ["Nos.img"],
        "whitney_sim": ["Wossim.img"]
    }
    
    # Constants
    base_ip = "http://10.46.4.37"
    base_dir = "/bop/images"
    aos_major_fmt = aos_major.replace('.', '_')
    
    # Step 3: Iterate over each host
    for host in hosts:
        ip = host["ip"]
        print(f"\nConnecting to {ip}...")
        try:
            # Connect via SSH
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(ip, username=host["username"], password=host["password"], timeout=10)
            shell = client.invoke_shell()
            shell.send("su\n")
            time.sleep(1)
            shell.recv(1024)  # No password needed
            shell.send("echo $PS1\n")
            time.sleep(1)
            output = shell.recv(2048).decode("utf-8")
            lines = output.strip().splitlines()
            ps1 = lines[-1] if lines else ""
            family = ps1.split()[0].lower() if ps1 else None
            if not family or family not in image_map:
                print(f"[{ip}] Unknown or missing platform family: '{family}'")
                client.close()
                continue
            print(f"[{ip}] Platform family: {family}")
            images = image_map[family]
            image_path = f"{base_dir}/OS_{aos_major_fmt}_{aos_build}_{aos_release}/{family}/Release/"
            for img in images:
                url = f"{base_ip}{image_path}{img}"
                cmd = f"curl -kL \"{url}\" --output /flash/{img}"
                shell.send(cmd + "\n")
                print(f"[{ip}] Downloading {img}...")
                download_output = wait_for_shell(shell)
                print(f"[{ip}] Downloaded {img} to /flash/")
            client.close()
        except Exception as e:
            print(f"[{ip}] ERROR: {e}")

if __name__ == "__main__":
    main()


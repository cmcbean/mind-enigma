import random
import os
import pandas as pd
import glob
import time


def parse_csv():
    # List all .csv files in the current directory
    csv_files = glob.glob("*.csv")

    # If there are no .csv files in the directory, notify the user
    if not csv_files:
        print("No .csv files found in the current directory.")
        return

    # Print out the files for the user to choose
    for i, file in enumerate(csv_files):
        print(f"{i + 1}. {file}")

    # Get the user's choice
    choice = int(input("Enter the number of the file to use: ")) - 1
    device_list_path = csv_files[choice]

    # Read the .csv file
    read_in = pd.read_csv(device_list_path, header=None)  # Indicate that there is no header

    # Filter the data based on the device type and column "E"
    device_types = ["Network", "DC-UCS", "DC-VMware", "IPT", "Network-Voice"]
    filtered = read_in[read_in[0].isin(device_types) & (read_in[4] != 'N')]
    return filtered


class HiveMind:
    def __init__(self):
        self.filename = None
        # Check if the directory exists, create it if it doesn't
        if not os.path.exists('mRemoteNG Sessions - Optanix'):
            os.makedirs('mRemoteNG Sessions - Optanix')

        # Establish list to contain port forwarding information
        self.port_forwardings = []
        self.timestr = time.strftime("%Y%m%d-%H%M%S")

        # Collect some data
        self.session_name = input("Enter the session name: ")
        # self.hostname = input("Enter the hostname/IP: ")
        # self.username = input("Enter the username: ")
        # self.ppk_path = input("Enter the .ppk file path: ")

    def get_tunnel_config(self, tech_type):
        """
        Returns the tunnel configuration based on the device type.
        """
        ssh_port = random.randint(30000, 35000)
        ssh_tunnel = f"L{ssh_port}=localhost:22"

        if tech_type in ["Network", "Network-Voice"]:
            self.port_forwardings.append(ssh_tunnel)
        elif tech_type in ["IPT", "DC-UCS", "DC-VMware"]:
            https_port = random.randint(35000, 40000)
            https_tunnel = f"L{https_port}=localhost:443"
            self.port_forwardings.append(f"{ssh_tunnel},{https_tunnel}")

    def construct_port_forwards(self, tech_type):
        # Get the tunnel configuration
        self.get_tunnel_config(tech_type)

    def construct_reg_key(self):
        # Generate random port number between 20000 and 30000
        port = random.randint(20000, 30000)

        # Define registry key path
        key_path = r"[HKEY_CURRENT_USER\Software\SimonTatham\PuTTY\Sessions\{}]".format(self.session_name)

        # Define the session details
        session_details = f"""Windows Registry Editor Version 5.00 

{key_path}

"HostName"=sz:"localhost"
"PortNumber"=dword:{port:08x}
"UserName"=sz:"sampson"
"PublicKeyFile"=sz:"C:\sampsonppk\Sampson.ppk"
"Protocol"="ssh"
"""

        # Define the filename using the session name and hostname
        self.filename = f"{self.session_name}-DMA-Tunnels-{self.timestr}.reg"

        # Create a new file and write the session details
        with open(os.path.join('mRemoteNG Sessions - Optanix', self.filename), 'w') as f:
            f.write(session_details)

        # Inform user that the .reg file was created successfully
        print(f"Reg file {self.session_name} created successfully.")

    def director(self):

        # Construct the base reg key to add a session to the end device for tunneling
        self.construct_reg_key()

        # Read in and parse .csv file to gather interesting data
        filtered = parse_csv()

        # Iterate over each row in the filtered data
        for _, row in filtered.iterrows():
            tech_type = row[0]
            ip_addr = row[2]
            dev_name = row[1]
            descrip = row[3]
            site = row[10]

            self.construct_port_forwards(tech_type)

        # Generate port forward string from list
        print(self.port_forwardings)
        pfwdlist = ",".join(self.port_forwardings)
        print(pfwdlist)

        # Add in port forwards
        with open(os.path.join('mRemoteNG Sessions - Optanix', self.filename), 'a') as f:
            f.write(f""""PortForwardings"=sz:"{pfwdlist}"
                                            """)


if __name__ == "__main__":
    HiveMind().director()

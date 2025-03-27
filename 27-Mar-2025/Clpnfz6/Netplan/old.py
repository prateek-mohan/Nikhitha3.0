import paramiko
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time

def ssh_jump_login(jump_host, jump_user, jump_password, target_host, target_user, key_path):
    """
    Establishes SSH connection to the jump host and the target host via the jump host.
    Returns the jump_client and jump_shell for later use.
    """
    try:
        # Step 1: Connect to Jump Host
        jump_client = paramiko.SSHClient()
        jump_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        jump_client.connect(jump_host, username=jump_user, password=jump_password)

        # Open an interactive shell on the jump host
        jump_shell = jump_client.invoke_shell()
        time.sleep(1)  # Give it some time to establish the session

        # Step 2: SSH into Target Host from Jump Host using the provided key
        jump_shell.send(f"ssh {target_user}@{target_host} -i {key_path}\n")
        time.sleep(5)  # Wait for the SSH connection to establish

        #print(f"✅ Successfully connected to target host {target_host} via {jump_host}")
        return jump_client, jump_shell  # Return jump_client and jump_shell for later use

    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

def run_command(jump_shell, command):
    """Run a command on the target host via the jump host shell."""
    try:
        # Send the command to the target host via the jump shell
        jump_shell.send(command + "\n")
        time.sleep(2)  # Wait for command execution

        # Read the output of the command
        output = jump_shell.recv(65535).decode()
        return output

    except Exception as e:
        return f"❌ Error: {e}"
    
def ssh_connect(hostname, username, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, password=password)
    return ssh

def execute_command(ssh_client, command):
    stdin, stdout, stderr = ssh_client.exec_command(command)
    output = stdout.read().decode()
    error = stderr.read().decode()
    return output, error
    
row=[]
# Replace these details with actual values
jump_host = "10.84.64.132"  # First SSH host
jump_user = "root"  # Username for jump host
jump_password = "starent"  # Password for jump host
#target_host = "10.84.106.241"  # Final target host
target_user = "cloud-user"  # Username for target host



username = "cloud-user"
password = "Csco@123"
input_file = 'input.txt'
header = f"{'Setup Name':<25} {'Setup IP':<20} {'CNDP Version':<15} {'SMF SMI Version':<40} {'UPF SMI Version':<40} {'Client Version':<20} {'Server Version':<20} {'Ubuntu Version':<15} "
line = "-" * len(header)
print(header)
print(line)
row.append(header)
row.append(line)
setup_list=[]

with open(input_file, 'r') as file:
    for f_line in file:
        setup_list.append(f_line.strip().split(': '))

htmlpage_ls=[]
html_start = '<html lang="en">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Document</title>\n</head>\n<body>\n</body>\n</html>\n<html>\n<head>\n<style>\ntable {border-collapse: collapse;}\nth, td { border: 1px solid black; padding: 8px;}\nth { background-color: lightgrey; } /* Added background color */\n</style>\n</head>\n<body>\n<table>\n<tr>\n<th>Setup Name</th>\n<th>Setup IP</th>\n<th>CNDP Version</th>\n<th>SMF SMI Version</th>\n<th>UPF SMI Version</th>\n<th>Client Version</th>\n<th>Server Version</th>\n<th>Ubuntu Version</th>\n</tr>\n'
html_end = '\n</table>\n</body>\n</html>'


command="helm list -n cee-cee"
command2 = 'sudo cat /etc/smi/base-image-version'
command3 = "kubectl version"
command4 = "lsb_release -a"
smi_ver = []

# Initialize a variable to track the last printed setup name
last_setup_name = None
for set_i in range(len(setup_list)):
    hostname = setup_list[set_i][-1]
    setup_name = setup_list[set_i][0].strip()
    setup_ip = setup_list[set_i][1]
    if hostname in ["10.84.106.241","10.84.106.242"]:
        target_host = hostname
        if target_host == "10.84.106.241":
            key_path = "key.pem"  # Path to SSH private key for target host
        elif target_host == "10.84.106.242":    
            key_path = "key-ru26.pem"  # Path to SSH private key for target host
        # Establish SSH connection and get jump_client and jump_shell
        jump_client, jump_shell = ssh_jump_login(jump_host, jump_user, jump_password, target_host, target_user, key_path)

        if jump_client and jump_shell:
            # Now you can run multiple commands later using the jump_shell
            command_1 = "helm list -n cee-global"
            command_2 = "sudo cat /etc/smi/base-image-version"
            command_3 = "kubectl version"
            command_4 = "lsb_release -a"

            output1 = run_command(jump_shell, command_1)
            out2 = run_command(jump_shell, command_2)
            out3 = run_command(jump_shell, command_3)
            out4 = run_command(jump_shell, command_4)

        
            # Process SMI Versions
            smi_version = ""
            for line in out2.split("\n"):
                        if "SMI_BASE_IMAGE_BUILD_FULL_VERSION" in line:
                            smi_version = line.split("=")[1].strip()
                            break

            # Process Client Versions
            client_version = ""
            for line in out3.split("\n"):
                        if "Client Version" in line:
                            client_version = line.split(":")[1].strip()
                            break

            # Process Server Versions
            server_version = ""
            for line in out3.split("\n"):
                        if "Server Version" in line:
                            server_version = line.split(":")[1].strip()
                            break

            # Process Release Versions
            release_version = ""
            for line in out4.split("\n"):
                        if "Release" in line:
                            ubuntu_version = line.split(":")[1].strip()
                            break
                        
            

            # Construct Table Row
            #cndp_version = cee_d['APP VERSION'][0] if 'APP VERSION' in cee_d else "N/A"    
            #setup_name_display = "Dalton"
            #setup_ip = "192.84.106.241"
            #cndp_version = "2023.459i.456"
            
            
            # Parse Helm List Output for CNDP Version
            op_ls = output1.split("\n")
            col = []
            for index in op_ls[-2].split("\t"):
                index = index.strip()  # Removes extra spaces and carriage returns
                if index.endswith(" "):
                    if "APP" in index:
                        col.append("APP VERSION")
                    else:
                        col.append(index.split(" ")[0])
                else:
                    col.append(index)      
                        
            # Populate content for each column
            cont_ls = [[] for _ in range(len(col))]
            cee_d = {}
            for i in range(1, len(op_ls)):
                temp = op_ls[i].split("\t")
                for j in range(len(temp)):
                    cont_ls[j].append(temp[j].split(" ")[0] if " " in temp[j] else temp[j])
            for k in range(len(col)):
                cee_d[col[k]] = cont_ls[k]
            # Construct Table Row
            #cndp_version = cee_d['APP VERSION'][0] if 'APP VERSION' in cee_d else "N/A"
            #cndp_version = cee_d['APP VERSION'][0] if 'APP VERSION' in cee_d and cee_d['APP VERSION'] else None
            if 'APP VERSION' in cee_d and cee_d['APP VERSION']:
                cndp_version = "N/A" if cee_d['APP VERSION'][0] == "APP" else cee_d['APP VERSION'][0]
            else:
                cndp_version = "N/A"
                
            
            # Check if the setup name is the same as the last printed setup name
            if setup_name == last_setup_name:
                setup_name_display = ""  # Empty string for duplicate setup name
            else:
                setup_name_display = setup_name  # Print the setup name
                last_setup_name = setup_name  # Update the last printed setup name
                
            temp_row = f"{setup_name_display:<25} {setup_ip:<20} {cndp_version:<15} {smi_version:<40} {smi_version:<40} {client_version:<20} {server_version:<20} {ubuntu_version:<20}"
            print(temp_row)
            row.append(temp_row)      
            
            # Add Row to HTML Table with conditional background color
            row_style = ('style="background-color:skyblue; color: black;"' if setup_name.lower() == "cndp-a08-cm-cm" else 'style="background-color: orange;"' if setup_name.lower().startswith("cndp") else "")
            htmlpage_ls.append(f'<tr {row_style}><td>{setup_name_display}</td><td>{setup_ip}</td><td>{cndp_version}</td><td>{smi_version}</td><td>{smi_version}</td><td>{client_version}</td><td>{server_version}</td><td>{ubuntu_version}</td></tr>')
    
                        
            #print(f"smi = {smi_version}")
            #print(f"cli = {client_version}")
            #print(f"ser = {server_version}")
            #print(f"rele = {release_version}")

            # Close the connection after use
            jump_client.close()
            
    else:
            ssh_client = ssh_connect(hostname, username, password)
            # Establish SSH connection and get jump_client and jump_shell
            #jump_client, jump_shell = ssh_jump_login(jump_host, jump_user, jump_password, target_host, target_user, key_path)
            # Execute helm list command
            output, error = execute_command(ssh_client, command)

            if setup_name == "Gamma":
                out2, err2 = execute_command(ssh_client, "sudo cat /etc/smi/base-image-version")
            else:
                out2, err2 = execute_command(ssh_client, command2)

            if setup_name in ["Gamma", "Watson", "Castor,Pollux", "cndp-a08-cm-cm", "Perf_RCM", "Castor", "Pollux"]:
                out3, err3  = execute_command(ssh_client, "kubectl version --short")
            else:
                out3, err3  = execute_command(ssh_client, command3)

            out4, err4  = execute_command(ssh_client, command4)

            # Process SMI Versions
            smi_version = ""
            for line in out2.split("\n"):
                if "SMI_BASE_IMAGE_BUILD_FULL_VERSION" in line:
                    smi_version = line.split("=")[1].strip()
                    break

            # Process Client Versions
            client_version = ""
            for line in out3.split("\n"):
                if "Client Version" in line:
                    client_version = line.split(":")[1].strip()
                    break

            # Process Server Versions
            server_version = ""
            for line in out3.split("\n"):
                if "Server Version" in line:
                    server_version = line.split(":")[1].strip()
                    break

            # Process Release Versions
            release_version = ""
            for line in out4.split("\n"):
                if "Release" in line:
                    ubuntu_version = line.split(":")[1].strip()
                    break

            # Parse Helm List Output for CNDP Version
            op_ls = output.split("\n")
            col = []
            for index in op_ls[0].split("\t"):
                if index.endswith(" "):
                    if "APP" in index:
                        col.append("APP VERSION")
                    else:
                        col.append(index.split(" ")[0])
                else:
                    col.append(index)

            # Populate content for each column
            cont_ls = [[] for _ in range(len(col))]
            cee_d = {}
            for i in range(1, len(op_ls)):
                temp = op_ls[i].split("\t")
                for j in range(len(temp)):
                    cont_ls[j].append(temp[j].split(" ")[0] if " " in temp[j] else temp[j])
            for k in range(len(col)):
                cee_d[col[k]] = cont_ls[k]
            # Construct Table Row
            if 'APP VERSION' in cee_d and cee_d['APP VERSION']:  
                cndp_version = "N/A" if cee_d['APP VERSION'][0] == "APP" else cee_d['APP VERSION'][0]  
            else:
                cndp_version = "N/A"  

            # Check if the setup name is the same as the last printed setup name
            if setup_name == last_setup_name:
                setup_name_display = ""  # Empty string for duplicate setup name
            else:
                setup_name_display = setup_name  # Print the setup name
                last_setup_name = setup_name  # Update the last printed setup name

            temp_row = f"{setup_name_display:<25} {setup_ip:<20} {cndp_version:<15} {smi_version:<40} {smi_version:<40} {client_version:<20} {server_version:<20} {ubuntu_version:<20}"
            print(temp_row)
            row.append(temp_row)
            
            # Add Row to HTML Table with conditional background color
            row_style = ('style="background-color:skyblue; color: black;"' if setup_name.lower() == "cndp-a08-cm-cm" else 'style="background-color: orange;"' if setup_name.lower().startswith("cndp") else "")
            htmlpage_ls.append(f'<tr {row_style}><td>{setup_name_display}</td><td>{setup_ip}</td><td>{cndp_version}</td><td>{smi_version}</td><td>{smi_version}</td><td>{client_version}</td><td>{server_version}</td><td>{ubuntu_version}</td></tr>')

            
            ssh_client.close()
            
final_html_page = html_start + "\n".join(htmlpage_ls) + html_end

message = "\n".join(row)
me = ['pratemoh@cisco.com']
recipients = ['pratemoh@cisco.com']
#recipients = ['pratemoh@cisco.com','anborde@cisco.com']
#recipients = ['pratemoh@cisco.com','anborde@cisco.com','vaikadam@cisco.com','amitgu3@cisco.com','rohdeshm@cisco.com','githorat@cisco.com','satsable@cisco.com','avngupta@cisco.com','madhurpa@cisco.com','rusahoo@cisco.com','sabselva@cisco.com','akadwive@cisco.com','neepande@cisco.com']


msg = MIMEMultipart('alternative')
msg['Subject'] = 'SMI/CNDP Version Report'
msg['From'] = ','.join(me)
msg['To'] = ', '.join(recipients)
html_msg = MIMEText(final_html_page, 'html')
msg.attach(html_msg)

try:
    # SMTP server configuration
    with smtplib.SMTP('localhost') as s:
        s.sendmail(me, recipients, msg.as_string())
    print("Email sent successfully.")
except Exception as e:
    print(f"Failed to send email: {e}")
            
            

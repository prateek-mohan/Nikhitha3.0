import paramiko
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


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
username = "cloud-user"
password = "Csco@123"
command="helm list -n cee-cee"
input_file = 'input.txt'
header = f"{'Setup Name':<25} {'Setup IP':<20} {'CNDP Version':<15} {'SMF SMI Version':<40} {'UPF SMI Version':<40}"
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
html_start='<html lang="en">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>Document</title>\n</head>\n<body>\n</body>\n</html>\n<html>\n<head>\n<style>\ntable {border-collapse: collapse;}\nth, td { border: 1px solid black; padding: 8px;}\n</style>\n</head>\n<body>\n<table>\n<tr>\n<th>Setup Name</th>\n <th>Setup IP</th>\n<th>CNDP Version</th>\n<th>SMF SMI Version</th>\n<th>UPF SMI Version</th>\n</tr>\n'
html_end='\n</table>\n</body>\n</html>'
command2=' sudo cat /etc/smi/base-image-version'
smi_ver=[]
for set_i in range(len(setup_list)):
    hostname = setup_list[set_i][-1]
    setup_name = setup_list[set_i][0]
    setup_ip = setup_list[set_i][1]

    try:
        ssh_client = ssh_connect(hostname, username, password)

        # Execute helm list command
        output, error = execute_command(ssh_client, command)

        if setup_name == "Gamma":
            out2, err2 = execute_command(ssh_client, "sudo cat /etc/smi/base-image-version")
        else:
            out2, err2 = execute_command(ssh_client, command2)

        # Process SMI Versions
        smi_version = ""
        for line in out2.split("\n"):
            if "SMI_BASE_IMAGE_BUILD_FULL_VERSION" in line:
                smi_version = line.split("=")[1].strip()
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
        cndp_version = cee_d['APP VERSION'][0] if 'APP VERSION' in cee_d else "N/A"
        if setup_name == "Watson":
            watson_smi_version = smi_version
        if setup_name == "Castor,Pollux":
            castor_pollux_smi_version = smi_version

        if setup_name == "Gamma":
            smf_version = watson_smi_version or "N/A"
            upf_version = watson_smi_version or "N/A"
        else:
            smf_version = smi_version
            upf_version = smi_version
        temp_row = f"{setup_name:<25} {setup_ip:<20} {cndp_version:<15} {smi_version:<40} {smi_version:<40}"
        print(temp_row)
        row.append(temp_row)

        # Add Row to HTML Table
        htmlpage_ls.append(f"<tr><td>{setup_name}</td><td>{setup_ip}</td><td>{cndp_version}</td><td>{smi_version}</td><td>{smi_version}</td></tr>")
    except Exception as e:
        print(f"Error processing setup {setup_name} ({setup_ip}): {e}")
    finally:
        ssh_client.close()
        

    ssh_client.close()

final_html_page=html_start+"\n".join(htmlpage_ls)+html_end

message="\n".join(row)
me = ['pratemoh@cisco.com']
recipients = ['pratemoh@cisco.com' ,  'anborde@cisco.com','vaikadam@cisco.com','amitgu3@cisco.com','rohdeshm@cisco.com','githorat@cisco.com','satsable@cisco.com','avngupta@cisco.com','madhurpa@cisco.com','rusahoo@cisco.com','sandetha@cisco.com','akadwive@cisco.com','neepande@cisco.com']

msg = MIMEMultipart('alternative')
msg['Subject'] = 'SMI/CNDP Version Report'
msg['From'] = ','.join(me)
msg['To'] = ', '.join(recipients)
html_msg=MIMEText(final_html_page, 'html')
#msg.attach(MIMEText(message, 'plain'))
msg.attach(html_msg)
try:
    # SMTP server configuration
    s = smtplib.SMTP('localhost')
    s.sendmail(me, recipients, msg.as_string())
    s.quit()
    print("Email sent successfully.")

except Exception as e:
    print(f"Failed to send email: {e}")
s = smtplib.SMTP('localhost')

#s.sendmail(me, recipients, msg.as_string())
s.quit()


                                                      


                                                      

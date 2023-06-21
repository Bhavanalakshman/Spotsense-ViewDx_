import os
import subprocess
output = subprocess.check_output(['sudo','iwlist', 'wlan0','scan'])
output_str = output.decode('utf-8')
output_lines = output_str.split('\n')
networks = []
for line in output_lines:
    if 'ESSID' in line:
        network = line.split(':')[1].strip().strip('"')
        networks.append(network)
print(networks)
# interface = "wlan0"
# name = "Airtel_Zerotouch"
# password = "Airtel@123"
# os.system('iwconfig ' + interface +' essid '+ name + ' key ' +password)
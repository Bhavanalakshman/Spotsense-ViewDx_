# Get list of Wifis
import subprocess

"""
* RUN sudo nmcli dev wifi rescan BEFORE CHANGING WIFI
* 
* Check Internet Connection
* import requests
* requests.get('ANY_HOST_URL').status_code # returns 200, if connected
"""

def execute(cmd):
	popen = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, universal_newlines=True)
	response = [line for line in iter(popen.stdout.readline, "")]
	popen.stdout.close()
	return_code = popen.wait()
	if return_code:
		raise subprocess.CalledProcessError(return_code, cmd)
	return response

wifi_list = []

for line in execute("sudo nmcli dev wifi")[1:]:
	single = line.split()
        start_index = single.index('*')+1 if '*' in single else 0
        end_index = single.index('Infra')

        wifi_list.append(' '.join(single[start_index:end_index]))

print(wifi_list)
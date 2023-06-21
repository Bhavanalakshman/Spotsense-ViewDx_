from utils.sub_process import run_cmd

def ssid_list():
  # RESCAN FOR WIFI SSID'S
  run_cmd("sudo nmcli dev wifi rescan")
  list = run_cmd("nmcli dev wifi")
  wifi_list = []
  print("[WIFI] CHECKING AVAILABLE WIFI SSID'S")

  for line in list[1:]: # SKIP THE HEADINGS
    single_line = line.split()
    si = single_line.index('*') + 1 if '*' == single_line[0] else 0
    ei = single_line.index('Infra')
    wifi_list.append(' '.join(single_line[si:ei]))

  return wifi_list

def connect_to_ssid(ssid, key):
  add_connection = run_cmd("sudo nmcli con add con-name " + ssid + " ifname wlan0 type wifi ssid " + ssid)[0]
  print("[WIFI] UUID", add_connection[add_connection.index('(')+1 : add_connection.index(')')])
  
  connect = run_cmd("sudo nmcli dev wifi connect " + ssid + " password " + key)[0]
  if('Error' in connect):
    print("[WIFI] INCORRECT PASSWORD")
    return False
  else:
    print("[WIFI] WIFI CONNECTED")
    return True

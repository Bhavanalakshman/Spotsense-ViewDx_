import subprocess

def run_cmd(cmd):
  popen = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, universal_newlines=True)
  response = [line.replace('\n', '') for line in iter(popen.stdout.readline, "")] # REMOVE \N IN EVERY STD.OUTPUT.LINE
  popen.stdout.close()
  return_code = popen.wait()
  return response

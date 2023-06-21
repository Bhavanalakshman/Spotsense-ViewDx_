from utils.sub_process import run_cmd

def check_for_updates():
	print("[UPDATER] CHECKING FOR UPDATES")
	try:
		run_cmd(cmd="git fetch")
		status = run_cmd(cmd="git status")

		if "up-to-date" in status[1]:
			print("[UPDATER] NO UPDATES AVAILABLE")
			return False
		elif "behind" in status[1]:
			print("[UPDATER] UPDATE IS AVAILABLE")
			return True
		elif "ahead" in status[1]:
			print("[UPDATER] YOU ARE IN DEVELOPMENT MODE")
			return False
		elif "No commits" in status[2]:
			print("[UPDATER] YOU ARE IN DEVELOPMENT MODE w/ 0 COMMITS")
			return False
		else:
			print("[UPDATER] REPO NOT RECOGNISED")
			return False
	except:
		print("[UPDATER] SOME ERROR OCCURED")
		return False

def do_update():
	res = run_cmd(cmd="git pull")
	version = run_cmd(cmd="git log -1 --format=%s")
	print(version)
	# PENDING > Push version to DynamoDB using boto3. 

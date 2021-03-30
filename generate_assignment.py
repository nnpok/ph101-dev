import argparse, fileinput
import sys, subprocess, shutil
import re, os, json
from os import listdir
from os.path import isfile, join

def replace_in_file(fpath, match_key, new_str):
	""" Given an input file at `fpath`, replace all usages of
	{{replace:`match_key`}} with `new_str`. """
	with fileinput.FileInput(fpath, inplace=True) as file:
		for line in file:
			print(line.replace("{{replace:" + match_key + "}}", new_str), end='')

def delete_in_file(fpath, match_str):
	""" Given an input file at `fpath`, remove all lines that have `match_str` in them."""
	with fileinput.FileInput(fpath, inplace=True) as file:
		for line in file:
			if match_str not in line:
				print(line, end='')

################
# Args + setup #
################
parser = argparse.ArgumentParser(description='Parse args')
parser.add_argument('--name', metavar='n', type=str,
					help='Name of assignment (e.g. hw5, lab11)')
parser.add_argument('--prog-id', metavar='p', type=int, 
	help="Gradescope programming assignment ID (6 digits")
parser.add_argument('--frq-id', metavar='f', type=int, 
	help="Gradescope FRQ assignment ID (6 digits")
parser.add_argument("--copy", action="store_true", help='Special command to copy files from old directory')
args = parser.parse_args()

ASST_NAME = args.name.lower()
try:
	for asst_label in ("hw", "lab"):
		if asst_label in ASST_NAME:
			ASST_TYPE, ASST_NUM = asst_label, int(ASST_NAME[len(asst_label):])		
except Exception as e:
	print("!!!> Error in parsing args:", e)
	sys.exit(1)

print(f"===> Generating files for {ASST_TYPE.upper()} {ASST_NUM}")

# Copy files over from old directory 
if args.copy:
	ASST_DIR = os.path.join(ASST_TYPE + "_old")
	AG_DIR = os.path.join(ASST_DIR, ASST_TYPE + "-ag", ASST_NAME)
	STUDENT_DIR = os.path.join(ASST_DIR, ASST_TYPE + "-student", ASST_NAME)
	SOL_DIR = os.path.join(ASST_DIR, ASST_TYPE + "-sol", ASST_NAME)

	try:
		new_path = os.path.join(ASST_TYPE, ASST_NAME)
		os.makedirs(new_path)
	except FileExistsError:
		pass

	# Files to copy over
	solution_file = os.path.join(SOL_DIR, ASST_NAME + "-sol.Rmd")
	hidden_tests_file = os.path.join(AG_DIR, "setup", ASST_NAME + ".RAGS.R")
	public_tests_file = os.path.join(STUDENT_DIR, "setup", ASST_NAME + ".RAGS.R")
	install_packages_file = os.path.join(AG_DIR, "install_packages.R")

	shutil.copy(solution_file, os.path.join(new_path, ASST_NAME + "-sol.Rmd"))
	shutil.copy(hidden_tests_file, os.path.join(new_path, ASST_NAME + ".RAGS-hidden.R"))
	shutil.copy(public_tests_file, os.path.join(new_path, ASST_NAME + ".RAGS-public.R"))
	shutil.copy(install_packages_file, new_path)
	print("===> Successfully copied files from old directory.")

# Create directories
ASST_DIR = os.path.join(ASST_TYPE, ASST_NAME)
AG_DIR = os.path.join(ASST_DIR, "autograder")
STUDENT_DIR = os.path.join(ASST_DIR, "student")
COMMON_DIR = os.path.join(ASST_TYPE, "common")


try:
	os.makedirs(ASST_DIR)
except FileExistsError:
	pass

for folder in (AG_DIR, STUDENT_DIR):
	try:
		shutil.rmtree(folder)
	except FileNotFoundError:
		pass
	try:
		os.makedirs(os.path.join(folder, "setup"))
	except FileExistsError:
		pass
		
try:
  os.makedirs(os.path.join(STUDENT_DIR, "src"))
except FileExistsError:
  pass

###################
# Copy over files #
###################

# Remove solutions from solutions file
SOL_PATH = os.path.join(ASST_DIR, f"{ASST_NAME}-sol.Rmd")
subprocess.check_call(["bash", "remove_solution.sh", SOL_PATH])

# source paths for files included in autograder/
AUTOGRADER_FILES = \
	[os.path.join(COMMON_DIR, f) for f in ("autograde.R", "run_autograder", "setup.sh", "setup/autograder_setup.R", "install_rags_packages.R")] + \
	[os.path.join(ASST_DIR, f) for f in listdir(ASST_DIR) if isfile(join(ASST_DIR, f)) and 'public' not in f] + \
	[os.path.join(ASST_DIR, f"{ASST_NAME}.RAGS-hidden.R")] 
	# [os.path.join(ASST_DIR, f) for f in ("install_packages.R", f"{ASST_NAME}.RAGS-hidden.R")] 
	

# source path for files included in student/
STUDENT_FILES = \
	[os.path.join(COMMON_DIR, f) for f in ("turn_in.py", "setup/autograder_setup.R", "src/NULL")] + \
	[os.path.join(ASST_DIR, f) for f in listdir(ASST_DIR) if isfile(join(ASST_DIR, f)) and '-sol' not in f and 'public' not in f] + \
	[os.path.join(ASST_DIR, f"{ASST_NAME}.RAGS-hidden.R")] 
	#[os.path.join(ASST_DIR, f) for f in (ASST_NAME + ".Rmd", f"{ASST_NAME}.RAGS-public.R")]
	

# name of file to be renamed -> new file name (without base paths)
RENAME_MAPPING = {
	f"{ASST_NAME}.RAGS-hidden.R": f"setup/{ASST_NAME}.RAGS.R",
#f"{ASST_NAME}.RAGS-public.R": f"setup/{ASST_NAME}.RAGS.R",
}

# Copy template files from common directories
for file_list, dst_dir in [(AUTOGRADER_FILES, AG_DIR), (STUDENT_FILES, STUDENT_DIR)]:
	for src in file_list:
		path_prefix, fname = os.path.split(src)
		if "setup" in path_prefix:
			fname = "setup/" + fname
		elif "src" in path_prefix:
		  fname = "src/" + fname
		new_name = RENAME_MAPPING.get(fname, fname) # get new name from RENAME_MAPPING, if it exists
		dst = os.path.join(dst_dir, new_name)
		try:
			copied_path = shutil.copy(src, dst)
		except Exception as e:
			print(e)
			print(src, dst)

print("===> Successfully copied files.")

############################
# Special files processing #
############################

# Delete blanked assignment file from ASST_DIR (already copied to student/)
os.remove(os.path.join(ASST_DIR, ASST_NAME + ".Rmd"))

# run_autograder.sh: Insert ASST_NAME 
run_autograder_path = os.path.join(AG_DIR, "run_autograder")
replace_in_file(run_autograder_path, "asst_name", ASST_NAME)

print("===> Successfully completed special files processing.")

######################
# Assignment testing #
######################
# Make sure autograder functions as expected
# Also extract info such as total number of problems, FRQ questions to extract, etc.
shutil.copy(SOL_PATH, os.path.join(AG_DIR, ASST_NAME + ".Rmd")) # Copy solutions file as "submission" to grade
try:
	subprocess.check_call(["bash", "run_autograder"], cwd=AG_DIR) # Run autograder
except subprocess.CalledProcessError:
	print("!!!> ERROR: Could not run autograder on solutions file.")
	print("   Check autograder/NUL output for more info.")
	sys.exit(1)

# results below gets filled as a list of dicts, containing a dict for every autograded question.
# each dict is of the form: {'score': 1, 'max_score': 1, 'name': 'Problem 2', 'number': '2'}
# e.g. results = [
# 	{'score': 1, 'max_score': 1, 'name': 'Problem 1', 'number': '1'}, 
# 	{'score': 1, 'max_score': 1, 'name': 'Problem 2', 'number': '2'}]
results_path = os.path.join(AG_DIR, "results", "results.json")
try:
	with open(results_path) as json_file:
		results = json.load(json_file)
		results, NUM_PROBLEMS = results["tests"], results["num_problems"]

	# Now remove the temp num_problem attribute placed in results.json...
	delete_in_file(results_path, "num_problems")
	# ...and also the line in autograde.R that added it.
	autograde_path = os.path.join(AG_DIR, "autograde.R")
	delete_in_file(autograde_path, "num_problems")

except Exception as e:
	print("!!!> Error in parsing results.json")
	print(e)
	sys.exit(1)

autograded_qs = set()
not_full_credit = set()
score, total = 0, 0
for prob in results:
	autograded_qs.add(int(prob["number"]))
	score += prob["score"]
	total += prob["max_score"]
	if prob["score"] != prob["max_score"]:
		not_full_credit.add(int(prob["number"]))

frqs = set(list(range(1, NUM_PROBLEMS + 1))) - autograded_qs
FRQ_NUMS = sorted(list(frqs))
autograded_qs = sorted(list(autograded_qs))

# Sanity checks on autograder results
if len(autograded_qs) + len(FRQ_NUMS) != NUM_PROBLEMS:
	print("!!!> ERROR: Total # of problems does not equal number of autograded + FRQ questions.")
	print(f"   Autograded Question #s (total: {len(autograded_qs)}): {autograded_qs}")
	print(f"   Free-Response Question #s (total: {len(FRQ_NUMS)}): {FRQ_NUMS}")
	print(f"   Total number of questions: {NUM_PROBLEMS}")
	sys.exit(1)

if score != total:
	print("!!!> ERROR: Solutions did not get full score on autograded questions.")
	print(f"   Score: {score} / {total}")
	print(f"   Questions that did not get full credit: {sorted(list(not_full_credit))}")
	sys.exit(1)

print("===> Successfully verified autograder on solutions.")
print("===> Parsed results:")
print(f"   FRQs to extract: {FRQ_NUMS}")


##################
# Backfill files #
##################

# turn_in.py: Replace Gradescope assignment ID if provided
turn_in_path = os.path.join(STUDENT_DIR, "turn_in.py")
for gs_id, match_key, id_type in ((args.prog_id, "prog_id", "programming"), (args.frq_id, "frq_id", "FRQ")):
	if id_type == "FRQ" and gs_id == -1:
		if len(FRQ_NUMS) > 0:
			print("!!!> ERROR: FRQ Gradescope assignment disabled, but at least one FRQ question detected.")
			sys.exit(1)
		print("===> FRQ Gradescope assignment disabled.")
		delete_in_file(turn_in_path, "FRQ_ASSIGNMENT_ID")
	elif id_type == "FRQ" and len(FRQ_NUMS) == 0:
		print("!!!> WARNING: Detected no FRQ questions to extract. Assuming there is no FRQ portion. ")
		delete_in_file(turn_in_path, "FRQ_ASSIGNMENT_ID")
	elif gs_id:
		assert len(str(gs_id)) == 6, f"Gradescope assignment ID should be 6 digits (value: {gs_id})"
		replace_in_file(turn_in_path, match_key, str(gs_id))
	else:
		print(f"===> WARNING: Gradescope {id_type} assignment ID was not provided; remember to add it later.")

replace_in_file(turn_in_path, "asst_name", ASST_NAME + ".Rmd")
replace_in_file(turn_in_path, "frq_nums", str(FRQ_NUMS))

if os.path.exists("LOG"):
  os.remove("LOG")

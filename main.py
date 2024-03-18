#!/usr/bin/env python3
#     _____ __                           __           
#    / __(_) /__        _________  _____/ /____  _____
#   / /_/ / / _ \______/ ___/ __ \/ ___/ __/ _ \/ ___/
#  / __/ / /  __/_____(__  ) /_/ / /  / /_/  __/ /    
# /_/ /_/_/\___/     /____/\____/_/   \__/\___/_/     
#                                                     
# https://github.com/PepeBigotes/file-sorter


def try_input(msg) -> str:
    try: x = input(msg)
    except KeyboardInterrupt: print("\nKeyboardInterrupt"); exit()
    return x

import os

try:
	try: import yaml
	except ImportError:
		print("[!] No YAML installed idiot")
		try_input("  Press ENTER to install the dependencies (or CTRL+C to exit)")
		os.system('pip3 install -r requirements.txt')
		try: import yaml
		except ImportError: print("\n[!] The dependencies couldn't be installed"); exit(1)
		try_input("\n  Dependencies installed, press ENTER to continue")
except KeyboardInterrupt: print("\nKeyboardInterrupt"); exit()

from argparse import ArgumentParser
import shutil
import re


# FUNCS
def check_file(x): return os.path.isfile(x)
def check_dir(x): return os.path.isdir(x)
def check_any(x): return os.path.exists(x)
def new_file(x):
    if not check_file(x): file = open(x, 'a'); file.close()
def new_dir(x):
    if not check_dir(x): os.makedirs(x)

def transfer(x, y):  # CAUTION: OVERWRITES
	if TRANSFER_MODE == 'copy':
		if check_dir(x): shutil.copytree(x, y)
		else: shutil.copy2(x,y)
	if TRANSFER_MODE == 'move': shutil.move(x, y)


# ARGPARSE
argp = ArgumentParser(prog='file-sorter',
	description='Sort your messy files',
	#epilog='epilog',
 	)
argp.add_argument('-c', '--config',
	default='configs/default-config.yml',
	help="Path to a custom config YML file",
 	)
argp.add_argument('-s', '--src',
    default='.',
	help="Source path with your messy files",
    )
argp.add_argument('-d', '--dst',
    default=None,
	help="Destination path where to put the sorted files",
    )
argp.add_argument('--debug',
    action="store_true",
	help="Print additional debug messages",
    )
args = argp.parse_args()
DEBUG = args.debug
if DEBUG: print(f"[debug] Args: {args}")

if not args.dst: args.dst = args.src



# YML CONFIG
TRANSFER_MODES = ('move', 'copy')
SORT_MODES = ('normal', 'artist')

with open(args.config, 'r') as file: CONFIG = yaml.safe_load(file)
if DEBUG: print(f"[debug] Config: {CONFIG}")
invalid = False

if not 'directories' in CONFIG:
    invalid = True
    print(f"[!] '{args.config}' lacks the required 'directories' dictionary")
if not 'transfer-mode' in CONFIG:
    invalid = True
    print(f"[!] '{args.config}' lacks the required 'transfer-mode' variable")
if not CONFIG['transfer-mode'] in TRANSFER_MODES:
	invalid = True
	print(f"[!] Invalid transfer-mode in '{args.config}'")
	print(f" └─ Expected {TRANSFER_MODES} got {CONFIG['transfer-mode']}")
if not CONFIG['sort-mode'] in SORT_MODES:
	invalid = True
	print(f"[!] Invalid sort-mode in '{args.config}'")
	print(f" └─ Expected {SORT_MODES} got {CONFIG['sort-mode']}")
if invalid: exit(1)

SORT_MODE = CONFIG['sort-mode']
TRANSFER_MODE = CONFIG['transfer-mode']



# LIST OF SRC CONTENTS
LISTDIR = os.listdir(args.src)
if DEBUG: print(f"[debug] LISTDIR: {LISTDIR}")


# PREPARE 'regexs' (config directories) DICT
regexs = {}

if SORT_MODE == 'artist':
	SEP_CHAR = ' - '
	for i in LISTDIR:
		parts = i.split(SEP_CHAR)
		if len(parts) < 2: continue
		artist = parts[0]
		if not artist in regexs: regexs[r"^" + re.escape(artist + SEP_CHAR)] = artist
if SORT_MODE == 'normal':
	for i in CONFIG['directories']:
		regexs[CONFIG['directories'][re.compile(i).pattern]] = re.compile(i).pattern
if DEBUG: print(f"[debug] Regexs: {regexs}")



# MAIN SORT LOOP
print(f"[*] Sorting {args.src} -> {args.dst}")

all_ans = None

for i in LISTDIR:
	for regex in regexs:

		if re.search(regex, i):  # Matches RegEx
			dst = f"{args.dst}/{regexs[regex]}/{i}"
			src = f"{args.src}/{i}"
			new_dir(os.path.dirname(dst))
			is_ow = False

			if check_any(dst):  # Dst already exists
				if not all_ans:  # No 'All' option yet
					print(f"[?] The file or directory '{dst}' already exists")
					ans = None
					while not ans in ('', 'S', 'O', 'OA', 'SA'):
						ans = str.upper(try_input(" └─ [S] Skip, (O) Overwrite, (SA) Skip All, (OA) Overwrite All: "))
					if ans == 'SA': all_ans = 'S'; print("[*] Skipping all existing files from now on..."); continue
					if ans == 'OA': all_ans = 'O'; print("[*] Overwriting all existing files from now on..."); is_ow = True; pass
				else: ans = all_ans  # Has 'All' option

				if ans in ('', 'S'): print(f"[-] Skipping {src} ({dst} already exists)"); continue
				if ans == 'O': is_ow = True; pass

			transfer(src, dst)
			print(f"[+] {'(OW) ' if is_ow else ''}{src} -> {dst}")
			break

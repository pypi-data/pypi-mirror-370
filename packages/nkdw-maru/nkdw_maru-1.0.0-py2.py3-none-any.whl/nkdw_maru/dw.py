#!/usr/bin/env python3
import inquirer
from dwlib import *

while True:
    questions = [
        inquirer.List(
            "size",
            message="NK Declaritive Wrapper Menu",
            choices=["Upsync", "Downsync", "Backup", "Restore", "BinaryConfig", "FileConfig", "exit"],
        ),
    ]
    result = inquirer.prompt(questions)
    if result is None:
        print("Prompt cancelled. Exiting.")
        break
    a = result['size'].lower()
    if a == "upsync":
        sync()
    elif a == "downsync":
        dnf_install_from_conf()
        flatpak_install_from_config()
        dnf_prune()
        flatpak_prune()
        restore_files_from_config()
        restore_binaries_from_config()
    elif a == "backup":
        os.system(f"cp {CONFIG_FILE} {CONFIG_DIR}nkdw.yaml.old && echo done")
    elif a == "restore":
        a = input("Are you sure you want to restore the backup? (y/n): ").strip().lower()
        if a == "y":
            os.system(f"cp {CONFIG_DIR}nkdw.yaml.old {CONFIG_FILE} && echo restored")
        else:
            print("Restore cancelled.")
    elif a == "fileconfig":
        newsavebinaryconf()
    elif a == "binaryconfig":
        newsavefileconf()
    elif a == "exit":
        break
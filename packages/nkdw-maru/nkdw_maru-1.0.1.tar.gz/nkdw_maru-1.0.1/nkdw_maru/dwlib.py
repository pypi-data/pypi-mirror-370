#!/usr/bin/env python3
import os
import dnf
import yaml
from pathlib import Path
import re
import files
from subprocess import check_output, run
import base64

logs=True
CONFIG_DIR = "/home/maru/.config/nknk/"
CONFIG_FILE = "/home/maru/.config/nknk/nkdw.yaml"

#
# DOES NOT DOWNSYNC VERSIONS YET
# might not ever add that tbh, its not really important for things other that isolation

#todo
# make file moving use sudo if in root for yum.d repos
# finish pip backup
# from-source tracking somehow(longtermgoal)


import hashlib
def is_diff(a, b):
    if isinstance(a, str):
        a = a.encode('utf-8')
    if isinstance(b, str):
        b = b.encode('utf-8')
    return hashlib.md5(a).digest() != hashlib.md5(b).digest()


# =========================
# DNF PACKAGE FUNCTIONS
# =========================

def dnf_get_installed():
    base = dnf.Base()
    base.read_all_repos()
    base.fill_sack()
    installed_query = base.sack.query().installed()
    all_installed = {pkg.name: pkg for pkg in installed_query}
    packages = []
    for pkg in installed_query:
        resolved_deps = set()
        for require in pkg.requires:
            if require.name.startswith("rpmlib(") or require.name.startswith("config("):
                if logs:
                    print("Log: skipping system provides")
                continue
            providing_query = base.sack.query().installed().filter(provides=require.name)
            for provider in providing_query:
                resolved_deps.add(provider.name)
                if logs:
                    print(f"added {provider.name} to resolved deps")
        packages.append({
            "name": pkg.name,
            "version": pkg.evr,
            "repo": pkg.reponame or "unknown",
            "dependencies": sorted(resolved_deps)
        })
    return packages

def dnf_install_from_conf(config_path=CONFIG_FILE):
    import os
    with open(config_path, 'r') as f:
        data = yaml.safe_load(f)
    packages = data.get("dnf", [])
    all_deps = set()
    top_packages = []
    for pkg in packages:
        top_packages.append(pkg["name"])
        for dep in pkg.get("dependencies", []):
            all_deps.add(dep)
    dep_only = sorted(all_deps - set(top_packages))
    print("Installing dependencies (no top-level packages)...")
    if dep_only:
        os.system(f"sudo dnf install -y {' '.join(dep_only)}")
    else:
        print("No dependencies to install.")
    print("\nInstalling main packages (no dependency resolution)...")
    if top_packages:
        os.system(f"sudo dnf install -y --setopt=install_weak_deps=False --setopt=tsflags=nodocs {' '.join(top_packages)}")
    else:
        print("No top-level packages to install.")
    print("\nInstallation complete.")

def dnf_prune(config_path=CONFIG_FILE):
    with open(config_path, 'r') as f:
        data = yaml.safe_load(f)

    config_pkgs = {pkg['name'] for pkg in data.get("dnf", [])}
    
    base = dnf.Base()
    base.read_all_repos()
    base.fill_sack()
    installed_query = base.sack.query().installed()
    installed_pkgs = {pkg.name for pkg in installed_query}

    to_remove = installed_pkgs - config_pkgs

    if not to_remove:
        print("Nothing to prune. System matches the config.")
        return

    print(f"The following packages are NOT in the config and will be removed:\n{', '.join(sorted(to_remove))}")
    confirm = input("Continue? (y/N): ").strip().lower()
    if confirm == 'y':
        os.system(f"sudo dnf remove -y {' '.join(to_remove)}")
        print("Removed successfully")
    else:
        print("No changes made. System is out of sync with config.")

def dnf_install_pkg(pkg):
    os.system(f"sudo dnf in {pkg}")

def dnf_uninstall_pkg(pkg):
    os.system(f"sudo dnf rm {pkg}")

def update():
    os.system("sudo dnf update")

# =========================
# FLATPAK FUNCTIONS
# =========================

def get_installed_flatpaks():
    output = check_output(["flatpak", "list", "--app", "--columns=application"], text=True)
    flatpaks = [line.strip() for line in output.strip().splitlines() if line.strip()]
    return sorted(flatpaks)

def flatpak_install_from_config(config_path=CONFIG_FILE):
    import subprocess
    with open(config_path, 'r') as f:
        data = yaml.safe_load(f)
    flatpaks = [fp["name"] for fp in data.get("flatpak", [])]
    if not flatpaks:
        print("No flatpaks to install.")
        return
    print("Installing Flatpaks:")
    for fp in flatpaks:
        print(f"Installing {fp}...")
        subprocess.run(["flatpak", "install", "-y", "--noninteractive", "flathub", "--user", fp])

def flatpak_prune(config_path=CONFIG_FILE):
    with open(config_path, 'r') as f:
        data = yaml.safe_load(f)
    configured = {fp["name"] for fp in data.get("flatpak", [])}
    installed = set(get_installed_flatpaks())
    to_remove = sorted(installed - configured)
    if not to_remove:
        print("Nothing to prune. System matches the config.")
        return
    print("Flatpaks not in config and will be removed:\n", "\n".join(to_remove))
    confirm = input("Continue? [y/N]: ").lower().strip()
    if confirm == 'y':
        for fp in to_remove:
            run(["flatpak", "uninstall", "-y", fp])
    else:
        print("No changes made. System is out of sync with config.")

# =========================
# FILE BACKUP/CONFIG FUNCTIONS
# =========================

def write_multiline_yaml(file_path, data):
    class LiteralStr(str): pass

    def literal_str_representer(dumper, data):
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')

    yaml.add_representer(LiteralStr, literal_str_representer, Dumper=yaml.SafeDumper)

    return {file_path: LiteralStr(data)}

def newsavefileconf():
    os.system(f"nvim {CONFIG_DIR}mybinarys.txt")

def read_and_append_to_yaml():
    data = []
    for line in files.read(CONFIG_DIR + "myfiles.txt").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            file_content = files.read(line)
        except Exception as e:
            print(f"Warning: Could not read {line}: {e}")
            file_content = ""
        data.append(write_multiline_yaml(line, file_content))
    return data

def restore_files_from_config(config_path=CONFIG_FILE):
    with open(config_path, "r") as f:
        data = yaml.safe_load(f)
    files_section = data.get("files", [])
    for file_entry in files_section:
        for path, content in file_entry.items():
            try:
                current_content = files.read(path)
            except Exception:
                current_content = ""
            if is_diff(current_content, content):
                try:
                    print("Ensuring directory exists:", os.path.dirname(path))
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                    with open(path, "w") as out:
                        out.write(str(content))
                    print(f"Restored: {path}")
                except Exception as e:
                    print(f"Error while restoring file: {path} ({e})")
            else:
                print(f"Path {path}: is identical to current system state.")
                
# =========================
# BINARY BACKUP FUNCTIONS
# =========================

def read_and_append_to_binary_yaml():
    data = []
    for line in files.read(CONFIG_DIR + "mybinarys.txt").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            encoded = encode_file_base64(line)
        except Exception as e:
            print(f"Warning: Could not read {line}: {e}")
            encoded = ""
        data.append({line: encoded})
    return data
def newsavebinaryconf():
    os.system(f"nvim {CONFIG_DIR}mybinarys.txt")
def restore_binaries_from_config(config_path=CONFIG_FILE):
    with open(config_path, "r") as f:
        data = yaml.safe_load(f)
    binaries_section = data.get("binarys", [])
    for file_entry in binaries_section:
        for path, b64content in file_entry.items():
            print(f"Checking binary path: {path}")
            try:
                current_content = encode_file_base64(path)
            except Exception:
                current_content = ""
            if is_diff(current_content, b64content):
                if not b64content:
                    print(f"Warning: No content to restore for {path} (empty base64 string)")
                    continue
                try:
                    dir_path = os.path.dirname(path)
                    print(f"Ensuring directory exists: {dir_path}")
                    os.makedirs(dir_path, exist_ok=True)
                    try:
                        decode_file_base64(b64content, path)
                        print(f"Restored binary: {path}")
                    except Exception as decode_err:
                        print(f"Error decoding base64 for {path}: {decode_err}")
                except Exception as e:
                    print(f"Error while restoring binary file: {path} ({e})")
            else:
                print(f"Binary path {path}: is identical to current system state.")

# =========================
# PIP FUNCTIONS(WIP)
# =========================

def get_installed_pypackages():
    output = check_output("pip freeze", text=True)
    pips = [line.strip() for line in output.strip().splitlines() if line.strip()]
    return sorted(pips)
# =========================
# SYNC/DOWNSYNC FUNCTIONS
# =========================

def sync():
    packages = dnf_get_installed()
    flatpaks = get_installed_flatpaks()
    files_data = read_and_append_to_yaml()
    binary_data = read_and_append_to_binary_yaml()
    data = {
        "dnf": packages,
        "flatpak": [{"name": name} for name in flatpaks],
        "files": files_data,
        "binarys": binary_data
    }
    with open(CONFIG_FILE, "w") as f:
        yaml.safe_dump(data, f, sort_keys=False)
    print(f"Saved {len(packages)} DNF packages, {len(flatpaks)} Flatpaks, {len(binary_data)} binaries to {CONFIG_FILE}")

def encode_file_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")

def decode_file_base64(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(base64.b64decode(data))

def main():
    print("Don't execute me directly :3")
if __name__ == "__main__":
    main()
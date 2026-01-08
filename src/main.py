import os
import subprocess
import sys
import shutil
import time
import re
import hashlib
import json

# ==========================================
# DUNGEON RAMPAGE MOD ENGINE
# ==========================================

if getattr(sys, 'frozen', False):
    EXE_LOCATION = os.path.dirname(sys.executable)
    INTERNAL_RES_DIR = sys._MEIPASS
else:
    EXE_LOCATION = os.path.dirname(os.path.abspath(__file__))
    INTERNAL_RES_DIR = EXE_LOCATION

GAME_ROOT_DIR = os.path.dirname(EXE_LOCATION)

# --- PATHS ---
TOOLS_DIR = os.path.join(INTERNAL_RES_DIR, 'tools')
INJECT_DIR = os.path.join(INTERNAL_RES_DIR, 'inject') 

USER_MODS_DIR = os.path.join(GAME_ROOT_DIR, 'mods')
TARGET_SWF = os.path.join(GAME_ROOT_DIR, "DungeonBustersProject.swf")
BACKUP_SWF = os.path.join(GAME_ROOT_DIR, "DungeonBustersProject_Original.bak")
STATE_FILE = os.path.join(EXE_LOCATION, "mod_state.json")

JAVA_EXECUTABLE = os.path.join(TOOLS_DIR, 'java', 'bin', 'java.exe')
FFDEC_JAR = os.path.join(TOOLS_DIR, 'ffdec', 'ffdec.jar')

# --- HELPERS ---

def log(message):
    print(f"[{time.strftime('%H:%M:%S')}] {message}")

def normalize_path(path):
    return os.path.abspath(path).replace('\\', '/')

def calculate_file_md5(file_path):
    if not os.path.exists(file_path): return None
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except: return None

def calculate_mods_hash(mod_list):
    if not mod_list: return "no_mods"
    combined_hash = hashlib.md5()
    for _, file_path in sorted(mod_list, key=lambda x: x[1]):
        try:
            with open(file_path, "rb") as f:
                combined_hash.update(f.read())
        except: pass
    return combined_hash.hexdigest()

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except: pass
    return {}

def save_state(backup_hash, mods_hash):
    final_target_hash = calculate_file_md5(TARGET_SWF)
    state = {
        "backup_hash": backup_hash,
        "mods_hash": mods_hash,
        "target_hash": final_target_hash,
        "last_run": time.time()
    }
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def extract_class_name(as_file_path):
    try:
        with open(as_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        pkg_match = re.search(r'package\s+([\w\.]+)', content)
        pkg_name = pkg_match.group(1) if pkg_match else ""
        class_match = re.search(r'public\s+class\s+(\w+)', content)
        if not class_match: return None 
        class_name = class_match.group(1)
        return f"{pkg_name}.{class_name}" if pkg_name else class_name
    except: return None

def scan_directory_for_mods(directory_path):
    mod_list = []
    if not os.path.exists(directory_path):
        return mod_list
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.as'):
                full_path = normalize_path(os.path.join(root, file))
                class_name = extract_class_name(full_path)
                if class_name:
                    mod_list.append((class_name, full_path))
    return mod_list

def manage_game_files(last_state):
    if not os.path.exists(TARGET_SWF) and not os.path.exists(BACKUP_SWF):
        log(f"[!] Error: Game file not found: {TARGET_SWF}")
        return None

    if not os.path.exists(BACKUP_SWF):
        log("[-] First setup: Creating backup...")
        shutil.copyfile(TARGET_SWF, BACKUP_SWF)
        return calculate_file_md5(BACKUP_SWF)

    current_target_hash = calculate_file_md5(TARGET_SWF)
    last_known_target_hash = last_state.get("target_hash")

    if last_known_target_hash and current_target_hash != last_known_target_hash:
        log("[!] File change detected (Update/Edit). Updating backup...")
        try: os.remove(BACKUP_SWF)
        except: pass
        shutil.copyfile(TARGET_SWF, BACKUP_SWF)
        return calculate_file_md5(BACKUP_SWF)
    
    return calculate_file_md5(BACKUP_SWF)

# --- MAIN ---

def run_injector():
    # log("--- Dungeon Rampage Mod Engine ---")
    
    if not os.path.exists(JAVA_EXECUTABLE):
        log(f"[!] ERROR: Embedded Java runtime not found!")
        return

    all_mods_data = []
    all_mods_data.extend(scan_directory_for_mods(INJECT_DIR))
    all_mods_data.extend(scan_directory_for_mods(USER_MODS_DIR))

    current_mods_hash = calculate_mods_hash(all_mods_data)
    last_state = load_state()
    current_backup_hash = manage_game_files(last_state)
    
    if current_backup_hash is None: return

    files_are_same = (last_state.get("backup_hash") == current_backup_hash)
    mods_are_same = (last_state.get("mods_hash") == current_mods_hash)
    target_exists = os.path.exists(TARGET_SWF)

    if files_are_same and mods_are_same and target_exists:
        # System is up to date
        return 

    if not all_mods_data:
        log("[-] No mods detected. Restoring original file.")
        shutil.copyfile(BACKUP_SWF, TARGET_SWF)
        save_state(current_backup_hash, "no_mods")
        return

    log("[-] Patching SWF file...")
    
    startupinfo = None
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    command = [
        normalize_path(JAVA_EXECUTABLE),
        '-jar',
        normalize_path(FFDEC_JAR),
        '-replace',
        normalize_path(BACKUP_SWF),
        normalize_path(TARGET_SWF)
    ]
    
    for class_name, file_path in all_mods_data:
        command.append(class_name)
        command.append(file_path)

    try:
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            startupinfo=startupinfo
        )
        
        if process.returncode == 0:
            log("[+] MODIFICATION SUCCESSFUL!")
            save_state(current_backup_hash, current_mods_hash)
        else:
            log("[!] JPEXS Error!")
            print(process.stderr)
            shutil.copyfile(BACKUP_SWF, TARGET_SWF)
            log("[-] Original file restored.")

    except Exception as e:
        log(f"[!] Critical Error: {e}")

if __name__ == "__main__":
    run_injector()
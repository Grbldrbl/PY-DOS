import os

ROOT_DIR = "/storage/emulated/0/PyDOS"  # Change this to a safe place on your device

def in_root(path):
    abs_path = os.path.abspath(os.path.join(ROOT_DIR, path))
    if not abs_path.startswith(ROOT_DIR):
        raise Exception("Out of bounds!")
    return abs_path

def run_batch(filepath, shell):
    try:
        with open(filepath, "r") as f:
            lines = f.readlines()
        for line in lines:
            line = line.strip()
            if not line or line.upper().startswith("REM"):
                continue
            print(f"> {line}")
            shell(line, from_script=True)
    except Exception as e:
        print("Script error:", e)

def py_dos():
    cwd = ""
    def shell(cmd, from_script=False):
        nonlocal cwd
        abs_cwd = in_root(cwd)
        if cmd == "exit":
            if not from_script:
                exit()
        elif cmd.startswith("cd "):
            folder = cmd[3:].strip()
            try:
                new_dir = in_root(os.path.join(cwd, folder))
                if os.path.isdir(new_dir):
                    cwd = os.path.relpath(new_dir, ROOT_DIR)
                    if cwd == ".":
                        cwd = ""
                else:
                    print("Directory not found!")
            except Exception:
                print("Invalid path!")
        elif cmd == "dir":
            for entry in sorted(os.listdir(abs_cwd)):
                entry_path = os.path.join(abs_cwd, entry)
                print(f"<DIR> {entry}" if os.path.isdir(entry_path) else f"     {entry}")
        elif cmd.startswith("mkdir "):
            folder = cmd[6:].strip()
            try:
                os.mkdir(in_root(os.path.join(cwd, folder)))
                print(f"Directory '{folder}' created.")
            except FileExistsError:
                print("Directory exists.")
            except Exception as e:
                print("Error creating directory:", e)
        elif cmd.startswith("type "):
            filename = cmd[5:].strip()
            file_path = in_root(os.path.join(cwd, filename))
            if os.path.isfile(file_path):
                with open(file_path, "r") as f:
                    print(f.read())
            else:
                print("File not found.")
        elif cmd.startswith("write "):
            # write foo.txt Hello World!
            parts = cmd.split(maxsplit=2)
            if len(parts) < 3:
                print("Usage: write filename content")
            else:
                filename = parts[1]
                content = parts[2]
                with open(in_root(os.path.join(cwd, filename)), "w") as f:
                    f.write(content + "\n")
                print(f"File '{filename}' written.")
        elif cmd.startswith("edit "):
            filename = cmd[5:].strip()
            file_path = in_root(os.path.join(cwd, filename))
            # Read existing lines if present
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    contents = f.read().splitlines()
                print(f"--- Existing lines in {filename} ---")
                for line in contents:
                    print(line)
                print("--- Add or edit lines below. Enter .save to finish. ---")
            else:
                contents = []
                print(f"Creating new batch/script file {filename}. Enter .save to finish.")
            # Line editor loop
            while True:
                line = input()
                if line.strip() == ".save":
                    break
                contents.append(line)
            with open(file_path, "w") as f:
                f.write("\n".join(contents))
            print(f"{filename} saved.")
        elif cmd.startswith("run "):
            filename = cmd[4:].strip()
            file_path = in_root(os.path.join(cwd, filename))
            if os.path.isfile(file_path):
                if filename.lower().endswith(".py"):
                    print(f"RUNNING PYTHON PROGRAM: {filename}\n---")
                    with open(file_path, "r") as f:
                        code = f.read()
                    try:
                        exec(code, {})
                    except Exception as e:
                        print("Program crashed:", e)
                    print("--- End program ---")
                elif filename.lower().endswith((".pyatch", ".bat", ".txt")):
                    print(f"RUNNING BATCH SCRIPT: {filename}\n---")
                    run_batch(file_path, shell)
                    print("--- End script ---")
                else:
                    print("Unknown file type for run.")
            else:
                print("File not found.")
        elif cmd.upper().startswith("REM "):
            pass  # Comment line, do nothing
        else:
            if not from_script:
                print("Unknown command.")

    os.makedirs(ROOT_DIR, exist_ok=True)
    print("Welcome to PY-DOS! Type 'help' for commands.")
    while True:
        abs_cwd = in_root(cwd)
        prompt = os.path.relpath(abs_cwd, ROOT_DIR)
        prompt = "" if prompt == "." else prompt
        cmd = input(f"C:\\{prompt.replace(os.sep, '\\')}> ").strip()
        if cmd == "help":
            print("""Supported commands:
dir            - List files/folders
cd <folder>    - Change directory
cd ..          - Up one level
mkdir <folder> - Create directory
type <file>    - View file contents
write <f> <c>  - Write content c to file f
edit <file>    - Line by line batch/text editor
run <file>     - Run .py (Python) or .pyatch/.bat/.txt batch file
REM <comment>  - Batch/script comment
exit           - Quit the shell""")
            continue
        shell(cmd)

if __name__ == "__main__":
    py_dos()

import os
import sys
import signal
import time
import datetime
import subprocess
import psutil

PID = os.getpid()


def get_real_path(directory, raw_filename):
    if os.path.isabs(raw_filename):
        file_path = raw_filename
    else:
        file_path = os.path.join(directory, raw_filename)
    if os.path.exists(file_path):
        return os.path.realpath(file_path)
    return raw_filename


def get_std_cmdline(process):
    try:
        cwd = process.cwd()
        cmdline = [get_real_path(cwd, i) for i in process.cmdline()]
        return cmdline
    except Exception:
        return None


def kill_process_tree(pid, sig_n=signal.SIGKILL):
    if pid == PID:
        return
    sig = signal.SIGTERM
    if sig_n == 9:
        sig = signal.SIGKILL
    pid_list = [pid]
    while True:
        if len(pid_list) == 0:
            break
        tmp_pid = pid_list.pop(0)
        if not psutil.pid_exists(tmp_pid):
            continue
        parent = psutil.Process(tmp_pid)
        if parent is not None:
            children = parent.children(recursive=False)
            if children is not None:
                for child in children:
                    pid_list.append(child.pid)
            try:
                cmdline = " ".join(parent.cmdline())
                print(f"kill {parent.pid} {cmdline}")
                parent.send_signal(sig)
            except psutil.NoSuchProcess:
                continue


def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def RUN():
    if len(sys.argv) < 2:
        print("usage RUN [script_file]")
        return
    if len(sys.argv) >= 3:
        args = " ".join(sys.argv[2:])
    else:
        args = ""
    script_file = os.path.realpath(os.path.abspath(sys.argv[1]))
    path, name = os.path.split(script_file)
    log_path = os.path.join(path, "log")
    log_file = os.path.join(path, "log", f"{name}.log")
    mkdir(log_path)
    now = datetime.datetime.now()
    if name.endswith(".py"):
        cmd = f"nohup python3 {script_file} {args} &"
    elif name.endswith(".sh"):
        cmd = f"nohup bash {script_file} {args} &"
    else:
        cmd = f"nohup {script_file} {args} &"

    with open(log_file, "a") as f:
        f.write(f"{now} | start run {name}\n")
    subprocess.Popen(
        cmd,
        cwd=path,
        stdout=open(log_file, "a"),
        stderr=open(log_file, "a"),
        shell=True,
    )


def KILL():
    if len(sys.argv) < 2 or "-h" in sys.argv:
        print("usage: KILL [script_file]")
        return
    signal_num = 9
    use_key_word = True
    if "-f" in sys.argv:
        use_key_word = False
    argv = [i for i in sys.argv[1:] if i != "-f"]
    keys = [i for i in argv if i[0] == "-"]
    for arg in argv:
        if arg[0] == "-":
            signal_num = int(arg[1:])
            continue
        key = arg
        break
    if not use_key_word:
        key = os.path.realpath(os.path.abspath(key))
    for process in psutil.process_iter(["pid", "name", "cmdline"]):
        cmdll = get_std_cmdline(process)
        if cmdll is None:
            continue
        cmdline = " ".join(cmdll)
        if "KILL" in cmdline:
            continue
        if key in cmdline:
            pid = process.info["pid"]
            kill_process_tree(pid, signal_num)


def RESTART():
    if len(sys.argv) < 2 or "-h" in sys.argv:
        print("usage: RESTART [script_file]")
        return
    signal_num = 15
    key = sys.argv[-1]
    key = os.path.realpath(os.path.abspath(key))
    if not os.path.exists(key):
        print(f"{key} is not exists")
        return

    for process in psutil.process_iter(["pid", "name", "cmdline"]):
        cmdll = get_std_cmdline(process)
        if cmdll is None:
            continue
        cmdline = " ".join(cmdll)
        if "RESTART" in cmdline:
            continue
        if key in cmdline:
            pid = process.info["pid"]
            if pid == PID:
                continue
            for i in range(30):
                if psutil.pid_exists(pid):
                    kill_process_tree(pid, signal_num)
                    time.sleep(1)
                else:
                    print(f"kill {key} success!")
                    break
            if psutil.pid_exists(pid):
                kill_process_tree(pid, 9)
    TASK()


def today():
    return datetime.datetime.now().strftime("%Y%m%d")


def TASK():
    if len(sys.argv) < 2 or "-h" in sys.argv:
        print("usage TASK [script_file]")
        return
    if "--daemon" not in sys.argv:
        ll = " ".join(i for i in sys.argv[1:]) + " --daemon"
        os.system(f"TASK {ll} &")
        return
    available_argv = [i for i in sys.argv[1:] if i[0] != "-"]
    script_file = available_argv[0]
    no_log = "-nolog" in sys.argv or "-q" in sys.argv
    now = datetime.datetime.now()
    if not os.path.exists(script_file):
        print(f"{now} ERROR | script {script_file} is not exists")
        return
    script_file = os.path.realpath(os.path.abspath(sys.argv[1]))
    date = today()
    mkdir(os.path.expanduser("~/.cache/task_log/"))
    task_log = os.path.expanduser(f"~/.cache/task_log/out.{date}")
    for process in psutil.process_iter(["pid", "name", "cmdline"]):
        cmdline = get_std_cmdline(process)
        if cmdline is None or len(cmdline) == 0:
            continue
        if process.info["pid"] == PID:
            continue
        exe_name = cmdline[0]
        norm_exe = any(i in exe_name for i in ["bash", "python3"])
        if script_file in cmdline and norm_exe and "bash -c TASK" not in cmdline:
            with open(task_log, "a") as f:
                f.write(f"{now} | {script_file} is running {cmdline}\n")
            s = " ".join(cmdline)
            create_time = process.create_time()
            readable_time = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(create_time)
            )
            print(f"{now} INFO | already running, ps:\n {readable_time} {s}\n")
            return
    path, name = os.path.split(script_file)
    if script_file.endswith(".py"):
        cmd = ["python3", script_file]
    elif script_file.endswith(".sh"):
        cmd = ["bash", script_file]
    else:
        cmd = [script_file]
    if len(sys.argv) >= 3:
        cmd += [i for i in sys.argv[2:] if i != "--daemon"]
    with open(task_log, "a") as f:
        f.write("{} | start run {}\n".format(datetime.datetime.now(), script_file))
        f.write("{} | cmd: {}\n".format(datetime.datetime.now(), " ".join(cmd)))
    if no_log:
        cmd += [">>", "/dev/null", "2>&1"]
    else:
        log_path = os.path.join(path, "log")
        mkdir(log_path)
        log_file = os.path.join(log_path, f"{name}.log")
        cmd += [">>", log_file, "2>&1"]
    one_line_cmd = "nohup {} &".format(" ".join(cmd))
    os.system(one_line_cmd)
    print("start:", one_line_cmd, "\n")
    return


def DELETE():
    if len(sys.argv) < 2 or "-h" in sys.argv:
        print("usage DELETE [file]")
        return
    file = sys.argv[1]
    os.system(f"nohup shred -u -n 5 -z {file} >> /dev/null &")

# bpcode/startnas.py
import os
import sys
import subprocess

def main():
    project = os.path.join(os.path.dirname(__file__), 'nas.py')
    # 定义子进程参数
    popen_kwargs = {
        'args': [sys.executable, project],
        'cwd': os.path.dirname(__file__),
        'stdout': subprocess.DEVNULL,
        'stderr': subprocess.DEVNULL,
    }
    
    # 根据操作系统设置不同参数
    if os.name == 'nt':  # Windows 系统
        # 添加不显示窗口的标志
        popen_kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
    else:  # 非 Windows 系统（保持原有的进程组设置）
        popen_kwargs['preexec_fn'] = os.setpgrp
    
    subprocess.Popen(** popen_kwargs)

if __name__ == "__main__":
    main()

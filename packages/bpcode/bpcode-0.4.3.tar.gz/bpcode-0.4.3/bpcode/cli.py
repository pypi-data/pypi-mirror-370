# bpcode/cli.py
import os
import sys
import subprocess

def main():
    project_dir = os.path.join(os.path.dirname(__file__), 'bpserver')
    manage_py = os.path.join(project_dir, 'manage.py')

    # 先收集静态文件
    try:
        import django
        sys.path.insert(0, project_dir)
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bpserver.settings")
        django.setup()

        from django.core.management import call_command
        call_command('collectstatic', interactive=False, clear=True)
        print("[bpserver] Static files collected.")
    except Exception as e:
        print(f"[bpserver] collectstatic failed: {e}")
    subprocess.Popen(
        [sys.executable, manage_py, 'runserver', '0.0.0.0:8888'],
        cwd=project_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        preexec_fn=os.setpgrp
    )

    print("!运行前一定配置环境变量! bpserver 已在后台运行")
    print("访问 http://127.0.0.1:8888/ 控制面板")
    print("访问 http://127.0.0.1:8888/doc 查看帮助文档")

if __name__ == "__main__":
    main()

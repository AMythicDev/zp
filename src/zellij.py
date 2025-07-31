import subprocess


def switch_session(name: str):
    subprocess.run(["zellij", "--layout", "project", "attach", "-c", name])


def delete_session(name: str):
    subprocess.run(["zellij", "delete-session", "-f", name])

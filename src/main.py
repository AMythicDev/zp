import typer
import os
from appdirs import user_data_dir
import json
import subprocess
from zellij import switch_session, delete_session
import shutil
from urllib.parse import urlparse
from typing import Annotated

APPNAME = "zp"
APPAUTHOR = "AMythicDev"


class Zp:
    projects_dir: str
    data_dir: str
    projfile: str
    projects: set[str]

    def __init__(self) -> None:
        self.projects_dir = os.environ.get(
            "ZP_PROJECTS_DIR", os.path.expanduser("~/projects")
        )
        self.data_dir = user_data_dir(APPNAME, APPAUTHOR)
        self.projfile = self.data_dir + "/projects.json"
        if not os.path.exists(self.data_dir):
            os.mkdir(self.data)
        if not os.path.exists(self.projfile):
            with open(self.projfile, "w") as f:
                f.write("[]\n")

        with open(self.projfile, "r") as f:
            self.projects = set(json.load(f))

    def _sync_projects(self) -> None:
        with open(self.projfile, "w") as f:
            json.dump(list(self.projects), f, indent=2)

    def new(self, name: str, switch: bool, dir_exists: bool) -> None:
        self.projects.add(name)

        new_projdir = self.projects_dir + "/" + name

        if not dir_exists:
            if os.path.exists(new_projdir):
                raise FileExistsError(
                    f"error: project directory {new_projdir} already exists",
                )
            os.mkdir(new_projdir)

        self._sync_projects()

        if switch:
            os.chdir(new_projdir)
            switch_session(name)

    def delete(self, name: str, session: bool, dir: bool) -> None:
        self.projects.remove(name)
        del_projdir = self.projects_dir + "/" + name

        if session:
            delete_session(name)

        if dir:
            shutil.rmtree(del_projdir)

        self._sync_projects()


app = typer.Typer()


@app.command()
def new(name: str, switch: bool = True):
    zp = Zp()
    zp.new(name, switch)


@app.command()
def rm(
    name: str,
    session: Annotated[
        bool,
        typer.Option(
            "--no-session",
            "-ns",
            help="Do not delete the associated multiplexer session.",
        ),
    ] = True,
    dir: Annotated[
        bool,
        typer.Option(
            "--dir",
            "-d",
            help="Delete the associated project directory.",
        ),
    ] = False,
):
    zp = Zp()
    zp.delete(name, session, dir)


@app.command("import")
def importp(origin: str, switch: bool = True):
    zp = Zp()
    os.chdir(zp.projects_dir)
    if origin.startswith("gh:"):
        subprocess.run(["git", "clone", f"git@github.com:{origin[3:]}"])
        name = os.path.basename(origin)
    elif origin.startswith("gl:"):
        subprocess.run(["git", "clone", f"git@gitlab.com:{origin[3:]}"])
        name = os.path.basename(origin)
    elif origin.startswith("http://") or origin.startswith("https://"):
        subprocess.run(["git", "clone", name])
        name = os.path.basename(urlparse(origin).path)
    zp.new(name, switch, True)


@app.command()
def sw(
    name: str,
):
    zp = Zp()
    if name in zp.projects:
        switch_session(name)
    else:
        print(f"error: project '{name}' not found")


@app.callback(invoke_without_command=True)
def nain(
    ctx: typer.Context,
    fzf: Annotated[
        bool,
        typer.Option(
            "--fzf",
            "-f",
            help="Start fzf if no project name is given. This option is deprecated and is present only for historical reasons.",
        ),
    ] = True,
    dir: Annotated[
        bool,
        typer.Option(
            "--dir",
            "-d",
            help="Initialize project in current directory. This option is deprecated and is present only for historical reasons. Prefer the 'import' command instead",
        ),
    ] = False,
):
    if ctx.invoked_subcommand is None:
        zp = Zp()
        if dir:
            sel = os.path.basename(os.getcwd())
            if sel not in zp.projects:
                zp.new(sel, True, True)
                return
        else:
            fzfsel = subprocess.run(
                ["fzf", "--layout", "reverse-list"],
                input="\n".join(zp.projects),
                text=True,
                capture_output=True,
            )
            sel = fzfsel.stdout[:-1].strip()

        if len(sel) != 0:
            switch_session(sel)


if __name__ == "__main__":
    app()

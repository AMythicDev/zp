import typer
import os
from appdirs import user_data_dir
import json
import subprocess
from zellij import switch_session, delete_session
import shutil
from urllib.parse import urlparse
from typing import Annotated
import sys
from pathlib import Path

APPNAME = "zp"
APPAUTHOR = "AMythicDev"


class Zp:
    projects_dir: Path
    data_dir: Path
    projfile: Path
    projects: dict[str, str] = {}

    def __init__(self) -> None:
        self.projects_dir = Path(
            os.environ.get("ZP_PROJECTS_DIR", os.path.expanduser("~/projects"))
        )
        self.data_dir = Path(user_data_dir(APPNAME, APPAUTHOR))
        self.projfile = self.data_dir / "projects.json"
        if not self.data_dir.exists():
            os.mkdir(self.data)
        if not self.projfile.exists():
            self._sync_projects()

        with open(self.projfile, "r") as f:
            self.projects = json.load(f)

    def _sync_projects(self) -> None:
        with open(self.projfile, "w") as f:
            json.dump(self.projects, f, indent=2)

    def new(
        self,
        path: Path,
        out_of_projects_dir: bool,
        switch: bool,
        dir_exists: bool,
    ) -> None:
        if out_of_projects_dir:
            new_projdir = path.resolve()
        else:
            new_projdir = self.projects_dir / path

        if not dir_exists:
            if new_projdir.exists():
                raise FileExistsError(
                    f"error: project directory {new_projdir} already exists",
                )
            new_projdir.mkdir()

        self.projects[new_projdir.name] = str(new_projdir)

        self._sync_projects()

        if switch:
            os.chdir(new_projdir)
            switch_session(path.name)

    def delete(self, name: str, session: bool, dir: bool) -> None:
        del_projdir = self.projects[name]
        del self.projects[name]

        if session:
            delete_session(name)

        if dir:
            shutil.rmtree(del_projdir)

        self._sync_projects()


app = typer.Typer()


def is_path_like(text: str) -> bool:
    return text.find("/") != -1 or text == "." or text == ".."


@app.command()
def new(path: str, switch: bool = True):
    zp = Zp()
    out_of_projects_dir: bool = is_path_like(path)

    zp.new(Path(path), out_of_projects_dir, switch, False)


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


@app.command("im")
def importp(origin: str, switch: bool = True):
    zp = Zp()
    out_of_projects_dir = False
    if origin.startswith("gh:"):
        os.chdir(zp.projects_dir)
        subprocess.run(["git", "clone", f"git@github.com:{origin[3:]}"])
        name = os.path.basename(origin)
    elif origin.startswith("gl:"):
        os.chdir(zp.projects_dir)
        subprocess.run(["git", "clone", f"git@gitlab.com:{origin[3:]}"])
        name = os.path.basename(origin)
    elif origin.startswith("http://") or origin.startswith("https://"):
        os.chdir(zp.projects_dir)
        subprocess.run(["git", "clone", name])
        name = os.path.basename(urlparse(origin).path)
    elif not is_path_like(origin) and os.path.isdir(zp.projects_dir / origin):
        os.chdir(zp.projects_dir)
        name = origin
    elif is_path_like(origin):
        name = Path(origin).resolve()
        out_of_projects_dir = True
    else:
        print(
            f"cannot import {
                origin
            }: origin not a valid url or a valid directory under projects directory",
            file=sys.stderr,
        )
        raise typer.Exit(code=1)
    zp.new(Path(name), out_of_projects_dir, switch, True)


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
            help="Start fzf if no project name is given or zp is called inside project directory.",
        ),
    ] = False,
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
        dirname = os.path.basename(os.getcwd())
        sel = None
        if dir:
            if dirname not in zp.projects:
                zp.new(dirname, True, True)
                raise typer.Exit()
        elif fzf or dirname not in zp.projects:
            fzfsel = subprocess.run(
                ["fzf", "--layout", "reverse-list"],
                input="\n".join(zp.projects),
                text=True,
                capture_output=True,
            )
            if len(fzfsel.stdout) == 0:
                raise typer.Abort()
            sel = fzfsel.stdout[:-1].strip()
        elif dirname in zp.projects:
            sel = dirname

        if sel is not None:
            switch_session(sel)


if __name__ == "__main__":
    app()

# Zp
An highly opinionated projects manager

`zp` lets you create and manage projects. It works by maintaining a global project directory which hosts
all your projects. It also integrates with [fzf](https://github.com/junegunn/fzf) for quickly selecting projects,
[Zellij](https://zellij.dev/) to provide multiplexing support and workspace
persistence and git to easily import external repositories.

`zp` works for only certain set of people:
1. Your development IDE is basically a terminal and Vim/Neovim.
2. You use Zellij/Tmux for persisting project sessions and multiplexing.

If you don't satisfy any of the above conditions, **don't use this and go away**.

## Why?
You are probably looking into this because
1. You have to deal with >= 5 active projects and a dozen side projects.
2. You are a total hipster who wants to overcomplicate typing 3-4 commands everyday on the terminal.
3. You are fine hacking and maintaining a project manager by yourself.

If you don't satisfy any of the above conditions, **don't use this and go away, and yes its a repetition.**.

## Philosophy
Only one: type as less as possible in the terminal for project related tasks, let the fuzzy finder type for you.

## Requirements
- Python >= 3.13
- fzf
- Zwllij
- Have a global project directory under which you host all your projects. By default, it is assumed to be `$HOME/projects/`
  but can be overriden by the `ZP_PROJECTS_DIR` enviroment variable

## Installation
Maybe later

## Docs
### Create a new project
```sh
zp new [PROJECT_NAME]
```
This will create a new directory under your global projects directory and start a zellij session inside that project directory.

### Open project switcher
```sh
zp
```
Opens fzf and let's you select and switch to a project

### Open project by name
```sh
zp sw [PROJECT_NAME]

```
**Do not use this unless you are writing a shell script or you've gone insane and want to keep hitting your fingers on your keyboard.**

### Remove a project
```sh
zp rm [PROJECT_NAME]
```
1. By default, `zp` removes the associated session from Zellij, use the `--no-session` to also keep the session.
2. Zellij leaves the project directory as it is, essentially deregistering it from `zp`. Use the `--dir` flag to also remove it
   from the global projects directory.

### Import a project
#### Import a project as a Zp project already residing under the global projects directory
```sh
zp import [PROJECT_NAME]
```

#### Import a GitHub repo as a Zp project
```sh
zp import gh:[USERNAME]/[REPONAME]
```

#### Import a GitLab repo as a Zp project
```sh
zp import gl:[USERNAME]/[REPONAME]
```

#### Import a git project from a arbitrary URL
```sh
zp import [URL starting with http:// or https://]
```

## Extending
Clone it, change it, enjoy your life

### Use Tmux over Zellij
Create a new file under `src/` directory, defining two functions `switch_session()` and `delete_session()` and import it in the `src/main.py`
instead of the `zellij.py` file. Use the `zellij.py` for an example.

## Contributing
Don'd send PRs unless its a bug or feature that everyone can benefit from.

All contributions are under the BSD 3 Clause license. See the [LICENSE](./LICENSE) file.


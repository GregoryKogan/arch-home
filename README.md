# universal-home-builder

## Installation

### Dependencies

This is a python script, so the only dependecy is `python3`.

### Download

Just clone the repo

```shell
git clone https://github.com/GregoryKogan/universal-home-builder.git ~/uhb
```

## Usage

Inspired by nix's home-manager.
[example](https://github.com/GregoryKogan/dotfiles)

With universal-home-builder you can configure your home directory with `.toml` files. **Each** file may have these options:

```toml
# import other toml files to make the whole system modular.
imports = [
  "../modules/alacritty/config.toml"
]

# symlink any files or directories. `dest` path is relative to home directory.
files = [
  {src="zshrc-conf", dest=".zshrc"},
  {src="../images", dest=".config/images"}
]

[scripts]
# build scripts run on each rebuild
build = ["install_software"]
# user scripts get symlinked to ~/.bin/. You should add it to your path to be able to run them by name.
user = ["say-hello"]
```

### Run

Run `build` script with a single argument of a path to the entry point `.toml` file.  
For example:

```shell
~/uhb/build ~/dotfiles/hosts/arch.toml
```

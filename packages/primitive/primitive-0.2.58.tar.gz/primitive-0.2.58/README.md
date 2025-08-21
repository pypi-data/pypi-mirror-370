# primitive

[![PyPI - Version](https://img.shields.io/pypi/v/primitive.svg)](https://pypi.org/project/primitive)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/primitive.svg)](https://pypi.org/project/primitive)

---

**Table of Contents**

- [Installation](#installation)
- [Configuration](#configuration)
- [License](#license)
- [Development Setup](#development-setup)

## Installation

```console
pip install primitive
```

## Configuration

### Authenticate

```console
primitive config
```

### Register your Hardware

```console
primitive hardware register
```

## License

`primitive` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

## Development Setup

For Primitive engineers, you may have these steps completed.

### Python Setup

```bash
# install required libs for macos
xcode-select --install

# install brew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# install fish
brew install fish
echo /usr/local/bin/fish | sudo tee -a /etc/shells
chsh -s /usr/local/bin/fish

# install fisher
brew install fisher
fisher install jorgebucaran/nvm.fish

# install git
brew install git

# set global info
git config --global user.email "<user@email.com>"
git config --global user.name “<firstName lastName>”

# install make
brew install make
fish_add_path /opt/homebrew/opt/make/libexec/gnubin

# install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
uv python install
fish_add_path "$(uv python dir)/bin"
```

### Repository Setup

Clone and run setup.

```bash
cd ~/Development/primitivecorp/
git clone git@github.com:primitivecorp/primitive-cli.git
cd primitive-cli
make setup
```

With the backend and frontend development environments running, configure the CLI for local use.

```bash
# bash or zsh
source .venv/bin/activate
# fish
source .venv/bin/activate.fish

primitive --host localhost:8000 config --transport http
You can find or create a Primitive API token at http://localhost:3000/account/tokens
Please enter your Primitive API token: # create a token and copy the value here
Config created at '/Users/<user>/.config/primitive/credentials.json' on host 'localhost:8000'

# verify the configuration worked via
primitive --host localhost:8000 whoami
Logged in as <username>
```

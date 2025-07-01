For setup:

- `python -m venv venv`
- `venv/Scripts/activate`
- `pip3 install -r requirements.txt`

Build python nix configuration: `nix run github:nix-community/pip2nix -- ./requirements.txt`
# Shell script to set up the project development environment

# Make sure we're on linux
$ {OSTYPE} != "linux-gnu" && echo "This script is intended for Linux systems only." && exit 1
# Set up venv
python3 -m venv venv
venv/Scripts/activate
# Check if the user is using pip or pip3, and write the correct script
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
else
    PIP_CMD="pip"
fi
# Upgrade pip and install requirements
$PIP_CMD install --upgrade pip
$PIP_CMD install -r requirements.txt
# Deactivate the venv
deactivate
# Se up .conda
conda create -n fbenv python=3.11 ncbi-datasets-cli blast orthofinder gemoma memote -y
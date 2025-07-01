# Shell script to set up the project development environment

# Make sure we're on linux
$ {OSTYPE} != "linux-gnu" && echo "This script is intended for Linux systems only." && exit 1

echo "Searching for conda package manager ... (may take 1-2 mins)"
# Search for the conda package manager in the os, show loading bar in the process, leave error message if not found and exit
if ! command -v conda &> /dev/null; then
    echo "Conda package manager not found. Please install Anaconda or Miniconda."
    exit 1
fi

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

# Set up .conda
conda create -n fbenv python=3.11 ncbi-datasets-cli blast orthofinder gemoma memote -y
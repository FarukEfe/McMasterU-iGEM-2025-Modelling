# Shell script to download the genome datasets from NCBI via bioconda

# Setup
$ {OSTYPE} != "linux-gnu" && echo "This script is intended for Linux systems only." && exit 1
source "$(conda info --base)/etc/profile.d/conda.sh"
echo ""

# Target
target_accession='GCA_002245835.2' # C. sorokiniana
ref_accession=('GCF_000002595.2' 'GCA_001021125.1') # C. reinhardtii, C. vulgaris ... (add 2 other)

# Setup: create reference and target folder if they don't exist (inside data/genome)
mkdir -p data/genome/reference data/genome/target

# Clean: deactivate conda environments before running the script
if [ -n "$CONDA_DEFAULT_ENV" ]; then
    echo "Deactivating current conda environment: $CONDA_DEFAULT_ENV"
    conda deactivate # 2>/dev/null
fi

# Check: conda installed
if ! command -v conda &> /dev/null; then
    echo "Conda is not installed. Please install Anaconda or Miniconda first."
    exit 1
fi

# Conda: list available envs & select one
conda env list
echo "Please select an environment to activate (e.g., base):"
read -r env_name
if [ -z "$env_name" ]; then
    echo "No environment selected. Exiting."
    exit 1
fi

# Conda: activate the environment
if ! conda info --envs | grep -q "$env_name"; then
    echo "Environment '$env_name' does not exist. Please run the setup script first."
    exit 1
fi

conda activate ncbi_datasets # 2>/dev/null

# Check: exit if activation failed
if [ $? -ne 0 ]; then
    echo "Failed to activate conda environment '$env_name'. Please check the environment name."
    exit 1
fi

# Check: ncbi-datasets-cli installed
if ! command -v datasets &> /dev/null; then
    echo "ncbi-datasets-cli is not installed. Please install it using conda."
    echo "You can install it with: conda install -c bioconda ncbi-datasets-cli"
    exit 1
fi

# MARK: Target Download
echo "Processing target genome: $target_accession ..."
datasets download genome accession "$target_accession" \
    --filename "${target_accession}.zip" \
    --assembly-level chromosome \
    --include gbff \
    2>/dev/null # Suppress default output

# Check if the download was successful
if [ ! -f "target_genome.zip" ]; then
    echo "Download failed: target_genome.zip not found. Exiting ..."
    exit 1
fi

template="ncbi_dataset/data/${target_accession}/genomic.gbff"
result="./data/genome/target/${target_accession}/"

mkdir -p "${result}" # Create the directory if it doesn't exist
#unzip -l "target_genome.zip" # List the contents of the zip file
echo "Extracting genomic.gbff from ${template} into ${result}"
unzip -j -o "${target_accession}.zip" "${template}" -d "${result}"
rm -f "${target_accession}.zip" # Remove the zip file after extraction

# MARK: Ref. Download
for species in "${ref_accession[@]}"; do
    echo "Processing $species ..."
    datasets download genome accession "$species" \
        --filename "${species}.zip" \
        --assembly-level chromosome \
        --include gbff \
        2>/dev/null # Suppress default output
    
    if [ ! -f "${species}.zip" ]; then
        echo "Download failed: ${species}.zip not found. Skipping ..."
        continue
    fi
    echo "Download completed: ${species}.zip"

    template="ncbi_dataset/data/${species}/genomic.gbff"
    result="./data/genome/reference/${species}/"

    mkdir -p "${result}" # Create the directory if it doesn't exist
    #unzip -l "${species}.zip" # List the contents of the zip file
    echo "Extracting genomic.gbff from ${template} into ${result}"
    unzip -j -o "${species}.zip" "${template}" -d "${result}" # Extract the genomic.gbff file"
    rm -f ${species}.zip # Remove the zip file after extraction
done

# Conda: deactivate
conda deactivate
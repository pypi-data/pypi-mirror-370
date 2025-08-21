# Symclatron

[![PyPI version](https://badge.fury.io/py/symclatron.svg)](https://badge.fury.io/py/symclatron)
[![License: BSD-3-Clause](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/release/python-390/)

## Machine learning-based classification of microbial symbiotic lifestyles

symclatron is a tool that classifies microbial genomes into three symbiotic lifestyle categories:

- **Free-living**
- **Symbiont; Host-associated**
- **Symbiont; Obligate-intracellular**

## Installation

### From PyPI (recommended)

```bash
pip install symclatron
```

### From source

```bash
git clone https://github.com/NeLLi-team/symclatron.git
cd symclatron/
pip install .
```

### Development installation

```bash
git clone https://github.com/NeLLi-team/symclatron.git
cd symclatron/
pip install -e ".[dev]"
```

## System Requirements

symclatron requires HMMER to be installed and available in your PATH:

**Ubuntu/Debian:**
```bash
sudo apt-get install hmmer
```

**macOS (with Homebrew):**
```bash
brew install hmmer
```

**Conda/Mamba:**
```bash
conda install -c bioconda hmmer
```

## Quick Start

1. **Setup data (required)** - Download required database files (only needed once):
```bash
symclatron setup
```

2. **Test with sample genomes:**
```bash
symclatron test
```

3. **Classify your genomes:**
```bash
symclatron classify --genome-dir /path/to/genomes/ --output-dir results/
```

## Usage

### Getting help

```bash
# Main help
symclatron --help

# Command-specific help
symclatron classify --help
symclatron setup --help

# Show version and information
symclatron --version
symclatron info
```

### Classification command

The main classification command with all options:

```bash
symclatron classify [OPTIONS]
```

**Options:**

- `--genome-dir, -i`: Directory containing genome FASTA files (.faa) [default: input_genomes]
- `--output-dir, -o`: Output directory for results [default: output_symclatron]
- `--keep-tmp`: Keep temporary files for debugging
- `--threads, -t`: Number of threads for HMMER searches [default: 2]
- `--quiet, -q`: Suppress progress messages
- `--verbose`: Show detailed progress information

**Examples:**

```bash
# Basic usage
symclatron classify --genome-dir genomes/ --output-dir results/

# With more threads and keeping temporary files
symclatron classify -i genomes/ -o results/ --threads 8 --keep-tmp

# Quiet mode
symclatron classify --genome-dir genomes/ --quiet

# Verbose mode with detailed progress
symclatron classify --genome-dir genomes/ --verbose
```

## Results

The classification results are saved in the specified output directory:

### Main output files

1. **`symclatron_results.tsv`** - Main classification results with columns:
   - `taxon_oid` - Genome identifier
   - `completeness_UNI56` - Completeness metric based on universal marker genes
   - `confidence` - Overall confidence score for the classification
   - `classification` - Final classification label:
     - `Free-living`
     - `Symbiont;Host-associated`
     - `Symbiont;Obligate-intracellular`

2. **`classification_summary.txt`** - Summary report with statistics

3. **Log files** - Detailed execution logs with timestamps

### Debug files

When using `--keep-tmp`, intermediate files are preserved in `tmp/` directory for analysis.

## Performance

symclatron is designed for efficiency:

- **~2 minutes per genome** on consumer-level laptops
- **Most recent benchmark**: 306 genomes in ~162 minutes (1.9 min/genome)
- **Memory efficient** - suitable for standard workstations

## Input requirements

- **File format**: Protein FASTA files (.faa, .fasta, .fa)
- **Content**: Predicted protein sequences from genomes
- **Quality**: Complete or near-complete genomes recommended, but good performance for MQ MAGs are expected

## Container usage

### Docker

Pull the latest container:

```bash
docker pull docker.io/jvillada/symclatron:latest
```

**Test with sample genomes:**

```bash
my_test_dir=$PWD/test_output_symclatron
mkdir -p $my_test_dir
docker run --rm \
    -v $my_test_dir:/usr/src/symclatron/output \
    docker.io/jvillada/symclatron:latest \
    symclatron test --output-dir output
```

**Classify your genomes:**

```bash
my_genomes_dir="/path/to/genome/faa_files/"
my_output_dir="/path/to/output/directory/"
mkdir -p $my_output_dir
docker run --rm \
    -v $my_genomes_dir:/usr/src/symclatron/input_genomes \
    -v $my_output_dir:/usr/src/symclatron/output \
    docker.io/jvillada/symclatron:latest \
    symclatron classify --genome-dir input_genomes/ --output-dir output
```

### Apptainer/Singularity

Pull the latest container:

```bash
apptainer pull docker://docker.io/jvillada/symclatron:latest
```

**Test with sample genomes:**

```bash
my_test_dir=$PWD/test_output_symclatron
mkdir -p $my_test_dir
apptainer run \
    --pwd /usr/src/symclatron \
    --bind $my_test_dir:/usr/src/symclatron/output \
    docker://docker.io/jvillada/symclatron:latest \
    symclatron test --output-dir output
```

**Classify your genomes:**

```bash
my_genomes_dir="/path/to/genome/faa_files/"
my_output_dir="/path/to/output/directory/"
mkdir -p $my_output_dir
apptainer run \
    --pwd /usr/src/symclatron \
    --bind $my_genomes_dir:/usr/src/symclatron/input_genomes \
    --bind $my_output_dir:/usr/src/symclatron/output \
    docker://docker.io/jvillada/symclatron:latest \
    symclatron classify --genome-dir input_genomes/ --output-dir output
```

## Citation

If you use symclatron in your research, please cite:

A genomic catalog of Earth's bacterial and archaeal symbionts.
Juan C. Villada, Yumary M. Vasquez, Gitta Szabo, Ewan Whittaker-Walker, Miguel F. Romero, Sarina Qin, Neha Varghese, Emiley A. Eloe-Fadrosh, Nikos C. Kyrpides, SymGs data consortium, Axel Visel, Tanja Woyke, Frederik Schulz
bioRxiv 2025.05.29.656868; doi: https://doi.org/10.1101/2025.05.29.656868

## Support

- **Repository**: [https://github.com/NeLLi-team/symclatron](https://github.com/NeLLi-team/symclatron)
- **Issues**: [https://github.com/NeLLi-team/symclatron/issues](https://github.com/NeLLi-team/symclatron/issues)
- **Author**: Juan C. Villada <jvillada@lbl.gov>

## License

This project is licensed under the BSD-3-Clause License - see the [LICENSE](LICENSE) file for details.

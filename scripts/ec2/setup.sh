#!/bin/bash

# Update package list and install required packages
echo "Updating system packages..."
sudo apt update -y && sudo apt upgrade -y || sudo yum update -y

echo "Installing Make and Python..."
sudo apt install -y make python3 python3-pip || sudo yum install -y make python3 python3-pip

# Install Miniconda
CONDA_INSTALLER="Miniconda3-latest-Linux-x86_64.sh"
CONDA_URL="https://repo.anaconda.com/miniconda/$CONDA_INSTALLER"

echo "Downloading Miniconda..."
curl -o ~/miniconda.sh $CONDA_URL

echo "Installing Miniconda..."
bash ~/miniconda.sh -b -p $HOME/miniconda

# Initialize Conda
echo "Configuring Conda..."
export PATH="$HOME/miniconda/bin:$PATH"
source $HOME/miniconda/bin/activate
conda init bash

# Verify installations
echo "Verifying installations..."
make --version
python3 --version
conda --version

echo "Installation completed successfully!"
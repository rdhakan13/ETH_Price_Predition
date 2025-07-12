#!/bin/bash
# Update system
sudo yum update -y

# Install Git, Make, and build dependencies
sudo yum groupinstall -y "Development Tools"
sudo yum install -y gcc openssl-devel bzip2-devel libffi-devel wget make git zlib-devel readline-devel sqlite-devel xz-devel
echo 'Git and Make installation complete'

# Setup Git
cd home/ec2-user/
git config --global user.name "ec2-deploy-bot"
git config --global user.email "ec2@myinfra.local"
ssh-keygen -t ed25519 -C "ec2-deploy-key" -f ./ec2_deploy_key

# Download and compile Python 3.11.7
cd /usr/src
sudo wget https://www.python.org/ftp/python/3.11.7/Python-3.11.7.tgz
sudo tar xzf Python-3.11.7.tgz
cd Python-3.11.7
sudo ./configure --enable-optimizations
sudo make -j$(nproc)
sudo make altinstall

# Overwrite system python3 and pip3 symlinks
sudo ln -sf /usr/local/bin/python3.11 /usr/bin/python3
sudo ln -sf /usr/local/bin/pip3.11 /usr/bin/pip3

# (Optional) Also set 'python' and 'pip' to point to Python 3.11
sudo ln -sf /usr/local/bin/python3.11 /usr/bin/python
sudo ln -sf /usr/local/bin/pip3.11 /usr/bin/pip

# Verify installation
python3 --version
pip3 --version

sudo rm -rf /tmp/*

echo 'Python 3.11.7 installation complete'
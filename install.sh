#!/bin/bash
echo "This script will install Python39, docker-compose and composer, if they do not already exist on your system."
echo "This could break some python installations as it will attempt to overwrite the python3 binary for earlier versions."
read -p "Are you sure you want to continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Exiting."
    exit 1
fi

# Check if the script is running as root
if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

# Function for installing python
install_python(){
  if [ "$DISTRO" == "Ubuntu" ]; then
      apt update -y
      apt install -y software-properties-common
      add-apt-repository -y ppa:deadsnakes/ppa
      apt install -y python3.9
      apt-get install -y python3-pip
    fi
    if [ "$DISTRO" == "Amazon" ]; then
      wget https://www.python.org/ftp/python/3.9.7/Python-3.9.7.tgz
      tar zxvf Python-3.9.7.tgz
      cd Python-3.9.7/ || exit 1
      yum groupinstall "Development Tools" -y
      yum install openssl-devel libffi-devel bzip2-devel -y
      echo "Configuring make"
      ./configure --enable-optimizations
      echo "Doing make install"
      make altinstall
      echo "Cleaning up python install files"
      rm Python-3.9.7.tgz
      rm -rf Python-3.9.7/
    fi
}

# Determine OS platform
UNAME=$(uname | tr "[:upper:]" "[:lower:]")
# If Linux, try to determine specific distribution
if [ "$UNAME" == "linux" ]; then
    # If available, use LSB to identify distribution
    if [ -f /etc/lsb-release -o -d /etc/lsb-release.d ]; then
        export DISTRO=$(lsb_release -i | cut -d: -f2 | sed s/'^\t'//)
    # Otherwise, use release info file
    else
        export DISTRO=$(ls -d /etc/[A-Za-z]*[_-][rv]e[lr]* | grep -v "lsb" | cut -d'/' -f3 | cut -d'-' -f1 | cut -d'_' -f1)
    fi
fi
# For everything else (or if above failed), just use generic identifier
[ "$DISTRO" == "" ] && export DISTRO=$UNAME
# For AWS Linux check /etc/system-release
if [ -s /etc/system-release ]; then
  DISTROSTR=$(cat /etc/system-release)
  if [[ $DISTROSTR =~ ^Amazon.*$ ]]; then
    export DISTRO="Amazon"
  fi
fi
unset UNAME

echo "Installation OS: $DISTRO"
if [ "$DISTRO" == "Ubuntu" ]; then
    export PIP="pip3"
    export PYTHON="python3"
    export COMPOSE="/usr/bin/docker-compose"
fi
if [ "$DISTRO" == "Amazon" ]; then
    export PIP="/usr/local/bin/pip3.9"
    export PYTHON="/usr/local/bin/python3.9"
    export COMPOSE="/usr/local/bin/docker-compose"
fi
echo "---Docker---"
if ! command -v docker &> /dev/null
then
    echo "Docker could not be found, installing it."
    if [ "$DISTRO" == "Ubuntu" ]; then
      curl -fsSL https://get.docker.com -o get-docker.sh
      chmod +x get-docker.sh
      sudo sh get-docker.sh
      systemctl start docker
      systemctl enable docker
      # Enable rootless docker
      usermod -aG docker ssm-user || true
      usermod -aG docker ec2-user || true
    fi
    if [ "$DISTRO" == "Amazon" ]; then
      yum install -y docker
      service docker start
      systemctl enable docker
      # Enable rootless docker
      usermod -aG docker ssm-user || true
      usermod -aG docker ec2-user || true
    fi
fi
echo "---Docker Composer---"
# Check if docker-composer exists
if ! command -v "$COMPOSE" &> /dev/null
then
    echo "Docker-compose could not be found, installing it."
    if [ "$DISTRO" == "Ubuntu" ]; then
      curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
      sudo chmod +x /usr/local/bin/docker-compose
    fi
    if [ "$DISTRO" == "Amazon" ]; then
      curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
      sudo chmod +x /usr/local/bin/docker-compose
    fi
fi
echo "---Python3---"
# Check if python3 exists
if ! command -v "$PYTHON" &> /dev/null
then
    echo "Python 3 could not be found, installing it."
    install_python
fi
echo "---Python3 Version Check---"
pythonVer=$($PYTHON -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}") if sys.version_info.major < 3 or sys.version_info.major >= 3 and sys.version_info.minor < 9 else print(0)')
if [[ ! $pythonVer == "0" ]]
then
    echo "Current Python Version: $pythonVer"
    echo "Required Python Version: 3.9 or later"
    install_python
fi

echo "---Composer---"
# Check if docker-composer exists
if command -v composer &> /dev/null
then
    echo "Composer already exists, updating to latest version."
fi
$PIP install --upgrade docker-composition

echo "---Install complete---"
echo "Please restart for changes to fully take effect."
echo "At minimum run newgrp docker as your current user."
echo ""
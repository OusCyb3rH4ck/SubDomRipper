#!/bin/bash

install_apt_package() {
    local package_name=$1
    if ! command -v "$package_name" &> /dev/null; then
        echo -e "\e[1;35m\n[+] Installing $package_name (apt)...\e[0m"
        sudo apt-get update && sudo apt-get install -y "$package_name"
        if [ $? -ne 0 ]; then
            echo -e "\e[1;31m\n[!] Error installing $package_name (apt)\n\e[0m"
            exit 1
        fi
    else
        echo -e "\e[1;32m[+] $package_name already installed.\e[0m"
    fi
}

install_go_package() {
    local go_package=$1
    local binary_name=$2
    if ! command -v "$binary_name" &> /dev/null; then
        echo -e "\e[1;35m\n[+] Installing $binary_name (Go)...\e[0m"
        go install -v "$go_package"
        if [ $? -ne 0 ]; then
            echo -e "\e[1;31m\n[!] Error installing $binary_name (Go)\n\e[0m"
            exit 1
        fi
        export PATH=$PATH:$(go env GOPATH)/bin
    else
        echo -e "\e[1;32m[+] $binary_name already installed.\e[0m"
    fi
}

sudo apt-get update && sudo apt update

install_apt_package "python3"
install_apt_package "python3-pip"
install_apt_package "figlet"
install_apt_package "lolcat"
install_apt_package "golang-go"
install_apt_package "assetfinder"

install_go_package "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest" "subfinder"
install_go_package "github.com/PentestPad/subzy@latest" "subzy"

python3 -m pip install --break-system-packages --upgrade httpx pwn pwntools colorama argparse

mkdir -p output

echo -e "\e[1;34m\n[+] All dependencies installed successfully!\e[0m\n"

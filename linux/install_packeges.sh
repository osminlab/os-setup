#!/bin/bash
# Author: Osmin Larreynaga
# Date: 2023/01/25
# Description: 
# Program that allows the user to install packages from a file, edit the package list, or exit the program.

# Enable error handling
set -e

# Name of the file containing the package list
package_file="./linux/listallpackages.sh"

# Function to install packages from a file
install_packages () {
    echo -e "\nInstalling packages from '$package_file'..."

    # Update & package list
    sudo apt update && sudo apt upgrade -y

    # Install packages listed in the file
    sudo apt install -y $(cat "$package_file")

    echo "Package installation completed."
}

# Function to edit the package list file
edit_packages () {
    echo -e "\nEditing package list with nano..."
    nano "$package_file"
}

# Function to exit the program
exit_program () {
    echo "Exiting the program."
    exit 0
}

while :
do
    # Clear the screen
    clear
    # Display the menu options
    echo "_________________________________________"
    echo "        My Data Science Toolbox          "
    echo "_________________________________________"
    echo "               MAIN MENU                 "
    echo "_________________________________________"
    echo "  1. Install default packages            "    
    echo "  2. Edit package list                   "
    echo "  3. Exit                                "

    # Read user input
    read -n1 -p "Enter an option [1-3]:" option

    # Validate the option entered
    case $option in
        1)
            install_packages
            sleep 3
            echo "Everything was correct install..."
            ;;
        2) 
            edit_packages
            ;;
        3)  
            exit_program
            ;;
        *)
            echo -e "\nInvalid option. Please enter a valid option."
            sleep 2
            ;;
    esac
done


# Path where the backup will save (change as you need)
cd 'D:\GoogleDrive\05_Backups\02_WSL_Backups\'

# Get the current date in YYYYMMDD format
$fechaActual = Get-Date -Format "yyyyMMdd"

# Create the file name with the current date
$nombreArchivo = "${fechaActual}_Ubuntubackup.tar"

# Run the command wsl to export the file using the PowerShell
wsl --export Ubuntu $nombreArchivo

# END SCRIPT


# ******************************************************************
#                   ---------------------------
#                           WHAT NOW?
#                   ---------------------------
# If you want to import the backup to a new WSL instance, you can use 
# the following  example and command:

# Example:
# wsl --import ubuntu_test C:\Users\mmcgo\AppData\Local\Packages\ubuntu_test .\wsl_ubuntu_20.tar --version 2

# ******************************************************************

# Following next comand:
# wsl --import distro_name install_location file_name.tar





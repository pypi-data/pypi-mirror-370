# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                     Powershell script for Jenkins 4 Windows 7/10 (x64)                       %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Powershell script to initialize build environment for GNU compilers on Windows (FA-STM).
# Created on 11.08.2020
# 
# Version: 1.0
# -------------------------------------------------------------------------------------------------
#    Requirements and dependencies:
#        - 
#
#     Changelog:
#        - Created // mg 11.08.2020
#	
# -------------------------------------------------------------------------------------------------
param ($pyx_choco_install = $null)
# Do not perform any action if an installation directory has not been specified.
if ([string]::IsNullOrWhiteSpace("$pyx_choco_install")) {
Write-Host "A mandatory command line variable defining the installation directory for Chocolatey was not given. Abort installation."
} else {
# Set directory for installation - Chocolatey does not lock
# down the directory if not the default
$InstallDir="$pyx_choco_install"
$AppsDir="$InstallDir\apps"
$Pristine=[Environment]::GetEnvironmentVariable("Path", "User")

# Create a process local environment variable containing the chosen installation directory.
[Environment]::SetEnvironmentVariable("ChocolateyInstall", "$InstallDir", "Process")

# If your PowerShell Execution policy is restrictive, you may
# not be able to get around that. Try setting your session to
# Bypass.
Set-ExecutionPolicy Bypass -Scope Process -Force;

# All install options - offline, proxy, etc at
# https://chocolatey.org/install
iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))

# Create a user environment variable defining the application directory for 3rd party program files.
[Environment]::SetEnvironmentVariable("ChocolateyToolsLocation", "$AppsDir", "User")

# Install Msys2 to fetch GNU compilers for Windows.
choco install msys2 -y

# Refresh all environment variables
refreshenv

# Fetch GNU compilers with all major dependencies
$command = @'
msys2_shell.cmd -defterm -no-start -c "pacman --noconfirm -Syu base-devel mingw-w64-x86_64-toolchain mingw64/mingw-w64-x86_64-gcc-fortran mingw64/mingw-w64-x86_64-lapack --disable-download-timeout | tee -a /update.log; ps -ef | grep '[?]' | awk '{print $2}' | xargs -r kill"
'@

# Execute as CMD command
Invoke-Expression -Command:"$AppsDir\msys64\$command"

# Delete environment variables created by Chocolatey. 
[Environment]::SetEnvironmentVariable("ChocolateyLastPathUpdate", $null, "User")
[Environment]::SetEnvironmentVariable("ChocolateyToolsLocation", $null, "User")
[Environment]::SetEnvironmentVariable("ChocolateyInstall", $null, "Process")
[Environment]::SetEnvironmentVariable("Path", $Pristine, "User")
}
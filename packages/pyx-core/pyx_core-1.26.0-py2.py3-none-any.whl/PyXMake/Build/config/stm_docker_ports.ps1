# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                     Powershell script to establish Docker on Windows 7/10 (x64)              %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Powershell script to publish ports from WSL to external machines.
# Created on 26.10.2021
# 
# Version: 1.0
# -------------------------------------------------------------------------------------------------
#    Requirements and dependencies:
#        - 
#
#     Changelog:
#        - Created // mg 26.10.2021
#	
# -------------------------------------------------------------------------------------------------

# User options
param ($pyx_wsl_config = "$env:public\.wslconfig")

# Do not perform any action if an installation directory has not been specified.
if ([string]::IsNullOrWhiteSpace("$pyx_wsl_config")) {
Write-Host "A mandatory command line variable defining the configuration file for WSL was not given. Abort publishing ports." 
exit -1 ; 
} else {
# Set directory for installation - Docker does not lock
# down the directory if not the default
$file="$pyx_wsl_config" ; 
}

function global:Get-Watcher {
# Establish a watcher
$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = Split-Path $file
$watcher.Filter = "*.*"
$watcher.IncludeSubdirectories = $false
$watcher.EnableRaisingEvents = $true

# Action to perform after any changes in the folder
$action = { Get-Published-Ports }  

# Events triggering execution of the defined action
Register-ObjectEvent $watcher "Created" -Action $action
Register-ObjectEvent $watcher "Changed" -Action $action
Register-ObjectEvent $watcher "Deleted" -Action $action
Register-ObjectEvent $watcher "Renamed" -Action $action
while ($true) {sleep 5}
}

function global:Get-Published-Ports {
# [Check]
$found = Test-Path -Path $file
if( !$found ){
  Write-Host "The Script Exited, configuration file cannot be found";
  exit 0;
}

#[WSL IP]
$content = Get-Content -Path $file -Raw
$found = $content -match '\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}';
if( $found ){
  $remoteport = $matches[0];
} else{
  Write-Host "The Script Exited, the ip address of WSL 2 cannot be found";
  exit 0;
}

#[Ports]
$ports = Select-String -Path $file -Pattern '\[ports\]' -Context 0,1 | ForEach-Object { $_.Context.PostContext }
$found = $ports -match '\d{2,5}';
#All the ports you want to forward separated by coma
if( $found ){
  $ports = $ports.Split(",")
} else{
  Write-Host "The Script Exited, no published ports from WSL 2 are found";
  exit 0;
}

#[Static IP]
$addr='0.0.0.0';

#[Publish]
iex "netsh interface portproxy reset" ; 
for( $i = 0; $i -lt $ports.length; $i++ ){
  $port = $ports[$i];
  iex "netsh interface portproxy add v4tov4 listenport=$port listenaddress=$addr connectport=$port connectaddress=$remoteport";
}}

Get-Published-Ports ; Get-Watcher ; 
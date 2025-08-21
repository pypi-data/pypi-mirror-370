# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                     Powershell script to establish Docker on Windows 7/10 (x64)              %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Powershell script to initialize a Docker environment environment on Windows w/o Docker Desktop.
# Created on 19.10.2021
# 
# Version: 1.0
# -------------------------------------------------------------------------------------------------
#    Requirements and dependencies:
#        - 
#
#     Changelog:
#        - Created // mg 19.10.2021
#	
# -------------------------------------------------------------------------------------------------

# User options
param ($pyx_docker_install = $null, $pyx_docker_mode = $null)

# Do not perform any action if an installation directory has not been specified.
if ([string]::IsNullOrWhiteSpace("$pyx_docker_install")) {
Write-Host "A mandatory command line variable defining the installation directory for Docker was not given. Abort installation." 
exit -1 ; 
} else {
# Set directory for installation - Docker does not lock
# down the directory if not the default
$INSTALL_DIR="$pyx_docker_install" ; 
$WORK=$PWD ; 
}

# Establish POSIX container using WSL2
function Get-Linux {
Set-Location -Path $INSTALL_DIR ; 
md docker 2>&1>$null ; cd docker ; 
$command=@'
cat > stm_wsl_install.sh <<'EOF' 2>/dev/null
POWERSHELL=powershell.exe
{ echo [network] | sudo tee /etc/wsl.conf ; } > /dev/null ; 
{ echo generateResolvConf = false | sudo tee -a /etc/wsl.conf ; } > /dev/null ; 
{ echo [automount] | sudo tee -a /etc/wsl.conf ; } > /dev/null ; 
{ echo root = /mnt | sudo tee -a /etc/wsl.conf ; } > /dev/null ; 
{ echo options = "metadata" | sudo tee -a /etc/wsl.conf ; } > /dev/null ; 
sudo chattr -i /etc/resolv.conf > /dev/null 2>&1 ; 
sudo rm /etc/resolv.conf ; 
# Establish DLR and Cloudflare DNS for VPN support.
{ echo nameserver 10.184.193.20  | sudo tee -a /etc/resolv.conf ; } > /dev/null ; 
{ echo nameserver 172.21.154.193 | sudo tee -a /etc/resolv.conf ; } > /dev/null ; 
{ echo nameserver 208.67.222.222 | sudo tee -a /etc/resolv.conf ; } > /dev/null ; 
{ echo nameserver 208.67.220.220 | sudo tee -a /etc/resolv.conf ; } > /dev/null ; 
for i in `$POWERSHELL -Command \"Get-DnsClientServerAddress -AddressFamily ipv4 | Select-Object -ExpandProperty ServerAddresses\"`; do
    { echo nameserver $i | tr -d '\r' | sudo tee -a /etc/resolv.conf ; } > /dev/null ; 
done
{ echo nameserver 1.1.1.1 | sudo tee -a /etc/resolv.conf ; } > /dev/null ; 
sudo chattr +i /etc/resolv.conf
cat /etc/resolv.conf
apt-get -y update && apt-get -y upgrade && apt-get -y install git git-lfs python3-pip net-tools ; 
curl -fsSL https://get.docker.com -o get-docker.sh ; 
sudo sh get-docker.sh && rm -rf get-docker.sh ; 
sudo curl -L --fail https://github.com/docker/compose/releases/download/1.29.2/run.sh -o /usr/local/bin/docker-compose ; 
sudo chmod +x /usr/local/bin/docker-compose ; 
service docker start ; 
EOF
'@
wsl --set-default-version 2 2>&1>$null ; 
Invoke-WebRequest -Uri https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi -OutFile wsl_update_x64.msi -UseBasicParsing ; 
cmd /c "wsl_update_x64.msi /q" ; 
Remove-Item wsl_update_x64.msi ; 
Invoke-WebRequest -Uri https://aka.ms/wslubuntu2004 -OutFile ubuntu.appx -UseBasicParsing ; 
Rename-Item .\ubuntu.appx .\ubuntu.zip; Expand-Archive .\ubuntu.zip .\ubuntu; Remove-Item ubuntu.zip ;
cd ubuntu ; md data 2>&1>$null ; 
cmd /c "ubuntu2004.exe install --root" ;
wsl --export Ubuntu-20.04 "Ubuntu-20.04.tar" ;
wsl --unregister Ubuntu-20.04 ;
wsl --import docker "data" "Ubuntu-20.04.tar" --version 2 ;
wsl -e bash -c $command ;  
((Get-Content stm_wsl_install.sh) -join "`n") + "`n" | Set-Content -NoNewline stm_wsl_install.sh ; 
wsl sh stm_wsl_install.sh ;
Set-Location -Path $WORK ; 
} ; 

# Establish NT container
function Get-Windows {
Set-Location -Path $INSTALL_DIR ;
md docker 2>&1>$null ; cd docker ;
curl.exe -o windows.zip -LO https://download.docker.com/win/static/stable/x86_64/docker-20.10.9.zip ;
Expand-Archive windows.zip -DestinationPath $INSTALL_DIR\docker ; 
Remove-Item -Recurse -Force ~/.docker 2>&1>$null ;
Remove-Item windows.zip; Rename-Item .\docker .\windows; cd windows; md data\exec-root ; 
$DIR = $PWD.ProviderPath ; 
Start-Process -Verb RunAs -WindowStyle Hidden cmd.exe @"
/c SET "PATH=%PATH%;$DIR" & powershell -Command Remove-Item -Recurse -Force ~/.docker & powershell -Command New-NetFirewallRule -DisplayName "WSL" -Direction Inbound  -InterfaceAlias "vEthernet (WSL)"  -Action Allow & dockerd.exe -H tcp://127.0.0.1:2375 --register-service --data-root $DIR\data --exec-root $DIR\data\exec-root & powershell -Command Start-Service docker ; 
"@
Set-Location -Path $WORK ; 
} ; 

# Install all selected features. Defaults to only Linux containers by default.
if ( ( [string]::IsNullOrWhiteSpace("$pyx_docker_mode") ) -or ("$pyx_docker_mode" -eq "--package=linux") ) { Get-Linux ; }
if ( ( "$pyx_docker_mode" -eq "--package=all" ) -or ( "$pyx_docker_mode" -eq "--package=windows" ) ) { Get-Windows ; }
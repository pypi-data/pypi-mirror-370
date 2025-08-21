#!/bin/sh
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                    	     Shell script for Docker/Linux (x64)                                 %     
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Bash script for creating modern STM Lab documentation
# Created on 24.06.2021
# 
# Version: 1.0
# -------------------------------------------------------------------------------------------------
#    Requirements and dependencies:
#        - 
#
#     Changelog:
#        - 
#
# -------------------------------------------------------------------------------------------------
export PATH=/opt/conda/bin:$PATH
export DOCKER_TIMEZONE=Europe/Berlin
rm -f ~/.gitconfig
git config --global http.sslverify false
git config --global core.ignorecase false
git config --global credential.helper store
git config --global user.name "${GIT_USER}" && git config --global user.password "${GIT_PASSWORD}"
git config --global url."https://${GIT_USER}:${GIT_PASSWORD}@gitlab.dlr.de/".insteadOf "https://gitlab.dlr.de/"
cd src && /opt/conda/envs/stmlab/bin/python -c "import PyCODAC" && cd ..
ln -snf /usr/share/zoneinfo/$DOCKER_TIMEZONE /etc/localtime && echo $DOCKER_TIMEZONE > /etc/timezone
apt-get update && apt-get install -y perl pandoc texlive
conda run -n stmlab python ${CI_PROJECT_DIR}/src/PyCODAC/__setenv__.py ${CI_PROJECT_DIR}/src/PyCODAC/Plugin/PyXMake/VTL/sphinx.py;
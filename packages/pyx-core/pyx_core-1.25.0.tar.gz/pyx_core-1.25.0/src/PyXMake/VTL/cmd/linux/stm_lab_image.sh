#!/bin/sh
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                    	     Shell script for Docker/Linux (x64)                                 %     
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Bash script for creating Docker image of STM Lab.
# Created on 25.06.2021
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
for i in "$@"
do
case $i in
    -r=*|--resolve=*)
    resolve="${i#*=}"
    shift # Past Argument=Value
    ;;
    *)    # Unknown option
    ;;
esac
done
# All local variables
export PATH=/opt/conda/bin:$PATH; 
export DOCKER_BUILDKIT=0; export COMPOSE_DOCKER_CLI_BUILD=0
export environment=${CI_PROJECT_DIR}/src/PyCODAC/__setenv__.py
export makefile=${CI_PROJECT_DIR}/src/PyCODAC/Plugin/Peridigm/__install__.py
# Set flag to explicitly resolve the resource server. Defaults to False.
export resolve=${resolve:-"false"}
# Create a temporary install script for Peridigm
mkdir -p ${CI_PROJECT_DIR}/scratch
echo "from PyCODAC.Plugin import Peridigm" >> ${CI_PROJECT_DIR}/scratch/__image__.py
echo "Peridigm.GetDockerContainer()" >> ${CI_PROJECT_DIR}/scratch/__image__.py
# Install PyCODAC with all dependencies
rm -f ~/.gitconfig
git config --global http.sslverify false
git config --global core.ignorecase false
git config --global credential.helper store
git config --global user.name "${GIT_USER}" && git config --global user.password "${GIT_PASSWORD}"
git config --global url."https://${GIT_USER}:${GIT_PASSWORD}@gitlab.dlr.de/".insteadOf "https://gitlab.dlr.de/"
cd src && /opt/conda/envs/stmlab/bin/python -c "import PyCODAC" && cd ..
# Backwards compatibility. 
export GIT_PASSWORD=${GIT_CREDENTIALS:-$GIT_PASSWORD}
export CI_IMAGE=${CI_IMAGE:-$CI_REGISTRY/garb_ma/pycodac/stmlab:latest}
# Install Docker Composer
curl -L --fail https://github.com/docker/compose/releases/download/1.29.2/docker-compose-Linux-x86_64 -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
# Login to Docker registries
docker login -u $DOCKER_USER -p $DOCKER_PASSWORD; docker login -u $GIT_USER -p $GIT_PASSWORD $CI_REGISTRY
# Create latest Peridgim image with MCODAC support
# conda run -n stmlab python ${environment} ${makefile}
# conda run -n stmlab python ${environment} ${CI_PROJECT_DIR}/scratch/__image__.py
# Build STMLab main image
cp -a ${CI_PROJECT_DIR}/src/PyCODAC/API/config/. ${CI_PROJECT_DIR}/src/
cp -a ${CI_PROJECT_DIR}/src/PyCODAC/API/config/linux/. ${CI_PROJECT_DIR}/src/
cd ${CI_PROJECT_DIR}/src 
# Explicitly resolve external resource server.
if [ "$resolve"="true" ]; then sed -i 's@fa-jenkins2.intra.dlr.de@'"$CI_ARCHIVE"'@' Dockerfile; fi; 
# Reuse cache if available
# docker pull ${CI_IMAGE} || true
DOCKER_BUILDKIT=1 docker build --build-arg BUILDKIT_INLINE_CACHE=1 --network=host $* .
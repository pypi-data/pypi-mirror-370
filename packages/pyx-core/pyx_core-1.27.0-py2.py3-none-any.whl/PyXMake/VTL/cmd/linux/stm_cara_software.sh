#!/bin/bash
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                    	   Build environment for CARA/Linux (x64)                                %     
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Bash script for downloading and installing various software packages from source on CARA.
# Created on 03.07.2021
# 
# Version: 1.0
# -------------------------------------------------------------------------------------------------
#    Requirements and dependencies:
#        - 
#
#     Changelog:
#        - Created                                                                 // mg 02.07.2021
#        - Harmonized                                                              // mg 03.07.2021
#        - Added Code Aster installation (provided by Andreas.Schuster@dlr.de)     // mg 07.07.2021
#        - Added Singularity installation serving Docker container                 // mg 13.09.2021
#        - Added toogle to use internal development branches over external sources // mg 16.11.2021
#        - Added MCODAC redistribution package                                     // mg 18.11.2021
#
# -------------------------------------------------------------------------------------------------
#SBATCH --nodes=1
#SBATCH --time=06:00:00
#SBATCH --account=2263032
#SBATCH --tasks-per-node=1
#SBATCH --cpus-per-task=64
#SBATCH --output=install.log
#SBATCH --error=install.log
# Search command line for keyword
for i in "$@"
do
case $i in
    -a=*|--account=*)
    account="${i#*=}"
    shift # Move to next keyword
    ;;
    -c=*|--cpus=*)
    cpus="${i#*=}"
    shift # Move to next keyword
    ;;
    -d=*|--directory=*)
    directory="${i#*=}"
    shift # 
    ;;
    -p=*|--package=*)
    package="${i#*=}"
    shift # Past Argument=Value
    ;;
    -r=*|--refresh=*)
    refresh="${i#*=}"
    shift # 
    ;;
    -i=*|--internal=*)
    internal="${i#*=}"
    shift # 
    ;;
    -u=*|--user=*)
    user="${i#*=}"
    shift # Past Argument=Value
    ;;
    -t=*|--token=*)
    token="${i#*=}"
    shift # Past Argument=Value
    ;;
    *)    # Unknown option
    ;;
esac
done
# Check which package is requested for installation. Defaults to all.
export INSTALL_PACKAGE=${package:-"all"};
# Get default installation directory from command line. Defaults to user home directory
export INSTALL_DIR=${directory:-${HOME}/software}; 
# Get number of requested cpus
export ncpus=${cpus:-64}
# Get default account information
export account=${account:-2263032}
# Set flag to reinstall/refresh an existing installation. Defaults to False.
export refresh=${refresh:-"false"}
# Set flag to use toogle between internal projects over external references. Defaults to False.
export internal=${internal:-"false"}
# Set user and token (password) for non-interactive mode
export GIT_USER=${user:-""}; export GIT_PASSWORD=${token:-""}; 
# Default installation directory. Create base directory if not yet available.
mkdir -p ${INSTALL_DIR};
# Store GIT credentials locally in cache, expiring in 30mins.
git config credential.helper cache 1800s
if [[ "$GIT_USER" != "" && "$GIT_PASSWORD" != "" ]]; then git config --global url."https://${GIT_USER}:${GIT_PASSWORD}@gitlab.dlr.de/".insteadOf "https://gitlab.dlr.de/"; fi;
## Function definitions
# Create a function for creating a Conda Base environment
function cara_install_conda()
{
[ -d "${INSTALL_DIR}/conda" ] &&  return 0 || echo "Installing Conda (Forge)."
# Load all required modules (order matters!)
module purge; export PATH=$(getconf PATH)
# Reset shells PYTHONHOME and PYTHONPATH environment variables
unset PYTHONHOME; unset PYTHONPATH; 
# Downlaod miniforge from Git.
wget https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-$(uname)-$(uname -m).sh -O miniconda.sh
# Install conda and delete levtover files
chmod u+x miniconda.sh && ./miniconda.sh -b -p ${INSTALL_DIR}/conda && rm -rf miniconda.sh
# Download and install PyCODAC to create a elaborate default environment supporting all STM software projects.
git clone --single-branch --branch pyc_core https://gitlab.dlr.de/fa_sw/stmlab/PyCODAC.git pyc_core
source ${INSTALL_DIR}/conda/bin/activate base \
 && mamba env create -n stmlab -f pyc_core/PyCODAC/API/config/conda.yml \
 && source ${INSTALL_DIR}/conda/bin/activate stmlab \
 && pip install -r pyc_core/PyCODAC/API/config/pip.yml \
 && conda deactivate && rm -rf pyc_core \
 && chmod -R 777 ${INSTALL_DIR}/conda
}
export -f cara_install_conda
# Create a function to install PyCODAC into predefined conda environment.
function cara_install_pycodac()
{
# Check required dependencies first. If not yet present, install them first.
[ -d "${INSTALL_DIR}/conda" ] &&  echo "Found Conda." > /dev/null || cara_install_conda
# Uninstall previous version in case of refresh.
if [[ "$refresh" == "true" ]]; 
then 
  source ${INSTALL_DIR}/conda/bin/activate ${1:-stmlab} && pip uninstall -y pyc-core > /dev/null ; 
fi
# Download and install PyCODAC
export GIT_AUTH="";
# Get default values for authentification
if [[ "$GIT_USER" != "" && "$GIT_PASSWORD" != "" ]]; then export GIT_AUTH="${GIT_USER}:${GIT_PASSWORD}@"; fi; 
# Try to connect to download server. Timeout by 20 seconds
curl https://fa-jenkins2:8080/job/STM_Archive/lastSuccessfulBuild/artifact/Archive/pyc_core-latest-py2.py3-none-any.whl -o pyc_core-latest-py2.py3-none-any.whl --connect-timeout 20 --insecure --resolve fa-jenkins2:8080:129.247.54.235 > /dev/null
# Activate conda environment STMLab
source ${INSTALL_DIR}/conda/bin/activate ${1:-stmlab} \
 && { pip install pyc_core-latest-py2.py3-none-any.whl > /dev/null ; } \
 || { pip install pyc-core --index-url https://${GIT_AUTH}gitlab.dlr.de/api/v4/projects/12703/packages/pypi/simple ; } \
 && conda deactivate && rm -rf pyc_core-latest-py2.py3-none-any.whl
}
export -f cara_install_pycodac
# Create a function for creating MCODAC redistribution libraries.
function cara_install_mcodac()
{
# Check required dependencies first. If not yet present, install them first.
[ -d "${INSTALL_DIR}/conda" ] &&  echo "Found Conda." > /dev/null || cara_install_conda
 # Install MCODAC
if [ -d "${INSTALL_DIR}/mcodac" ]
then 
 echo "Found MCODAC." > /dev/null ;
else
 module purge; export PATH=$(getconf PATH); export LD_LIBRARY_PATH="";
 module load DLR/global;
 module load GCCcore/11.3.0;
 module load git/2.36.0-nodocs;
 git clone --single-branch --branch pyc_core https://gitlab.dlr.de/fa_sw/stmlab/PyCODAC.git pyc_core ; 
 # Load STMLab base environment
 return=$PWD && cd pyc_core && source ${INSTALL_DIR}/conda/bin/activate base ; 
 conda run -n stmlab python -c "import os; from PyCODAC import Core; Core.GetDevelopment('mcodac', output=os.getcwd(), platform='linux')" 
 conda deactivate && rm -rf pyc_core ; 
 mv mcodac.zip ${INSTALL_DIR}/mcodac.zip && cd ${INSTALL_DIR} && unzip -nu mcodac.zip -d mcodac && chmod 777 -R mcodac && rm -f mcodac.zip ; cd $return
fi
}
export -f cara_install_mcodac
# Create a function for downloading and installing Calculix
function cara_install_calculix()
{
# Check required dependencies first. If not yet present, install them first.
[ -d "${INSTALL_DIR}/conda" ] &&  echo "Found Conda." > /dev/null || cara_install_conda
 # Install Calculix
if [ -d "${INSTALL_DIR}/conda/envs/calculix" ]
then 
 echo "Found Calculix." > /dev/null ;
else
 # Load base environment
 source ${INSTALL_DIR}/conda/bin/activate base ; 
 conda create -y --name calculix calculix ;
 conda deactivate
fi
}
export -f cara_install_calculix
# Create a function for downloading and installing Code Aster
function cara_install_aster()
{
# Check required dependencies first. If not yet present, install them first.
[ -d "${INSTALL_DIR}/aster" ] &&  return 0 || echo "Installing Code Aster."
# Download Code ASTER into the current workspace
curl https://www.code-aster.org/FICHIERS/aster-full-src-14.6.0-1.noarch.tar.gz -o aster-full.tar.gz
mkdir -p aster-full
# Load all required modules (order matters!)
module purge; export PATH=$(getconf PATH)
# Use STM prebuild modules
module use /sw/DLR/FA/BS/STM/modulefiles
# Load all cluster dependencies
module load foss/2019a
module load Python
module load SciPy-bundle
module load flex
module load Bison
module load Xterm/3.5.1
module load boost/1.69.0
module load bash/5.1.8
export PYTHONHOME=$(dirname $(dirname $(which python)))
export LD_LIBRARY_PATH=$PYTHONHOME/lib:$LD_LIBRARY_PATH
export PATH=$PYTHONPATH:$PYTHONHOME/lib:$PATH
export LC_ALL=en_US.UTF-8
# Extract archive
tar -zxvf aster-full.tar.gz -C aster-full --strip-components 1 \
 && rm -f aster-full.tar.gz && cd aster-full \
 && sed -i 's/# mfront path\b/self.env["CATALO_CMD"] = "mpirun"/g' products_data.py
# Execute make command
[[ -z "${SLURM_JOB_NAME}" ]] && srun --ntasks=1 --account=${account} --cpus-per-task=${ncpus} --pty python setup.py install --noprompt --reinstall='ignore' --prefix=${INSTALL_DIR}/aster \
 || python setup.py install --noprompt --reinstall='ignore' --prefix=${INSTALL_DIR}/aster
cd .. && rm -rf aster-full
}
export -f cara_install_aster
# Create a function for downloading and installing Code Aster
function cara_install_b2000pp()
{
# Check required dependencies first. If not yet present, install them first.
[ -d "${INSTALL_DIR}/conda" ] &&  echo "Found Conda." > /dev/null || cara_install_conda
[ -d "${INSTALL_DIR}/simples" ] &&  return 0 || echo "Installing B2000++."
# Download B2000pp into the current workspace 
module purge; export PATH=$(getconf PATH); export LD_LIBRARY_PATH="";
module load DLR/global;
module load dos2unix/7.3.4;
module load GCC; 
module load OpenMPI; 
module load OpenBLAS; 
module load SCOTCH; 
module load Boost; 
module load ScaLAPACK;
# Install MUMPS
if [ -d "${INSTALL_DIR}/conda/envs/mumps" ]
then 
 echo "Found MUMPS." > /dev/null ;
else
 source ${INSTALL_DIR}/conda/bin/activate base ; 
 conda create -y --name mumps mumps ; 
 conda deactivate ; 
fi
# Load STMLab environment
source ${INSTALL_DIR}/conda/bin/activate stmlab
# Get latest version of CMake
if [ -d "${INSTALL_DIR}/cmake" ] 
then
  echo "Found CMake." > /dev/null ;
else
  export version=3.22 && export build=0 \
  && ( wget https://cmake.org/files/v$version/cmake-$version.$build-linux-x86_64.sh -O cmake.sh || wget https://cmake.org/files/v$version/cmake-$version.$build-Linux-x86_64.sh -O cmake.sh ) \
  && mkdir -p ${INSTALL_DIR}/cmake && bash cmake.sh --prefix=${INSTALL_DIR}/cmake --skip-license && rm -rf cmake.sh
fi
# Download B2000pp into the current workspace 
if [ -d "${INSTALL_DIR}/memcom" ] 
then 
 echo "Found memcom." > /dev/null ;
else 
 curl https://fa-jenkins2:8080/job/STM_Archive/lastSuccessfulBuild/artifact/Archive/Image/linux/memcom-master.tar.gz -o memcom.tar.gz --insecure --resolve fa-jenkins2:8080:129.247.54.235 \
 && mkdir -p memcom && tar -zxvf memcom.tar.gz -C memcom --strip-components 1 && rm -f memcom.tar.gz && cd memcom find . -type f -print0 | xargs -0 dos2unix \
 && mkdir -p memcom/build && cd memcom/build \
 && ${INSTALL_DIR}/cmake/bin/cmake -DCMAKE_PREFIX_PATH=${INSTALL_DIR} -DCMAKE_INSTALL_PREFIX=${INSTALL_DIR}/memcom ../../memcom && make install \
 && cd ../.. &&  rm -rd memcom ;
fi
## Depracation:
# Pymemcom is part of memcom and no longer a stand-alone project. Thus, the following
# code snippet is now longer necessary. It is kept for documentation purposes only. The download
# link is dead and cannot be used anymore.
if [ -d "${INSTALL_DIR}/pymemcom" ] || [ -d "${INSTALL_DIR}/memcom/share/pymemcom" ]
then 
 echo "Found pymemcom." > /dev/null ;
else
 # Additional dependencies defined here
 module load SWIG
 # Add memcom libs explicitly
 export PATH=${INSTALL_DIR}/memcom:${INSTALL_DIR}/memcom/include:${INSTALL_DIR}/memcom/lib64:$PATH ;
 curl https://fa-jenkins2:8080/job/STM_Archive/lastSuccessfulBuild/artifact/Archive/Image/linux/pymemcom-master.tar.gz -o pymemcom.tar.gz --insecure --resolve fa-jenkins2:8080:129.247.54.235 \
 && mkdir -p pymemcom && tar -zxvf pymemcom.tar.gz -C pymemcom --strip-components 1 && rm -f pymemcom.tar.gz && cd pymemcom find . -type f -print0 | xargs -0 dos2unix \
 && mkdir -p pymemcom/build && cd pymemcom/build \
 && ${INSTALL_DIR}/cmake/bin/cmake -DCMAKE_PREFIX_PATH=${INSTALL_DIR} -DCMAKE_INSTALL_PREFIX=${INSTALL_DIR}/pymemcom ../../pymemcom && make install \
 && cd ../.. && rm -rd pymemcom ;
fi
# Install B2000++
if [ -d "${INSTALL_DIR}/b2000pp" ] 
then 
 echo "Found B2000++." > /dev/null ;
else
 # Additional B2000 dependencies
 module load arpack-ng/3.7.0
 module load Bison
 module load NLopt
 module load flex
 module load GCC
 # Create a soft-link if non-existing
 ([ -d "${INSTALL_DIR}/pymemcom/lib64" ] || [ -d "${INSTALL_DIR}/memcom/share/pymemcom" ]) &&  echo "Found pymemcom." > /dev/null || ln -s ${INSTALL_DIR}/memcom/lib64 ${INSTALL_DIR}/pymemcom/lib64
 # Add memcom libs explicitly
 export PATH=${INSTALL_DIR}/memcom:${INSTALL_DIR}/memcom/include:${INSTALL_DIR}/memcom/lib64:${INSTALL_DIR}/conda/envs/mumps/lib:$PATH ;
 export PATH=${INSTALL_DIR}/memcom/lib/python3.7/site-packages:${INSTALL_DIR}/memcom/bin:${INSTALL_DIR}/memcom/share/memcom:${INSTALL_DIR}/memcom/share/pymemcom:$PATH ;
 ## Retain backwards compatibiity here. However, pymemcom is integrated in memcom in all versions going forward. 
 export PATH=${INSTALL_DIR}/pymemcom/lib/python3.7/site-packages:${INSTALL_DIR}/pymemcom/bin:${INSTALL_DIR}/pymemcom/share/pymemcom:$PATH ;
 export PATH=${INSTALL_DIR}/conda/envs/mumps/include:$PATH ;
 export PATH=/sw/DLR/global/b2000++pro/libs/tbb2019U9/include:$PATH ;
 export PATH=/sw/DLR/global/b2000++pro/libs/tbb2019U9/lib:$PATH ;
 export PATH=/sw/DLR/global/b2000++pro/libs/tbb2019U9/lib64:$PATH ;
 export LD_LIBRARY_PATH=:${INSTALL_DIR}/memcom/lib64:${INSTALL_DIR}/conda/envs/mumps/lib:$LD_LIBRARY_PATH
 export PYTHONPATH=${INSTALL_DIR}/pymemcom/lib/python3.7/site-packages:${INSTALL_DIR}/memcom/lib/python3.7/site-packages:${INSTALL_DIR}/memcom/lib64:${PYTHONPATH}
 curl https://fa-jenkins2:8080/job/STM_Archive/lastSuccessfulBuild/artifact/Archive/Image/linux/b2000pp-master.tar.gz -o b2000pp.tar.gz --insecure --resolve fa-jenkins2:8080:129.247.54.235 \
 && mkdir -p b2000pp && tar -zxvf b2000pp.tar.gz -C b2000pp --strip-components 1 && rm -f b2000pp.tar.gz && cd b2000pp && find . -type f -print0 | xargs -0 dos2unix \
 && curl https://fa-jenkins2:8080/job/STM_Archive/lastSuccessfulBuild/artifact/Archive/Image/linux/CMakeModules-master.tar.gz -o CMakeModules.tar.gz --insecure --resolve fa-jenkins2:8080:129.247.54.235 \
 && mkdir -p cmake && tar -zxvf CMakeModules.tar.gz -C cmake --strip-components 1 && rm -f CMakeModules.tar.gz && cd cmake && find . -type f -print0 | xargs -0 dos2unix && cd .. \
 && mkdir -p build && cd build \
 && ${INSTALL_DIR}/cmake/bin/cmake \
   -DUSE_MPI=ON \
   -DCMAKE_PREFIX_PATH=${INSTALL_DIR} \
   -DCMAKE_INSTALL_PREFIX=${INSTALL_DIR}/b2000pp ../../b2000pp
 # Execute make command
 [[ -z "${SLURM_JOB_NAME}" ]] && srun --ntasks=1 --cpus-per-task=${ncpus} --account=${account} --pty make -j${ncpus} install || make -j${ncpus} install
 cd ../.. ;  rm -rd b2000pp ;
fi
# Install postprocessor simples
if [ -d "${INSTALL_DIR}/simples" ] 
then 
 echo "Found Simples." > /dev/null ;
else
 # Import redefinition
 module purge ; export PATH=$(getconf PATH) ; 
 module load DLR/global
 module load dos2unix/7.3.4;
 module load intel/2020a
 module load GCC
 export PATH=${INSTALL_DIR}/memcom:${INSTALL_DIR}/memcom/include:${INSTALL_DIR}/memcom/lib64:${INSTALL_DIR}/conda/envs/mumps/lib:${INSTALL_DIR}/conda/envs/mumps/include:$PATH ;
 export PATH=${INSTALL_DIR}/b2000pp/lib64:${INSTALL_DIR}/b2000pp/include:$PATH ;
 export LD_LIBRARY_PATH=${INSTALL_DIR}/b2000pp/lib64:${INSTALL_DIR}/memcom/lib64:${INSTALL_DIR}/conda/envs/mumps/lib:${INSTALL_DIR}/conda/envs/mumps/include:$LD_LIBRARY_PATH
 export PYTHONPATH=${INSTALL_DIR}/pymemcom/lib/python3.7/site-packages:${INSTALL_DIR}/memcom/lib/python3.7/site-packages:${INSTALL_DIR}/memcom/lib64:${INSTALL_DIR}/conda/envs/mumps/include:${PYTHONPATH} ; 
 export CPATH=${CPATH}:${INSTALL_DIR}/conda/envs/mumps/include
 # Download and install simples
 curl https://fa-jenkins2:8080/job/STM_Archive/lastSuccessfulBuild/artifact/Archive/Image/linux/simples-master.tar.gz -o simples.tar.gz --insecure --resolve fa-jenkins2:8080:129.247.54.235 \
 && mkdir -p simples && tar -zxvf simples.tar.gz -C simples --strip-components 1 && rm -f simples.tar.gz && cd simples && find . -type f -print0 | xargs -0 dos2unix \
 && curl https://fa-jenkins2:8080/job/STM_Archive/lastSuccessfulBuild/artifact/Archive/Image/linux/CMakeModules-master.tar.gz -o CMakeModules.tar.gz --insecure --resolve fa-jenkins2:8080:129.247.54.235 \
 && mkdir -p cmake && tar -zxvf CMakeModules.tar.gz -C cmake --strip-components 1 && rm -f CMakeModules.tar.gz && cd cmake && find . -type f -print0 | xargs -0 dos2unix && cd .. \
 && mkdir -p build && cd build \
 && ${INSTALL_DIR}/cmake/bin/cmake \
   -DCMAKE_PREFIX_PATH=${INSTALL_DIR} \
   -DCMAKE_INSTALL_PREFIX=${INSTALL_DIR}/simples ../../simples
 # Execute make command
 [[ -z "${SLURM_JOB_NAME}" ]] && srun --ntasks=1 --cpus-per-task=${ncpus} --account=${account} --pty make -j${ncpus} install || make -j${ncpus} install
 cd ../.. ;  rm -rd simples ;
fi
}
export -f cara_install_b2000pp
# Create a function for downloading and installing libyaml
function cara_install_libyaml()
{
# Delete existing installation if requested
if [[ "$refresh" == "true" ]]; then rm -rf ${INSTALL_DIR}/libyaml; fi;
[ -d "${INSTALL_DIR}/libyaml" ] &&  return 0 || echo "Installing LibYAML."
# Download libyaml into the current workspace
git clone https://github.com/jbeder/yaml-cpp.git libyaml 2> /dev/null || (cd libyaml ; git pull);
mkdir -p libyaml/build;
# Reset all paths
export PATH=$(getconf PATH); export LD_LIBRARY_PATH="";
# Load all required modules (order matters!)
module purge; 
module load GCC; 
module load GCCcore/10.2.0; 
module load CMake/3.18.4;
# Go into build directory
cd libyaml/build
# Execute CMake to prepare the make script
cmake \
-DYAML_BUILD_SHARED_LIBS=ON \
-DCMAKE_INSTALL_PREFIX=${INSTALL_DIR}/libyaml ../../libyaml
# Execute make command
[[ -z "${SLURM_JOB_NAME}" ]] && srun --ntasks=1 --account=${account} --pty make install || make install
# Clean up workspace if successfull
cd ../.. ; rm -rf libyaml
}
export -f cara_install_libyaml
# Create a function for downloading and installing Trilinos
function cara_install_trilinos()
{
# Delete existing installation if requested
if [[ "$refresh" == "true" ]]; then rm -rf ${INSTALL_DIR}/trilinos; fi;
# Check required dependencies first. If not yet present, install them first.
[ -d "${INSTALL_DIR}/libyaml" ] &&  echo "Found LibYAML." > /dev/null || cara_install_libyaml
[ -d "${INSTALL_DIR}/trilinos" ] &&  return 0 || echo "Installing Trilinos."
# Download Trilinos into the current workspace
git clone https://github.com/trilinos/Trilinos.git trilinos 2> /dev/null || (cd trilinos ; git pull);
# Restrict supported release of Trilinos. Trilinos above 13.2 currently contains a bug, wherein the latest
# version of libyaml (> 0.6) is not supported due to unsupported boolean casting of a variable. This behaviour
# was changed in libyaml but not honored in Trilinos. 
(cd trilinos; git fetch --all --tags; git checkout tags/trilinos-release-13-2-0 -b release; cd .. ) || true;
mkdir -p trilinos/build;
# Reset all paths
export PATH=$(getconf PATH); export LD_LIBRARY_PATH="";
# Load all required modules (order matters!)
module purge; 
module load GCC; 
module load OpenMPI; 
module load OpenBLAS; 
module load netCDF; 
module load Boost; 
module load ScaLAPACK; 
module load GCCcore/8.3.0; 
module load HDF5; 
module load GCCcore/10.2.0; 
module load CMake/3.18.4;
# Go into build directory
cd trilinos/build
# Execute CMake to prepare the make script
cmake \
-DTPL_ENABLE_MPI=ON \
-DTPL_ENABLE_Matio=OFF \
-DTPL_ENABLE_HDF5=ON \
-DTPL_LAPACK_LIBRARIES='/sw/MPI/GCC/8.2.0-2.31.1/OpenMPI/3.1.3/ScaLAPACK/2.0.2-OpenBLAS-0.3.5/lib/liblapack.a' \
-DTPL_ENABLE_yaml-cpp=ON \
-DTPL_yaml-cpp_LIBRARIES=${INSTALL_DIR}/libyaml/lib64/libyaml-cpp.so \
-DTPL_yaml-cpp_INCLUDE_DIRS=${INSTALL_DIR}/libyaml/include/yaml-cpp \
-DTrilinos_ENABLE_ALL_PACKAGES=ON \
-DCMAKE_INSTALL_PREFIX=${INSTALL_DIR}/trilinos ../../trilinos
# Execute make command
[[ -z "${SLURM_JOB_NAME}" ]] && srun --ntasks=1 --account=${account} --cpus-per-task=${ncpus} --pty make -j${ncpus} install || make -j${ncpus} install
# Clean up workspace if successfull
cd ../.. ; rm -rf trilinos
}
export -f cara_install_trilinos
# Create a function for downloading and installing Peridigm
function cara_install_peridigm()
{
# Support multiple repositories and versions for Peridigm simultaneously
export repository=${1:-"https://github.com/peridigm/peridigm.git"}
export version=${2:-"peridigm"}
## Support installation of internal development branches
if [[ "$internal" == "true" ]]; 
then 
  export repository="https://gitlab.dlr.de/fa_sw/stmlab/plugins/peridev.git";
  export version="peridev"; 
fi
# Delete existing installation if requested
if [[ "$refresh" == "true" ]]; then rm -rf ${INSTALL_DIR}/${version}; fi;
# Check required dependencies first. If not yet present, install them first.
[ -d "${INSTALL_DIR}/trilinos" ] &&  echo "Found Trilinos." > /dev/null || cara_install_trilinos
[ -d "${INSTALL_DIR}/${version}" ] &&  return 0 || echo "Installing Peridigm."
# Download Peridigm into the current workspace
git clone ${repository} ${version} 2> /dev/null || (cd ${version} ; git pull);
mkdir -p ${version}/build;
# Reset all paths
export PATH=$(getconf PATH); export LD_LIBRARY_PATH="";
# Load all required modules (order matters!)
module purge; 
module load GCC; 
module load OpenMPI; 
module load OpenBLAS; 
module load netCDF; 
module load Boost; 
module load ScaLAPACK; 
module load GCCcore/8.3.0; 
module load HDF5; 
module load GCCcore/10.2.0; 
module load CMake/3.18.4;
# Go into build directory
cd ${version}/build
## Check if additional user materials are being defined. This applies only to the internal Peridigm branch.
if [[ "$internal" == "true" ]]; then export user="-DUSER_LIBRARY_DIRS=src/materials/umats" ; fi;
## Execute CMake to prepare the make script. Check if source code accepts MCODAC 
# and all dependencies can be resolved.
# Execute CMake to prepare the make script
CMAKE_CUSTOM_FLAGS="-DMPICH_IGNORE_CXX_SEEK -O2 -Wall -ftrapv -Wno-deprecated -Wl,-rpath=${ORIGIN}:${LD_LIBRARY_PATH}:${INSTALL_DIR}/${version}/bin:${INSTALL_DIR}/mcodac/bin: -Wl,--enable-new-dtags"
if [[ -d "${INSTALL_DIR}/mcodac" ]];
then
 cmake \
 -DUSE_MCODAC=ON \
 -DCMAKE_CXX_COMPILER="mpicxx" \
 -DCMAKE_BUILD_TYPE=Release \
 -DCMAKE_PREFIX_PATH=${INSTALL_DIR} \
 -DCMAKE_CXX_FLAGS="-DUSE_MCODAC ${CMAKE_CUSTOM_FLAGS}" \
 -DCMAKE_EXE_LINKER_FLAGS="${pyx_per_linking:--L${INSTALL_DIR}/mcodac/bin -lperuser}" \
 -DCMAKE_INSTALL_PREFIX=${INSTALL_DIR}/${version} ${user:-""} ../../${version}
else
 cmake \
 -DCMAKE_CXX_COMPILER="mpicxx" \
 -DCMAKE_BUILD_TYPE=Release \
 -DCMAKE_PREFIX_PATH=${INSTALL_DIR} \
 -DCMAKE_CXX_FLAGS=${CMAKE_CUSTOM_FLAGS} \
 -DCMAKE_INSTALL_PREFIX=${INSTALL_DIR}/${version} ${user:-""} ../../${version}
fi
# Execute make command
[[ -z "${SLURM_JOB_NAME}" ]] && srun --ntasks=1 --account=${account} --cpus-per-task=${ncpus} --pty make -j${ncpus} install || make -j${ncpus} install
if [[ "$internal" == "true" ]]; then cp -n ../../${version}/src/materials/umats/*.so ${INSTALL_DIR}/${version}/bin ; fi;
# Clean up workspace if successfull
cd ../.. ; rm -rf ${version}
}
export -f cara_install_peridigm
# Create a function for creating a GO base environment serving Singularity.
function cara_install_singularity()
{
# Check required dependencies first. If not yet present, install them first.
[ -d "${INSTALL_DIR}/conda" ] &&  echo "Found Conda." > /dev/null || cara_install_conda
[ -d "${INSTALL_DIR}/go" ] &&  return 0 || echo "Installing Singularity."
# Create a fresh environment
module purge; export PATH=$(getconf PATH)
 # Install SQUASHFS for image packaging
if [ -d "${INSTALL_DIR}/conda/envs/squashfs" ]
then 
 echo "Found SquashFS." > /dev/null ;
else
 source ${INSTALL_DIR}/conda/bin/activate base ; 
 conda create -y --name squashfs squashfs-tools ; 
 conda deactivate ; 
 export PATH=PATH=${INSTALL_DIR}/conda/envs/squashfs/bin:${PATH}
fi
# Downlaod and install GO
export VERSION=1.17.3 OS=linux ARCH=amd64 \
&& wget https://dl.google.com/go/go$VERSION.$OS-$ARCH.tar.gz \
&& mkdir -p ${INSTALL_DIR} \
&& tar -C ${INSTALL_DIR} -xzvf go$VERSION.$OS-$ARCH.tar.gz \
&& rm go$VERSION.$OS-$ARCH.tar.gz
# Download and install dependency manager
export GOPATH=${INSTALL_DIR}/go/user && export VERSION=v3.9.0 \
&& mkdir -p $GOPATH/src/github.com/sylabs \
&& cd $GOPATH/src/github.com/sylabs \
&& git clone https://github.com/sylabs/singularity.git \
&& cd $GOPATH/src/github.com/sylabs/singularity \
&& git fetch && git checkout ${VERSION} \
&& PATH=${INSTALL_DIR}/go/bin:${GOPATH}:${PATH} \
&& ./mconfig --prefix=${INSTALL_DIR}/singularity --without-suid \
&& cd builddir && make
# Execute make command
[[ -z "${SLURM_JOB_NAME}" ]] && srun --ntasks=1 --account=${account} --cpus-per-task=${ncpus} --pty make -j${ncpus} install || make -j${ncpus} install
}
export -f cara_install_singularity
# Execute installation procedures
if [[ "$INSTALL_PACKAGE" == "all" || "$INSTALL_PACKAGE" == "conda" ]]; then cara_install_conda; fi;
if [[ "$INSTALL_PACKAGE" == "all" || "$INSTALL_PACKAGE" == "libyaml" ]]; then cara_install_libyaml; fi;
if [[ "$INSTALL_PACKAGE" == "all" || "$INSTALL_PACKAGE" == "trilinos" ]]; then cara_install_trilinos; fi;
if [[ "$INSTALL_PACKAGE" == "all" || "$INSTALL_PACKAGE" == "peridigm" ]]; then cara_install_peridigm; fi;
if [[ "$INSTALL_PACKAGE" == "all" || "$INSTALL_PACKAGE" == "calculix" ]]; then cara_install_calculix; fi;
if [[ "$INSTALL_PACKAGE" == "all" || "$INSTALL_PACKAGE" == "mcodac" ]]; then cara_install_mcodac; fi;
if [[ "$INSTALL_PACKAGE" == "all" || "$INSTALL_PACKAGE" == "pycodac" ]]; then cara_install_pycodac; fi;
if [[ "$INSTALL_PACKAGE" == "all" || "$INSTALL_PACKAGE" == "b2000pp" ]]; then cara_install_b2000pp; fi;
if [[ "$INSTALL_PACKAGE" == "all" || "$INSTALL_PACKAGE" == "singularity" ]]; then cara_install_singularity; fi;
# if [[ "$INSTALL_PACKAGE" == "all" || "$INSTALL_PACKAGE" == "aster" ]]; then cara_install_aster; fi;

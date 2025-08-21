@REM %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@REM %                    		PyXMake 4 Jenkins on Windows 7/10 (x64)                             %
@REM %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@REM Command script to run PyXMake jobs on Jenkins (FA-STM).
@REM Created on 18.05.2018
@REM 
@REM Version: 1.0
@REM -------------------------------------------------------------------------------------------------
@REM    Requirements and dependencies:
@REM        - 
@REM
@REM     Changelog:
@REM        - Added dummy Python 36 to build process // mg 07.11.2019
@REM        - Added support for Windows 10 (Jenkins 2.0)
@REM	
@REM -------------------------------------------------------------------------------------------------
@ECHO OFF
@SETLOCAL EnableDelayedExpansion

@TITLE %~nx0
@REM This script is mostly executed on the Jenkins test server.
@IF %COMPUTERNAME% == FA-JENKINS2 (
@SET USERNAME=f_testpa
@SET USERPROFILE=C:\Users\%USERNAME%
@SET STM_MAKE=py37_stmlab
@SET "PATH=C:\Miniforge_envs;%PATH%"
)

@REM Activate latest make environment
@IF NOT DEFINED STM_CONDA SET "STM_CONDA=py37_stmlab"

@REM Get current windows realease
@FOR /f "tokens=4-7 delims=[.] " %%i IN ('ver') DO (if %%i==Version (SET v=%%j.%%k) ELSE (SET v=%%i.%%j))
@SET make_windows_version=%v%

@IF NOT %make_windows_version% == 10.0 (
@REM Redefine MPI directories.
@REM -------------------------------------------------------------------------------------------------
@SET MSMPI_BIN="C:\Program Files\Microsoft MPI\Bin\"
@SET MSMPI_INC="C:\Program Files (x86)\Microsoft SDKs\MPI\Include\"
@SET MSMPI_LIB32="C:\Program Files (x86)\Microsoft SDKs\MPI\Lib\x86\"
@SET MSMPI_LIB64="C:\Program Files (x86)\Microsoft SDKs\MPI\Lib\x64\"
@REM -------------------------------------------------------------------------------------------------

@REM -------------------------------------------------------------------------------------------------
IF EXIST pyxmake_env GOTO ENV_READY
    pip install virtualenv
    virtualenv --distribute --system-site-packages pyxmake_env
    pip install -r requires-dev.txt
:ENV_READY 
@REM -------------------------------------------------------------------------------------------------
)

@IF %make_windows_version% == 10.0 (
@REM Activate powershell scripts for the current active user.
@CALL powershell -c "Set-ExecutionPolicy Unrestricted -Scope CurrentUser" >> nul
)

@REM Check if current workspace is a GIT repository
FOR /F "tokens=* USEBACKQ" %%F IN (`powershell -c "(git rev-parse --is-inside-work-tree) -or 0"`) DO (
SET GIT=%%F
)

@REM Set to False if not defined
IF NOT DEFINED GIT SET "GIT=False"

@REM Store pristine paths
@SET pristine_workspace="%CD%"
@SET pristine_path="%path%"
@SET pristine_pythonpath="%pythonpath%"

@REM Get current workspace and crop final backslash for convienience
CD %~dp0 && CD ..

@REM Define user paths
@IF NOT DEFINED stm_workspace SET "stm_workspace=%CD%"

@REM Set script paths
@SET workspace=%stm_workspace%

@REM Go back to pristine workspace
CD "%pristine_workspace%"

@REM Check if current workspace is a GIT repository
IF %GIT% == True (

@REM Set all build variables
@SET workspace=%CD%
@SET environment=%workspace%\PyCODAC\__setenv__.py
@SET makefile=%workspace%\PyCODAC\Plugin\PyXMake\VTL

@REM Activate local CONDA environment
@CALL conda activate %stm_conda% || CALL conda activate py37

@REM Run all predefined test scripts in the given conda environment
python !environment! !makefile!\doxygen.py
python !environment! !makefile!\ifort.py
python !environment! !makefile!\py2x.py
python !environment! !makefile!\java.py
python !environment! !makefile!\abaqus.py
python !environment! !makefile!\gfortran.py
python !environment! !makefile!\chocolatey.py

@REM SVN style of make script. Kept in here for backwards compatibility.
@REM Deprecated. Should not be executed anymore.
) ELSE (

@REM Get makefile
@SET makefile=%workspace%\PyXMake\stm_make.py

@REM Source code directories.
@SET stm_pyxmake=%workspace%\PyXMake\src\pyx_core
@SET stm_pycodac=%workspace%\MCODAC\src\mcd_pycodac

@REM -------------------------------------------------------------------------------------------------
@REM Add ABAQUS executable to environment variable. Use always the 
@REM latest installment for all builds. 
@SET pyx_abaqus=abaqus

@REM Define local job paths. // Scratch Directory.
@SET scratch=%workspace%\build

@REM Define base path names for BoxBeam & MCODAC.
@SET box_base=%workspace%\BoxBeam
@SET mcd_base=%workspace%\MCODAC

@REM Source code directories.
@SET pyx_source=%workspace%\PyXMake\src\pyx_core
@SET beos_source=%workspace%\Beos\src
@SET box_source=%workspace%\BoxBeam\src
@SET mcd_source=%workspace%\MCODAC\src\mcd_core
@SET mcd_pycodac=%workspace%\MCODAC\src\mcd_pycodac
@SET mcd_mapsrc=%workspace%\MCODAC\src\mcd_mapper
@SET mcd_subsrc=%workspace%\MCODAC\src\mcd_subbuckling

@REM Html documentation output paths.
@SET pyx_core_html=%workspace%\PyXMake\doc\src\pyx_core
@SET box_beam_html=%workspace%\BoxBeam\doc\src\box_core
@SET mcd_core_html=%workspace%\MCODAC\doc\src\mcd_core
@SET mcd_pycodac_html=%workspace%\MCODAC\doc\src\mcd_pycodac
@SET mcd_mapper_html=%workspace%\MCODAC\doc\src\mcd_mapper
@SET mcd_subbuck_html=%workspace%\MCODAC\doc\src\mcd_subbuckling

@REM Python package output paths.
@SET beos_f2pyout=%workspace%\Beos\bin\windows\x64
@SET box_f2pyout=%workspace%\BoxBeam\bin\windows\x64
@SET mcd_f2pyout=%workspace%\MCODAC\bin\windows\x64

@REM Java output paths (shared library).
@SET box_javaout=%box_f2pyout%
@SET mcd_javaout=%mcd_f2pyout%

@REM Static library output paths.
@SET box_libout=%workspace%\BoxBeam\lib\windows\x64
@SET mcd_libout=%workspace%\MCODAC\lib\windows\x64

@REM Shared library source and output paths (ABAQUS). 
@SET abq_source=%workspace%\MCODAC\src\mcd_solver
@SET abq_libout=%workspace%\MCODAC\bin\windows\x64

@REM Define source files for ABAQUS Standard & Explicit. 
@SET standard=mcd_astandard
@SET explicit=mcd_aexplicit
@REM -------------------------------------------------------------------------------------------------

@REM Add ABAQUS commands.
@REM -------------------------------------------------------------------------------------------------
@SET abaqus=C:\SIMULIA\Abaqus\Commands;C:\SIMULIA\Commands
@REM -------------------------------------------------------------------------------------------------

@REM Add defined paths to environment variables.
@REM -------------------------------------------------------------------------------------------------
@SET PATH=%stm_pyxmake%;%abaqus%;%workspace%;%pristine_path%
@REM -------------------------------------------------------------------------------------------------

@REM %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@REM Additional build process for Python 35
@REM %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@REM Add Python executable paths and add all custom packages. 
@REM -------------------------------------------------------------------------------------------------
@CALL conda activate py35_stmlab || CALL conda activate py35
@SET PYTHONPATH=%stm_pyxmake%;%workspace%;%pythonpath%
@REM -------------------------------------------------------------------------------------------------

@REM Build documentation.
@REM -------------------------------------------------------------------------------------------------
python %makefile%^
 doxy_boxbeam --source-path=%box_source% --scratch-path=%scratch% --output-file-path=%box_beam_html%^
 doxy_mcdcore --source-path=%mcd_source% --scratch-path=%scratch% --output-file-path=%mcd_core_html%^
 doxy_pyxmake --source-path=%pyx_source% --scratch-path=%scratch% --output-file-path=%pyx_core_html% --stype="Python"^
 doxy_mcdpycodac --source-path=%mcd_pycodac% --scratch-path=%scratch% --output-file-path=%mcd_subbuck_html% --stype="Python"^
 doxy_mcdmapper --source-path=%mcd_mapsrc% --scratch-path=%scratch% --output-file-path=%mcd_mapper_html% --stype="Java"^
 doxy_mcdsubbuck --source-path=%mcd_subsrc% --scratch-path=%scratch% --output-file-path=%mcd_subbuck_html% --stype="Java"^
 clean
@REM -------------------------------------------------------------------------------------------------

@REM Build core utils.
@REM -------------------------------------------------------------------------------------------------
python %makefile%^
 f2py_beos --source-path=%beos_source% --scratch-path=%scratch% --output-file-path=%beos_f2pyout%^
 f2py_boxbeam --source-path=%box_source% --scratch-path=%scratch% --output-file-path=%box_f2pyout%^
 f2py_mcodac --source-path=%mcd_source% --base-path=%mcd_base% --scratch-path=%scratch% --output-file-path=%mcd_f2pyout%^
 java_boxbeam --source-path=%box_source% --base-path=%mcd_base% --scratch-path=%scratch% --output-file-path=%box_javaout% --btype="shared"^
 java_mcodac --source-path=%mcd_source% --base-path=%mcd_base% --scratch-path=%scratch% --output-file-path=%mcd_javaout% --btype="shared"^
 win_boxbeam --source-path=%box_source% --base-path=%box_base% --scratch-path=%scratch% --output-file-path=%box_libout%^
 win_mcodac --source-path=%mcd_source% --base-path=%mcd_base% --scratch-path=%scratch% --output-file-path=%mcd_libout%^
 clean
@REM -------------------------------------------------------------------------------------------------

@REM Build solver utils.
@REM -------------------------------------------------------------------------------------------------
python %makefile%^
 abq_mcodac --source-path=%abq_source% --source-file=%standard% --base-path=%mcd_base% --scratch-path=%scratch% --output-file-path=%abq_libout%^
 clean
python %makefile%^
 abq_mcodac --source-path=%abq_source% --source-file=%explicit% --base-path=%mcd_base% --scratch-path=%scratch% --output-file-path=%abq_libout%^
 clean
@REM ------------------------------------------------------------------------------------------------

@REM %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@REM Additional build process for Python 36
@REM %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@REM Add Python executable paths and add all custom packages. 
@REM -------------------------------------------------------------------------------------------------
@CALL conda deactivate
@CALL conda activate py36_stmlab || CALL conda activate py36
@SET PYTHONPATH=%stm_pyxmake%;%workspace%;%pythonpath%
@REM -------------------------------------------------------------------------------------------------

@REM Build Beos, BoxBeam and MCODAC for Python36
@REM -------------------------------------------------------------------------------------------------
python %makefile%^
 f2py_beos --source-path=%beos_source% --scratch-path=%scratch% --output-file-path=%beos_f2pyout%^
 f2py_boxbeam --source-path=%box_source% --scratch-path=%scratch% --output-file-path=%box_f2pyout%^
 f2py_mcodac --source-path=%mcd_source% --base-path=%mcd_base% --scratch-path=%scratch% --output-file-path=%mcd_f2pyout%^
 clean
@REM -------------------------------------------------------------------------------------------------

@REM %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@REM Additional build process for Python 37
@REM %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@REM Add Python executable paths and add all custom packages. 
@REM -------------------------------------------------------------------------------------------------
@CALL conda deactivate
@CALL conda activate %stm_conda%
@SET PYTHONPATH=%stm_pyxmake%;%workspace%;%pythonpath%
@REM -------------------------------------------------------------------------------------------------

@REM Build Beos, BoxBeam and MCODAC for Python36
@REM -------------------------------------------------------------------------------------------------
python %makefile%^
 f2py_beos --source-path=%beos_source% --scratch-path=%scratch% --output-file-path=%beos_f2pyout%^
 f2py_boxbeam --source-path=%box_source% --scratch-path=%scratch% --output-file-path=%box_f2pyout%^
 f2py_mcodac --source-path=%mcd_source% --base-path=%mcd_base% --scratch-path=%scratch% --output-file-path=%mcd_f2pyout%^
 clean
@REM -------------------------------------------------------------------------------------------------

@REM %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

@REM Commit changes in trunk folders.
@REM -------------------------------------------------------------------------------------------------
@SET Beos=%workspace%\Beos
@SET BoxBeam=%workspace%\BoxBeam
@SET MCODAC=%workspace%\MCODAC

svn commit %Beos% --message "Daily compiled version of Beos library" --non-interactive
svn commit %BoxBeam% --message "Daily compiled version of BoxBeam library" --non-interactive
svn commit %MCODAC% --message "Daily compiled version of MCODAC library" --non-interactive
@REM -------------------------------------------------------------------------------------------------

@REM %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

@REM %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@REM Reset pristine environment for Python 36 API
@REM %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@CALL conda deactivate

@REM Set up API
@REM -------------------------------------------------------------------------------------------------
@REM Define output directory. 
@SET Service=%workspace%\Service
@SET Target=%Service%\PyCODAC
@REM -------------------------------------------------------------------------------------------------

@REM Get apifile. Setting the correct environment first.
@SET apifile=%Target%\__setenv__.py %Target%\API\Jenkins.py

@REM Terminate all scheduled API tasks before copying. Create a fresh copy of PyCODAC
@REM -------------------------------------------------------------------------------------------------
schtasks /end /TN pyc_api 1>NUL 2>&1
taskkill /IM cmd.exe /FI "WINDOWTITLE eq mcd2api*" 1>NUL 2>&1
@RD /S /Q %Target% 1>NUL 2>&1
@REM -------------------------------------------------------------------------------------------------

@REM Create new copies of PyXMake/PyCODAC to spawn tasks in 
@REM -------------------------------------------------------------------------------------------------
robocopy %stm_pyxmake%\PyXMake %Service%\PyXMake /MIR /IS /IT /XD .svn /XA:SH 1>NUL 2>&1
robocopy %stm_pycodac%\PyCODAC %Service%\PyCODAC /MIR /IS /IT /XD .svn /XA:SH 1>NUL 2>&1
@REM -------------------------------------------------------------------------------------------------

@REM Add Python executable paths and add all custom packages. 
@REM -------------------------------------------------------------------------------------------------
@CALL conda activate %stm_conda%
@SET PYTHONPATH=%stm_pyxmake%;%workspace%;%pythonpath%
@REM -------------------------------------------------------------------------------------------------

@REM Restart all scheduled API tasks after the build process.
@REM -------------------------------------------------------------------------------------------------
ECHO =======================================
ECHO Starting API
ECHO =======================================
python %apifile%
@REM -------------------------------------------------------------------------------------------------
@EXIT 0
)
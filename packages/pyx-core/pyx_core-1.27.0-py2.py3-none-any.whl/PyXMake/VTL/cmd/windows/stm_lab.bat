@REM %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@REM %                    	    	PyXMake 4 Jenkins on Windows 10 (x64)                           %
@REM %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@REM Command script to run PyXMake jobs on Jenkins (FA-STM).
@REM Created on 11.05.2020
@REM 
@REM Version: 1.0
@REM -------------------------------------------------------------------------------------------------
@REM    Requirements and dependencies:
@REM        - 
@REM
@REM     Changelog:
@REM        - Created // mg 11.05.2020
@REM	
@REM -------------------------------------------------------------------------------------------------
@ECHO OFF
@SETLOCAL EnableDelayedExpansion
@TITLE %~nx0
@REM This script is mostly executed on the Jenkins test server.
@IF %COMPUTERNAME% == FA-JENKINS2 (
@SET USERNAME=f_testpa
@SET USERPROFILE=C:\Users\%USERNAME%
@SET STM_LAB=py37_stmlab
@SET "PATH=C:\Miniforge_envs;%PATH%"
)

@REM Activate lab conda environment
@IF NOT DEFINED STM_LAB SET "STM_LAB=py37"

@REM Activate powershell scripts for the current active user.
@CALL powershell -c "Set-ExecutionPolicy Unrestricted -Scope CurrentUser" >> nul

@REM Store pristine paths
@SET pristine_workspace=%CD%
@SET pristine_path=%path%
@SET pristine_pythonpath=%pythonpath%

@REM Get current workspace and crop final backslash for convenience.
CD %~dp0 && CD ..

@REM Define user paths
@IF NOT DEFINED stm_workspace SET "stm_workspace=%CD%"
@IF NOT DEFINED stm_service   SET "stm_service=%CD%\Service"

@REM To back to initial work space
CD %pristine_workspace%

@REM Prevent error message from GIT from popping up while packaging.
@SET GIT_PYTHON_REFRESH=quiet

@REM Add defined paths to environment variables.
@REM -------------------------------------------------------------------------------------------------
@REM Set script paths
@SET workspace=%stm_workspace%

@REM Define output directory. 
@SET service=%stm_service%

@REM Define local scratch directory.
@SET scratch=%pristine_workspace%\build

@REM Define local assembly directory and create it, if it does not already exist.
@SET assembly=%pristine_workspace%\build\DLR
@MKDIR %assembly% 2> NUL
@MKDIR %service% 2> NUL

@REM Source code directories.
@SET stm_pycodac=%workspace%
@SET stm_pyxmake=%stm_pycodac%\PyCODAC\Plugin
@SET stm_source=%stm_pycodac%\PyCODAC

@REM ReadTheDocs directory
@SET stm_rtd_source=%stm_source%\VTL\doc\mcd_stmlab\source
@SET stm_rtd_html=%stm_source%\VTL\doc\mcd_stmlab

@REM Get makefile
@SET makefile=%stm_pyxmake%\PyXMake\VTL\stm_make.py
@REM -------------------------------------------------------------------------------------------------

@REM Add Python executable paths and add all custom packages. 
@REM -------------------------------------------------------------------------------------------------
@CALL conda activate %stm_lab%
@SET PYTHONPATH=%stm_pyxmake%;%stm_pycodac%;%workspace%;%pythonpath%
@REM -------------------------------------------------------------------------------------------------

@REM Rebuild JupyterLab application to set a custom name.
@REM -------------------------------------------------------------------------------------------------
@CALL jupyter lab build --name='STMLab'
@CALL jupyter lab clean
@REM -------------------------------------------------------------------------------------------------

@REM Install all PyCODAC dependencies on the fly
@REM -------------------------------------------------------------------------------------------------
@CALL python -c "import PyCODAC"
@REM -------------------------------------------------------------------------------------------------

@REM Build standalone application.
@REM -------------------------------------------------------------------------------------------------
python %makefile%^
 app_pycodac --source-path=%stm_source% --scratch-path=%scratch% --output-file-path=%assembly%^
 bundle_pycodac --source-path=%assembly% --scratch-path=%scratch% --output-file-path=%service%^
 clean
@REM -------------------------------------------------------------------------------------------------

@REM Build documentation using scheme from Read The Docs.
@REM -------------------------------------------------------------------------------------------------
python %makefile%^
 sphinx_stmlab --source-path=%stm_rtd_source% --output-file-path=%stm_rtd_html% --scratch-path=%scratch%^
 clean
@REM -------------------------------------------------------------------------------------------------

@REM Revert changes in JupyterLab application
@REM -------------------------------------------------------------------------------------------------
@CALL jupyter lab build --name='JupyterLab'
@CALL jupyter lab clean
@REM -------------------------------------------------------------------------------------------------
@EXIT 0
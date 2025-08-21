@REM %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@REM %                    	    	Docker 4 Jenkins on Windows 10 (x64)                        %
@REM %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@REM Command script to run PyXMake jobs on Jenkins (FA-STM).
@REM Created on 26.01.2021
@REM 
@REM Version: 1.0
@REM -------------------------------------------------------------------------------------------------
@REM    Requirements and dependencies:
@REM        - 
@REM
@REM     Changelog:
@REM        - Created // mg 26.01.2021
@REM	
@REM -------------------------------------------------------------------------------------------------
@ECHO OFF
@SETLOCAL EnableDelayedExpansion

@TITLE %~nx0
@REM This script is mostly executed on the Jenkins test server.
@IF %COMPUTERNAME% == FA-JENKINS2 (
@SET STM_LAB=py37_stmlab
@SET "PATH=C:\Miniforge_envs;C:\Windows\Sysnative;%PATH%"
)

@REM If GIT user and/or GIT token is not given, use Docker credentials
IF NOT DEFINED GIT_USER  SET GIT_USER=%DOCKER_USER%
IF NOT DEFINED GIT_TOKEN SET GIT_TOKEN=%DOCKER_PASSWORD%

@REM Activate lab conda environment
@IF NOT DEFINED STM_LAB SET "STM_LAB=py37"

@REM Activate powershell scripts for the current active user.
@CALL powershell -c "Set-ExecutionPolicy Unrestricted -Scope CurrentUser" > nul 2>&1

@REM Store pristine paths
@SET pristine_workspace=%CD% 
@SET pristine_path=%path%
@SET pristine_pythonpath=%pythonpath%

@REM Get current workspace and crop final backslash for convenience.
CD %~dp0 && CD ..
@IF NOT DEFINED stm_workspace SET "stm_workspace=%CD%"
@SET workspace=%stm_workspace%
CD %pristine_workspace%

@REM Restart Docker CLI
ECHO =======================================
ECHO Starting Docker
ECHO =======================================

@REM Start Docker for STMLab safely (if not already been done)
@SET DOCKER_START=C:\Program Files\Docker\Docker\Docker Desktop.exe
@SET "PATH=%PATH%;%workspace%\PyCODAC\API\cmd"
@CALL "%DOCKER_START%" > nul 2>&1
@ping -n 40 localhost > nul 2>&1
@REM Execute docker login safely
@ECHO | SET /p="%DOCKER_PASSWORD%" | CALL docker login -u %DOCKER_USER% --password-stdin

@REM Add Python executable paths and add all custom packages. 
@SET stm_pycodac=%workspace%
@REM -------------------------------------------------------------------------------------------------
@CALL conda activate %stm_lab%
@REM -------------------------------------------------------------------------------------------------

@REM Rebuild web-based JupyterLab application.
@REM -------------------------------------------------------------------------------------------------
@CALL python %stm_pycodac%\PyCODAC\__setenv__.py %stm_pycodac%\PyCODAC\API\Docker.py
@REM -------------------------------------------------------------------------------------------------

ECHO =======================================
ECHO Update Docker registry server
ECHO =======================================

@REM Update staging build of STMLab on STMHub (Docker registry server of STM)
@REM -------------------------------------------------------------------------------------------------
@ECHO | SET /p="%GIT_TOKEN%" | CALL docker login -u %GIT_USER% --password-stdin %GIT_REGISTRY%
@CALL docker tag stmlab:latest %GIT_REGISTRY%/stmlab:latest >nul 2>&1 && SET stm_update=%GIT_REGISTRY%
@REM Update only if successfully tagged
@IF DEFINED stm_update CALL docker push %GIT_REGISTRY%/stmlab:latest
@IF DEFINED stm_update CALL docker image remove %GIT_REGISTRY%/stmlab:latest
@REM -------------------------------------------------------------------------------------------------

@REM Leave no trace on Jenkins
@CALL docker logout
@EXIT 0
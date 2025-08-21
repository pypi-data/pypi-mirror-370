@REM %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@REM %                    	 Postprocessing 4 Jenkins on Windows 7/10 (x64)                     %     
@REM %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@REM Command script to run release PyXMake jobs on Jenkins (FA-STM).
@REM Created on 21.01.2020
@REM 
@REM Version: 1.0
@REM -------------------------------------------------------------------------------------------------
@REM    Requirements and dependencies:
@REM        - 
@REM
@REM     Changelog:
@REM        - 
@REM	
@REM -------------------------------------------------------------------------------------------------
@ECHO OFF
where /q conda
@IF %ERRORLEVEL% NEQ 0 %windir%\system32\cmd.exe "/K" C:\ProgramData\Miniforge3\Scripts\activate.bat
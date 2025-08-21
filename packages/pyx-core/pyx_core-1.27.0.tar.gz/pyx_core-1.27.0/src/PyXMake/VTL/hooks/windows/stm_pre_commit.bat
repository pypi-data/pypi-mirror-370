@REM %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@REM %                    	  	  	PyXMake 4 on Windows 10 (x64)          		                  %
@REM %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
@REM Manual user pre-commit hook for commit checks  (FA-STM).
@REM Created on 23.03.2021
@REM 
@REM Version: 1.0
@REM -------------------------------------------------------------------------------------------------
@REM    Requirements and dependencies:
@REM        - 
@REM
@REM     Changelog:
@REM        - 
@REM
@REM 	Original:
@REM		   - https://stackoverflow.com/questions/1928023/how-can-i-prevent-subversion-commits-without-comments
@REM	
@REM -------------------------------------------------------------------------------------------------
@ECHO OFF
@SETLOCAL

@REM Subversion sends through the path to the repository and transaction id
@SET REPOS=%1
@SET TXN=%2

rem check for an empty log message
type %TXN% | findstr . > nul
IF %ERRORLEVEL% gtr 0 (goto err) ELSE EXIT 0

:ERR
ECHO. 1>&2
ECHO Your commit has been blocked because you didn't give any log message 1>&2
ECHO Please write a log message describing the purpose of your changes and 1>&2
ECHO then try committing again. -- Thank you 1>&2
EXIT 1
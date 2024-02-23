@echo off
rem This bat is useful to run via shoutcut or hotkey

rem Conda env activation
call activate dev-3-9-18

rem Alternative run to check import perfomance if script starts too slowly
rem python -X importtime src\main.py 2> import.log
python src\main.py

if %errorlevel% neq 0 (
	pause
) else (
	conda deactivate
)
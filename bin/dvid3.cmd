@echo off
REM dvid3 — Griffin encode/decode CLI launcher for Windows.
REM Finds wasmtime in PATH or %USERPROFILE%\.wasmtime\bin.
REM First-time install: powershell -Command "iwr https://wasmtime.dev/install.ps1 -useb | iex"

setlocal

set "SELF_DIR=%~dp0"
set "WASM=%SELF_DIR%dvid3.wasm"

if not exist "%WASM%" (
    echo error: %WASM% not found 1>&2
    exit /b 1
)

where wasmtime >nul 2>&1
if %ERRORLEVEL% == 0 (
    set "WASMTIME=wasmtime"
) else if exist "%USERPROFILE%\.wasmtime\bin\wasmtime.exe" (
    set "WASMTIME=%USERPROFILE%\.wasmtime\bin\wasmtime.exe"
) else (
    echo error: wasmtime not found. 1>&2
    echo. 1>&2
    echo Install it: 1>&2
    echo     powershell -Command "iwr https://wasmtime.dev/install.ps1 -useb ^| iex" 1>&2
    echo. 1>&2
    echo Then re-run this command. 1>&2
    exit /b 127
)

"%WASMTIME%" run -W relaxed-simd=y --dir "%CD%" "%WASM%" -- %*

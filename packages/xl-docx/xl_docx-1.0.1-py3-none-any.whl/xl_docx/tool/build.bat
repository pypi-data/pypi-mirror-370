@echo off
if exist "build" (
    echo Deleting the "build" folder in the current directory...
    rmdir /s /q "build"
    if %errorlevel% equ 0 (
        echo Deletion succeeded.
    ) else (
        echo Error occurred during deletion.
    )
) else (
    echo The "build" folder does not exist in the current directory.
)

@echo off
if exist "dist" (
    echo Deleting the "dist" folder in the current directory...
    rmdir /s /q "dist"
    if %errorlevel% equ 0 (
        echo Deletion succeeded.
    ) else (
        echo Error occurred during deletion.
    )
) else (
    echo The "dist" folder does not exist in the current directory.
)

pyinstaller -F tool.pyw
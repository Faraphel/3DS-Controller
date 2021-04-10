from cx_Freeze import setup, Executable
import sys

options = {
    "build_exe":{
        "include_files":[
            "./assets/",
            "./icon.ico",
            sys.exec_prefix + "\\DLLs\\tcl86t.dll",
            sys.exec_prefix + "\\DLLs\\tk86t.dll",
            "./3DS/",
            ("./venv/Lib/site-packages/pynput", "./lib/pynput")
        ],
        "includes": ["tkinter", "pyvjoy", "pynput"],
        "packages": [],
        "excludes": []
    }
}

setup(
    options=options,
    name='MC-Log-Viewer',
    version='0.3',
    url='https://github.com/Faraphel/3DS-Controller',
    license='GPL-3.0',
    author='Faraphel',
    author_email='rc60650@hotmail.com',
    description='Utiliser votre 3DS comme une manette.',
    executables = [Executable("./main.pyw",
                              icon = "icon.ico",
                              base = "win32gui",
                              target_name = "Controller 3DS.exe",
                              shortcut_name = "3DS Controller",
                              shortcut_dir = "DesktopFolder")],
)
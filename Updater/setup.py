from cx_Freeze import setup, Executable

options = {
    "build_exe":{
        "includes": ["requests"],
        "packages": [],
        "excludes": []
    }
}

setup(
    options=options,
    name='3DS-Controller',
    version='0.3',
    url='https://github.com/Faraphel/3DS-Controller',
    license='GPL-3.0',
    author='Faraphel',
    author_email='rc60650@hotmail.com',
    description='Logiciel de mise à jour pour 3DS Controller.',
    executables = [Executable("./Updater.py",
                              target_name = "Updater.exe",
                              shortcut_name = "3DS Controller Updater",
                              shortcut_dir = "DesktopFolder")],
)
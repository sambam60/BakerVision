from setuptools import setup

APP = ['VirtualMouse.py']
DATA_FILES = [
    ('.', ['./focus_change_keyboard.caf', './focus_change_small.caf', './Hand.png',
           './focus_change_large.caf', './jbl_begin.caf', './jbl_cancel.caf', 'VirtualMouse.ico']),
]

OPTIONS = {
    'argv_emulation': True,
    'packages': ['pathlib'],  # Ensure pathlib is included
    'plist': {
        'CFBundleName': 'Virtual Mouse',
        'CFBundleDisplayName': 'Virtual Mouse',
        'CFBundleVersion': '0.1',
        'CFBundleShortVersionString': '0.1',
        'CFBundleIdentifier': 'com.SpatialSilicon.VirtualMouse',
        'CFBundleIconFile': 'VirtualMouse.ico',  # Set the icon file
    },
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    data_files=DATA_FILES,
    setup_requires=['py2app']
)

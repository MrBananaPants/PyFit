"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['PyFit.py']
DATA_FILES = [('', ['media'])]
OPTIONS = {
    'iconfile': 'media/icon.icns',
    'plist': {'CFBundleShortVersionString': '0.6.2', },
    'packages': ['customtkinter', 'PIL']}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)

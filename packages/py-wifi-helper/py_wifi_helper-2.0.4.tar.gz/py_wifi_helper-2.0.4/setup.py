from setuptools import setup, find_packages
import os
import re
import pathlib

CWD = pathlib.Path(__file__).parent.resolve()

VERSION = '1.0.0' 
with open(os.path.join(CWD, 'py_wifi_helper', '__init__.py'), 'r') as f:
    re_version_pattern = re.compile(r"=[\s]*['\"]([0-9\.]+)['\"]")
    for line in f:
        line = line.strip()
        if line.find('version') >= 0:
            extractVersionInfo = re_version_pattern.search(line)
            if extractVersionInfo:
                VERSION = extractVersionInfo.group(1)

PYTHON_REQUIRES = ">=3.10"
URL = "https://github.com/changyy/py-wifi-helper"
DOWNLOAD_URL = "https://pypi.org/project/py-wifi-helper/"
DESCRIPTION = 'A cross-platform WiFi management tool for Windows, macOS, and Ubuntu'
LONG_DESCRIPTION = DESCRIPTION
LONG_DESCRIPTION_TYPE = 'text/plain'
try:
    with open(os.path.join(CWD, "README.md"), 'r') as f:
        data = f.read()
        if len(data) > 10:
            LONG_DESCRIPTION = data
            LONG_DESCRIPTION_TYPE = 'text/markdown'
except Exception as e:
    pass

INSTALL_REQUIRES = ['pandas']
try:
    with open(os.path.join(CWD, "requirements.txt"), 'r') as f:
        requirements = [s.strip() for s in f.read().split("\n") if s.strip()]
        if requirements:  # 只有在成功讀取到內容時才更新
            INSTALL_REQUIRES = requirements
except Exception as e:
    print(f"Warning: Could not read requirements.txt: {e}")  # 加入錯誤提示

setup(
    name="py-wifi-helper", 
    version=VERSION,
    author="Yuan-Yi Chang",
    author_email="<changyy.csie@gmail.com>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESCRIPTION_TYPE,
    packages=find_packages(),
    install_requires=INSTALL_REQUIRES,
    keywords=['python', 'wifi', 'interface', 'macos', 'ubuntu', 'windows', 'network', 'wireless'],
    python_requires=PYTHON_REQUIRES,
    url=URL,
    download_url=DOWNLOAD_URL,
    entry_points={
        'console_scripts': [
            'py-wifi-helper = py_wifi_helper.cmd:main',
            'wifi-helper = py_wifi_helper.cmd:main',
            'py-wifi-helper-macos-setup=py_wifi_helper.cli_permission:main',
            'wifi-helper-macos-setup=py_wifi_helper.cli_permission:main',
        ],
    },
    classifiers= [
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: Microsoft :: Windows :: Windows 11",
        "Operating System :: POSIX :: Linux",
        "Topic :: System :: Networking",
        "Topic :: Utilities",
    ]
)

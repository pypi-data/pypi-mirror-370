# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages
from kytest import __version__, __description__

try:
    long_description = open(os.path.join('kytest', "README.md"), encoding='utf-8').read()
except IOError:
    long_description = ""

setup(
    name="kytest",
    version=__version__,
    description=__description__,
    author="杨康",
    author_email="772840356@qq.com",
    url="https://gitee.com/bluepang2021/ktest_project",
    platforms="API/Android/IOS/HM/WEB",
    packages=find_packages(),
    long_description=long_description,
    python_requires='>=3.8',
    classifiers=[
        "Programming Language :: Python :: 3.8"
    ],
    include_package_data=True,
    package_data={
        r'': ['*.yml'],
    },
    install_requires=[
        'requests==2.31.0',
        'requests-toolbelt==1.0.0',
        'urllib3==1.26.15',
        'jmespath==0.9.5',
        'jsonschema==4.17.0',
        'click==8.1.7',
        'loguru==0.7.0',
        'PyYAML==6.0.1',
        'allure-pytest==2.9.45',
        'pytest==6.2.5',
        'pytest-xdist==2.5.0',
        'pytest-rerunfailures==10.2',
        'pytest-repeat==0.9.3',
    ],
    extras_require={
        "web": ['playwright==1.33.0'],
        "android": ['uiviewer==1.1.3', 'uiautomator2==3.2.4'],
        "ios": ['uiviewer==1.1.3', 'tidevice== 0.12.10', 'facebook-wda==1.5.0'],
        "hm": ['hmdriver2==1.3.0']
    },
    entry_points={
        'console_scripts': [
            'kytest = kytest.cli:main'
        ]
    }
)

'''
Author: seven 865762826@qq.com
Date: 2023-03-24 09:26:29
LastEditors: seven 865762826@qq.com
LastEditTime: 2023-11-24 11:46:54
FilePath: \VSCode_Pro\Python_Pro\TSMasterApi\setup.py
'''
from distutils.core import setup
from setuptools import find_packages

with open("README.rst", "r",encoding="utf-8") as f:
  long_description = f.read()

# 
setup(name='libTSCANAPI',  # 包名
      version='1.4.7',  # 版本号
      description='Use TSMaster hardware',
      long_description=long_description,
      author='seven',
      author_email='865762826@qq.com',
      license='MIT License',
      packages=find_packages(),
      include_package_data=True,
      # data_files=[
      #   ('./libTSCANAPI/linux', ['./libTSCANAPI/linux/libbinlog.so', './libTSCANAPI/linux/libLog.so','./libTSCANAPI/linux/libTSCANApiOnLinux.so','./libTSCANAPI/linux/libTSH.so']),
      #   ('./libTSCANAPI/windows/x86', ['./libTSCANAPI/windows/x86/binlog.dll', './libTSCANAPI/windows/x86/libLog.dll','./libTSCANAPI/windows/x86/libTSCAN.dll','./libTSCANAPI/windows/x86/libTSH.dll','./libTSCANAPI/windows/x86/libTSDevBase.dll']),
      #   ('./libTSCANAPI/windows/x64', ['./libTSCANAPI/windows/x64/binlog.dll', './libTSCANAPI/windows/x64/libLog.dll','./libTSCANAPI/windows/x64/libTSCAN.dll','./libTSCANAPI/windows/x64/libTSH.dll','./libTSCANAPI/windows/x64/libTSDevBase.dll']),
      #   ('./libTSCANAPI/rules', ['./libTSCANAPI/rules/99-tosun.rules', './libTSCANAPI/rules/说明.txt',]),
      # ],
      install_requires = [
        "python-can",
        "ldfparser",
        "cantools",
      ],
      platforms=["Any"],
      classifiers=[
          'Intended Audience :: Developers',
          'Natural Language :: Chinese (Simplified)',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',
          'Programming Language :: Python :: 3.12',
          'Topic :: Software Development :: Libraries'
      ],
      )

from distutils.core import setup
from setuptools import find_packages
 
setup(name = 'wf_daobao',     # 包名
      version = '20250817.4.1',  # 版本号
      description = 'pyinstaller_打包模块',
      long_description = '试着改变世界<br>用于界面版打包exe文件;<br>', 
      author = 'xwf',
      author_email = '453211170@qq.com',
      url = '',
      license = '',
      install_requires=["pandas>=2.3.1","xlrd>=2.0.1","openpyxl>=3.1.2","pyperclip>=1.8.2","setuptools>=75.3.0","windnd>=1.0.7","loguru>=0.7.2"], #申明依赖包
      classifiers = [
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Natural Language :: Chinese (Simplified)',      
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Utilities'
      ],
      keywords = '',
      packages = find_packages('src'),  # 必填，就是包的代码主目录
      package_dir = {'':'src'},         # 必填
      include_package_data = True,
)

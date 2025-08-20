#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os
from setuptools import setup, find_packages

# Đọc nội dung README.md để làm long_description
here = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='thuongcli',                    # Tên gói: thường chỉ gồm chữ thường và dấu gạch ngang
    version='1.0.9',                      # Phiên bản: tuân theo Semantic Versioning
    author='Tran Dinh Thuong',
    author_email='qbquangbinh@gmail.com',
    url='https://github.com/qbquangb/thuongcli',  # URL của project
    description='Điều khiển máy tính bằng CLI',
    long_description=long_description,    # nội dung README.md
    long_description_content_type='text/markdown',  
    # license='MIT',                        # Loại license
    # packages=find_packages(exclude=['tests*']),  # tự động tìm tất cả packages
    packages=find_packages(),
    python_requires='>=3.7',              # yêu cầu Python
    install_requires=[
        'thuonglib>=1.0.4',           # thư viện phụ thuộc chính
        # 'requests>=2.0',                  # dependencies chính
        # 'numpy>=1.20',                  # thêm nếu cần
    ],
    # extras_require={                      # optional dependencies
    #     'dev': [
    #         'pytest>=6.0',
    #         'flake8',
    #     ],
    # },
    classifiers=[
        # Dev Status
        # 'Development Status :: 4 - Beta',
        # License
        # 'License :: OSI Approved :: MIT License',
        # Python versions
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        # Operating system
        'Operating System :: OS Independent',
    ],
    entry_points={                        # nếu bạn có command-line scripts
        'console_scripts': [
            'cli=thuongcli.thuongcli:main',
        ],
    },
    # include_package_data=True,            # bao gồm các file theo MANIFEST.in (nếu có)
    # zip_safe=False,
)


'''
1. python setup.py sdist bdist_wheel
2. python -m twine upload --repository testpypi dist/*
   python -m twine upload dist/*
   python -m twine upload --skip-existing dist/*
3. pip install --index-url https://test.pypi.org/simple/ my-package
   pip install thuonglib
   pip install --no-cache-dir thuongcli
'''
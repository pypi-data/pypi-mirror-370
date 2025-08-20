from setuptools import setup, find_packages

setup(
    name='csv_parser_cnic_test_2025',  # 包名
    version='0.1.0',  # 包版本
    description='A CSV parser that converts CSV to Arrow format',  # 简短描述
    long_description=open('README.md').read(),  # 从 README 中读取详细描述
    long_description_content_type='text/markdown',  # 说明 Markdown 格式
    author='ZZA',
    author_email='zhouziang1996@outlook.com',
    url='https://github.com/scottie1996/algorithmTest',  # 你的 GitHub 仓库 URL
    packages=find_packages(),  # 自动寻找该包中的模块
    install_requires=[
        'pyarrow',
        'pandas',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # 支持的 Python 版本
)

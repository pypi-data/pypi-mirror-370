from setuptools import setup, find_packages

setup(
    name='yuipybase',  # PyPIでの名前（他と被らないように）
    version='0.1.0',
    packages=find_packages(),
    install_requires=[],  # 必要なライブラリがあればここに
    python_requires='>=3.8',
    author='結愛ちゃん',
    description='Python basic environment setup library',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/FlandollScarlet495/pybase',  # GitHubなどあれば
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

from setuptools import setup, find_packages

setup(
    name="myfuncbank_alex",
    version="1.5.5",
    packages=find_packages(),
    install_requires=[
        # 添加你的依赖项
        "pandas"
    ],
    author="Alex Han",
    author_email="Mr.Alex.usa@hotmail.com",
    description="This is my private function bank package",
    url="https://github.com/yourusername/mypackage",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

from setuptools import setup, find_packages

setup(
    name="TkinterLite",  # Easy Tkinter
    version="3.2.1",
    packages=find_packages(),
    install_requires=[
        'future~=1.0.0',
        'pillow~=11.3.0',
        'PyQt5~=5.15.11',
        'setuptools~=78.1.1',
    ],
    author="YanXinle",
    author_email="1020121123@qq.com",
    description="tkinter库的简化版",
    url="https://github.com/Yanxinle1123/LeleEasyTkinter",
)

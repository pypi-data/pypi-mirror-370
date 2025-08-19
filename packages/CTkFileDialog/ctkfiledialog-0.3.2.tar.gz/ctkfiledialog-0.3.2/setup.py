
from setuptools import setup, find_packages

setup(
    name="CTkFileDialog",
    version="0.3.2",
    packages=find_packages(),
    include_package_data=True,  
    author='Flick',
    long_description=open(file='README.md', encoding='utf-8', mode='r').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/FlickGMD/CTkFileDialog',
    install_requires=[
        "customtkinter",
        "CTkMessagebox",
        "Pillow",
        "opencv-python",
        "CTkToolTip",
    ],
)


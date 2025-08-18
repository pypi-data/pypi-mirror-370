import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='f_tools_pkg',
    version='0.0.21',
    packages=setuptools.find_packages(),
    url='',
    license='MIT',
    author='wushengyan',
    author_email='WUSY1991@163.com',
    description='some common tools(bmp/crypt/excel/log ...)',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['Crypto','xlwt','openpyxl','pyserial'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)


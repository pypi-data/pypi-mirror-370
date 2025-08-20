import setuptools

# with open("README.md", "r") as fh:
#     long_description = fh.read()

setuptools.setup(
    # name="uhfReaderApi",
    # version="1.0.4",
    # name="uhfReaderApi_Cykeo",
    # version="1.0.3",
    name="uhfReaderApi_NoHid",
    version="1.0.4",
    author="rfid",
    description="ReaderApi",
    platforms=['linux/Windows'],
    # uhf.
    packages=setuptools.find_namespace_packages(
        exclude=["*.qt", "qt.*", "qt", "*.qt.*", "*.test", "test.*", "test",
                 "*.test.*"]),
    # package_dir={"": "uhf"},
    include_package_data=False,
    # 排除所有 README.md
    # exclude_package_data={'': ['README.md', "setup.py"]},
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'bitstring==3.1.7',
        'pyserial==3.4',
        # 'pyusb==1.1.0',
        # 'hidapi==0.13.1'
    ]
)

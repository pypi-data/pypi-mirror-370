from setuptools import setup

VERSION = "v1.8.7"

setup(
    name="devvio_util",
    version=VERSION,
    long_description=open("README.txt").read(),
    long_description_content_type="text/markdown",
    description="Utility to be used inside Devvio projects",
    author="Devvio Team",
    author_email="support@devv.io",
    license="Devvio",
    packages=[
        "devvio_util",
        "devvio_util/primitives",
        "devvio_util/exceptions",
        "devvio_util/inn_sdk",
    ],
    install_requires=["flake8==6.0.0", "cryptography==41.0.1"],
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

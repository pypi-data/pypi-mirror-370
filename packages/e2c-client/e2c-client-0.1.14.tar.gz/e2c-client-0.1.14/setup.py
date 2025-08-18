import setuptools

with open("README.md", "r") as f:
    readme = f.read()

setuptools.setup(
    name="e2c-client",
    version="0.1.14",
    description="ALMA Ethernet-To-CAN socket server Python client package for LRU monitoring and control.",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Jose L. Ortiz / ADE",
    author_email="jose.ortiz@alma.cl",
    url="https://bitbucket.alma.cl/projects/ENG/repos/e2c-client",
    packages=setuptools.find_packages(include=["e2c_client", "e2c_client.*"]),
    package_data={"e2c_client": ["resources/*"]},
    entry_points={
        "console_scripts": [
            "e2c-client=e2c_client.__main__:main",
        ],
    },
    license="LGPL-2.1-only",
    install_requires=["typer>=0.11.0", "rich>=10.13.0"],
    extras_require={"test": ["pytest"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)",
        "Operating System :: OS Independent",
    ],
)

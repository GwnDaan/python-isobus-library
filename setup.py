from setuptools import setup, find_packages

setup(
    name="pyisolib",
    url="https://github.com/GwnDaan/python-isobus-library",
    version="1.0.0",
    packages=find_packages(exclude=['docs', 'examples']),
    author="Daan Steenbergen",
    description="ISOBUS stack implementation",
    keywords="ISOBUS ISO-11783",
    # license="MIT",
    # platforms=["any"],
    # classifiers=[
    #     "License :: OSI Approved :: MIT License",
    #     "Operating System :: OS Independent",
    #     "Programming Language :: Python :: 3",
    #     "Intended Audience :: Developers",
    #     "Topic :: Scientific/Engineering"
    # ],
    install_requires=[
        "can-j1939>=2.0.4",
    ],
)
from setuptools import find_packages, setup

setup(
    name="prefect-anyscale",
    version="0.2.2",
    description="Prefect integrations with Anyscale.",
    license="Apache License 2.0",
    author="Anyscale, Inc.",
    author_email="support@anyscale.com",
    keywords="prefect",
    url="https://github.com/anyscale/prefect-anyscale",
    packages=find_packages(include=["prefect_anyscale"]),
    python_requires=">=3.7",
    install_requires = [
        "prefect>=2.7.1",
    ],
    classifiers=[
        "Natural Language :: English",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries",
    ],
)

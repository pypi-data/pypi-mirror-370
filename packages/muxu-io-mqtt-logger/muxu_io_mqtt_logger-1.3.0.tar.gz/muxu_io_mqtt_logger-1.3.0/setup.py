from setuptools import find_packages, setup

setup(
    name="mqtt-logger",
    version="0.1.0",
    author="Alex Gonzalez",
    author_email="alex@muxu.io",
    description="A logger that logs messages to an MQTT topic.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/muxu-io/mqtt-logger",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "paho-mqtt>=1.6.1",
        "muxu-io-mqtt-connector",
    ],
    extras_require={
        "systemd": ["systemd-python>=234"],
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18",
            "pytest-cov>=3.0",
            "black>=22.0",
            "flake8>=4.0",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)

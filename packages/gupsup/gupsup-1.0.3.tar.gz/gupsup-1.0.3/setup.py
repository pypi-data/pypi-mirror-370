from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="terminalchat",
    version="1.0.2",
    author="Rahul Deka",
    author_email="rahuldeka072@gmail.com",
    description="Terminal-based chat app using WebSockets with improved error handling and reconnection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/iamRahul21/terminalchat",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "websockets>=11.0",
    ],
    entry_points={
        'console_scripts': [
            'terminalchat=terminalchat.client:run_client',
        ],
    },
    keywords="chat terminal websocket real-time",
)
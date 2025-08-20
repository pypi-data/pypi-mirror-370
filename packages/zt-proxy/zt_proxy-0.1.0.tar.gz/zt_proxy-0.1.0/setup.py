from setuptools import setup, find_packages

setup(
    name="ztproxy",
    version="0.1.0",
    description="ZT Proxy tool",
    author="Your Name",
    py_modules=["main"],
    install_requires=[
        "mitmproxy",
    ],
    entry_points={
        "console_scripts": [
            "ztproxy=main:main"
        ]
    },
    include_package_data=True,
)

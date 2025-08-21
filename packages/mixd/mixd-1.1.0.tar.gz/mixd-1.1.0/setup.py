from setuptools import setup, find_packages

setup(
    name="mixd",
    version="1.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "rich"
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "mixd=mixd.main:main",
        ],
    },
    description="Dev HTTPS server with optional Cloudflared tunnel",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="mixddev",
    url="https://github.com/yourusername/mixd",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

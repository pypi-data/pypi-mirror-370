from setuptools import setup

setup(
    name="sh_mod_loader",
    license=open("LICENSE").read(),
    version="0.1.0",
    packages=["sh_mod_loader"],
    install_requires=[],
    author="SeniorShadifer",
    description="Simple ModLoader for Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/SeniorShadifer/MyModLoader",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)

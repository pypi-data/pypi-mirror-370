from setuptools import setup, find_packages

setup(
    name="hanifx",
    version="19.0.0",
    author="Hanif",
    author_email="sajim4653@gmail.com",
    description="HanifX v19.0.0 - Real-time Auto App Detection",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/hanifx-540",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[],
    entry_points={
        "console_scripts": [
            "hanifx-scan=hanifx.v19:HanifX_v19",
        ],
    },
)

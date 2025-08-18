from setuptools import setup, find_packages


with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="detectionDataCollection",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy>=2.2.6",
        "opencv-python>=4.12.0.88",
        "PyYAML>=6.0.2"
    ],
    project_urls={
        "Source Code": "https://github.com/ShashwatDev-26/imageDataCollection.git",
    },
    author="Shashwat dev Hans",
    author_email="shashwatdevhans@gmail.com",
    description="A live camera or video to collect data for CNN projects.",
    long_description=long_description,
    long_description_content_type="text/markdown",

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    python_requires=">=3.6",
)


from setuptools import setup, find_packages

setup(
    name="picarta",
    version="1.1.3",
    packages=find_packages(),
    install_requires=[
        "requests",
        "pillow",
        "simplekml==1.3.6",
    ],
    entry_points={
        "console_scripts": [
            "localize-image=picarta.picarta:main",
        ],
    },
    author="Picarta",
    author_email="info@picarta.ai",
    description="A package to geolocate images from URL or local files using Picarta AI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/PicartaAI/Picarta-API",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)

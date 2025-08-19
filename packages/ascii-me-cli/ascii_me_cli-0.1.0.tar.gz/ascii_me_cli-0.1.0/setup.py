from setuptools import setup, find_packages

setup(
    name="ascii-me-cli",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "Pillow>=9.0.0"
    ],
    entry_points={
        "console_scripts": [
            "ascii-art=ascii_gif_player:main"
        ]
    },
    python_requires=">=3.7",
    author="WetZap",
    author_email="jorgerlvdg2016@gmail.com",  
    description="Convierte imágenes y GIFs en animaciones ASCII en la terminal",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/WetZap/Ascii-Me",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Terminals",
    ],
)

from setuptools import setup, find_packages

setup(
    name="library3d",
    version="0.25",
    packages=find_packages(),
    install_requires=["Pillow"],
    author="Mehmet",
    description="Saf Python 3D kütüphanesi (OpenGL kullanmadan, v0.25)",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/kullaniciadi/library3d",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)

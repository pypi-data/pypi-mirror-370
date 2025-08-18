from setuptools import setup, find_packages

setup(
    name="3dlibrary",
    version="0.2",
    packages=find_packages(),
    install_requires=["Pillow"],
    author="Mehmet",
    description="Saf Python 3D kütüphanesi (OpenGL kullanmadan, v0.2)",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/kullaniciadi/3dlibrary",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)

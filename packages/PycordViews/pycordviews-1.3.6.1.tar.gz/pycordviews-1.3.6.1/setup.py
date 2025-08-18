from setuptools import setup

with open("README.md", encoding='utf-8') as file:
    file = file.read()

setup(
    name="PycordViews",
    version="1.3.6.1",
    url="https://github.com/BOXERRMD/Py-cord_Views",
    author="Chronos (alias BOXERRMD)",
    author_email="vagabonwalybi@gmail.com",
    maintainer="Chronos",
    license="MIT License",
    description="Views and multibot for py-cord library",
    long_description=file,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: Microsoft :: Windows :: Windows 11",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 3.9"
    ],
    install_requires=[
        "immutable-Python-type"
    ],
    packages=['pycordViews', 'pycordViews/pagination', 'pycordViews/views', 'pycordViews/menu', 'pycordViews/multibot', 'pycordViews/kit', 'pycordViews/modal'],
    python_requires='>=3.9'
)
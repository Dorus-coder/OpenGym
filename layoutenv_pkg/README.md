[build-system]
requires = ["setuptools>=61.0", "piascomms", "gymnasium", "stable-baselines3"]
build-backend = "setuptools.build_meta"

[project]
name = "piascomms"
version = "0.0.1"
authors = [
  { name="Dorus Boogaard", email="dorus.boogaard@outlook.com" },
]
description = "a package that allows for communication with the Pias software suite with xml over TCP/IP"
readme = "README.md"
requires-python = ">=3.7"
dependencies = [
  "xsdata>=21.1",
  "lxml>=4.9",
  "matplotlib>=3.6"
]
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]

[project.urls]
"Homepage" = "https://github.com/Dorus-coder/ThesisResearch"


[tools.setuptools.packages]
find = {}





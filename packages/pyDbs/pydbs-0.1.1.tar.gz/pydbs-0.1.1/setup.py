import setuptools

with open("README.md", "r") as file:
  long_description = file.read()

setuptools.setup(
  name="pyDbs",
  version="0.1.1",
  author="Rasmus K. Skjødt Berg",
  author_email="rasmus.kehlet.berg@econ.ku.dk",
  description="Custom database class (relies on pandas, numpy, scipy)",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/ChampionApe/pyDbs",
  packages=setuptools.find_packages(),
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
  ],
  python_requires='>=3.11',
  install_requires=["pandas", "scipy","openpyxl"],
)
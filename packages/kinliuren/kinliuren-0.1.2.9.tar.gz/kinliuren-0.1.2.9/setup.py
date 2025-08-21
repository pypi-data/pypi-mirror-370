import setuptools 

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()
   
setuptools.setup(
    name="kinliuren",
    version="0.1.2.9",
    author="Ken Tang",
    author_email="kinyeah@gmail.com",
    install_requires=[            
      ],
	description="Dailiuren (大六壬) is one of the three greatest Chinese Divination systems ever.",
	long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kentang2017/kinliuren",
	packages=setuptools.find_packages(),
	package_data = {},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
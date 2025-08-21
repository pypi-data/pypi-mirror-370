from setuptools import setup, find_packages

setup(
    name="dz_locations",
    version="0.1.5",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Django>=5.2",
        "djangorestframework>=3.12"
    ],
    description="Algerian Wilaya & Commune data for Django projects",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Mohammed Taha Khamed",
    url="https://github.com/khamedtaha/dz_locations",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

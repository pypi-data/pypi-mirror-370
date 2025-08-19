from setuptools import setup, find_packages

setup(
    name="LIB_ADTECH",
    version="3.9.4",
    packages=find_packages(),
    include_package_data=True,
    description="Melhorias para automação web",
    long_description=open('README.md', encoding="utf-8").read(),
    long_description_content_type='text/markdown',
    author="Alan, Dannilo, Fabiano e Yan",
    author_email="desenvolvimento@adpromotora.com.br",
    url="https://github.com/DesenvolvimentoAD/Adlib",
    package_data={
        "my_package": ["Adlib/webdriver/*", "requirements.txt"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
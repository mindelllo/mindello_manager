from setuptools import setup, find_packages

setup(
    name="mindello_manager",
    version="0.1.1",
    description="Scanner e autenticador de dispositivos Matter FALL-R1 na rede local.",
    author="Mindêllo Casas Inteligentes",
    author_email="lucas@mindello.com.br",
    packages=find_packages(
        include=["mindello_manager", "mindello_manager.*"],
        exclude=["tests", "tests.*"],
    ),
    install_requires=[
        "zeroconf",
        "scapy",
        "requests"
    ],
    entry_points={
        'console_scripts': [
            'mindello_manager = mindello_manager.main:main'
        ]
    },
    python_requires='>=3.8',
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

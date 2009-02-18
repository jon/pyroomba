from setuptools import setup, find_packages

setup(
    name = "PyRoomba",
    version = "0.1",
    packages = find_packages(),
    
    install_requires = ['pyserial>=2.0'],
    
    author = "Jon Olson",
    author_email = "jon@damogran.com",
    description = "Roomba vacuum-cleaning robot serial control library",
    keywords = "roomba robot control"
    
)


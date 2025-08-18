from setuptools import setup,find_packages

setup(
    name ='Shourya',
    version = '0.1',
    author ='Arya panda',
    author_email ='aryapanda069@gmail.com',
    description = 'this is sppech to text package created by Arya'
    )
    
packages = find_packages(),
install_requiremants = [
    'selenium'
    'webdriver_manager'
]
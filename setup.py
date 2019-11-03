from setuptools import setup

setup(
   name='live',
   version='0.12',
   description='live modelling',
   author='Anand Jain, Ethan Abraham',
   author_email='anandj@uchicago.edu',
   packages=['live'],  #same as name
   install_requires= \
           ['pandas', 'requests', 'beautifulsoup4', 'numpy', 
           'scikit-learn'] # external packages as dependencies
)

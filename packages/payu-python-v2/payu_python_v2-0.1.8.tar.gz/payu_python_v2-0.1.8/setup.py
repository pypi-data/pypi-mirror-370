import os

from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='payu-python-v2',
      version='0.1.8',
      description='API wrapper for Payu written in Python',
      long_description=read('README.md'),
      long_description_content_type='text/markdown',
      url='https://github.com/teatrix/payu-python',
      author='Miguel Ferrer',
      author_email='ingferrermiguel@gmail.com',
      license='MIT',
      packages=['payu'],
      install_requires=[
          'requests',
      ],
      zip_safe=False)

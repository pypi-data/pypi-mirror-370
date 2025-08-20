
from distutils.core import setup
from setuptools import find_packages

with open("README.MD", "r", encoding="utf-8") as f:
  long_description = f.read()

setup(name='glcl',
      version='0.2.3',
      description='glcl for python studio',
      long_description=long_description,
      author='glsite.com',
      author_email='admin@glsite.com',
      url='',
      install_requires=[],
      license='MIT License',
      platforms=["Windows"],
      python_requires='>=3.8',
      packages=find_packages(),
      include_package_data=True,
      classifiers=[
          'Intended Audience :: Developers',
          'Operating System :: Microsoft :: Windows',
          'Natural Language :: Chinese (Simplified)',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',
          'Programming Language :: Python :: 3.12',
          'Programming Language :: Python :: 3.13',
          'Programming Language :: Python :: 3.14',
          'Programming Language :: Python :: 3 :: Only',
          'Topic :: Software Development :: Libraries',
      ],
      )


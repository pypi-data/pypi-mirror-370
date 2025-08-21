from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='ss12000client',
    version='0.2.0',        
    author='Andreas Galistel',
    author_email='andreas.galistel@gmail.com', 
    description='A Python client library for the SS12000 API.', 
    long_description=long_description, 
    long_description_content_type='text/markdown', 
    url='https://github.com/Delph1/python-ss12000client/', 
    packages=find_packages(), 
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License', # Licensen för ditt paket
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
    ],
    python_requires='>=3.7', 
    install_requires=[  
        'requests>=2.25.1'
        ],
    py_modules=['ss12000_client'],
)
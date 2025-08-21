import platform
from setuptools import setup, find_packages

setup(
    name='HakObserverLinuxpy',  # Your package name
    version='2.2.2',  # Start with a version number
    description='A package connect endpoints to the Hakware Application for Linux',  # Short description
    long_description=open('README.md').read(),  # Long description from README
    long_description_content_type='text/markdown',
    author='Jacob O\'Brien',  # Your name
    # author_email='your.email@example.com',  # Your email
    # url='https://github.com/your-username/XGRCPy',  # Your package's URL (if applicable)
    packages=find_packages(),  # Find all sub-packages
    install_requires=[  # Add your package dependencies here
    'requests',
    'psutil',
    'requests_html'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # Choose your license
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # Specify Python version compatibility
)

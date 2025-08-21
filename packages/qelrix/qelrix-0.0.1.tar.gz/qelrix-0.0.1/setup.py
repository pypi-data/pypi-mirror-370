from setuptools import setup, find_packages

setup(
    name='qelrix',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    author='Your Name',
    author_email='your.email@example.com',
    description='A simple library for interacting with Gemini API',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/qelrix',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)


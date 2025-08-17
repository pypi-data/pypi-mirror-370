from setuptools import setup, find_packages

setup(
    name='electroblocks',
    version='0.1.0',
    packages=find_packages(),
    install_requires=['pyserial'],
    author='Your Name',
    author_email='you@example.com',
    description='Python client library to interact with ElectroBlocks Arduino firmware',
    url='https://github.com/yourusername/electroblocks',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
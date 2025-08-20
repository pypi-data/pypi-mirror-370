from setuptools import setup, find_packages

setup(
    name='tiktok-username-finder',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'requests',
        'SignerPy',
    ],
    author='Your Name',
    author_email='your.email@example.com',
    description='A Python library to find TikTok usernames by email',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/tiktok-username-finder',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)



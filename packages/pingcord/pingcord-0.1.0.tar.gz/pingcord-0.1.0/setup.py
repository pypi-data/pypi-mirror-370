from setuptools import setup, find_packages

setup(
    name='pingcord',
    version='0.1.0',
    description="Send shell command output to Discord using webhooks.",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='theo_vdml',
    url='https://github.com/theo-vdml/pingcord',
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests>=2.0.0",
        "pyyaml>=6.0"
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'pingcord=pingcord.cli:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
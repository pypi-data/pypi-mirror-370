from setuptools import setup, find_packages

setup(
    name='dde-agent-lib',
    version='1.0.2a16',
    packages=find_packages(),
    install_requires=[

    ],
    author='geogpt',
    author_email='zhuquezhitu@zhejianglab.com',
    description='geogpt agent library',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    python_requires='>=3.6',
    package_data={"": ["*.yaml"]}
)
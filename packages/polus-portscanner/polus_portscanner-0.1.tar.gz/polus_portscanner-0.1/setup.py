from setuptools import setup, find_packages
setup(
name='polus_portscanner',
version='0.1',
packages=find_packages(),
install_requires=[],
entry_point={
    'console_scripts': [
        'portscanner = portscanner.portscanner:main'
    ]
}
)

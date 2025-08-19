from setuptools import setup

name = 'KeyisBClient'
filesName = 'KeyisBClient'

setup(
    name=name,
    version='1.4.0.1.72',
    author="KeyisB",
    author_email="keyisb.pip@gmail.com",
    description=name,
    long_description = 'GW and MMB Project libraries',
    long_description_content_type= 'text/plain',
    url=f"https://github.com/KeyisB/libs/tree/main/{name}",
    include_package_data=True,
    package_data = {'KeyisBClient.gw_certs': ['*']}, # type: ignore
    package_dir={'': f'{filesName}'.replace('-','_')},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.12',
    license="MMB License v1.0",
    install_requires = ['KeyisBLogging', 'httpx', 'KeyisBClient-httpx', 'KeyisBClient-mmbp', 'msgpack'],
)

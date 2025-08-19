from setuptools import setup, find_packages

setup(
    name='external-vision-gateway-adapter-package',
    version='0.1.5',
    author='Ugenteraan',
    author_email='ugen@evlos.ai',
    description='Gateway Adapter to be used by clients to communicate with the gateway service.',
    packages=find_packages(),
    install_requires=[
        'grpcio',
        'grpcio-tools',
        'protobuf'
    ],
    include_package_data=True,
    python_requires='>=3.9',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)

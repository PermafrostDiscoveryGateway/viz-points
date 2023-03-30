import setuptools
from pdgpoints import _version

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    author='Ian Nesbitt',
    author_email='nesbitt@nceas.ucsb.edu',
    name='pdgpoints',
    version=_version.version,
    description='PDG point cloud staging pipeline',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/PermafrostDiscoveryGateway/viz-points',
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=['py3dtiles'],
    entry_points = {
        'console_scripts': [
            'tilepoints=pdgpoints.pipeline:run',
        ],
    },
    python_requires='>=3.9, <4.0',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
    ],
    license='Apache Software License 2.0',
)
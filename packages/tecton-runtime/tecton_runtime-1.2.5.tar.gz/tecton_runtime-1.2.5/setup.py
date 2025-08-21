import setuptools
import os

with open('README.pypi.md') as readme_f:
  long_description = readme_f.read()

packages = setuptools.find_packages()
for root, _, files in os.walk("tecton_proto"):
  if any([f.endswith("_pb2.py") for f in files]):
    packages.append(root.replace("/", "."))
for root, _, files in os.walk("protoc_gen_swagger"):
  if any([f.endswith("_pb2.py") for f in files]):
    packages.append(root.replace("/", "."))
for root, _, files in os.walk("protoc_gen_openapiv2"):
  if any([f.endswith("_pb2.py") for f in files]):
    packages.append(root.replace("/", "."))

setuptools.setup(
    classifiers=['Programming Language :: Python :: 3', 'Operating System :: OS Independent', 'License :: Other/Proprietary License'],
    python_requires='>=3.7',
    author='Tecton, Inc.',
    author_email='support@tecton.ai',
    url='https://tecton.ai',
    license='Tecton Proprietary',
    include_package_data=True,
    description='Tecton Transformation Service Sidecar',
    name='tecton_runtime',
    version='1.2.5',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=['grpcio==1.60.0', 'grpcio-reflection==1.60.0', 'grpcio-health-checking==1.60.0', 'numpy>=1.24.4', 'pandas>=1.3.5', 'pyarrow>=8.0.0', 'statsd>=3.3.0', 'psutil>=5.8.0', 'prometheus_client>=0.20.0', 'requests>=2.24', 'py-grpc-prometheus', 'boto3', 'readerwriterlock', 'schedule', 'attrs'],
    packages=packages,
)

from setuptools import setup, find_packages

setup(
    name='agl_frame_extractor',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'opencv-python',
        'tqdm',
    ],
    author='Thomas J. Lux',
    author_email='lux_t1@ukw.de',
    description='A package to extract frames and metadata from .MOV files.',
)

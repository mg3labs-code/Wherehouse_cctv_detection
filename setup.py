from setuptools import setup, find_packages

setup(
    name='gls-warehouse-safety',
    version='1.0.0',
    description='GLS Warehouse Safety Compliance System',
    author='Safety Team',
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=[
        'torch>=2.0.0',
        'ultralytics>=8.0.0',
        'opencv-python>=4.8.0',
        'numpy>=1.24.0',
        'pyyaml>=6.0',
    ],
    entry_points={
        'console_scripts': [
            'gls-safety=src.main:main',
        ],
    },
)

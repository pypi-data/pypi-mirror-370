from setuptools import setup, find_packages

setup(
    name='mofo',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'torch',
        'torchvision',
        'torchinfo',
        'thop',
        'pynvml'
    ],
    description='PyTorch 模型分析与性能基准工具',
    author='17fine',
    python_requires='>=3.8'
)

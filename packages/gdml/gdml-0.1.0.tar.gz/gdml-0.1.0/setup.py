from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='gdml',
    version='0.1.0',
    author='Gokulraj S',
    author_email='gokulsenthil0906@gmail.com',
    packages=find_packages(),
    install_requires=[
        'scikit-learn',
        'xgboost',
        'pandas',
        'gymnasium',
        'numpy',
        'opencv-python',
        'Pillow',
        'matplotlib',
        'seaborn',
        'statsmodels',
        'prophet',
        'scipy',
        'catboost',
        'lightgbm',
        'joblib',
        'numpy',
        'torch',
        'torchvision',
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    data_files=[("", ["README.md", "CHANGELOG.md"])],
)
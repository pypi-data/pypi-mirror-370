from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gdml",
    version="0.1.1",
    author="Gokulraj S",
    author_email="gokulsenthil0906@gmail.com",
    description="A machine learning and deep learning utilities library.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gokulraj0906/gdml",
    packages=find_packages(),
    install_requires=[
        "scikit-learn",
        "xgboost",
        "pandas",
        "gymnasium",
        "numpy",
        "opencv-python",
        "Pillow",
        "matplotlib",
        "seaborn",
        "statsmodels",
        "prophet",
        "scipy",
        "catboost",
        "lightgbm",
        "joblib",
        "torch",
        "torchvision",
    ],
    include_package_data=True,  # requires MANIFEST.in for extra files
    license="Apache-2.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
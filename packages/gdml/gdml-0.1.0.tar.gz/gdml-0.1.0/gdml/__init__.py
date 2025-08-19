__author__ = "GOkulraj S"
__email__ = "gokulsenthil0906@gmail.com"
__version__ = "0.1.0"
__description__ = "A Python package for Machine Learning, Deep Learning and Data Processing"


from gdml.ML import ML_regression
from gdml.ML import ML_classification
from gdml.ML import ML_Clustering
from gdml.ML import ML_TimeSeriesToolkit
from gdml.ML import ML_RLAgent
from gdml.Data import DataReader, DataSplitter,ImageDataLoader
from gdml.DL import DLModel

__all__ = [
    'ML_regression',
    'ML_classification',
    'ML_Clustering',
    'ML_TimeSeriesToolkit',
    'ML_RLAgent',
    'DLModel',
    'DataReader',
    'DataSplitter',
    'ImageDataLoader'
]

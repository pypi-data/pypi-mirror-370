import pandas as pd
class DataReader:
    def __init__(self, filepath:str, *args, **kwargs):
        """
        Initialize the DataReader with a file path.
        """
        self.filepath = filepath
        if not isinstance(filepath, str):
            raise ValueError("Filepath must be a string.")
        if not filepath:
            raise ValueError("Filepath cannot be empty.")
        if not any(filepath.endswith(ext) for ext in ['.csv', '.xlsx', '.xls', '.json', '.parquet',
                                                       '.txt', '.html', '.feather', '.pickle', 
                                                       '.pkl', '.hdf', '.h5', '.dta', '.sas7bdat']):
            raise ValueError(f"Unsupported file format: {filepath}")
        if not pd.io.common.file_exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
    
    def __repr__(self):
        return f"DataReader(filepath={self.filepath})"

    def read(self):
        if self.filepath.endswith('.csv'):
            return pd.read_csv(self.filepath)
        elif self.filepath.endswith('.xlsx') or self.filepath.endswith('.xls'):
            return pd.read_excel(self.filepath)
        elif self.filepath.endswith('.json'):
            return pd.read_json(self.filepath)
        elif self.filepath.endswith('.parquet'):
            return pd.read_parquet(self.filepath)
        elif self.filepath.endswith('.txt'):
            return pd.read_table(self.filepath)
        elif self.filepath.endswith('.html'):
            return pd.read_html(self.filepath)
        elif self.filepath.endswith('.feather'):
            return pd.read_feather(self.filepath)
        elif self.filepath.endswith('.pickle') or self.filepath.endswith('.pkl'):
            return pd.read_pickle(self.filepath)
        elif self.filepath.endswith('.hdf') or self.filepath.endswith('.h5'):
            return pd.read_hdf(self.filepath)
        elif self.filepath.endswith('.dta'):
            return pd.read_stata(self.filepath)
        elif self.filepath.endswith('.sas7bdat'):
            return pd.read_sas(self.filepath)
        else:
            raise ValueError(f"Unsupported file format: {self.filepath}")
    
    def read_sql(self, query, con):
        """
        Read a SQL query into a DataFrame.
        """
        return pd.read_sql(query, con=con)

    def mean(self, column):
        """
        Return the mean of a specified column in the DataFrame.
        """
        df = self.read()
        if column not in df.columns:
            raise ValueError(f"Column '{column}' does not exist in the DataFrame.")
        return df[column].mean()

    def median(self, column:pd.Series|pd.DataFrame):
        """
        Return the median of a specified column in the DataFrame.
        """
        df = self.read()
        if column not in df.columns:
            raise ValueError(f"Column '{column}' does not exist in the DataFrame.")
        return df[column].median()
    
    def mode(self, column:pd.Series|pd.DataFrame):
        """
        Return the mode of a specified column in the DataFrame.
        """
        df = self.read()
        if column not in df.columns:
            raise ValueError(f"Column '{column}' does not exist in the DataFrame.")
        return df[column].mode()

    def describe(self):
        """ 
        Generate descriptive statistics of the DataFrame.
        """
        df = self.read()
        return df.describe()
    def head(self, n=5):
        """ 
        Return the first n rows of the DataFrame.
        """
        df = self.read()
        return df.head(n)
    def tail(self, n=5):
        """ 
        Return the last n rows of the DataFrame.
        """
        df = self.read()
        return df.tail(n)
    def shape(self):
        """ 
        Return the shape of the DataFrame.
        """
        df = self.read()
        return df.shape
    def info(self):
        """ 
        Return information about the DataFrame.
        """
        df = self.read()
        return df.info()
    def columns(self):
        """ 
        Return the columns of the DataFrame.
        """
        df = self.read()
        return df.columns.tolist()
    def dtypes(self):
        """ 
        Return the data types of the columns in the DataFrame.
        """
        df = self.read()
        return df.dtypes
    def isnull(self):
        """ 
        Return the number of missing values in each column of the DataFrame.
        """
        df = self.read()
        return df.isnull().sum()
    def dropna(self):
        """ 
        Return a DataFrame with missing values dropped.
        """
        df = self.read()
        return df.dropna()
    def drop(self, columns):
        """ 
        Return a DataFrame with specified columns dropped.
        """
        df = self.read()
        return df.drop(columns=columns)
    
    def fillna(self, value):
        """ 
        Return a DataFrame with missing values filled.
        """
        df = self.read()
        return df.fillna(value)
    def sample(self, n=5):
        """ 
        Return a random sample of n rows from the DataFrame.
        """
        df = self.read()
        return df.sample(n)
    def unique(self, column):
        """ 
        Return unique values from a specified column in the DataFrame.
        """
        df = self.read()
        if column not in df.columns:
            raise ValueError(f"Column '{column}' does not exist in the DataFrame.")
        return df[column].unique()
    
    def value_counts(self, column):
        """ 
        Return the counts of unique values in a specified column.
        """
        df = self.read()
        if column not in df.columns:
            raise ValueError(f"Column '{column}' does not exist in the DataFrame.")
        return df[column].value_counts()
    def groupby(self, column):
        """ 
        Return a DataFrame grouped by a specified column.
        """
        df = self.read()
        if column not in df.columns:
            raise ValueError(f"Column '{column}' does not exist in the DataFrame.")
        return df.groupby(column).size()
    def sort_values(self, column, ascending=True):
        """
          Return a DataFrame sorted by a specified column.
        """
        df = self.read()
        if column not in df.columns:
            raise ValueError(f"Column '{column}' does not exist in the DataFrame.")
        return df.sort_values(by=column, ascending=ascending)
    def to_csv(self, df, output_path):
        if not output_path.endswith('.csv'):
            raise ValueError("Output path must end with '.csv'")
        df.to_csv(output_path, index=False)
    def to_excel(self, df, output_path):
        if not output_path.endswith('.xlsx') and not output_path.endswith('.xls'):
            raise ValueError("Output path must end with '.xlsx' or '.xls'")
        df.to_excel(output_path, index=False)
    def to_json(self, df, output_path):
        if not output_path.endswith('.json'):
            raise ValueError("Output path must end with '.json'")
        df.to_json(output_path, orient='records', lines=True)
    def to_parquet(self, df, output_path):
        if not output_path.endswith('.parquet'):
            raise ValueError("Output path must end with '.parquet'")
        df.to_parquet(output_path, index=False)
    def to_html(self, df, output_path):
        if not output_path.endswith('.html'):
            raise ValueError("Output path must end with '.html'")
        df.to_html(output_path, index=False)
    def to_feather(self, df, output_path):
        if not output_path.endswith('.feather'):
            raise ValueError("Output path must end with '.feather'")
        df.to_feather(output_path)
    def to_pickle(self, df, output_path):
        if not output_path.endswith('.pickle') and not output_path.endswith('.pkl'):
            raise ValueError("Output path must end with '.pickle' or '.pkl'")
        df.to_pickle(output_path)
    def to_hdf(self, df, output_path):
        if not output_path.endswith('.hdf') and not output_path.endswith('.h5'):
            raise ValueError("Output path must end with '.hdf' or '.h5'")
        df.to_hdf(output_path, key='df', mode='w')
    def to_stata(self, df, output_path):
        if not output_path.endswith('.dta'):
            raise ValueError("Output path must end with '.dta'")
        df.to_stata(output_path, write_index=False)
    def to_sas(self, df, output_path):
        if not output_path.endswith('.sas7bdat'):
            raise ValueError("Output path must end with '.sas7bdat'")
        df.to_sas(output_path, index=False)
    def to_sql(self, df, table_name, con):
        """
        Write a DataFrame to a SQL database table.
        """
        df.to_sql(table_name, con=con, if_exists='replace', index=False)


class DataSplitter:
    """
    A class to split a pandas DataFrame into training and testing sets
    upon initialization. The split data is then accessible via properties.
    
    This class is designed to perform the split only once for efficiency.
    """
    import pandas as pd
    from sklearn.model_selection import train_test_split
    from typing import Tuple
    def __init__(self, data: pd.DataFrame, target_column: str, test_size: float = 0.2, random_state: int = None):
        """
        Initializes the DataSplitter and performs the data split immediately.

        :param data: pandas DataFrame containing the full dataset.
        :param target_column: The name of the column to be used as the target (y).
        :param test_size: Proportion of the dataset to include in the test split.
        :param random_state: Controls the shuffling applied to the data before splitting for reproducibility.
        """
        # --- Input Validation ---
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Input 'data' must be a pandas DataFrame.")
        if target_column not in data.columns:
            raise ValueError(f"Target column '{target_column}' not found in the DataFrame's columns.")
        if not 0 < test_size < 1:
            raise ValueError("test_size must be a float between 0 and 1.")

        # The core logic is now in a private method called from the initializer
        self._split_data(data, target_column, test_size, random_state)

    def _split_data(self, data: pd.DataFrame, target_column: str, test_size: float, random_state: int):
        """A private helper method to perform the split and store the results."""
        from sklearn.model_selection import train_test_split
        # Separate features (X) and target (y)
        X = data.drop(columns=[target_column])
        y = data[target_column]

        self._X_train, self._X_test, self._y_train, self._y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )

    def __repr__(self):
        return (f"DataSplitter(test_size={self._X_test.shape[0] / (self._X_train.shape[0] + self._X_test.shape[0])}, "
                f"random_state={self._y_train.index})")
    
    @property
    def X_train(self) -> pd.DataFrame:
        """Returns the training features DataFrame."""
        return self._X_train

    @property
    def X_test(self) -> pd.DataFrame:
        """Returns the testing features DataFrame."""
        return self._X_test

    @property
    def y_train(self) -> pd.Series:
        """Returns the training target Series."""
        return self._y_train

    @property
    def y_test(self) -> pd.Series:
        """Returns the testing target Series."""
        return self._y_test

    def get_all_splits(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """A convenience method to get all four data splits at once."""
        return self.X_train, self.X_test, self.y_train, self.y_test


class ImageDataLoader:
    """
    A fully dynamic image data loader and preprocessor for ML/DL projects.
    """
    import os
    import random
    from typing import Tuple, List, Optional, Dict, Generator
    import numpy as np
    from PIL import Image, ImageOps, ImageEnhance
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import OneHotEncoder
    from collections import Counter
    def __init__(
        self,
        file_path: str,
        target_size: Tuple[int, int] = (128, 128),
        color_mode: str = "rgb",
        shuffle: bool = True,
        seed: Optional[int] = 42,
        channels_last: bool = True,
        one_hot: bool = True,
        **kwargs
    ):
        """Initialize the ImageDataLoader with the given parameters.

        Args:
            file_path (str): The path to the image dataset.
            target_size (Tuple[int, int], optional): The target size for resizing images. Defaults to (128, 128).
            color_mode (str, optional): The color mode to use for loading images. Defaults to "rgb".
            shuffle (bool, optional): Whether to shuffle the dataset. Defaults to True.
            seed (Optional[int], optional): Random seed for reproducibility. Defaults to 42.
            channels_last (bool, optional): Whether to use channels_last data format. Defaults to True.
            one_hot (bool, optional): Whether to use one-hot encoding for labels. Defaults to True.
            **kwargs: Additional keyword arguments.
        """
        import numpy as np
        import random

        self.file_path = file_path
        self.target_size = target_size
        self.color_mode = color_mode.lower()
        self.shuffle = shuffle
        self.seed = seed
        self.channels_last = channels_last
        self.one_hot = one_hot

        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

    def load_data(self) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Load all images from folder structure: root/class_name/image.ext
        """
        import os
        import numpy as np
        from PIL import Image
        from sklearn.preprocessing import OneHotEncoder

        images = []
        labels = []

        # Classes are folder names
        class_names = sorted([
            d for d in os.listdir(self.file_path)
            if os.path.isdir(os.path.join(self.file_path, d))
        ])

        if class_names:
            # Images are organized in subfolders (classes)
            for label_index, class_name in enumerate(class_names):
                class_folder = os.path.join(self.file_path, class_name)
                for img_file in os.listdir(class_folder):
                    if img_file.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp")):
                        img_path = os.path.join(class_folder, img_file)
                        try:
                            img = Image.open(img_path)

                            # Convert color mode
                            if self.color_mode == "rgb":
                                img = img.convert("RGB")
                            elif self.color_mode == "grayscale":
                                img = img.convert("L")

                            # Resize
                            img = img.resize(self.target_size)

                            img_array = np.array(img, dtype=np.float32)

                            if not self.channels_last:
                                if self.color_mode == "rgb":
                                    img_array = np.transpose(img_array, (2, 0, 1))
                                else:
                                    img_array = np.expand_dims(img_array, axis=0)

                            images.append(img_array)
                            labels.append(label_index)

                        except Exception as e:
                            print(f"Skipping {img_path}: {e}")
        else:
            # No subfolders: treat all images in root as one class
            class_names = ["default"]
            for img_file in os.listdir(self.file_path):
                if img_file.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp")):
                    img_path = os.path.join(self.file_path, img_file)
                    try:
                        img = Image.open(img_path)

                        # Convert color mode
                        if self.color_mode == "rgb":
                            img = img.convert("RGB")
                        elif self.color_mode == "grayscale":
                            img = img.convert("L")

                        # Resize
                        img = img.resize(self.target_size)

                        img_array = np.array(img, dtype=np.float32)

                        if not self.channels_last:
                            if self.color_mode == "rgb":
                                img_array = np.transpose(img_array, (2, 0, 1))
                            else:
                                img_array = np.expand_dims(img_array, axis=0)

                        images.append(img_array)
                        labels.append(0)

                    except Exception as e:
                        print(f"Skipping {img_path}: {e}")

        images = np.array(images, dtype=np.float32)
        labels = np.array(labels)

        if len(images) == 0 or len(labels) == 0:
            print("No images found in the specified directory.")
            return images, labels, class_names

        if self.shuffle:
            idx = np.arange(len(images))
            np.random.shuffle(idx)
            images, labels = images[idx], labels[idx]

        # One-hot encode labels for DL models
        if self.one_hot:
            enc = OneHotEncoder(sparse_output=False)
            labels = enc.fit_transform(labels.reshape(-1, 1))

        return images, labels, class_names

    def preprocess_data(self, images, normalize: bool = True, standardize: bool = False):
        """
        Preprocess image data (normalization, standardization, etc.)
        Ensures uniform shape for DL models.
        """
        import cv2
        import numpy as np
        processed_images = []
        for img in images:
            # Skip non-array or non-numeric types
            if isinstance(img, str):
                continue
            img = np.array(img, dtype=np.float32)

            # If grayscale, convert to 3 channels
            if self.color_mode == "rgb" and img.ndim == 2:
                img = np.stack([img] * 3, axis=-1)
            elif self.color_mode == "grayscale" and img.ndim == 3:
                img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
                img = np.expand_dims(img, axis=-1)

            processed_images.append(img)

        images = np.array(processed_images, dtype=np.float32)

        if normalize:
            images = images / 255.0
        if standardize:
            mean = np.mean(images, axis=(0, 1, 2), keepdims=True)
            std = np.std(images, axis=(0, 1, 2), keepdims=True) + 1e-7
            images = (images - mean) / std

        return images
    
    def list_folder(self):
        """List the subfolders in the given dataset path."""
        import os
        if not os.path.isdir(self.file_path):
            raise NotADirectoryError(f"{self.file_path} is not a valid directory.")
        return [d for d in os.listdir(self.file_path) if os.path.isdir(os.path.join(self.file_path, d))]


    def augment_data(self, images: np.ndarray, **kwargs) -> np.ndarray:
        """
        Apply basic augmentations for DL models.
        Args:
            images (np.ndarray): Input images.
        Returns:
            np.ndarray: Augmented images.
        """
        import random
        from PIL import Image, ImageOps, ImageEnhance
        import numpy as np
        augmented_images = []
        for img_array in images:
            img = Image.fromarray((img_array * 255).astype(np.uint8))

            if random.random() > 0.5:
                img = ImageOps.mirror(img)
            if random.random() > 0.5:
                img = img.rotate(random.randint(-15, 15))
            if random.random() > 0.5:
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(random.uniform(0.8, 1.2))

            aug_img = np.array(img) / 255.0
            if not self.channels_last and len(aug_img.shape) == 3:
                aug_img = np.transpose(aug_img, (2, 0, 1))

            augmented_images.append(aug_img)

        return np.array(augmented_images, dtype=np.float32)

    def stratified_split(
        self, images: np.ndarray, labels: np.ndarray,
        split_ratio: Dict[str, float] = None,
        **kwargs
    ):
        """
        Stratified split the dataset into train, validation, and test sets.
        Args:
            images (np.ndarray): Input images.
            labels (np.ndarray): Input labels.
            split_ratio (Dict[str, float], optional): Split ratios for train, val, and test sets.
        Returns:
            Tuple[Tuple[np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray]]: Split datasets.
        """
        import numpy as np
        from sklearn.model_selection import train_test_split
        if split_ratio is None:
            split_ratio = {"train": 0.7, "val": 0.2, "test": 0.1}

        y_indices = np.argmax(labels, axis=1) if self.one_hot else labels

        X_train, X_temp, y_train, y_temp = train_test_split(
            images, labels, test_size=1 - split_ratio["train"],
            stratify=y_indices, random_state=self.seed
        )
        val_size = split_ratio["val"] / (split_ratio["val"] + split_ratio["test"])
        X_val, X_test, y_val, y_test = train_test_split(
            X_temp, y_temp, test_size=1 - val_size,
            stratify=np.argmax(y_temp, axis=1) if self.one_hot else y_temp,
            random_state=self.seed
        )

        return (X_train, y_train), (X_val, y_val), (X_test, y_test)

    def batch_generator(
        self, images: np.ndarray, labels: np.ndarray, batch_size: int = 32, augment: bool = False, **kwargs
    ) -> Generator[Tuple[np.ndarray, np.ndarray], None, None]:
        """
        Create a generator for DL frameworks like TensorFlow/Keras/PyTorch.
        Args:
            images (np.ndarray): Input images.
            labels (np.ndarray): Input labels.
            batch_size (int, optional): Batch size for the generator.
            augment (bool, optional): Whether to apply data augmentation.
        Returns:
            Generator[Tuple[np.ndarray, np.ndarray], None, None]: A generator that yields batches of images and labels.
        """
        import numpy as np
        total_samples = len(images)
        while True:
            idx = np.arange(total_samples)
            if self.shuffle:
                np.random.shuffle(idx)
            for start in range(0, total_samples, batch_size):
                end = min(start + batch_size, total_samples)
                batch_idx = idx[start:end]
                batch_x = images[batch_idx]
                batch_y = labels[batch_idx]

                if augment:
                    batch_x = self.augment_data(batch_x)

                yield batch_x, batch_y

    def compute_class_weights(self, labels: np.ndarray, **kwargs) -> Dict[int, float]:
        """
        Compute class weights for imbalanced datasets.
        """
        import numpy as np
        from collections import Counter
        if self.one_hot:
            labels = np.argmax(labels, axis=1)
        counts = Counter(labels)
        total = sum(counts.values())
        return {cls: total / (len(counts) * count) for cls, count in counts.items()}
    
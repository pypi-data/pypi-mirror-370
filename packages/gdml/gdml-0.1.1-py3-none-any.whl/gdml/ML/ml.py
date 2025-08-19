import dis
import os


class ML_regression:
    import pandas as pd
    def __init__(self, model: str, dataset: dict | pd.DataFrame, **kwargs):
        """
        Initialize the ML_regression class with a specific regression algorithm.
        Args:
            model (str): The name of the model to be used.
            dataset (dict | pd.DataFrame): A dictionary containing 'X_train' and 'y_train' for training data.
            train_size (int, optional): Size of the training set. Defaults to None.
            test_size (int, optional): Size of the test set. Defaults to None.
        """
        self.available_models = [
            'LinearRegression', 'Ridge_regression', 'Lasso_regression', 'ElasticNet_regression',
            'SVR_regression', 'Logistic_regression', 'GradientBoosting',
            'XGBoost_regression', 'CatBoost_regression', 'LightGBM_regression','DecisionTree_Regressor','RandomForest_Regressor'
        ]
        if model not in self.available_models:
            raise ValueError(f"Model '{model}' is not supported. Choose from {self.available_models}")
        self.model_name = model
        self.dataset = dataset
        # Instantiate and fit the selected model
        model_method = getattr(self, model)
        self.model = model_method()
    def __repr__(self):
        return f"ML(model={self.model}, dataset={self.dataset})"
    def LinearRegression(self):
        """
        Train a Linear Regression model.
        Returns:
            model: Fitted Linear Regression model.
        """
        from sklearn.linear_model import LinearRegression
        model = LinearRegression()
        model.fit(self.dataset['X_train'], self.dataset['y_train'])
        return model
    def Ridge_regression(self):
        """
        Train a Ridge Regression model.
        Returns:
            model: Fitted Ridge Regression model.
        """
        from sklearn.linear_model import Ridge
        model = Ridge()
        return model.fit(self.dataset['X_train'], self.dataset['y_train'])
    def Lasso_regression(self):
        """
        Train a Lasso Regression model.
        Returns:
            model: Fitted Lasso Regression model.
        """
        from sklearn.linear_model import Lasso
        model = Lasso()
        return model.fit(self.dataset['X_train'], self.dataset['y_train'])
    def ElasticNet_regression(self):
        """
        Train an Elastic Net Regression model.
        Returns:
            model: Fitted Elastic Net Regression model.
        """
        from sklearn.linear_model import ElasticNet
        model = ElasticNet()
        return model.fit(self.dataset['X_train'], self.dataset['y_train'])
    def SVR_regression(self):
        """
        Train a Support Vector Regression model.
        Returns:
            model: Fitted Support Vector Regression model.
        """
        from sklearn.svm import SVR
        model = SVR()
        return model.fit(self.dataset['X_train'], self.dataset['y_train'])
    def Logistic_regression(self):
        """ Train a Logistic Regression model.
        Returns:
            model: Fitted Logistic Regression model.
        """
        from sklearn.linear_model import LogisticRegression
        model = LogisticRegression()
        return model.fit(self.dataset['X_train'], self.dataset['y_train'])
    def GradientBoosting(self):
        """ Train a Gradient Boosting model.
        Returns:
            model: Fitted Gradient Boosting model.
        """
        from sklearn.ensemble import GradientBoostingRegressor
        model = GradientBoostingRegressor()
        return model.fit(self.dataset['X_train'], self.dataset['y_train'])
    def DecisionTree_Regressor(self):
        """ Train a Decision Tree Regressor model.
        Returns:
            model: Fitted Decision Tree Regressor model.
        """
        from sklearn.tree import DecisionTreeRegressor
        model = DecisionTreeRegressor()
        return model.fit(self.dataset['X_train'], self.dataset['y_train'])
    def RandomForest_Regressor(self):
        """ Train a Random Forest Regressor model.
        Returns:
            model: Fitted Random Forest Regressor model.
        """
        from sklearn.ensemble import RandomForestRegressor
        model = RandomForestRegressor()
        return model.fit(self.dataset['X_train'], self.dataset['y_train'])
    def XGBoost_regression(self):
        """ Train an XGBoost Regression model.
        Returns:
            model: Fitted XGBoost Regression model.
        """
        from xgboost import XGBRegressor
        model = XGBRegressor()
        return model.fit(self.dataset['X_train'], self.dataset['y_train'])  
    def CatBoost_regression(self):
        """
        Train a CatBoost Regression model.
        Returns:
            model: Fitted CatBoost Regression model.
        """
        from catboost import CatBoostRegressor
        model = CatBoostRegressor()
        return model.fit(self.dataset['X_train'], self.dataset['y_train'])
    def LightGBM_regression(self):
        """
        Train a LightGBM Regression model.
        Returns:
            model: Fitted LightGBM Regression model.
        """
        from lightgbm import LGBMRegressor
        model = LGBMRegressor()
        return model.fit(self.dataset['X_train'], self.dataset['y_train'])
    def predict(self, X):
        """
        Predict values using the trained model.
        Args:
            X (array-like): Input features for prediction.
        Returns:
            array-like: Predicted values.
        """
        return self.model.predict(X)
    def score(self, X, y):
        """
        Evaluate the model's performance.
        Args:
            X (array-like): Input features for evaluation.
            y (array-like): True target values.
        Returns:
            float: R^2 score of the model.
        """
        return self.model.score(X, y)
    def plot(self, X, y_true=None):
        """
        Plots predicted vs actual target values for multi-feature regression models.

        Args:
            X (array-like): Test features.
            y_true (array-like, optional): True target values.
        """
        import matplotlib.pyplot as plt
        import seaborn as sns

        y_pred = self.model.predict(X)
        if y_true is None:
            y_true = y_pred

        plt.figure(figsize=(10, 6))
        sns.scatterplot(x=y_true, y=y_pred)
        plt.plot([min(y_true), max(y_true)], [min(y_true), max(y_true)], color='red', linestyle='--', label='Ideal Fit')
        plt.xlabel('True Values')
        plt.ylabel('Predicted Values')
        plt.title(f'{self.model_name} - Predicted vs Actual')
        plt.legend()
        plt.show()

    def get_params(self, deep=True):
        """
        Get model parameters.
        Args:
            deep (bool): Whether to return parameters for nested objects.
        Returns:
            dict: Model parameters.
        """
        return self.model.get_params(deep=deep)
    def set_params(self, **params):
        """ 
        Set model parameters.
        Args:
            **params: Parameters to set for the model.
        Returns:
            self: The instance of the model with updated parameters.
        """ 
        return self.model.set_params(**params)
    def coff(self):
        """
        Get the coefficients of the model.
        Returns:
            array-like: Coefficients of the model.
        """
        if hasattr(self.model, 'coef_'):
            return self.model.coef_
        else:
            raise AttributeError("This model does not have coefficients.")
        
    def intercept(self):
        """
        Get the intercept of the model.
        Returns:
            float: Intercept of the model.
        """
        if hasattr(self.model, 'intercept_'):
            return self.model.intercept_
        else:
            raise AttributeError("This model does not have an intercept.")
    def save_model(self, filename):
        """
        Save the trained model to a file.
        Args:
            filename (str): The name of the file to save the model.
        """
        import joblib
        joblib.dump(self.model, filename)
    def load_model(self, filename):
        """
        Load a trained model from a file.
        Args:
            filename (str): The name of the file to load the model from.
        Returns:
            model: The loaded model.
        """
        import joblib
        self.model = joblib.load(filename)
        return self.model
    def r2_score(self, X, y):
        """
        Calculate the R^2 score of the model.
        Args:
            X (array-like): Input features for evaluation.
            y (array-like): True target values.
        Returns:
            float: R^2 score of the model.
        """
        from sklearn.metrics import r2_score
        return r2_score(y, self.predict(X))
    def mean_squared_error(self, X, y):
        """
        Calculate the mean squared error of the model.
        Args:
            X (array-like): Input features for evaluation.
            y (array-like): True target values.
        Returns:
            float: Mean squared error of the model.
        """
        from sklearn.metrics import mean_squared_error
        return mean_squared_error(y, self.predict(X))
    def mean_absolute_error(self, X, y):
        """
        Calculate the mean absolute error of the model.
        Args:
            X (array-like): Input features for evaluation.
            y (array-like): True target values.
            Returns:
            float: Mean absolute error of the model.
        """
        from sklearn.metrics import mean_absolute_error
        return mean_absolute_error(y, self.predict(X))
    def explained_variance_score(self, X, y):
        """
        Calculate the explained variance score of the model.
        Args:
            X (array-like): Input features for evaluation.
            y (array-like): True target values.
        Returns:
            float: Explained variance score of the model.
        """
        from sklearn.metrics import explained_variance_score
        return explained_variance_score(y, self.predict(X))
    def model_matrix(self, X):
        """
        Get the model matrix for the input features.
        Args:
            X (array-like): Input features.
        Returns:
            array-like: Model matrix.
        """
        import numpy as np
        if hasattr(self.model, 'coef_'):
            return np.dot(X, self.model.coef_) + self.model.intercept_
        else:
            raise AttributeError("This model does not support model matrix calculation.")
    def feature_importances(self):
        """
        Get the feature importances of the model.
        Returns:
            array-like: Feature importances.
        """
        if hasattr(self.model, 'feature_importances_'):
            return self.model.feature_importances_
        else:
            raise AttributeError("This model does not have feature importances.")
    def get_model(self):
        """
        Get the trained model.
        Returns:
            model: The trained model.
        """
        return self.model
    def get_model_name(self):
        """
        Get the name of the model.
        Returns:
            str: The name of the model.
        """
        return self.model_name
    def model_confussion_matrix(self, X, y):
        """
        Calculate the confusion matrix for the model.
        Args:
            X (array-like): Input features for evaluation.
            y (array-like): True target values.
        Returns:
            array-like: Confusion matrix.
        """
        from sklearn.metrics import confusion_matrix
        return confusion_matrix(y, self.predict(X))

class ML_classification():
    import pandas as pd
    def __init__(self, model: str | None, dataset: dict | pd.DataFrame, **kwargs):
        """
        Initialize the ML_classification class with a specific classification algorithm.
        Args:
            model (str): The name of the model to be used.
            dataset (dict): A dictionary containing 'X_train' and 'y_train' for training data.
        """
        self.available_models = [
            'Logistic_regression', 'DecisionTree_Classifier', 'RandomForest_Classifier',
            'GradientBoosting_Classifier', 'XGBoost_classifier', 'CatBoost_classifier',
            'LightGBM_classifier', 'SVC_classifier', 'KNeighbors_classifier', 'NaiveBayes_classifier','MLP_classifier',
        ]
        self.model_name = model
        if model not in self.available_models:
            raise ValueError(f"Model '{model}' is not supported. Choose from {self.available_models}")
        X_train = dataset['X_train']
        if hasattr(X_train, 'ndim') and X_train.ndim > 2:
            X_train = X_train.reshape((X_train.shape[0], -1))
        self.dataset = dataset.copy()
        self.dataset['X_train'] = X_train
        model_method = getattr(self, model)
        self.model = model_method()
        
    def __repr__(self):
        """
        String representation of the ML_classification object.
        Returns:
            str: String representation of the object.
        """
        return f"ML_classification(model={self.model})"
    
    def Logistic_regression(self):
        """
        Logistic Regression model.
        Returns:
            model: Fitted Logistic Regression model.
        """
        from sklearn.linear_model import LogisticRegression
        model = LogisticRegression()
        return model.fit(self.dataset['X_train'], self.dataset['y_train'])
    def DecisionTree_Classifier(self):
        """
        Decision Tree Classifier model.
        Returns:
            model: Fitted Decision Tree Classifier model.
        """
        from sklearn.tree import DecisionTreeClassifier
        model = DecisionTreeClassifier()
        return model.fit(self.dataset['X_train'], self.dataset['y_train'])
    def RandomForest_Classifier(self):
        """
        Random Forest Classifier model.
        Returns:
            model: Fitted Random Forest Classifier model.
        """
        from sklearn.ensemble import RandomForestClassifier
        model = RandomForestClassifier()
        return model.fit(self.dataset['X_train'], self.dataset['y_train'])
    def GradientBoosting_Classifier(self):
        """
        Gradient Boosting Classifier model.
        Returns:
            model: Fitted Gradient Boosting Classifier model.
        """
        from sklearn.ensemble import GradientBoostingClassifier
        model = GradientBoostingClassifier()
        return model.fit(self.dataset['X_train'], self.dataset['y_train'])
    def XGBoost_classifier(self):
        """
        XGBoost Classifier model.
        Return:
        model: Fitted XGBoost Classifier model.
        """
        from xgboost import XGBClassifier
        model = XGBClassifier()
        return model.fit(self.dataset['X_train'], self.dataset['y_train'])
    def CatBoost_classifier(self):
        """
        CatBoost Classifier model.
        Return:
        model: Fitted CatBoost Classifier model.
        """
        from catboost import CatBoostClassifier
        model = CatBoostClassifier()
        return model.fit(self.dataset['X_train'], self.dataset['y_train'])
    def LightGBM_classifier(self):
        """
        LightGBM Classifier model.
        Return:
        model : Fitted LightGBM Classifier model.
        """
        from lightgbm import LGBMClassifier
        model = LGBMClassifier()
        return model.fit(self.dataset['X_train'], self.dataset['y_train'])
    def SVC_classifier(self):
        """
        SVC Classifier model.
        Return:
        model : Fitted SVC Classifier model.
        """
        from sklearn.svm import SVC
        model = SVC()
        return model.fit(self.dataset['X_train'], self.dataset['y_train'])
    def KNeighbors_classifier(self):
        """
        Kneighbors Classifier model.
        Return:
        model : Fitted Kneighbors Classifier model.
        """
        from sklearn.neighbors import KNeighborsClassifier
        model = KNeighborsClassifier()
        return model.fit(self.dataset['X_train'], self.dataset['y_train'])
    def NaiveBayes_classifier(self):
        """
        Naive Bayes Classifier model.
        Return:
        model : Fitted Naive Bayes Classifier model.
        """
        from sklearn.naive_bayes import GaussianNB
        model = GaussianNB()
        return model.fit(self.dataset['X_train'], self.dataset['y_train'])
    def MLP_classifier(self):
        """
        Multi-layer Perceptron Classifier model.
        Return:
        model : Fitted Multi-layer Perceptron Classifier model.
        """
        from sklearn.neural_network import MLPClassifier
        model = MLPClassifier()
        return model.fit(self.dataset['X_train'], self.dataset['y_train'])
    def predict(self, X):
        """
        Predict class labels for the input features.
        Returns:
            array-like: Predicted class labels.
        """
        return self.model.predict(X)
    def score(self, X, y):
        """
        It will Return The model score based on the input features and true labels.
        args:
        x (array-like): Input features for evaluation.
        y (array-like): True class labels.
        """
        return self.model.score(X, y)
    
    def get_params(self, deep=True):
        """
        Get model parameters.
        Args:
            deep (bool): Whether to return parameters for nested objects.
        Returns:
            dict: Model parameters.
        """
        return self.model.get_params(deep=deep)
    def set_params(self, **params):
        """
        Set model parameters.
        Args:
            **params: Parameters to set for the model.
        """
        return self.model.set_params(**params)
    def coff(self):
        """
        Get the coefficients of the model.
        Returns:
            array-like: Coefficients of the model.
        """
        if hasattr(self.model, 'coef_'):
            return self.model.coef_
        else:
            raise AttributeError("This model does not have coefficients.")
        
    def intercept(self):
        """
        Get the intercept of the model.
        Returns:
            float: Intercept of the model.
        """
        if hasattr(self.model, 'intercept_'):
            return self.model.intercept_
        else:
            raise AttributeError("This model does not have an intercept.")
    def save_model(self, filename):
        """
        Save the trained model to a file.
        Args:
            filename (str): The name of the file to save the model.
        """
        import joblib
        joblib.dump(self.model, filename)
    def load_model(self, filename):
        """
        Load a trained model from a file.
        Args:
            filename (str): The name of the file to load the model from.
        Returns:
            model: The loaded model.
        """
        import joblib
        self.model = joblib.load(filename)
        return self.model
    def plot(self, X, y=None):
        """
        Plots the predicted classes in 2D space.
        Args:
            X (array-like): Input features for plotting.
            y (array-like, optional): True class labels for coloring.
        """
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        if y is None:
            y = self.predict(X)
        
        plt.figure(figsize=(10, 6))
        # Use .iloc for pandas DataFrame, fallback to slicing for numpy arrays
        try:
            x1 = X.iloc[:, 0]
            x2 = X.iloc[:, 1]
        except AttributeError:
            x1 = X[:, 0]
            x2 = X[:, 1]
        sns.scatterplot(x=x1, y=x2, hue=y, palette='viridis', s=100)
        plt.title(f'Predicted Classes using {self.model_name}')
        plt.xlabel('Feature 1')
        plt.ylabel('Feature 2')
        plt.legend(title='Classes')
        plt.show()
    def classification_report(self, X, y):
        """
        Generate a classification report.
        Args:
            X (array-like): Input features for evaluation.
            y (array-like): True class labels.
        Returns:
            str: Classification report.
        """
        from sklearn.metrics import classification_report
        y_pred = self.predict(X)
        return classification_report(y, y_pred)
    def confusion_matrix(self, X, y):
        """
        Generates a classification confusion matrix.
        Args:
            X (array-like): Input features for evaluation.
            y (array-like): True class labels.
        Returns:
            str: Classification confusion matrix.
        """
        from sklearn.metrics import confusion_matrix
        return confusion_matrix(y, self.predict(X))
    def accuracy_score(self, X, y):
        """
        Calculate the accuracy score of the model.
        Args:
            X (array-like): Input features for evaluation.
            y (array-like): True class labels.
        Returns:
        str : Accuracy Score of the model.
        """
        from sklearn.metrics import accuracy_score
        return accuracy_score(y, self.predict(X))
    def ROC_AUC(self):
        """
        Generate the Receiver Operating Characteristic (ROC) curve.
        Returns:
            tuple: FPR, TPR, thresholds for the ROC curve.
        """
        from sklearn.metrics import roc_auc_score
        y_scores = self.model.predict_proba(self.dataset['X_train'])[:, 1]
        fpr, tpr, thresholds = roc_auc_score(self.dataset['y_train'], y_scores)
        return fpr, tpr, thresholds
    def feature_importances(self):
        """
        Get feature importances from the model.
        Returns:
            array-like: Feature importances.
        """
        if hasattr(self.model, 'feature_importances_'):
            return self.model.feature_importances_
        else:
            raise AttributeError("This model does not have feature importances.")
    def get_model(self):
        """
        It will Return The model
        """
        return self.model
    def mean_squared_error(self, X, y):
        """
        Calculate the mean squared error of the model.
        Args:
            X (array-like): Input features for evaluation.
            y (array-like): True target values.
        Returns:
            float: Mean squared error of the model.
        """
        from sklearn.metrics import mean_squared_error
        return mean_squared_error(y, self.predict(X))
    def mean_absolute_error(self, X, y):
        """
        Calculate the mean absolute error of the model.
        Args:
            X (array-like): Input features for evaluation.
            y (array-like): True target values.
            Returns:
            float: Mean absolute error of the model.
        """
        from sklearn.metrics import mean_absolute_error
        return mean_absolute_error(y, self.predict(X))
    def explained_variance_score(self, X, y):
        """
        Calculate the explained variance score of the model.
        Args:
            X (array-like): Input features for evaluation.
            y (array-like): True target values.
        Returns:
            float: Explained variance score of the model.
        """
        from sklearn.metrics import explained_variance_score
        return explained_variance_score(y, self.predict(X))
    def model_matrix(self, X):
        """
        Get the model matrix for the input features.
        Args:
            X (array-like): Input features.
        Returns:
            array-like: Model matrix.
        """
        import numpy as np
        if hasattr(self.model, 'coef_'):
            return np.dot(X, self.model.coef_) + self.model.intercept_
        else:
            raise AttributeError("This model does not support model matrix calculation.")
    

class ML_Clustering:
    import pandas as pd
    def __init__(self, model: str, dataset: pd.DataFrame, n:str|str = '4', **kwargs):
        """
        Initialize the ML_clustering class with a specific clustering algorithm.
        Args:
            model (str): The name of the model to be used.
            dataset (pd.DataFrame): A DataFrame containing 'X_train' for training data.
        """
        self.available_models = [
            'KMeans', 'DBSCAN', 'AgglomerativeClustering', 'GaussianMixture'
        ]
        if model not in self.available_models:
            raise ValueError(f"Model '{model}' is not supported. Choose from {self.available_models}")
        self.model_name = model
        self.dataset = dataset
        self.n = n
        model_method = getattr(self, model)
        self.model = model_method()
    
    def __repr__(self):
        return f"ML_clustering(model={self.model})"
    
    def KMeans(self):
        """ Train a KMeans clustering model.
        Returns:
            model: Fitted KMeans model.
        """
        import os
        os.environ['LOKY_MAX_CPU_COUNT'] = self.n
        from sklearn.cluster import KMeans
        model = KMeans()
        return model.fit(self.dataset['X_train'])
    
    def DBSCAN(self):
        """ Train a DBSCAN clustering model.
        Returns:
            model: Fitted DBSCAN model.
        """
        from sklearn.cluster import DBSCAN
        model = DBSCAN()
        return model.fit(self.dataset['X_train'])
    
    def AgglomerativeClustering(self):
        """ Train an Agglomerative Clustering model.
        Returns:
            model: Fitted Agglomerative Clustering model.
        """
        from sklearn.cluster import AgglomerativeClustering
        model = AgglomerativeClustering()
        return model.fit(self.dataset['X_train'])
    
    def GaussianMixture(self):
        """ Train a Gaussian Mixture Model.
        Returns:
            model: Fitted Gaussian Mixture Model.
        """
        import os
        os.environ['LOKY_MAX_CPU_COUNT'] = self.n
        from sklearn.mixture import GaussianMixture
        model = GaussianMixture()
        return model.fit(self.dataset['X_train'])
    def assign_labels(self, X):
        """
        Assigns cluster labels to the data.

        For inductive models like K-Means, this predicts labels for new data.
        For transductive models like DBSCAN, this fits the model to the data 
        and returns the labels for that same data.

        Args:
            X (array-like): Input features.

        Returns:
            array-like: Cluster labels.
        """
        # Check if the model is inductive (has a 'predict' method)
        if hasattr(self.model, 'predict'):
            # Assumes the model has already been fitted
            print("Model supports prediction. Assigning new data to existing clusters.")
            return self.model.predict(X)
        
        # Otherwise, assume it's transductive (like DBSCAN)
        elif hasattr(self.model, 'fit_predict'):
            print("Model does not support prediction. Fitting and labeling the provided data.")
            return self.model.fit_predict(X)
            
        else:
            raise NotImplementedError("The underlying model has neither a 'predict' nor a 'fit_predict' method.")
        
    def score(self, X, y):
        """
        Evaluate the model's performance.
        Args:
            X (array-like): Input features for evaluation.
        Returns:
            float: Silhouette score of the model.
        """
        from sklearn.metrics import silhouette_score
        return silhouette_score(X, y)
    def get_params(self, deep=True):
        """
        Get model parameters.
        Args:
            deep (bool): Whether to return parameters for nested objects.
        Returns:
            dict: Model parameters.
        """
        return self.model.get_params(deep=deep)
    def set_params(self, **params):
        """
        Set model parameters.
        Args:
            **params: Parameters to set for the model.
        Returns:
            self: The instance of the model with updated parameters.
        """
        return self.model.set_params(**params)
    def save_model(self, filename):
        """
        Save the trained model to a file.
        Args:
            filename (str): The name of the file to save the model.
        """
        import joblib
        joblib.dump(self.model, filename)
    def load_model(self, filename):
        """
        Load a trained model from a file.
        Args:
            filename (str): The name of the file to load the model from.   
        Returns:
            model: The loaded model.
        """
        import joblib
        self.model = joblib.load(filename)
        return self.model
    def get_model(self):
        """
        Get the trained model.
        Returns:
            model: The trained model.
        """
        return self.model
    def get_model_name(self):
        """
        Get the name of the trained model.
        Returns:
            str: The name of the trained model.
        """
        return self.model_name
    def feature_importances(self):
        """
        Get the feature importances of the model.
        Returns:
            array-like: Feature importances.
        """
        if hasattr(self.model, 'feature_importances_'):
            return self.model.feature_importances_
        else:
            raise AttributeError("This model does not have feature importances.")
    def Adjusted_Rand_Index(self, X, y):
        """
        Calculate the Adjusted Rand Index for clustering.
        Args:
            X (array-like): Input features for evaluation.
            y (array-like): True cluster labels.
        Returns:
            float: Adjusted Rand Index score.
        """
        from sklearn.metrics import adjusted_rand_score
        y_pred = self.predict(X)
        return adjusted_rand_score(y, y_pred)
    def Homogeneity_Score(self, X, y):
        """
        Calculate the Homogeneity Score for clustering.
        Args:
            X (array-like): Input features for evaluation.
            y (array-like): True cluster labels.
        Returns:
            float: Homogeneity Score.
        """
        from sklearn.metrics import homogeneity_score
        y_pred = self.predict(X)
        return homogeneity_score(y, y_pred)
    def Completeness_Score(self, X, y):
        """
        Calculate the Completeness Score for clustering.
        Args:
            X (array-like): Input features for evaluation.
            y (array-like): True cluster labels.
        Returns:
            float: Completeness Score.
        """
        from sklearn.metrics import completeness_score
        y_pred = self.predict(X)
        return completeness_score(y, y_pred)
    def V_measure_Score(self, X, y):
        """
        Calculate the V-measure Score for clustering.
        Args:
            X (array-like): Input features for evaluation.
            y (array-like): True cluster labels.
        Returns:
            float: V-measure Score.
        """
        from sklearn.metrics import v_measure_score
        y_pred = self.predict(X)
        return v_measure_score(y, y_pred)
    def Fowlkes_Mallows_Score(self, X, y):
        """
        Calculate the Fowlkes-Mallows Score for clustering.
        Args:
            X (array-like): Input features for evaluation.
            y (array-like): True cluster labels.
        Returns:
            float: Fowlkes-Mallows Score.
        """
        from sklearn.metrics import fowlkes_mallows_score
        y_pred = self.predict(X)
        return fowlkes_mallows_score(y, y_pred)
    def Davies_Bouldin_Index(self, X):
        """
        Calculate the Davies-Bouldin Index for clustering.
        Args:
            X (array-like): Input features for evaluation.
        Returns:
            float: Davies-Bouldin Index.
        """
        from sklearn.metrics import davies_bouldin_score
        y_pred = self.predict(X)
        return davies_bouldin_score(X, y_pred)
    def Calinski_Harabasz_Index(self, X):
        """
        Calculate the Calinski-Harabasz Index for clustering.
        Args:
            X (array-like): Input features for evaluation.
        Returns:
            float: Calinski-Harabasz Index.
        """
        from sklearn.metrics import calinski_harabasz_score
        y_pred = self.predict(X)
        return calinski_harabasz_score(X, y_pred)
    def predict(self, X):
        """
        Predict cluster labels for the input features.
        Args:
            X (array-like): Input features.
        Returns:
            array-like: Predicted cluster labels.
        """
        return self.assign_labels(X)

    def plot(self, X, y=None):
        """
        Plots the clusters in 2D space.
        Args:
            X (array-like): Input features for plotting.
            y (array-like, optional): True cluster labels for coloring.
        """
        import matplotlib.pyplot as plt
        from sklearn.decomposition import PCA

        pca = PCA(n_components=2)
        X_transformed = pca.fit_transform(X)

        plt.figure(figsize=(10, 6))
        if y is not None:
            plt.scatter(X_transformed[:, 0], X_transformed[:, 1], c=y, cmap='viridis', s=50, alpha=0.7)
            plt.title('Clusters with True Labels')
        else:
            y_pred = self.predict(X)
            plt.scatter(X_transformed[:, 0], X_transformed[:, 1], c=y_pred, cmap='viridis', s=50, alpha=0.7)
            plt.title('Clusters Predicted by Model')

        plt.xlabel('PCA Component 1')
        plt.ylabel('PCA Component 2')
        plt.show()

import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.exponential_smoothing.ets import ETSModel

from prophet import Prophet
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

class ML_TimeSeriesToolkit:
    """
    A comprehensive toolkit for time-series analysis, designed to handle
    everything from data loading and preprocessing to modeling and forecasting.
    """

    def __init__(self, data, value_col, date_col=None, freq=None):
        """
        Initializes the toolkit with time-series data.

        Args:
            data (pd.DataFrame): The input data containing the time series.
            value_col (str): The name of the column with the time-series values.
            date_col (str, optional): The name of the date column.
                                     If None, the DataFrame index is used.
            freq (str, optional): The frequency of the time series (e.g., 'D', 'M', 'MS').
                                If None, the frequency will be inferred.
        """
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Data must be a pandas DataFrame.")

        self.value_col = value_col
        self.df = data.copy()

        # --- Set up the Datetime Index ---
        if date_col:
            self.df[date_col] = pd.to_datetime(self.df[date_col])
            self.df.set_index(date_col, inplace=True)
        elif not isinstance(self.df.index, pd.DatetimeIndex):
            raise TypeError("DataFrame index must be a DatetimeIndex if date_col is not provided.")

        if freq:
            self.df = self.df.asfreq(freq)
        else:
            self.df = self.df.asfreq(self.df.index.inferred_freq)

        self.ts = self.df[self.value_col]
        self.model_results = {}
        self.active_model = None

        print("TimeSeriesToolkit initialized successfully.")
        print(f"Frequency: {self.df.index.inferred_freq}")
        print(f"Time range: {self.df.index.min()} to {self.df.index.max()}")

    def plot_series(self, title='Time Series'):
        """
        Plots the time series.
        """
        plt.style.use('seaborn-v0_8-whitegrid')
        plt.figure(figsize=(12, 6))
        plt.plot(self.ts)
        plt.title(title, fontsize=16)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel(self.value_col, fontsize=12)
        plt.show()

    def decompose(self, model='additive'):
        """
        Decomposes the time series into trend, seasonal, and residual components.

        Args:
            model (str): The model type, 'additive' or 'multiplicative'.
        """
        ts_clean = self.ts.dropna()
        if ts_clean.empty:
            print("Error: Time series is empty after dropping NaN values. Cannot perform decomposition.")
            return

        decomposition = seasonal_decompose(ts_clean, model=model)

        fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(12, 10), sharex=True)
        decomposition.observed.plot(ax=ax1, legend=False)
        ax1.set_ylabel('Observed')
        decomposition.trend.plot(ax=ax2, legend=False)
        ax2.set_ylabel('Trend')
        decomposition.seasonal.plot(ax=ax3, legend=False)
        ax3.set_ylabel('Seasonal')
        decomposition.resid.plot(ax=ax4, legend=False)
        ax4.set_ylabel('Residual')

        fig.suptitle('Time Series Decomposition', fontsize=16)
        plt.tight_layout(rect=[0, 0.03, 1, 0.97])
        plt.show()

    def check_stationarity(self):
        """
        Performs the Augmented Dickey-Fuller test to check for stationarity.
        """
        print('--- Augmented Dickey-Fuler Test ---')
        result = adfuller(self.ts.dropna())

        print(f'ADF Statistic: {result[0]:.4f}')
        print(f'p-value: {result[1]:.4f}')
        print('Critical Values:')
        for key, value in result[4].items():
            print(f'\t{key}: {value:.4f}')

        if result[1] <= 0.05:
            print("\nResult: The series is likely stationary (p-value <= 0.05).")
        else:
            print("\nResult: The series is likely non-stationary (p-value > 0.05).")

    def plot_autocorrelations(self, lags=40):
        """
        Plots the ACF and PACF plots to help determine model order.
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        plot_acf(self.ts.dropna(), ax=ax1, lags=lags)
        plot_pacf(self.ts.dropna(), ax=ax2, lags=lags)
        plt.show()

    def fit_arima(self, order=(1, 1, 1)):
        """
        Fits an ARIMA model to the time series.

        Args:
            order (tuple): The (p, d, q) order of the model.
        """
        print(f"Fitting ARIMA model with order {order}...")
        model = ARIMA(self.ts, order=order)
        self.model_results['ARIMA'] = model.fit()
        self.active_model = 'ARIMA'
        print(self.model_results['ARIMA'].summary())

    def fit_sarima(self, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12)):
        """
        Fits a SARIMA model to the time series.

        Args:
            order (tuple): The (p, d, q) order of the model.
            seasonal_order (tuple): The (P, D, Q, s) seasonal order of the model.
        """
        print(f"Fitting SARIMA model with order {order} and seasonal order {seasonal_order}...")
        model = SARIMAX(self.ts, order=order, seasonal_order=seasonal_order)
        self.model_results['SARIMA'] = model.fit(disp=False)
        self.active_model = 'SARIMA'
        print(self.model_results['SARIMA'].summary())

    def fit_ets(self, error="add", trend="add", seasonal="add", seasonal_periods=12):
        """
        Fits an Exponential Smoothing (ETS) model.

        Args:
            error (str): The error component ('add' or 'mul').
            trend (str): The trend component ('add', 'mul', or None).
            seasonal (str): The seasonal component ('add', 'mul', or None).
            seasonal_periods (int): The number of periods in a season.
        """
        print("Fitting ETS model...")
        model = ETSModel(self.ts, error=error, trend=trend, seasonal=seasonal, seasonal_periods=seasonal_periods)
        self.model_results['ETS'] = model.fit()
        self.active_model = 'ETS'
        print(self.model_results['ETS'].summary())

    def fit_prophet(self):
        """
        Fits Facebook's Prophet model.
        """
        print("Fitting Prophet model...")
        prophet_df = self.ts.reset_index()
        prophet_df.columns = ['ds', 'y']

        model = Prophet()
        model.fit(prophet_df)
        self.model_results['Prophet'] = model
        self.active_model = 'Prophet'
        print("Prophet model fitted successfully.")

    def plot_forecast(self, steps=12):
        """
        Generates and plots a forecast from the active fitted model.

        Args:
            steps (int): The number of future steps to forecast.
        """
        if not self.active_model:
            print("Error: No model has been fitted. Please run a fit method first.")
            return

        print(f"Generating forecast using {self.active_model} model...")

        if self.active_model in ['ARIMA', 'SARIMA', 'ETS']:
            forecast_results = self.model_results[self.active_model].forecast(steps=steps)
            # If forecast_results is a Series, use it directly; if it's a PredictionResults, use .predicted_mean
            if hasattr(forecast_results, 'predicted_mean'):
                forecast = forecast_results.predicted_mean
                conf_int = forecast_results.conf_int()
            else:
                forecast = forecast_results
                conf_int = None

        elif self.active_model == 'Prophet':
            model = self.model_results['Prophet']
            future = model.make_future_dataframe(periods=steps, freq=self.df.index.inferred_freq)
            forecast_df = model.predict(future)

            forecast = forecast_df.set_index('ds')['yhat'].tail(steps)
            conf_int = forecast_df[['ds', 'yhat_lower', 'yhat_upper']].set_index('ds').tail(steps)
        plt.figure(figsize=(12, 6))
        plt.plot(self.ts, label='Observed')
        plt.plot(forecast, label='Forecast', color='red')
        if conf_int is not None:
            plt.fill_between(conf_int.index,
                             conf_int.iloc[:, 0],
                             conf_int.iloc[:, 1], color='pink', alpha=0.5, label='Confidence Interval')
        plt.title(f'{self.active_model} Forecast', fontsize=16)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel(self.value_col, fontsize=12)
        plt.legend()
        plt.show()
    
class ML_RLAgent:
    """
    A Reinforcement Learning Agent that interacts with a Gym environment.
    """
    def __init__(self, env_name: str, algorithm: str = "q_learning", **kwargs):
        import gymnasium as gym
        import numpy as np
        import torch.nn as nn
        import torch.optim as optim
        import torch

        if algorithm.lower() not in ["q_learning", "sarsa", "dqn"]:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        env_ids = sorted(list(gym.envs.registry.keys()))
        if env_name not in env_ids:
            raise ValueError(f"Unknown environment: {env_name}. Available environments are: {env_ids}")

        self.env = gym.make(env_name)
        self.algorithm = algorithm.lower()
        self.kwargs = kwargs
        self.state = None
        self.done = False
        self.episode_rewards = []

        # Q-table (tabular)
        if self.algorithm in ["q_learning", "sarsa"]:
            if not hasattr(self.env.observation_space, 'n'):
                raise ValueError("Tabular methods require a discrete observation space.")
            self.q_table = np.zeros((self.env.observation_space.n, self.env.action_space.n))

        # DQN setup
        if self.algorithm == "dqn":
            if isinstance(self.env.observation_space, gym.spaces.Box):
                state_size = self.env.observation_space.shape[0]
            elif isinstance(self.env.observation_space, gym.spaces.Discrete):
                state_size = self.env.observation_space.n
            else:
                raise NotImplementedError(f"Observation space type {type(self.env.observation_space)} not supported for DQN")

            action_size = self.env.action_space.n
            self.model = self._build_dqn(state_size, action_size)
            self.target_model = self._build_dqn(state_size, action_size)
            self.target_model.load_state_dict(self.model.state_dict())
            self.target_model.eval()

            self.optimizer = optim.Adam(self.model.parameters(), lr=kwargs.get("lr", 0.001))
            self.criterion = nn.MSELoss()
            self.memory = []
            self.max_memory = 10000
            self.batch_size = kwargs.get("batch_size", 64)
            self.gamma = kwargs.get("gamma", 0.99)
            self.target_update_freq = kwargs.get("target_update_freq", 1000)
            self.update_counter = 0

    def _build_dqn(self, state_size, action_size):
        import torch.nn as nn
        import torch
        return nn.Sequential(
            nn.Linear(state_size, 64),
            torch.nn.ReLU(),
            nn.Linear(64, 64),
            torch.nn.ReLU(),
            nn.Linear(64, action_size)
        )

    def reset(self):
        self.state, _ = self.env.reset()
        self.done = False
        return self.state

    def step(self, action):
        next_state, reward, terminated, truncated, _ = self.env.step(action)
        self.state = next_state
        self.done = terminated or truncated
        return next_state, reward, self.done

    def get_action(self, epsilon):
        import numpy as np, random, torch
        if self.algorithm in ["q_learning", "sarsa"]:
            if np.random.rand() < epsilon:
                return self.env.action_space.sample()
            state_int = int(self.state) if not hasattr(self.state, "__len__") else int(self.state[0])
            return np.argmax(self.q_table[state_int])
        elif self.algorithm == "dqn":
            if random.random() < epsilon:
                return self.env.action_space.sample()
            state_tensor = torch.FloatTensor(self.state).unsqueeze(0)
            with torch.no_grad():
                return torch.argmax(self.model(state_tensor)).item()

    def _update_q_learning(self, state, action, reward, next_state, done):
        import numpy as np
        alpha = self.kwargs.get("alpha", 0.1)
        gamma = self.kwargs.get("gamma", 0.99)
        state_int = int(state) if not hasattr(state, "__len__") else int(state[0])
        next_state_int = int(next_state) if not hasattr(next_state, "__len__") else int(next_state[0])
        best_next = np.argmax(self.q_table[next_state_int])
        self.q_table[state_int, action] += alpha * (
            reward + (0 if done else gamma * self.q_table[next_state_int, best_next]) - self.q_table[state_int, action]
        )

    def _update_sarsa(self, state, action, reward, next_state, next_action, done):
        alpha = self.kwargs.get("alpha", 0.1)
        gamma = self.kwargs.get("gamma", 0.99)
        state_int = int(state) if not hasattr(state, "__len__") else int(state[0])
        next_state_int = int(next_state) if not hasattr(next_state, "__len__") else int(next_state[0])
        self.q_table[state_int, action] += alpha * (
            reward + (0 if done else gamma * self.q_table[next_state_int, next_action]) - self.q_table[state_int, action]
        )

    def _update_dqn(self):
        import random, torch
        if len(self.memory) < self.batch_size:
            return
        batch = random.sample(self.memory, self.batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)

        states = torch.FloatTensor(states)
        actions = torch.LongTensor(actions)
        rewards = torch.FloatTensor(rewards)
        next_states = torch.FloatTensor(next_states)
        dones = torch.FloatTensor(dones)

        # Current Q-values
        q_values = self.model(states).gather(1, actions.unsqueeze(1)).squeeze(1)

        # Target Q-values from target network
        with torch.no_grad():
            next_q_values = self.target_model(next_states).max(1)[0]
            target_q_values = rewards + (1 - dones) * self.gamma * next_q_values

        loss = self.criterion(q_values, target_q_values)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # Update target network periodically
        self.update_counter += 1
        if self.update_counter % self.target_update_freq == 0:
            self.target_model.load_state_dict(self.model.state_dict())

    def train(self, episodes=1000, epsilon=1.0, epsilon_min=0.1, epsilon_decay=0.99):
        for ep in range(episodes):
            state = self.reset()
            total_reward = 0
            if self.algorithm == "sarsa":
                action = self.get_action(epsilon)

            for _ in range(self.env.spec.max_episode_steps):
                if self.done:
                    break

                if self.algorithm in ["q_learning", "sarsa"]:
                    if self.algorithm == "q_learning":
                        action = self.get_action(epsilon)
                        next_state, reward, done = self.step(action)
                        self._update_q_learning(state, action, reward, next_state, done)
                        state = next_state
                    elif self.algorithm == "sarsa":
                        next_state, reward, done = self.step(action)
                        next_action = self.get_action(epsilon)
                        self._update_sarsa(state, action, reward, next_state, next_action, done)
                        state, action = next_state, next_action

                elif self.algorithm == "dqn":
                    action = self.get_action(epsilon)
                    next_state, reward, done = self.step(action)
                    self.memory.append((state, action, reward, next_state, done))
                    if len(self.memory) > self.max_memory:
                        self.memory.pop(0)
                    self._update_dqn()
                    state = next_state

                total_reward += reward

            self.episode_rewards.append(total_reward)
            if epsilon > epsilon_min:
                epsilon *= epsilon_decay

            if (ep + 1) % 100 == 0:
                print(f"Episode {ep+1}/{episodes} - Total Reward: {total_reward}")

        print("Training complete!")

    def test(self, episodes=5):
        import numpy as np, torch
        for ep in range(episodes):
            state = self.reset()
            total_reward = 0
            done = False
            while not done:
                if self.algorithm in ["q_learning", "sarsa"]:
                    state_int = int(state) if not hasattr(state, "__len__") else int(state[0])
                    action = np.argmax(self.q_table[state_int])
                elif self.algorithm == "dqn":
                    state_tensor = torch.FloatTensor(state).unsqueeze(0)
                    with torch.no_grad():
                        action = torch.argmax(self.model(state_tensor)).item()
                state, reward, done = self.step(action)
                total_reward += reward
            print(f"Test Episode {ep+1}: Total Reward = {total_reward}")

    def plot_progress(self):
        import matplotlib.pyplot as plt
        plt.figure(figsize=(10, 5))
        plt.plot(self.episode_rewards, label="Episode Reward")
        plt.xlabel("Episode")
        plt.ylabel("Reward")
        plt.title(f"Training Progress - {self.algorithm.upper()}")
        plt.legend()
        plt.grid(True)
        plt.show()
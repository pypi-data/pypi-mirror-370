# GDML

A documentation repository for machine learning projects.

## Overview

This project contains resources, guides, and documentation to support machine learning workflows.

## Features

- Project setup instructions
- Usage examples
- Best practices
- Reference materials

## Sample Code

```python
from gdml.Data import DataReader, DataSplitter
data_reader = DataReader(filepath='D:\\Projects\\ML_DOC\\california_housing_train.csv')
data = data_reader.read()
print(data.head())
x = data.drop(columns=['median_house_value'])
y = data['median_house_value']

data_splitter = DataSplitter(data=data, target_column='median_house_value', test_size=0.2, random_state=42)
X_train, X_test, y_train, y_test = data_splitter.get_all_splits()

# Regression

from gdml.ML import ML_regression
ml_regression = ML_regression(model='LinearRegression', dataset={'X_train': X_train, 'y_train': y_train})
ml_regression.plot(X_test, y_test)
print("Regression score:", ml_regression.score(X_test, y_test))

from sklearn.datasets import load_iris
import pandas as pd

iris = load_iris(as_frame=True)
iris_data = iris['data']
iris_target = iris['target']
iris_df = pd.concat([iris_data, iris_target.rename('target')], axis=1)

iris_splitter = DataSplitter(data=iris_df, target_column='target', test_size=0.2, random_state=42)
X_train_cls, X_test_cls, y_train_cls, y_test_cls = iris_splitter.get_all_splits()

# Classification

from gdml.ML import ML_classification
ml_classification = ML_classification(model='SVC_classifier', dataset={'X_train': X_train_cls, 'y_train': y_train_cls})
ml_classification.plot(X_test_cls, y_test_cls)
print("Classification score:", ml_classification.score(X_test_cls, y_test_cls))

from gdml.ML import ML_Clustering
ml_clustering = ML_Clustering(model='KMeans', dataset={'X_train': X_train_cls})
ml_clustering.plot(X_test_cls)
print("Clustering score:", ml_clustering.score(X_test_cls, y_test_cls))

# Time Series

from gdml.ML import ML_TimeSeriesToolkit
data_url = 'https://raw.githubusercontent.com/jbrownlee/Datasets/master/airline-passengers.csv'
df = pd.read_csv(data_url)

toolkit = ML_TimeSeriesToolkit(data=df, value_col='Passengers', date_col='Month', freq='MS')
toolkit.plot_series(title='Airline Passengers Over Time')
toolkit.decompose(model='multiplicative')
toolkit.check_stationarity()
toolkit.plot_autocorrelations()

toolkit.fit_sarima(order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
toolkit.plot_forecast(steps=36)
toolkit.fit_ets(seasonal='mul', seasonal_periods=12)
toolkit.plot_forecast(steps=36)
toolkit.fit_prophet()
toolkit.plot_forecast(steps=36)

# Reinforcement Learning

from gdml.ML import ML_RLAgent
agent = ML_RLAgent(env_name="FrozenLake-v1", algorithm="q_learning", alpha=0.5, gamma=0.99)
agent.train(episodes=500)
agent.plot_progress()
agent.test(episodes=3)

# Image Classification

from gdml.Data import ImageDataLoader
image_data_loader = ImageDataLoader(file_path='D:\\Projects\\ML_DOC\\img', batch_size=32, image_size=(224, 224))
images, labels, class_names = image_data_loader.load_data()
images = image_data_loader.preprocess_data(images)
images_augmented = image_data_loader.augment_data(images)
print(images_augmented, labels.shape, class_names)
ml_classification = ML_classification(model='Logistic_regression', dataset={'X_train': images_augmented, 'y_train': labels})
print("Classification score:", ml_classification.score(images_augmented, labels))


# CNN

import torch
from torch.utils.data import DataLoader, TensorDataset
from torchvision import datasets, transforms
from gdml.DL import DLModel
import numpy as np

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])

train_dataset = datasets.MNIST(root='./data', train=True, download=True, transform=transform)
val_dataset = datasets.MNIST(root='./data', train=False, download=True, transform=transform)
test_dataset = val_dataset

train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)
test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

model = DLModel(
    model_type="CNN",
    input_shape=(1, 28, 28),
    num_classes=10,
    task="classification",
    lr=0.001,
    optimizer="adam",
    loss_fn="cross_entropy",
    scheduler="step",
    scheduler_kwargs={"step_size": 10, "gamma": 0.1},
    gradient_clip=1.0,
    base=32,
    num_conv_layers=2,
    dropout=0.2,
    activation="relu",
    batch_norm=True,
    global_pool="avg"
)

model.fit(
    train_loader=train_loader,
    val_loader=val_loader,
    epochs=10,
    print_every=2,
    early_stopping=5
)

results = model.evaluate(test_loader)
print(f"Test Results: {results}")

sample_images, _ = next(iter(test_loader))
sample_predictions = model.predict(sample_images[:10])
print(f"Sample predictions shape: {sample_predictions.shape}")
print(f"Predicted classes: {sample_predictions.argmax(dim=1)}")

model.save_model("mnist_cnn_classifier.pth")

import time

class TrainingCallback:
    def __init__(self):
        self.start_time = None
        self.best_val_acc = 0

    def on_train_begin(self):
        self.start_time = time.time()
        print("Training started!")

    def on_epoch_end(self, epoch, train_metrics, val_metrics):
        val_acc = val_metrics.get('accuracy', 0)
        if val_acc > self.best_val_acc:
            self.best_val_acc = val_acc
            print(f"New best validation accuracy: {val_acc:.4f}")

    def on_train_end(self):
        elapsed = time.time() - self.start_time
        print(f"Training completed in {elapsed:.2f} seconds")
        print(f"Best validation accuracy: {self.best_val_acc:.4f}")

def train_with_callbacks(model, train_loader, val_loader, epochs, callback=None):
    if callback:
        callback.on_train_begin()
    for epoch in range(1, epochs + 1):
        train_metrics = model._train_one_epoch(train_loader)
        val_metrics = model._eval_one_epoch(val_loader) if val_loader else {}
        model.history["loss"].append(train_metrics.get("loss", 0))
        model.history["metric"].append(train_metrics)
        model.history["val_loss"].append(val_metrics.get("loss", 0))
        model.history["val_metric"].append(val_metrics)
        print(f"Epoch {epoch:03d} | Train Loss: {train_metrics.get('loss', 0):.4f} | Train Acc: {train_metrics.get('accuracy', 0):.4f} | Val Loss: {val_metrics.get('loss', 0):.4f} | Val Acc: {val_metrics.get('accuracy', 0):.4f}")
        if callback:
            callback.on_epoch_end(epoch, train_metrics, val_metrics)
        if model.scheduler:
            if isinstance(model.scheduler, torch.optim.lr_scheduler.ReduceLROnPlateau):
                model.scheduler.step(val_metrics.get('loss', 0))
            else:
                model.scheduler.step()
    if callback:
        callback.on_train_end()

def create_image_dataset(n_samples, image_size, n_classes):
    X = torch.randn(n_samples, 3, image_size, image_size)
    y = torch.randint(0, n_classes, (n_samples,))
    return X, y

train_X, train_y = create_image_dataset(800, 32, 5)
val_X, val_y = create_image_dataset(200, 32, 5)

train_dataset = TensorDataset(train_X, train_y)
val_dataset = TensorDataset(val_X, val_y)
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)

model = DLModel(
    model_type="CNN",
    input_shape=(3, 32, 32),
    num_classes=5,
    task="classification",
    lr=0.001,
    optimizer="adamw",
    scheduler="cosine_warm",
    scheduler_kwargs={"T_0": 10, "T_mult": 2}
)

callback = TrainingCallback()
train_with_callbacks(model, train_loader, val_loader, epochs=25, callback=callback)

import matplotlib.pyplot as plt

plt.figure(figsize=(12, 4))
plt.subplot(1, 2, 1)
plt.plot(model.history['loss'], label='Train Loss')
plt.plot(model.history['val_loss'], label='Val Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.title('Training and Validation Loss')

plt.subplot(1, 2, 2)
train_acc = [m.get('accuracy', 0) for m in model.history['metric']]
val_acc = [m.get('accuracy', 0) for m in model.history['val_metric']]
plt.plot(train_acc, label='Train Accuracy')
plt.plot(val_acc, label='Val Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()
plt.title('Training and Validation Accuracy')
plt.tight_layout()
plt.show()

from sklearn.datasets import make_classification
from sklearn.preprocessing import StandardScaler

X, y = make_classification(
    n_samples=1000,
    n_features=20,
    n_informative=15,
    n_redundant=5,
    n_classes=3,
    random_state=42
)

scaler = StandardScaler()
X = scaler.fit_transform(X)
X = torch.FloatTensor(X)
y = torch.LongTensor(y)

train_size = int(0.7 * len(X))
val_size = int(0.2 * len(X))

train_X, train_y = X[:train_size], y[:train_size]
val_X, val_y = X[train_size:train_size+val_size], y[train_size:train_size+val_size]
test_X, test_y = X[train_size+val_size:], y[train_size+val_size:]

train_dataset = TensorDataset(train_X, train_y)
val_dataset = TensorDataset(val_X, val_y)
test_dataset = TensorDataset(test_X, test_y)

train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)
test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

# MLP

model = DLModel(
    model_type="MLP",
    input_shape=(20,),
    num_classes=3,
    task="classification",
    lr=0.01,
    optimizer="sgd",
    optimizer_kwargs={"momentum": 0.9, "weight_decay": 1e-4},
    loss_fn="focal",
    loss_kwargs={"alpha": 1, "gamma": 2},
    scheduler="multistep",
    scheduler_kwargs={"milestones": [10, 20], "gamma": 0.1},
    hidden_sizes=(256, 128, 64),
    dropout=0.3,
    activation="gelu",
    batch_norm=True,
    bias=True
)

model.fit(
    train_loader=train_loader,
    val_loader=val_loader,
    epochs=30,
    print_every=5,
    early_stopping=10
)

results = model.evaluate(test_loader)
print(f"Test Results: {results}")

def get_feature_importance(model, X_sample):
    X_sample = X_sample.to(model.device)
    X_sample.requires_grad_()
    model.model.eval()
    output = model.model(X_sample)
    pred_class = output.argmax(dim=1)
    loss = output[range(len(pred_class)), pred_class].sum()
    loss.backward()
    importance = X_sample.grad.abs().mean(dim=0)
    return importance.cpu().numpy()

importance = get_feature_importance(model, test_X[:10])
print(f"Feature importance: {importance}")

def create_autoencoder_dataset(n_samples=1000, img_size=64):
    X = torch.randn(n_samples, 1, img_size, img_size)
    for i in range(n_samples):
        center_x, center_y = np.random.randint(10, img_size-10, 2)
        radius = np.random.randint(5, 15)
        y, x = torch.meshgrid(torch.arange(img_size), torch.arange(img_size))
        mask = ((x - center_x)**2 + (y - center_y)**2) < radius**2
        X[i, 0][mask] += 2.0
    X = torch.sigmoid(X)
    return X

train_X = create_autoencoder_dataset(800, 64)
val_X = create_autoencoder_dataset(200, 64)

train_dataset = TensorDataset(train_X)
val_dataset = TensorDataset(val_X)
train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=16, shuffle=False)

# ConvAutoencoder

model = DLModel(
    model_type="ConvAutoencoder",
    input_shape=(1, 64, 64),
    task="autoencoder",
    lr=0.001,
    optimizer="adam",
    loss_fn="mse",
    scheduler="step",
    scheduler_kwargs={"step_size": 15, "gamma": 0.5},
    latent_dim=128,
    base=32,
    num_layers=3,
    activation="relu",
    use_skip_connections=False
)

model.fit(
    train_loader=train_loader,
    val_loader=val_loader,
    epochs=30,
    print_every=3
)

with torch.no_grad():
    model.model.eval()
    sample_images = val_X[:8]
    reconstructed = model.model(sample_images.to(model.device))
    fig, axes = plt.subplots(2, 8, figsize=(16, 4))
    for i in range(8):
        axes[0, i].imshow(sample_images[i, 0], cmap='gray')
        axes[0, i].set_title('Original')
        axes[0, i].axis('off')
        axes[1, i].imshow(reconstructed[i, 0].cpu(), cmap='gray')
        axes[1, i].set_title('Reconstructed')
        axes[1, i].axis('off')
    plt.tight_layout()
    plt.show()

def create_time_series_dataset(n_samples=1000, seq_len=50, n_features=5):
    X = torch.randn(n_samples, seq_len, n_features)
    y = X[:, -10:, :].sum(dim=(1, 2)) + torch.randn(n_samples) * 0.1
    return X, y

train_X, train_y = create_time_series_dataset(800, 50, 3)
val_X, val_y = create_time_series_dataset(200, 50, 3)
test_X, test_y = create_time_series_dataset(100, 50, 3)

train_dataset = TensorDataset(train_X, train_y)
val_dataset = TensorDataset(val_X, val_y)
test_dataset = TensorDataset(test_X, test_y)

train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)
test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

# LSTM

model = DLModel(
    model_type="LSTM",
    input_shape=(50, 3),
    task="regression",
    output_dim=1,
    lr=0.001,
    optimizer="adam",
    loss_fn="mse",
    scheduler="plateau",
    scheduler_kwargs={"patience": 5, "factor": 0.5},
    hidden=128,
    num_layers=2,
    bidirectional=True,
    dropout=0.2,
    cell_type="LSTM",
    pooling="last",
    attention=True
)

model.fit(
    train_loader=train_loader,
    val_loader=val_loader,
    epochs=25,
    print_every=3,
    early_stopping=7
)

results = model.evaluate(test_loader)
print(f"Test Results: {results}")

predictions = model.predict(test_X[:10])
print(f"Sample predictions: {predictions.squeeze()}")
print(f"Actual values: {test_y[:10]}")
```
## Getting Started

1. Clone the repository:
    ```bash
    git clone https://github.com/gokulraj0906/gdml.git
    ```
2. Explore the documentation files for guidance.

## Contributing

Contributions are welcome! Please open issues or submit pull requests.

## License

This project is licensed under the License.
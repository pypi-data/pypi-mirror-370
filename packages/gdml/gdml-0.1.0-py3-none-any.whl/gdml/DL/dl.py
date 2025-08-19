# dl_module.py
import math
import warnings
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple, Iterable, Union, List, Callable
from pathlib import Path
import json

import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import _LRScheduler
import torch.nn.functional as F


# --------------------------
# Utility: device & metrics
# --------------------------
def get_device(device: Optional[str] = None) -> str:
    """Get the best available device with fallback options."""
    if device:
        if device.startswith('cuda') and not torch.cuda.is_available():
            warnings.warn("CUDA requested but not available. Falling back to CPU.")
            return "cpu"
        return device

    if torch.cuda.is_available():
        return "cuda"
    elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        return "mps"
    else:
        return "cpu"


def accuracy_from_logits(logits: torch.Tensor, targets: torch.Tensor) -> float:
    """Calculate accuracy from logits and targets."""
    preds = logits.argmax(dim=1)
    return (preds == targets).float().mean().item()


def top_k_accuracy(logits: torch.Tensor, targets: torch.Tensor, k: int = 5) -> float:
    """Calculate top-k accuracy."""
    _, pred = logits.topk(k, 1, True, True)
    pred = pred.t()
    correct = pred.eq(targets.view(1, -1).expand_as(pred))
    return correct[:k].sum().float() / targets.size(0)


class MetricTracker:
    """Track and compute various metrics."""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.metrics = {}
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if key not in self.metrics:
                self.metrics[key] = []
            if isinstance(value, torch.Tensor):
                value = value.item()
            self.metrics[key].append(value)
    
    def get_average(self, key: str) -> float:
        if key not in self.metrics or not self.metrics[key]:
            return 0.0
        return sum(self.metrics[key]) / len(self.metrics[key])
    
    def get_all_averages(self) -> Dict[str, float]:
        return {key: self.get_average(key) for key in self.metrics}


# --------------------------
# Base Architecture Class
# --------------------------
class BaseArchitecture(nn.Module, ABC):
    """Base class for all architectures with common functionality."""
    
    def __init__(self):
        super().__init__()
        self._input_shape = None
        self._output_shape = None
    
    @abstractmethod
    def forward(self, x):
        pass
    
    def get_num_parameters(self) -> int:
        """Get total number of parameters."""
        return sum(p.numel() for p in self.parameters())
    
    def get_num_trainable_parameters(self) -> int:
        """Get number of trainable parameters."""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)
    
    def freeze_layers(self, layer_names: List[str]):
        """Freeze specific layers by name."""
        for name, param in self.named_parameters():
            if any(layer_name in name for layer_name in layer_names):
                param.requires_grad = False
    
    def unfreeze_layers(self, layer_names: List[str]):
        """Unfreeze specific layers by name."""
        for name, param in self.named_parameters():
            if any(layer_name in name for layer_name in layer_names):
                param.requires_grad = True


# --------------------------
# Enhanced Architectures
# --------------------------
class MLPClassifier(BaseArchitecture):
    def __init__(
        self, 
        input_shape: Tuple[int, ...], 
        num_classes: int, 
        hidden_sizes=(256, 128), 
        dropout=0.1,
        activation='relu',
        batch_norm=False,
        bias=True
    ):
        super().__init__()
        self._input_shape = input_shape
        
        # Calculate input features
        in_features = 1
        for d in input_shape:
            in_features *= d
        
        # Activation function
        activations = {
            'relu': nn.ReLU,
            'gelu': nn.GELU,
            'leaky_relu': nn.LeakyReLU,
            'elu': nn.ELU,
            'swish': nn.SiLU,
            'tanh': nn.Tanh
        }
        if activation not in activations:
            raise ValueError(f"Unsupported activation: {activation}")
        act_fn = activations[activation]
        
        layers = [nn.Flatten()]
        prev = in_features
        
        for i, h in enumerate(hidden_sizes):
            layers.append(nn.Linear(prev, h, bias=bias))
            if batch_norm:
                layers.append(nn.BatchNorm1d(h))
            layers.append(act_fn())
            if dropout > 0:
                layers.append(nn.Dropout(dropout))
            prev = h
        
        layers.append(nn.Linear(prev, num_classes, bias=bias))
        self.net = nn.Sequential(*layers)
        self._output_shape = (num_classes,)

    def forward(self, x):
        return self.net(x)


class SimpleCNN(BaseArchitecture):
    def __init__(
        self, 
        input_shape: Tuple[int, int, int], 
        num_classes: int, 
        base=32,
        num_conv_layers=3,
        kernel_size=3,
        pool_size=2,
        dropout=0.1,
        activation='relu',
        batch_norm=True,
        global_pool='avg'
    ):
        super().__init__()
        self._input_shape = input_shape
        c, h, w = input_shape
        
        # Activation function
        activations = {'relu': nn.ReLU, 'gelu': nn.GELU, 'leaky_relu': nn.LeakyReLU}
        act_fn = activations.get(activation, nn.ReLU)
        
        # Build feature extractor
        layers = []
        in_channels = c
        current_h, current_w = h, w
        
        for i in range(num_conv_layers):
            out_channels = base * (2 ** i)
            layers.extend([
                nn.Conv2d(in_channels, out_channels, kernel_size, padding=kernel_size // 2),
            ])
            if batch_norm:
                layers.append(nn.BatchNorm2d(out_channels))
            layers.extend([
                act_fn(),
                nn.MaxPool2d(pool_size)
            ])
            if dropout > 0 and i < num_conv_layers - 1:
                layers.append(nn.Dropout2d(dropout))
            
            in_channels = out_channels
            current_h //= pool_size
            current_w //= pool_size
        
        self.features = nn.Sequential(*layers)
        
        # Global pooling or flatten
        if global_pool == 'avg':
            self.pool = nn.AdaptiveAvgPool2d(1)
            classifier_input = out_channels
        elif global_pool == 'max':
            self.pool = nn.AdaptiveMaxPool2d(1)
            classifier_input = out_channels
        else:
            self.pool = nn.Identity()
            classifier_input = out_channels * current_h * current_w
        
        # Classifier
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Dropout(dropout) if dropout > 0 else nn.Identity(),
            nn.Linear(classifier_input, 256),
            act_fn(),
            nn.Dropout(dropout) if dropout > 0 else nn.Identity(),
            nn.Linear(256, num_classes)
        )
        self._output_shape = (num_classes,)

    def forward(self, x):
        x = self.features(x)
        x = self.pool(x)
        return self.classifier(x)


class EnhancedLSTM(BaseArchitecture):
    def __init__(
        self, 
        input_shape: Tuple[int, int], 
        num_classes: int, 
        hidden=128, 
        num_layers=1, 
        bidirectional=False, 
        dropout=0.0,
        cell_type='LSTM',
        pooling='last',
        attention=False
    ):
        super().__init__()
        self._input_shape = input_shape
        t, f = input_shape
        
        # RNN cell type
        rnn_cells = {'LSTM': nn.LSTM, 'GRU': nn.GRU, 'RNN': nn.RNN}
        if cell_type not in rnn_cells:
            raise ValueError(f"Unsupported cell type: {cell_type}")
        
        rnn_kwargs = {
            'input_size': f,
            'hidden_size': hidden,
            'num_layers': num_layers,
            'batch_first': True,
            'bidirectional': bidirectional,
            'dropout': dropout if num_layers > 1 else 0.0
        }
        
        self.rnn = rnn_cells[cell_type](**rnn_kwargs)
        self.pooling = pooling
        self.attention = attention
        self.cell_type = cell_type
        
        mult = 2 if bidirectional else 1
        rnn_output_size = hidden * mult
        
        if attention:
            self.attention_layer = nn.MultiheadAttention(
                embed_dim=rnn_output_size, 
                num_heads=8, 
                batch_first=True
            )
        
        self.fc = nn.Linear(rnn_output_size, num_classes)
        self._output_shape = (num_classes,)

    def forward(self, x):
        # x: (B, T, F)
        if self.cell_type == 'LSTM':
            out, (h_n, c_n) = self.rnn(x)
        else:
            out, h_n = self.rnn(x)
        
        if self.attention:
            out, _ = self.attention_layer(out, out, out)
        
        if self.pooling == 'last':
            # Fixed: Handle bidirectional properly
            if self.rnn.bidirectional:
                # h_n shape: (num_layers * num_directions, batch, hidden_size)
                # We want the last layer's forward and backward hidden states
                forward_hidden = h_n[-2] if self.rnn.num_layers > 1 else h_n[0]
                backward_hidden = h_n[-1] if self.rnn.num_layers > 1 else h_n[1]
                pooled = torch.cat([forward_hidden, backward_hidden], dim=1)
            else:
                pooled = h_n[-1]  # Last layer
        elif self.pooling == 'mean':
            pooled = out.mean(dim=1)
        elif self.pooling == 'max':
            pooled = out.max(dim=1)[0]
        else:
            raise ValueError(f"Unsupported pooling: {self.pooling}")
        
        return self.fc(pooled)


class PositionalEncoding(nn.Module):
    def __init__(self, d_model: int, max_len: int = 5000, dropout: float = 0.1):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)
        
        self.register_buffer('pe', pe)

    def forward(self, x):
        # x: (B, T, D)
        x = x + self.pe[:, :x.size(1), :]
        return self.dropout(x)


class TransformerEncoderClassifier(BaseArchitecture):
    def __init__(
        self, 
        vocab_size: int, 
        num_classes: int, 
        d_model=512, 
        nhead=8, 
        num_layers=6, 
        dim_feedforward=2048, 
        dropout=0.1,
        max_seq_len=512,
        pooling='cls',
        use_pos_encoding=True
    ):
        super().__init__()
        
        self.d_model = d_model
        self.pooling = pooling
        self.use_pos_encoding = use_pos_encoding
        
        # Embedding layer
        self.embedding = nn.Embedding(vocab_size, d_model)
        
        # Positional encoding
        if use_pos_encoding:
            self.pos_encoder = PositionalEncoding(d_model, max_seq_len, dropout)
        
        # CLS token for classification
        if pooling == 'cls':
            self.cls_token = nn.Parameter(torch.randn(1, 1, d_model))
        
        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, 
            nhead=nhead, 
            dim_feedforward=dim_feedforward, 
            dropout=dropout,
            batch_first=True,
            activation='gelu'
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers)
        
        # Layer norm
        self.norm = nn.LayerNorm(d_model)
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(d_model, d_model // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_model // 2, num_classes)
        )
        
        self._output_shape = (num_classes,)

    def forward(self, input_ids, attention_mask=None):
        batch_size, seq_len = input_ids.shape
        
        # Embedding
        x = self.embedding(input_ids) * math.sqrt(self.d_model)
        
        # Add CLS token if using cls pooling
        if self.pooling == 'cls':
            cls_tokens = self.cls_token.expand(batch_size, -1, -1)
            x = torch.cat([cls_tokens, x], dim=1)
            if attention_mask is not None:
                cls_mask = torch.ones(batch_size, 1, device=attention_mask.device)
                attention_mask = torch.cat([cls_mask, attention_mask], dim=1)
        
        # Positional encoding
        if self.use_pos_encoding:
            x = self.pos_encoder(x)
        
        # Create padding mask for transformer
        key_padding_mask = None
        if attention_mask is not None:
            key_padding_mask = (attention_mask == 0)
        
        # Transformer encoding
        x = self.transformer(x, src_key_padding_mask=key_padding_mask)
        x = self.norm(x)
        
        # Pooling
        if self.pooling == 'cls':
            pooled = x[:, 0]  # use CLS token output
        elif self.pooling == 'mean':
            if attention_mask is not None:
                mask = attention_mask.unsqueeze(-1).float()
                pooled = (x * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1)
            else:
                pooled = x.mean(dim=1)
        elif self.pooling == 'max':
            pooled = x.max(dim=1)[0]
        else:
            raise ValueError(f"Unsupported pooling: {self.pooling}")
        
        return self.classifier(pooled)


class ConvAutoencoder(BaseArchitecture):
    def __init__(
        self, 
        input_shape: Tuple[int, int, int], 
        latent_dim=64, 
        base=32,
        num_layers=3,
        activation='relu',
        use_skip_connections=False
    ):
        super().__init__()
        self._input_shape = input_shape
        c, h, w = input_shape
        self.use_skip_connections = use_skip_connections
        
        # Activation function
        activations = {'relu': nn.ReLU, 'gelu': nn.GELU, 'leaky_relu': nn.LeakyReLU}
        act_fn = activations.get(activation, nn.ReLU)
        
        # Encoder
        encoder_layers = []
        in_channels = c
        self.encoder_channels = []
        
        for i in range(num_layers):
            out_channels = base * (2 ** i)
            encoder_layers.extend([
                nn.Conv2d(in_channels, out_channels, 3, stride=2, padding=1),
                nn.BatchNorm2d(out_channels),
                act_fn()
            ])
            self.encoder_channels.append(out_channels)
            in_channels = out_channels
            h, w = h // 2, w // 2
        
        self.encoder = nn.Sequential(*encoder_layers)
        
        # Latent space
        self.to_latent = nn.Sequential(
            nn.Flatten(),
            nn.Linear(in_channels * h * w, latent_dim)
        )
        
        self.from_latent = nn.Sequential(
            nn.Linear(latent_dim, in_channels * h * w),
            nn.Unflatten(1, (in_channels, h, w))
        )
        
        # Decoder
        decoder_layers = []
        for i in reversed(range(num_layers)):
            out_channels = base * (2 ** (i-1)) if i > 0 else c
            if i == 0:  # Final layer
                decoder_layers.extend([
                    nn.ConvTranspose2d(in_channels, out_channels, 4, stride=2, padding=1),
                    nn.Sigmoid()
                ])
            else:
                decoder_layers.extend([
                    nn.ConvTranspose2d(in_channels, out_channels, 4, stride=2, padding=1),
                    nn.BatchNorm2d(out_channels),
                    act_fn()
                ])
            in_channels = out_channels
        
        self.decoder = nn.Sequential(*decoder_layers)

    def encode(self, x):
        if self.use_skip_connections:
            skip_connections = []
            for layer in self.encoder:
                x = layer(x)
                if isinstance(layer, nn.Conv2d):
                    skip_connections.append(x)
        else:
            x = self.encoder(x)
            skip_connections = None
        
        z = self.to_latent(x)
        return z, skip_connections

    def decode(self, z, skip_connections=None):
        x = self.from_latent(z)
        if self.use_skip_connections and skip_connections:
            # Example: U-Net style skip connection addition
            for i, layer in enumerate(self.decoder):
                x = layer(x)
                if isinstance(layer, nn.ConvTranspose2d) and i < len(skip_connections):
                    skip = skip_connections[-(i // 3 + 1)]
                    if x.shape == skip.shape:
                        x = x + skip
        else:
            x = self.decoder(x)
        
        return x

    def forward(self, x):
        z, skip_connections = self.encode(x)
        return self.decode(z, skip_connections)


# --------------------------
# Enhanced Model Registry
# --------------------------
MODEL_REGISTRY = {
    "MLP": MLPClassifier,
    "CNN": SimpleCNN,
    "LSTM": EnhancedLSTM,
    "TransformerEncoderClassifier": TransformerEncoderClassifier,
    "ConvAutoencoder": ConvAutoencoder,
}


# --------------------------
# Loss Functions
# --------------------------
class FocalLoss(nn.Module):
    """Focal Loss for handling class imbalance."""
    def __init__(self, alpha=1, gamma=2, reduction='mean'):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction

    def forward(self, inputs, targets):
        ce_loss = F.cross_entropy(inputs, targets, reduction='none')
        pt = torch.exp(-ce_loss)
        focal_loss = self.alpha * (1 - pt) ** self.gamma * ce_loss
        if self.reduction == 'mean':
            return focal_loss.mean()
        elif self.reduction == 'sum':
            return focal_loss.sum()
        else:
            return focal_loss


class LabelSmoothingLoss(nn.Module):
    """Label smoothing loss."""
    def __init__(self, num_classes, smoothing=0.1):
        super().__init__()
        self.num_classes = num_classes
        self.smoothing = smoothing
        self.confidence = 1.0 - smoothing

    def forward(self, inputs, targets):
        log_probs = F.log_softmax(inputs, dim=1)
        targets_one_hot = torch.zeros_like(log_probs).scatter_(1, targets.unsqueeze(1), 1)
        targets_smooth = targets_one_hot * self.confidence + (1 - targets_one_hot) * self.smoothing / (self.num_classes - 1)
        return -(targets_smooth * log_probs).sum(dim=1).mean()


LOSS_REGISTRY = {
    'cross_entropy': nn.CrossEntropyLoss,
    'mse': nn.MSELoss,
    'mae': nn.L1Loss,
    'bce': nn.BCELoss,
    'bce_logits': nn.BCEWithLogitsLoss,
    'focal': FocalLoss,
    'label_smoothing': LabelSmoothingLoss,
    'huber': nn.HuberLoss,
}


# --------------------------
# Enhanced Model Wrapper
# --------------------------
class DLModel:
    """Enhanced unified interface for deep learning models."""
    
    def __init__(
        self,
        model_type: str,
        input_shape: Optional[Tuple[int, ...]] = None,
        num_classes: Optional[int] = None,
        task: str = "classification",
        vocab_size: Optional[int] = None,
        lr: float = 1e-3,
        device: Optional[str] = None,
        optimizer: str = 'adam',
        optimizer_kwargs: Optional[Dict[str, Any]] = None,
        loss_fn: str = 'auto',
        loss_kwargs: Optional[Dict[str, Any]] = None,
        scheduler: Optional[str] = None,
        scheduler_kwargs: Optional[Dict[str, Any]] = None,
        gradient_clip: Optional[float] = None,
        **arch_kwargs
    ):
        """
        Initialize the DLModel with the specified parameters.

        Args:
            model_type (str): The type of model to use.
            input_shape (Optional[Tuple[int, ...]]): The shape of the input data.
            num_classes (Optional[int]): The number of output classes.
            task (str): The task type (e.g., "classification", "regression").
            vocab_size (Optional[int]): The vocabulary size (for NLP tasks).
            lr (float): Learning rate.
            device (Optional[str]): Device to run the model on (e.g., "cuda", "cpu").
            optimizer (str): Optimizer type.
            optimizer_kwargs (Optional[Dict[str, Any]]): Additional arguments for the optimizer.
            loss_fn (str): Loss function type.
            loss_kwargs (Optional[Dict[str, Any]]): Additional arguments for the loss function.
            scheduler (Optional[str]): Learning rate scheduler type.
            scheduler_kwargs (Optional[Dict[str, Any]]): Additional arguments for the scheduler.
            gradient_clip (Optional[float]): Gradient clipping value.
            **arch_kwargs: Additional architecture-specific arguments.
        """
        self.model_type = model_type
        self.task = task
        self.device = get_device(device)
        self.gradient_clip = gradient_clip
        
        # Initialize history and metrics
        self.history = {"loss": [], "val_loss": [], "metric": [], "val_metric": []}
        self.metric_tracker = MetricTracker()
        
        # Build model
        self.model = self._build_model(
            model_type, input_shape, num_classes, vocab_size, task, **arch_kwargs
        )
        self.model.to(self.device)
        
        # Setup loss function
        self.criterion = self._setup_loss_function(loss_fn, task, num_classes, loss_kwargs)
        
        # Setup optimizer
        self.optimizer = self._setup_optimizer(optimizer, lr, optimizer_kwargs)
        
        # Setup scheduler
        self.scheduler = self._setup_scheduler(scheduler, scheduler_kwargs)
        
        # Model info
        print(f"Model: {model_type} | Task: {task}")
        print(f"Total parameters: {self.model.get_num_parameters():,}")
        print(f"Trainable parameters: {self.model.get_num_trainable_parameters():,}")
        print(f"Device: {self.device}")

    def _build_model(self, model_type, input_shape, num_classes, vocab_size, task, **arch_kwargs):
        """Build the model based on type and task."""
        if model_type not in MODEL_REGISTRY:
            raise ValueError(f"Unsupported model: {model_type}. Available: {list(MODEL_REGISTRY.keys())}")
        
        model_class = MODEL_REGISTRY[model_type]
        
        if model_type == "TransformerEncoderClassifier":
            if vocab_size is None or num_classes is None:
                raise ValueError("TransformerEncoderClassifier needs vocab_size and num_classes.")
            return model_class(vocab_size=vocab_size, num_classes=num_classes, **arch_kwargs)
        elif model_type == "ConvAutoencoder":
            if input_shape is None:
                raise ValueError("ConvAutoencoder needs input_shape=(C,H,W).")
            return model_class(input_shape=input_shape, **arch_kwargs)
        else:
            if input_shape is None:
                raise ValueError(f"{model_type} needs input_shape.")
            
            if task == "classification":
                if num_classes is None:
                    raise ValueError("Classification requires num_classes.")
                return model_class(input_shape=input_shape, num_classes=num_classes, **arch_kwargs)
            elif task == "regression":
                output_dim = arch_kwargs.pop('output_dim', 1)
                return model_class(input_shape=input_shape, num_classes=output_dim, **arch_kwargs)
            elif task == "autoencoder":
                if model_type != "ConvAutoencoder":
                    raise ValueError("For autoencoder task, use model_type='ConvAutoencoder'.")
                return model_class(input_shape=input_shape, **arch_kwargs)
            else:
                raise ValueError("task must be 'classification', 'regression', or 'autoencoder'.")

    def _setup_loss_function(self, loss_fn, task, num_classes=None, loss_kwargs=None):
        """Setup loss function based on task and parameters."""
        loss_kwargs = loss_kwargs or {}
        
        if loss_fn == 'auto':
            if task == "classification":
                loss_fn = 'cross_entropy'
            elif task == "regression":
                loss_fn = 'mse'
            elif task == "autoencoder":
                loss_fn = 'mse'
        
        if loss_fn not in LOSS_REGISTRY:
            raise ValueError(f"Unsupported loss function: {loss_fn}")
        
        loss_class = LOSS_REGISTRY[loss_fn]
        if loss_fn == 'label_smoothing' and num_classes:
            loss_kwargs.setdefault('num_classes', num_classes)
        
        return loss_class(**loss_kwargs)

    def _setup_optimizer(self, optimizer_name, lr, optimizer_kwargs):
        """Setup optimizer."""
        optimizer_kwargs = optimizer_kwargs or {}
        optimizers = {
            'adam': optim.Adam,
            'adamw': optim.AdamW,
            'sgd': optim.SGD,
            'rmsprop': optim.RMSprop,
            'adagrad': optim.Adagrad,
        }
        if optimizer_name not in optimizers:
            raise ValueError(f"Unsupported optimizer: {optimizer_name}")
        return optimizers[optimizer_name](self.model.parameters(), lr=lr, **optimizer_kwargs)

    def _setup_scheduler(self, scheduler_name, scheduler_kwargs):
        """Setup learning rate scheduler."""
        if scheduler_name is None:
            return None
        scheduler_kwargs = scheduler_kwargs or {}
        schedulers = {
            'step': optim.lr_scheduler.StepLR,
            'multistep': optim.lr_scheduler.MultiStepLR,
            'exponential': optim.lr_scheduler.ExponentialLR,
            'cosine': optim.lr_scheduler.CosineAnnealingLR,
            'plateau': optim.lr_scheduler.ReduceLROnPlateau,
            'cosine_warm': optim.lr_scheduler.CosineAnnealingWarmRestarts,
        }
        if scheduler_name not in schedulers:
            raise ValueError(f"Unsupported scheduler: {scheduler_name}")
        return schedulers[scheduler_name](self.optimizer, **scheduler_kwargs)

    def _compute_metrics(self, outputs, targets, task):
        """Compute metrics based on task type."""
        with torch.no_grad():
            if task == "classification":
                acc = accuracy_from_logits(outputs, targets)
                metrics = {'accuracy': acc}
                if outputs.size(1) >= 5:
                    metrics['top5_accuracy'] = top_k_accuracy(outputs, targets, k=5)
                return metrics
            elif task == "regression":
                # Fix: Ensure dimensions match
                if outputs.dim() > 1:
                    outputs = outputs.squeeze(-1)  # Remove last dimension if it's 1
                targets = targets.float()
                
                mse = F.mse_loss(outputs, targets)
                rmse = torch.sqrt(mse)
                mae = F.l1_loss(outputs, targets)
                return {'mse': mse.item(), 'rmse': rmse.item(), 'mae': mae.item()}
            else:
                return {}

    def _forward_batch(self, batch, training=True):
        """Process a single batch and return loss, outputs, and targets."""
        if self.model_type == "TransformerEncoderClassifier":
            if isinstance(batch, (list, tuple)):
                if len(batch) == 3:
                    input_ids, attention_mask, targets = batch
                elif len(batch) == 2:
                    input_ids, targets = batch
                    attention_mask = None
                else:
                    raise ValueError("Transformer batch must be (input_ids, attention_mask, targets) or (input_ids, targets).")
            else:
                raise ValueError("Transformer expects tuple batch.")
            input_ids = input_ids.to(self.device)
            targets = targets.to(self.device)
            if attention_mask is not None:
                attention_mask = attention_mask.to(self.device)
                outputs = self.model(input_ids, attention_mask=attention_mask)
            else:
                outputs = self.model(input_ids)
            loss = self.criterion(outputs, targets)
            return loss, outputs, targets
        
        # For standard supervised learning or autoencoder
        if isinstance(batch, (list, tuple)):
            if self.task == "autoencoder":
                x = batch[0].to(self.device)
                outputs = self.model(x)
                loss = self.criterion(outputs, x)
                return loss, None, None
            else:
                x, y = batch[0].to(self.device), batch[1].to(self.device)
                outputs = self.model(x)
                
                # Fix: Handle regression dimension mismatch
                if self.task == "regression":
                    if outputs.dim() > 1:
                        outputs = outputs.squeeze(-1)  # Remove last dimension if it's 1
                    y = y.float()
                
                loss = self.criterion(outputs, y)
                return loss, outputs, y
        else:
            raise ValueError("Unsupported batch format.")

    def _train_one_epoch(self, loader):
        """Train for one epoch."""
        self.model.train()
        self.metric_tracker.reset()
        for batch_idx, batch in enumerate(loader):
            self.optimizer.zero_grad()
            loss, outputs, targets = self._forward_batch(batch, training=True)
            loss.backward()
            if self.gradient_clip:
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.gradient_clip)
            self.optimizer.step()
            self.metric_tracker.update(loss=loss.item())
            if outputs is not None and targets is not None:
                metrics = self._compute_metrics(outputs, targets, self.task)
                self.metric_tracker.update(**metrics)
        return self.metric_tracker.get_all_averages()

    def _eval_one_epoch(self, loader):
        """Evaluate for one epoch."""
        self.model.eval()
        self.metric_tracker.reset()
        with torch.no_grad():
            for batch in loader:
                loss, outputs, targets = self._forward_batch(batch, training=False)
                self.metric_tracker.update(loss=loss.item())
                if outputs is not None and targets is not None:
                    metrics = self._compute_metrics(outputs, targets, self.task)
                    self.metric_tracker.update(**metrics)
        return self.metric_tracker.get_all_averages()

    def fit(self, train_loader, val_loader=None, epochs=10, print_every=1, early_stopping: Optional[int] = None):
        """Train the model for a number of epochs.
        Args:
            train_loader (DataLoader): DataLoader for the training dataset.
            val_loader (Optional[DataLoader]): DataLoader for the validation dataset.
            epochs (int): Number of training epochs.
            print_every (int): Print training progress every N epochs.
            early_stopping (Optional[int]): Early stopping patience.
        """
        best_val_loss = float('inf')
        epochs_no_improve = 0
        for epoch in range(1, epochs + 1):
            train_metrics = self._train_one_epoch(train_loader)
            if val_loader is not None:
                val_metrics = self._eval_one_epoch(val_loader)
            else:
                val_metrics = {}
            self.history["loss"].append(train_metrics.get("loss", 0))
            self.history["metric"].append(train_metrics)
            self.history["val_loss"].append(val_metrics.get("loss", 0))
            self.history["val_metric"].append(val_metrics)
            if epoch % print_every == 0:
                print(f"Epoch {epoch:03d} | Train Loss: {train_metrics.get('loss', 0):.4f} | Val Loss: {val_metrics.get('loss', 0):.4f}")
            if val_loader is not None and early_stopping is not None:
                if val_metrics.get('loss', float('inf')) < best_val_loss:
                    best_val_loss = val_metrics.get('loss')
                    epochs_no_improve = 0
                    best_state = self.model.state_dict()
                else:
                    epochs_no_improve += 1
                    if epochs_no_improve >= early_stopping:
                        print(f"Early stopping at epoch {epoch}, restoring best model.")
                        self.model.load_state_dict(best_state)
                        break
            if self.scheduler is not None:
                if isinstance(self.scheduler, optim.lr_scheduler.ReduceLROnPlateau):
                    self.scheduler.step(val_metrics.get('loss', 0))
                else:
                    self.scheduler.step()
        return self

    def evaluate(self, loader):
        """
        Evaluate the model on the given DataLoader.
        Args:
            loader (DataLoader): DataLoader for the evaluation dataset.
        """
        metrics = self._eval_one_epoch(loader)
        if self.task == "classification":
            print(f"Evaluation - Loss: {metrics.get('loss', 0):.4f}, Accuracy: {metrics.get('accuracy', 0):.4f}")
        elif self.task == "regression":
            print(f"Evaluation - Loss: {metrics.get('loss', 0):.4f}, Metrics: {metrics}")
        else:
            print(f"Evaluation - Reconstruction Loss: {metrics.get('loss', 0):.4f}")
        return metrics

    @torch.no_grad()
    def predict(self, X: torch.Tensor):
        """
        Make predictions using the trained model.
        Args:
            X (torch.Tensor): Input tensor for prediction.
        """
        self.model.eval()
        X = X.to(self.device)
        outputs = self.model(X)
        if self.task == "classification":
            return torch.softmax(outputs, dim=1).cpu()
        return outputs.cpu()

    def save_model(self, path: Union[str, Path]):
        """
        Save the model checkpoint.
        Args:
            path (Union[str, Path]): Path to save the model checkpoint.
        """
        torch.save({
            "state_dict": self.model.state_dict(),
            "model_type": self.model_type,
            "task": self.task
        }, path)
        print(f"Model saved to {path}")

    def load_model(self, path: Union[str, Path]):
        """
        Load the model checkpoint.
        Args:
            path (Union[str, Path]): Path to the model checkpoint.
        """
        checkpoint = torch.load(path, map_location=self.device)
        self.model.load_state_dict(checkpoint["state_dict"])
        self.model.to(self.device)
        print(f"Model loaded from {path}")
        return self
import random
import numpy as np
import torch
import torch.nn as nn
from src.models.base import Model
import logging

logger = logging.getLogger(__name__)


class CNN_GRU_Model(nn.Module):
    def __init__(
        self,
        input_channels,
        img_height,
        img_width,
        gru_hidden_size,
        num_classes,
        random_state=42,
    ):
        super(CNN_GRU_Model, self).__init__()
        random.seed(random_state)
        np.random.seed(random_state)
        torch.manual_seed(random_state)
        torch.cuda.manual_seed_all(random_state)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
        # 2D Convolutional Layer
        self.conv2d = nn.Conv2d(
            in_channels=input_channels, out_channels=32, kernel_size=3, padding=1
        )
        self.relu = nn.ReLU()

        # Dropout Layer
        self.dropout = nn.Dropout(0.3)

        # Compute the feature map size after Conv2D
        self.feature_dim = (
            32 * img_height * img_width
        )  # 32 filters, keeping the original HxW

        # GRU Layer
        self.gru = nn.GRU(
            input_size=self.feature_dim, hidden_size=gru_hidden_size, batch_first=True
        )

        # Dense Layer (Output)
        self.fc = nn.Linear(gru_hidden_size, num_classes)

    def forward(self, x):
        # Apply 2D CNN
        x = self.conv2d(x)  # (batch, 32, H, W)
        x = self.relu(x)

        # Apply Dropout
        x = self.dropout(x)

        # Reshape to (batch, seq_length, features) for GRU
        batch_size = x.shape[0]
        x = x.view(batch_size, 1, -1)  # (batch, 1, feature_dim)

        # Apply GRU
        x, _ = self.gru(x)  # (batch, 1, gru_hidden_size)

        # Take last time step's output
        x = x[:, -1, :]  # (batch, gru_hidden_size)

        # ReLU Activation before Dense Layer
        x = self.relu(x)

        # Output Layer
        x = self.fc(x)  # (batch, num_classes)

        return x


# class TwoDCNN_GRU(Model):
# def __init__(self, input_channels, img_height, img_width, gru_hidden_size, num_classes):
#     """
#     Initialize the 2D CNN-GRU model.

#     Parameters:
#         input_channels (int): The number of input channels.
#         img_height (int): The height of the input image.
#         img_width (int): The width of the input image.
#         gru_hidden_size (int): The hidden size of the GRU layer.
#         num_classes (int): The number of output classes.

#     Returns:
#         None
#     """
#     model = CNN_GRU_Model(input_channels, img_height, img_width, gru_hidden_size, num_classes)
#     super(2DCNN_GRU, self).__init__(model)

# def fit(self, x_train, y_train):
#     """
#     Fit the model to the training data.

#     Parameters:
#         x_train (pd.DataFrame): The features of the training data.
#         y_train (pd.Series): The target variable of the training data.

#     Returns:
#         None
#     """
#     pass

# def predict(self, x_test):
#     """
#     Make predictions on the test data.

#     Parameters:
#         x_test (pd.DataFrame): The features of the test data.

#     Returns:
#         None
#     """
#     pass

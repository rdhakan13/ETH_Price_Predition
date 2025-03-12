import torch
import torch.nn as nn

class CNN_GRU_Model(nn.Module):
    def __init__(self, input_channels, img_height, img_width, gru_hidden_size, num_classes):
        super(CNN_GRU_Model, self).__init__()

        # 2D Convolutional Layer
        self.conv2d = nn.Conv2d(in_channels=input_channels, out_channels=32, kernel_size=3, padding=1)
        self.relu = nn.ReLU()

        # Dropout Layer
        self.dropout = nn.Dropout(0.3)

        # Compute the feature map size after Conv2D
        self.feature_dim = 32 * img_height * img_width  # 32 filters, keeping the original HxW

        # GRU Layer
        self.gru = nn.GRU(input_size=self.feature_dim, hidden_size=gru_hidden_size, batch_first=True)

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

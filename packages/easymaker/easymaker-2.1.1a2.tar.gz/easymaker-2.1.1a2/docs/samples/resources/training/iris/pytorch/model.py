import torch.nn as nn
import torch.nn.functional as F


class Model(nn.Module):
    def __init__(self, input_features=4, hidden_layer1=5, hidden_layer2=5, output_features=3):
        super().__init__()
        self.fc1 = nn.Linear(input_features, hidden_layer1)
        self.fc2 = nn.Linear(hidden_layer1, hidden_layer2)
        self.fc3 = nn.Linear(hidden_layer2, output_features)

    def forward(self, x):
        out = F.relu(self.fc1(x))
        out = F.relu(self.fc2(out))
        out = F.softmax(self.fc3(out))
        return out

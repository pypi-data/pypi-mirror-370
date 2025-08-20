import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
from torchinfo import summary

import matplotlib.pyplot as plt

# 그래프 그리는 함수 정의
def plot_training_results(train_losses, test_losses):
    epochs = range(1, len(train_losses) + 1)

    # 손실(loss) 그래프
    plt.figure(figsize=(12, 5))
    plt.plot(epochs, train_losses, 'bo-', label='Training Loss')
    plt.plot(epochs, test_losses, 'ro-', label='Test Loss')
    plt.title('Training and Test Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.tight_layout()
    plt.show()


def train(model, train_loader, criterion, optimizer, epoch, device):
    model.train()  # 모델을 학습 모드로 설정
    running_loss = 0.0

    for data, labels in train_loader:
        data, labels = data.to(device), labels.to(device)
        outputs = model(data)
        loss = criterion(outputs, labels)

        # 역전파 및 옵티마이저 스텝
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        
    train_loss = running_loss / len(train_loader)
    return train_loss

# 평가 함수 정의
def evaluate(model, test_loader, criterion, device):
    model.eval()  # 모델을 평가 모드로 설정
    test_loss = 0.0
    
    with torch.no_grad():  # 평가 중에는 기울기 계산을 하지 않음
        for data, labels in test_loader:
            data, labels = data.to(device), labels.to(device)
            outputs = model(data)
            loss = criterion(outputs, labels)
            test_loss += loss.item()

            
    test_loss /= len(test_loader)
    return test_loss


def conv2d_output_size(input_size, kernel_size, stride=1, padding=0):
    height, width = input_size

    # Convolution 공식 적용 
    out_height = (height + 2 * padding - kernel_size) // stride + 1
    out_width = (width + 2 * padding - kernel_size) // stride + 1

    return out_height, out_width

def plot_activation_function(activation_function):
    import matplotlib.pyplot as plt
    x = torch.linspace(-5, 5, 500)
    y = activation_function(x)
    fig = plt.figure(figsize=(6, 4))
    plt.plot(x.numpy(), y.numpy())
    plt.grid(True)
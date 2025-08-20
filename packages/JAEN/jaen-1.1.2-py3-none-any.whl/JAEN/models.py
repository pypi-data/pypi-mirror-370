import os
import torch
import torch.nn as nn
import os
import torch
import torch.nn as nn

# CNN 모델 정의
class CNNModel(nn.Module):
    def __init__(self, pretrained=True, model_dir='data', model_file='models.pth'):
        super(CNNModel, self).__init__()
        
        # Convolutional Block (Conv -> Conv -> Pool -> Conv -> Conv -> Pool)
        self.conv_layers = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(16, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),  # pool1
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2)   # pool2
        )
        
        # Fully Connected Block (Flatten -> Linear -> Linear -> Linear)
        self.fc_layers = nn.Sequential(
            nn.Linear(32 * 7 * 7, 128),  # Flatten된 입력의 크기: 32 * 7 * 7
            nn.ReLU(),
            nn.Linear(128, 10)  # 10개의 클래스로 분류
        )
        
        # 사전 학습된 가중치를 불러올지 여부를 결정
        if pretrained:
            self.load_pretrained_weights(model_dir, model_file)

    def forward(self, x):
        x = self.conv_layers(x)          # Conv 블록을 통과
        x = x.view(x.size(0), -1)        # Flatten: FC에 넘기기 전 1차원 변환
        x = self.fc_layers(x)            # FC 블록을 통과
        return x

    # 사전 학습된 가중치 로드 함수
    def load_pretrained_weights(self, model_dir, model_file):
        # 현재 모듈의 절대 경로를 가져와서 모델 파일의 절대 경로 생성
        module_dir = os.path.dirname(__file__)  # 현재 모듈의 절대 경로
        model_path = os.path.join(module_dir, model_dir, model_file)
        
        # GPU 사용 여부 확인
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        if os.path.exists(model_path):
            # 사전 학습된 가중치를 지정한 장치로 매핑하여 로드
            self.load_state_dict(torch.load(model_path, map_location=device))
            print(f"Pretrained weights loaded successfully on {device}.")
        else:
            raise FileNotFoundError(f"Model weights not found at {model_path}.")


def Perceptron(*layers, X, y, epochs=10000):
    torch.manual_seed(42)
    import torch.optim as optim

    # nn.Sequential 빈 객체 생성
    model = nn.Sequential()

    for index, layer in enumerate(layers):
        # 레이어 하나씩 추가
        model.add_module(f'linear_{index}', layer)
        model.add_module(f'sigmoid_{index}', nn.Sigmoid())
                
    # 손실 함수와 옵티마이저 정의
    criterion = nn.BCELoss()  # 이진 분류 손실 함수
    optimizer = optim.SGD(model.parameters(), lr=0.1)  # 확률적 경사 하강법
    
    # 학습
    for epoch in range(epochs):
        optimizer.zero_grad()  # 기울기 초기화
        outputs = model(X)  # 모델 예측
        loss = criterion(outputs, y)  # 손실 계산
        loss.backward()  # 역전파
        optimizer.step()  # 가중치 업데이트
    
        if (epoch+1) % 2000 == 0:  # 2000번째 에포크마다 손실 출력
            print(f'Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}')
    return model
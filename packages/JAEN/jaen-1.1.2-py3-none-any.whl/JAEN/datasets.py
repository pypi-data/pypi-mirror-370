import os
import torch
from torch.utils.data import DataLoader, TensorDataset

import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split

# 경고 무시 설정
import warnings
warnings.filterwarnings("ignore")

def load_titanic():
    # 현재 파일의 디렉토리 경로를 가져옴
    current_dir = os.path.dirname(__file__)

    train_loader = torch.load(os.path.join(current_dir, 'data', '00', 'train_loader.pt'), weights_only=False)
    test_loader = torch.load(os.path.join(current_dir, 'data', '00', 'test_loader.pt'), weights_only=False)

    return train_loader, test_loader

# 프로젝트용 데이터 세트 
def load_house_price():
    # 현재 파일의 디렉토리 경로를 가져옴
    current_dir = os.path.dirname(__file__)

    # 절대 경로로 변환
    X_path = os.path.join(current_dir, 'data', '01', 'X_train_tensor.pt')
    y_path = os.path.join(current_dir, 'data', '01', 'y_train_tensor.pt')
    test_path = os.path.join(current_dir, 'data', '01', 'X_test_tensor.pt')

    # 파일을 로드
    X = torch.load(X_path, weights_only=True)
    y = torch.load(y_path, weights_only=True)
    TEST = torch.load(test_path, weights_only=True)

    return X, y, TEST

def load_small_image():
    # 현재 파일의 디렉토리 경로를 가져옴
    current_dir = os.path.dirname(__file__)

    # 절대 경로로 변환
    X_path = os.path.join(current_dir, 'data', '02', 'x_train.pt')
    y_path = os.path.join(current_dir, 'data', '02', 'y_train.pt')
    test_path = os.path.join(current_dir, 'data', '02', 'x_test.pt')

    # 저장된 데이터 불러오기
    X = torch.load(X_path, weights_only=True)
    y = torch.load(y_path, weights_only=True)
    TEST = torch.load(test_path, weights_only=True)


    # 평가용 데이터는 y_test가 없으므로 None으로 설정
    return X, y, TEST

def load_documents():
    # 현재 파일의 디렉토리 경로를 가져옴
    current_dir = os.path.dirname(__file__)

    # 절대 경로로 변환
    X_path = os.path.join(current_dir, 'data', '03', 'x_train.pt')
    y_path = os.path.join(current_dir, 'data', '03', 'y_train.pt')
    test_path = os.path.join(current_dir, 'data', '03', 'x_test.pt')

    # 저장된 데이터 불러오기
    X = torch.load(X_path, weights_only=True)
    y = torch.load(y_path, weights_only=True)
    TEST = torch.load(test_path, weights_only=True)


    # 평가용 데이터는 y_test가 없으므로 None으로 설정
    return X.long(), y, TEST.long()

def get_dataset_name():
    # 현재 파일의 디렉토리 경로를 가져옴
    current_dir = os.path.dirname(__file__)

    # 절대 경로로 변환
    path = os.path.join(current_dir, 'data', 'certi')

    
    return [name.replace('.csv', '') for name in os.listdir(path) if name != '.DS_Store']


def load_data(dataset_name, batch_size=32, test_size=0.2):
    Classification = [
                'bank_marketing',
                'heart_disease',
                'car_evaluation',
                'breast_cancer',
                'wine',
                'iris_dataset', 
                'credit_approval',
                'dry_bean',
                'mushroom'

            ]
    Regression = [
                'abalone',
                'air_quality',
                'forest_fires',
                'real_estate_valuation',
                'boston',
                'automobile',

            ]
    
    # 현재 파일의 디렉토리 경로를 가져옴
    current_dir = os.path.dirname(__file__)

    # 절대 경로로 변환
    path = os.path.join(current_dir, 'data', 'certi', dataset_name+'.csv')

    # 데이터셋 로드 및 전처리
    data = pd.read_csv(path)

    # 결측치를 0으로 처리
    data.fillna(0, inplace=True)

    # 문자열 컬럼이 존재하는 경우 Label Encoding 적용
    label_encoders = {}
    for column in data.select_dtypes(include=['object']).columns:
        le = LabelEncoder()
        data[column] = le.fit_transform(data[column].astype(str))  # 모든 값을 문자열로 변환
        label_encoders[column] = le

    # 타겟 변수와 특징 변수 분리
    if 'target' in data.columns:
        y = data['target']
        X = data.drop('target', axis=1)
        
        if dataset_name == 'wine':
            y = y - 1  # 타겟 변수를 0부터 시작하도록 변환

    else:
        raise ValueError("타겟 변수가 데이터에 존재하지 않습니다.")

    # 데이터 표준화
    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    # 학습 및 테스트 데이터셋 분리

    
    if dataset_name in Classification:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42, stratify=y)
    else:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)


    # 텐서로 변환

    if dataset_name in Classification:
        X_train = torch.tensor(X_train, dtype=torch.float32)
        X_test = torch.tensor(X_test, dtype=torch.float32)
        y_train = torch.tensor(y_train.values, dtype=torch.long)  # pandas Series를 numpy array로 변환
        y_test = torch.tensor(y_test.values, dtype=torch.long)      # pandas Series를 numpy array로 변환
    
    if dataset_name in Regression:
        X_train = torch.tensor(X_train, dtype=torch.float32)
        X_test = torch.tensor(X_test, dtype=torch.float32)
        y_train = torch.tensor(y_train.values, dtype=torch.float32)  # pandas Series를 numpy array로 변환
        y_test = torch.tensor(y_test.values, dtype=torch.float32)      # pandas Series를 numpy array로 변환
    

    # DataLoader 생성
    train_loader = DataLoader(TensorDataset(X_train, y_train), batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(TensorDataset(X_test, y_test), batch_size=batch_size, shuffle=False)   

    return train_loader, test_loader

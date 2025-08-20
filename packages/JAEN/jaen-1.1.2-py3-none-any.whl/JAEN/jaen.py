#!/usr/bin/env python
# coding: utf-8

URL = 'https://manage.jaen.kr'


import requests
import json
import datetime
import os
import pandas as pd
from requests.auth import HTTPBasicAuth
from IPython.display import display
from typing import Union, List, Tuple

class Dataset:
  
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        # data 폴더 생성
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        try:
            res = requests.get(URL+'/api/project/list_data')
            
        except requests.exceptions.Timeout as errd:
            print("Timeout Error : ", errd)
            
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting : ", errc)
            
        except requests.exceptions.HTTPError as errb:
            print("Http Error : ", errb)

        # Any Error except upper exception
        except requests.exceptions.RequestException as erra:
            print("AnyException : ", erra)

        if res.status_code == 200:
            project_data = json.loads(res.text)
            # project_data 변수로부터 데이터를 처리
        else:
            print("API에서 데이터를 가져오지 못했습니다. 상태 코드:", res.status_code)
            print("요청된 값:", json.loads(res.text))

        ids = []
        titles = []
        filenames = list(project_data['data_file'].values())
        infos = list(project_data['data_info'].values())
        datas = []
        for e in range(len(list(project_data['data_info'].keys()))):
            id_val = list(project_data['data_info'].keys())[e].split('_')[0]
            ids.append(id_val)
            titles.append((list(project_data['data_info'].keys())[e].split('_')[1]))
            if len(filenames[e])==1:
                datas.append(URL + f'/api/project/dataSingleDownload?pro_id={id_val}&fileName={str(filenames[e])[2:-2]}')
            else:
                temp = []
                for i in range(len(filenames[e])):
                    temp.append(URL + f'/api/project/dataSingleDownload?pro_id={id_val}&fileName={str(filenames[e][i])}')
                datas.append(temp)

        self.dataset = pd.DataFrame({
            'pro_id': ids,
            'name': titles,
            'info': infos,
            'data': datas,
            'filename': filenames,
        })


    def info(self):
        display(self.dataset[['pro_id', 'name', 'info', 'filename']])


    def load(self, dataset_names):
        global datasets
        username = 'mysuni'
        password = 'mysuni1!'

        if type(dataset_names) == str:
            df = self.dataset.loc[self.dataset['name'] == dataset_names]
            if df.shape[0] > 0:
                fileurl = df['data']
                filename = df['filename']
                if type(fileurl.iloc[0]) == str:
                    fileurl.iloc[0] = pd.Series(fileurl.iloc[0])
                for f_name, f_url in zip(filename.iloc[0], fileurl.iloc[0]):
                    r = requests.get(f_url, auth=HTTPBasicAuth(username, password))
                    filepath = os.path.join(self.data_dir, f_name)
                    open(filepath, 'wb').write(r.content)
                    print(f'파일 다운로드 완료\n====================\n\n데이터셋: {dataset_names}\n파일경로: {filepath}\n\n====================')
                return
            else:
                raise Exception('데이터셋 정보가 없습니다.')

        elif type(dataset_names) == list or type(dataset_names) == tuple:
            for dataset_name in dataset_names:
                df = self.dataset.loc[self.dataset['name'] == dataset_name]
                if df.shape[0] > 0:
                    fileurls = df['data'].iloc[0]
                    filenames = df['filename'].iloc[0]
                    if type(fileurls) == str:
                        fileurls = pd.Series(fileurls)
                    for fileurl, filename in zip(fileurls, filenames):
                        r = requests.get(fileurl, auth=HTTPBasicAuth(username, password))
                        filepath = os.path.join(self.data_dir, filename)
                        open(filepath, 'wb').write(r.content)
                        print(f'파일 다운로드 완료\n====================\n\n데이터셋: {dataset_name}\n파일경로: {filepath}\n\n====================')
                else:
                    raise Exception('데이터셋 정보가 없습니다.')
            return
        else:
            raise Exception('잘못된 정보입니다.')
            
try:
    dataset = Dataset()
except:
    dataset = None

def list_data():
    global dataset
    dataset.info()


def download_data(dataset_name):
    global dataset
    return dataset.load(dataset_name)

# data.jaen.kr 에서 수업용 데이터셋을 다운로드 하는 메서드
def fetch_file(
    dataset_names: Union[str, List[str], Tuple[str]],
    data_dir: str = 'data'
):
    """
    수업에 활용할 데이터를 다운로드 합니다.
    에러가 발생한다면 파일명이 잘못되었거나, 없는 파일을 요청하였을 때 입니다. 강사님께 문의 부탁드립니다.

    ex)  JAEN.fetch_file('boston.csv') -> 단일파일 다운로드
    ex2) JAEN.fetch_file(['boston.csv', 'diabetes.csv']) -> 여러 파일 다운로드
    ex3) JAEN.fetch_file('boston.csv', data_dir = 'files') -> files 디렉토리를 만들어 그 안에 boston 데이터를 넣기
    """

    if not dataset_names : 
        print("❌ 오류: 파일명은 비있을 수 없습니다.")
        return

    # 1. 입력된 dataset_names의 타입 확인 및 처리
    if isinstance(dataset_names, str):
        # 입력이 문자열이면, 단일 요소를 가진 리스트로 변환하여 로직을 통일합니다.
        files_to_download = [dataset_names]
    elif isinstance(dataset_names, (list, tuple)):
        # 입력이 리스트나 튜플이면 그대로 사용합니다.
        files_to_download = dataset_names
    else:
        # 그 외의 타입이면 오류 메시지를 출력하고 함수를 종료합니다.
        print("❌ 오류: 파일명은 문자열(str) 또는 리스트(list) 형태여야 합니다.")
        return

    # --- 기본 설정 (URL 등은 실제 환경에 맞게 조정) ---
    BASE_URL = 'https://data.jaen.kr'
    os.makedirs(data_dir, exist_ok=True)

    print(f"총 {len(files_to_download)}개 파일의 다운로드를 시작합니다.")
    print("=" * 30)

    # 2. 리스트의 각 파일명에 대해 다운로드 로직 반복
    for filename in files_to_download:
        if not isinstance(filename, str) or not filename:
            print(f"⚠️ 잘못된 파일명 '{filename}'은 건너뜁니다.")
            continue

        api_path = f"/api/v1/getdata/{filename}" # API 경로 예시
        download_url = BASE_URL + api_path
        file_path = os.path.join(data_dir, filename)

        print(f"'{filename}' 다운로드 중...")
        try:
            response = requests.get(download_url)
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                print(f"  ✅ 성공: {os.path.abspath(file_path)}")
            else:
                print(f"  ❌ 실패: 서버 오류 (상태 코드: {response.status_code})")
        except requests.exceptions.RequestException as e:
            print(f"  ❌ 실패: 네트워크 오류 ({e})")
        finally:
            print("-" * 20)

    print("모든 다운로드 작업이 완료되었습니다.")


class Project:
    def __init__(self, project_name, class_info, email, server='manage'):
        self.project_name = project_name
        self.edu_name = class_info['edu_name']
        self.edu_rnd = class_info['edu_rnd']
        self.edu_class = class_info['edu_class']
        self.email = email
        self.server = server

    def __make_submission(self, submission):
        timestring = datetime.datetime.now().strftime('%H-%M-%S')
        filename = 'submission-{}.csv'.format(timestring)
        submission.to_csv(filename, index=False)
        print('파일을 저장하였습니다. 파일명: {}'.format(filename))
        return filename

    def __project_submission(self, file_name):
        file_path = './'
        url = URL + f'/api/studentProject/apiScoring?edu_name={self.edu_name}&edu_rnd={self.edu_rnd}&edu_class={self.edu_class}&mail={self.email}&project_name={self.project_name}&file_name={file_name}'
        files = {'file': (file_name, open(file_path + file_name, 'rb'), 'text/csv')}
        r = requests.post(url, files=files)
        r.encoding = 'utf-8'
        message = ''
        try:
            data = json.loads(r.text) # json 변환 실패시 원본 메세지 사용
            if 'trial' in data.keys():
                message = '제출 여부 :{}\n오늘 제출 횟수 : {}\n제출 결과:{}'.format(data['msg'], data['trial'], data['score'])
            else:
                message = '제출 실패 : {}'.format(data['msg'])
        except:
            message = '변환 에러 발생 : {}'.format(r.text)
        return message

    def submit_ipynb(self, ipynb_file_path=None):
        if ipynb_file_path is None:
            raise Exception('노트북(ipynb) 파일의 경로를 입력해 주세요.') 
        url = URL + '/api/studentProject/ipynbUploadFromMod'
        upload = {'upload_file': open(ipynb_file_path, 'rb')}
        upload['filename'] = upload['upload_file'].name[2:]
        res = requests.post(url, data = upload, params = self.info(), verify = False)
        print(res.text)

    def submit(self, submission):
        filename = self.__make_submission(submission)
        print(self.__project_submission(filename))
    
    def info(self):
        return {'edu_name': self.edu_name, 
                'edu_rnd': self.edu_rnd,
                'edu_class': self.edu_class, 
                'email': self.email, 
                'project_name': self.project_name}

def submit(submission_file):
    global project
    project.submit(submission_file)

def submit_ipynb(ipynb_file_path):
    global project
    project.submit_ipynb(ipynb_file_path)


def update_project(project_name=None, class_info=None, email=None):
    global project
    if project_name:
        project.project_name = project_name
    if project.class_info:
        project.class_info = class_info
    if project.email:
        project.email = email
    print('정보 업데이트 완료')




class Exam:
    BASE_URL = "http://20.196.94.39"

    def __init__(self, student_name, class_name, class_round, exam_type):
        self.student_name = student_name
        self.class_name = class_name
        self.class_round = class_round
        self.exam_type = exam_type
       
        if self.class_name == 'AI Essential':
            print(f'{self.student_name} 프로님 환영합니다. {self.class_name} {self.class_round} 실기평가를 위해 아래의 시험 주의사항을 읽고 시험을 진행해주시면 됩니다.')

    def extract_code(self, func):
        import inspect
        """함수나 클래스의 소스 코드를 추출"""
        return inspect.getsource(func)

    def extract_dataloader_info(self, dataloader):
        import torch
        """DataLoader의 batch_size와 shuffle 속성을 추출"""
        return {
            "batch_size": dataloader.batch_size,
            "shuffle": isinstance(dataloader.sampler, torch.utils.data.sampler.RandomSampler)
        }

    def extract_model_info(self, model):
        import torch.nn as nn
        """CNN 또는 RNN 모델의 계층 정보 추출"""
        layers_info = []
        for layer in model.children():
            if isinstance(layer, nn.Conv2d):
                layers_info.append({
                    "type": "Conv2d",
                    "in_channels": layer.in_channels,
                    "out_channels": layer.out_channels,
                    "kernel_size": layer.kernel_size,
                    "padding": layer.padding
                })
            elif isinstance(layer, nn.MaxPool2d):
                layers_info.append({"type": "MaxPool2d", "kernel_size": layer.kernel_size})
            elif isinstance(layer, nn.Linear):
                layers_info.append({
                    "type": "Linear",
                    "in_features": layer.in_features,
                    "out_features": layer.out_features
                })
            elif isinstance(layer, nn.LSTM):
                layers_info.append({
                    "type": "LSTM",
                    "input_size": layer.input_size,
                    "hidden_size": layer.hidden_size
                })
            elif isinstance(layer, nn.RNN):
                layers_info.append({
                    "type": "RNN",
                    "input_size": layer.input_size,
                    "hidden_size": layer.hidden_size
                })
            elif isinstance(layer, nn.Flatten):
                layers_info.append({"type": "Flatten"})

            elif isinstance(layer, nn.Embedding):
                layers_info.append({
                    "type": "Embedding",
                    "num_embeddings": layer.num_embeddings,
                    "embedding_dim": layer.embedding_dim
                })
                    
            # 활성화 함수 체크
            elif isinstance(layer, nn.ReLU):
                layers_info.append({"type": "ReLU"})
            elif isinstance(layer, nn.Sigmoid):
                layers_info.append({"type": "Sigmoid"})
            elif isinstance(layer, nn.Tanh):
                layers_info.append({"type": "Tanh"})
            elif isinstance(layer, nn.Softmax):
                layers_info.append({"type": "Softmax", "dim": layer.dim})
        
        return layers_info

    def evaluate_model(self, model, test_loader, test_type):
        import torch
        import torch.nn as nn
        
        device = torch.device('cpu')
        model.to(device)
        model.eval()

        total_loss = 0
        correct = 0
        mse = 0
        
        if test_type == 'classification':
            criterion = nn.CrossEntropyLoss()
        elif test_type == 'regression':
            criterion = nn.MSELoss()
        else:
            raise ValueError("test_type should be either 'classification' or 'regression'")
        
        with torch.no_grad():
            for data, target in test_loader:
                data, target = data.to(device), target.to(device)
                output = model(data)
                
                total_loss += criterion(output, target).item()
                
                if test_type == 'classification':
                    pred = output.argmax(dim=1, keepdim=True)
                    correct += pred.eq(target.view_as(pred)).sum().item()
                elif test_type == 'regression':
                    mse += criterion(output, target).item()

        if test_type == 'classification':
            avg_loss = total_loss / len(test_loader.dataset)
            accuracy = correct / len(test_loader.dataset)
            return accuracy, avg_loss
        
        elif test_type == 'regression':
            avg_mse = mse / len(test_loader.dataset)
            return avg_mse, total_loss / len(test_loader.dataset)
        

    def submit_to_server(self, question_id, payload):
        import requests
        """서버로 데이터를 전송"""
        url = f"{self.BASE_URL}/submit_question/{question_id}"
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return "제출 성공"

        response_message = json.loads(response.text)
        print(response_message)
        # status_code, message = response_message.split(': ')
        # if status_code and message:
        #     return f"제출 실패: {message}"
        return f"제출 실패"

    def submit(self, question_id, answer=None, dataset_class=None, dataloader=None, model=None):
        """문제 제출 메소드"""
        payload = {
            "student_id": self.student_name,
            "class_name":   self.class_name,
            "class_round":  self.class_round,
            "exam_type":   self.exam_type,
         }
        
        if question_id == 1 and answer is not None:  # 함수 구현 제출
            try:
                payload["code"] = self.extract_code(answer)
            except:
                payload['code'] = 'Error'

        elif question_id == 2 and dataset_class is not None and dataloader is not None:  # 데이터셋 및 데이터로더 제출
            try:
                payload['dataset_code'] = {
                    'init':self.extract_code(dataset_class.__init__),
                    'len': self.extract_code(dataset_class.__len__),
                    'getitem':self.extract_code(dataset_class.__getitem__)
                }
            except:
                payload['dataset_code'] = {
                    'init':'Error',
                    'len': 'Error',
                    'getitem':'Error'
                }
            try:
                payload["dataloader_info"] = self.extract_dataloader_info(dataloader)
            except:
                payload["dataloader_info"] =  {
                    "batch_size": 'Error',
                    "shuffle": 'Error'
                }
                
        elif question_id == 3 and model is not None:  # CNN 모델 제출
            try:
                payload["model_info"] = self.extract_model_info(model)
            except Exception as e:
                payload['model_info'] = ['Error']

        elif question_id == 4 and model is not None:  # LSTM 모델 제출
            try:
                payload["model_info"] = self.extract_model_info(model)
            except Exception as e:
                payload['model_info'] = ['Error']

        elif question_id == 5 and model is not None:  # DNN 모델 성능 평가 후 제출

            if self.exam_type == '1형':
                import torch
                from torchvision import datasets, transforms
                torch.manual_seed(42)
                transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5,), (0.5,))])
                test_dataset = datasets.MNIST(root='./data', train=False, download=True, transform=transform)
                test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=64, shuffle=False)
                test_type = 'classification'

            else:
                datasets = {
                '2형': 'breast_cancer',
                '3형': 'boston', 
                '4형': 'abalone',
                '5형': 'bank_marketing',
                '6형': 'air_quality',
                '7형': 'heart_disease',
                '8형': 'forest_fires',
                '9형': 'car_evaluation',
                '10형': 'real_estate_valuation',
                '11형': 'automobile',
                '12형': 'wine',
                '13형': 'iris_dataset',
                '14형': 'credit_approval',
                '15형': 'mushroom',
            }
                
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

            dataset_name = datasets[self.exam_type]
            
            from .datasets import load_data
            _, test_loader = load_data(dataset_name)

            if dataset_name in Classification:
                test_type = 'classification'
            elif dataset_name in Regression:
                test_type = 'regression'

            try:
                score, loss = self.evaluate_model(model, test_loader, test_type)
                payload["score"] = score
                payload["loss"] = loss
            except:
                payload['score'] = 'Error'
                payload['loss'] = 'Error'

        else:
            return "지원되지 않는 문제이거나 잘못된 입력입니다."
       
        return self.submit_to_server(question_id, payload)
    





from urllib.parse import unquote

def download_file(slug: str):
    # 서버에서 파일 다운로드 요청
    response = requests.get(f"http://20.196.94.39/download/{slug}", stream=True)

    # 성공적으로 응답을 받았는지 확인
    if response.status_code == 200:
        # Content-Disposition 헤더에서 파일명 추출
        content_disposition = response.headers.get('Content-Disposition')

        if "filename*=" in content_disposition:
            filename = unquote(content_disposition.split("''")[1])
        else:
            filename = content_disposition.split("filename=")[1].strip('"')

        # 파일을 로컬에 저장
        with open(filename, "wb") as file:
            file.write(response.content)

        # 현재 작업 디렉토리에서의 절대 경로
        absolute_path = os.path.abspath(filename)
        # 상대 경로
        relative_path = filename

        print(f"파일이 성공적으로 다운로드되었습니다: {filename}")
        print(f"절대 경로: {absolute_path}")
        print(f"상대 경로: {relative_path}")
    else:
        print(f"파일 다운로드 실패: 상태 코드 {response.status_code}")



class Key:
    def __init__(self, username):
        self.username = username
        self.server_url = 'http://ai.jaen.kr/'  # Flask 서버 주소
        
        # Flask 서버에서 키 정보를 가져옴
        self.keys = self.get_keys() or {}  # 서버에서 가져온 키가 없으면 빈 딕셔너리 사용
        
        if self.keys:
            print(f"현재 등록된 키가 {len(self.keys)}개 있습니다.")
            self.register_keys_to_env()
        else:
            print("현재 등록된 키가 없습니다.")
    
    def get_keys(self):
        """Flask 서버에서 해당 사용자의 키 정보를 가져옴"""
        url = f'{self.server_url}get_keys/{self.username}'
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.json()  # {keyname: apikey, ...} 형태의 딕셔너리 반환
        else:
            return None
    
    def register_keys_to_env(self):
        """환경 변수에 키를 등록"""
        for key_name, api_key in self.keys.items():
            if api_key:  # 값이 None이 아닌 경우에만 환경 변수에 등록
                os.environ[key_name] = api_key
                print(f"  - 환경 변수에 '{key_name}' 등록 완료.")

    def save_keys(self, keys):
        """Flask 서버에 키를 전달하여 저장"""
        url = f'{self.server_url}save_keys'
        
        # 서버로 보낼 데이터 형식 {username: 사용자이름, keys: {keyname: apikey, ...}}
        data = {
            'username': self.username,
            'keys': keys  # {keyname: apikey, ...}
        }
        
        # POST 요청으로 키 저장
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            print(f"{len(keys)}개의 키가 서버에 저장되었습니다.")
            # 서버에 키 저장 후 다시 로드하여 환경 변수에 등록
            self.keys = self.get_keys()
            self.register_keys_to_env()
        else:
            print("키 저장에 실패했습니다. 서버 응답:", response.status_code)
    
    def get_registered_keys(self):
        """현재 등록된 키 정보를 조회"""
        if self.keys:
            print("현재 등록된 키 정보:")
            for key_name, api_key in self.keys.items():
                print(f"{key_name}: {api_key}")
        else:
            print("현재 등록된 키가 없습니다.")




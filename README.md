# GAMST
Generative Assistant Model framework for Surveillance and Threat detection

## Topic
BERT 모델을 통한 CCTV 영상 위험 분석 보조 시스템  

## 서비스 아키텍쳐
![architecture.png](./mdImg/architecture.png)  

[Model Workload Repo](https://github.com/omoknooni/GAMST-model-workflow)

## Install
- Requirements : Python3.10+  
### Install Dependency
```
python -m venv venv

source ./venv/bin/activate

pip install -r requirements.txt

```
### Create .env file
```
AWS_ACCESS_KEY=
AWS_SECRET_ACCESS_KEY=
VIDEO_BUCKET=
DB_HOST=
DB_USER=
DB_PASSWORD=
```


### Run server
```
python manage.py runserver
```

# 자람 허브

## v1

Django로 작성된 자람 허브

## v2

FastAPI로 새로 작성된 자람 허브

url endpoint 태그 v2가 붙여져 있는 url로 호출 가능하며(/hub/api/v2/~~), Docker을 기반으로 새로운 포트 번호를 가진 컨테이너로 실행됩니다.

API 문서 : [Link(Gitbook 문서 업로드 예정)]()

## (v2) 개발 환경 구성 방법

### 필수 환경
- Docker
- Python 3.10.10
- MariaDB

### 개발용 데이터베이스를 로컬에 설치 및 적용
1. 배포 환경과 유사한 테이블이 로컬 MariaDB에 없을 때
   1. Alembic을 이용한 데이터베이스 마이그레이션 (Alembic 환경 셋업은 추후 추가 예정)
   2. main.py를 실행해서 제대로 동작하는지 확인하거나 테스트케이스를 실행.
2. 배포 환경과 유사한 테이블이 로컬 MariaDB에 있을 때
   1. main.py를 실행해서 제대로 동작하는지 확인하거나 테스트케이스를 실행.

### 개발 환경 세팅
1. 가상 환경 생성 : `python -m venv venv`
2. `pip install -r requirements.txt`
3. `python main.py`를 실행해서 제대로 동작하는지 확인하거나 테스트케이스를 실행.
4. 코드를 최종적으로 수정하고 나면, black formatter를 이용해서 코드를 정리해주세요: `black .`

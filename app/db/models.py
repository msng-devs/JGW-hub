# --------------------------------------------------------------------------
# 자람 허브 model ORM을 정의한 모듈입니다.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.declarative import DeclarativeMeta

Base: DeclarativeMeta = declarative_base()


# class Something(Base):
#     pass

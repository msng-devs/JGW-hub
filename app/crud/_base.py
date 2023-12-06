# --------------------------------------------------------------------------
# 기본 Model CRUD 메서드를 정의한 모듈입니다.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from typing import Any, Type, List, Optional

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_object(
    db: AsyncSession, model: Any, model_id: int, response_model: Type[BaseModel]
) -> Optional[Any]:
    query = select(model).filter(model.id == model_id)
    result = (await db.execute(query)).scalar_one_or_none()
    if result:
        return response_model.model_validate(result.__dict__)
    else:
        return None


async def get_objects(
    db: AsyncSession,
    model: Any,
    response_model: Type[BaseModel],
    condition: Optional[Any] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Any]:
    query = select(model).offset(skip).limit(limit)
    if condition is not None:
        query = query.where(condition)
    result = await db.execute(query)
    result_list = result.scalars().all()
    return [response_model.model_validate(item.__dict__) for item in result_list]


async def create_object(
    db: AsyncSession, model: Any, obj: BaseModel, response_model: Type[BaseModel]
) -> Any:
    obj_data = obj.model_dump()
    db_obj = model(**obj_data)

    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return response_model.model_validate(db_obj.__dict__)


async def update_object(
    db: AsyncSession,
    model: Any,
    model_id: int,
    obj: BaseModel,
    response_model: Type[BaseModel],
) -> Optional[Any]:
    query = select(model).filter(model.id == model_id)
    db_obj = (await db.execute(query)).scalar_one_or_none()
    if db_obj is None:
        return None
    update_data = obj.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_obj, key, value)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return response_model.model_validate(db_obj.__dict__)


async def delete_object(db: AsyncSession, model: Any, model_id: int) -> Optional[int]:
    query = select(model).filter(model.id == model_id)
    db_obj = (await db.execute(query)).scalar_one_or_none()
    if db_obj:
        await db.delete(db_obj)
        await db.commit()
    else:
        return None
    return model_id

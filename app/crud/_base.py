# --------------------------------------------------------------------------
# 기본 Model CRUD 메서드를 정의한 모듈입니다.
#
# @author bnbong bbbong9@gmail.com
# --------------------------------------------------------------------------
from typing import Any, Type, Optional

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession


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
    db_obj = await db.get(model, model_id)
    if db_obj is None:
        return None
    update_data = obj.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in update_data.items():
        setattr(db_obj, key, value)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return response_model.model_validate(db_obj.__dict__)


async def delete_object(db: AsyncSession, model: Any, model_id: int) -> Optional[int]:
    db_obj = await db.get(model, model_id)
    if db_obj:
        await db.delete(db_obj)
        await db.commit()
    else:
        return None
    return model_id

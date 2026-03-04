from prometheus_client import Counter
import structlog
from fastapi import APIRouter, status, Depends
from sqlmodel import select
from app.core.db import SessionDep
from app.models.subscriber import Subscriber
from app.schemas.subscriber import SubscriberCreate, SubscriberRead
from app.core.exceptions import DuplicateException, NotFoundException
from app.core.security import get_admin_user

router = APIRouter()
logger = structlog.get_logger()

SUBSCRIBER_COUNTER = Counter("total_subscribers_added", "Total number of new subscriptions")

@router.post("/", response_model=SubscriberRead, status_code=status.HTTP_201_CREATED)
async def subscribe(sub_in: SubscriberCreate, session: SessionDep):
    logger.info("subscription_attempt", email=sub_in.email)

    statement = select(Subscriber).where(Subscriber.email == sub_in.email)
    # CHANGE: .execute() instead of .exec()
    result = await session.execute(statement)
    if result.scalars().first():
        logger.warning("duplicate_subscription", email=sub_in.email)
        raise DuplicateException(detail="This email is already on the list.")

    new_sub = Subscriber.model_validate(sub_in)
    session.add(new_sub)
    await session.commit()
    await session.refresh(new_sub)
    
    SUBSCRIBER_COUNTER.inc()
    logger.info("subscriber_added", subscriber_id=new_sub.id)
    return new_sub

@router.delete("/{email}", status_code=status.HTTP_204_NO_CONTENT)
async def unsubscribe(email: str, session: SessionDep):
    logger.info("unsubscribe_attempt", email=email)
    
    statement = select(Subscriber).where(Subscriber.email == email)
    # CHANGE: .execute() instead of .exec()
    result = await session.execute(statement)
    subscriber = result.scalars().first()
    
    if not subscriber:
        logger.warning("unsubscribe_failed_not_found", email=email)
        raise NotFoundException(detail="Subscriber not found") 
        
    await session.delete(subscriber)
    await session.commit()
    
    logger.info("subscriber_removed", email=email)
    return None

@router.get("/", response_model=list[SubscriberRead], dependencies=[Depends(get_admin_user)])
async def get_subscribers(session: SessionDep):
    logger.info("admin_fetch_subscribers_list")
    
    statement = select(Subscriber)
    # CHANGE: .execute() instead of .exec()
    result = await session.execute(statement)
    # return []
    return result.scalars().all()

"""
I am using a deprecated method for compatibility with synchronous testing functions 

If I do not have to run pytest, I can replace the last three lines with 

    statement = select(Subscriber)
    result = await session.exec(statement)
    return result.all()
"""

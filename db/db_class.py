from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from models.tables import InputEvent, DeliveryAttempt, Base
from sqlalchemy import insert , select, update , or_
from datetime import datetime
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.dialects.postgresql import insert as psq_insert
from models.result_class import Result


class Agent():
    def __init__(self, db_path : str):
        self.engine = create_async_engine(db_path)
        self.session_factory = async_sessionmaker(self.engine, expire_on_commit=False)

    async def connect(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def close(self):
        await self.engine.dispose()


    async def add_income_event(self, ev_id : str, ev_type : str , ev_data : dict ):
        async with self.session_factory() as session:
            try:
                query = (psq_insert(InputEvent).values(event_id=ev_id,event_type=ev_type,event_data=ev_data,
                event_status="pending", received_at=datetime.now())).on_conflict_do_nothing(index_elements=[InputEvent.event_id]
                ).returning(InputEvent.event_id)
                result = await session.execute(query)
                if result.scalar_one_or_none() is None:
                    await session.rollback()
                    return "duplicate"
                await session.commit()
                return "ok"
            
            except IntegrityError:
                await session.rollback()
                return "violation of terms"
            
            except SQLAlchemyError:
                await session.rollback()
                return "error"
            
            
    async def add_attempt(self,ev_id : str, att_num : int, targ : str, stat_code : int | None, err : str):
        async with self.session_factory() as session:
            try:
                query = insert(DeliveryAttempt).values(event_id=ev_id, attempt_number=att_num, target=targ, 
                status_code=stat_code, error=err, created_at=datetime.now()).returning(DeliveryAttempt.attempt_id)
                result = await session.execute(query)
                value = result.scalar_one_or_none()
                if value:
                    await session.commit()
                    return value
                else:
                    return None
            except IntegrityError:
                await session.rollback()
                return "volation conflict"
            
    async def check_only_pending_resp(self):
        async with self.session_factory() as session:
            query = select(InputEvent).where(InputEvent.event_status == "pending", or_( InputEvent.next_attempt.is_(None),
            InputEvent.next_attempt <= datetime.now() ,))
            result = await session.execute(query)
            reqs_item = result.scalar()
            if reqs_item :
                return reqs_item
            else:
                return None

    async def get_event_by_id(self, event_id : str):
        async with self.session_factory() as session:
            query = select(InputEvent).where(InputEvent.event_id == event_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()

            
    async def select_last_status_code(self, event_id : str):
        async with self.session_factory() as session:
            query = select(DeliveryAttempt.status_code).where(DeliveryAttempt.event_id==event_id).order_by(
            DeliveryAttempt.attempt_id.desc())
            result = await session.execute(query)
            last_error = result.scalar()
            return last_error

    async def update_after_request(self, result : Result):
        try:
            async with self.session_factory() as session:
                async with session.begin():
                    update_query1 = update(InputEvent).values(event_status = result.status).where(InputEvent.event_id == result.ev_id,InputEvent.event_status != result.status)
                    status_result = await session.execute(update_query1)

                    update_query2 = update(InputEvent).values( final_status_code = result.final_code,
                    attempt_count = result.attempt_count, next_attempt=result.next_attempt).where(InputEvent.event_id == 
                    result.ev_id)
                    update_result = await session.execute(update_query2)
        
                    if result.attempt_confirm:
                        insert_query = insert(DeliveryAttempt).values(event_id=result.ev_id, attempt_number=result.attempt_count, target=result.deliver_url, 
                        status_code=result.current_code, error=result.error, created_at=datetime.now()).returning(DeliveryAttempt.attempt_id)
                        insert_result = await session.execute(insert_query)

                        return insert_result.scalar()
                    else:
                        return update_result
                
        except SQLAlchemyError:
            return None    



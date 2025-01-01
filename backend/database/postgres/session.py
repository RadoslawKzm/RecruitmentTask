from typing import Annotated

from fastapi import Depends
from fastapi.exceptions import HTTPException
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy_utils import create_database, database_exists
from sqlmodel import SQLModel

from backend.database.postgres import config

Base = declarative_base()


def init_db():
    engine = create_engine(
        config.POSTGRES_SYNC_URL,
        pool_size=50,
        max_overflow=20,
    )
    # from sqlalchemy_utils import drop_database
    # if database_exists(engine.url):
    #     drop_database(engine.url)
    if not database_exists(engine.url):
        create_database(engine.url)
    SQLModel.metadata.create_all(engine)


class DbContext(AsyncSession):
    """
    Context manager class for managing SQLAlchemy session objects.
    It manages opening transactions, returns session object,
    then after transaction commits/rollbacks and closes.
    It manages all fallbacks for user.
    UserCore doesn't need to worry
        about committing changes to DB and exception handling.
    """

    def __init__(self, *args, suppress_exc: bool = False, **kwargs) -> None:
        self.engine: AsyncEngine = create_async_engine(
            url=config.POSTGRES_ASYNC_URL
        )
        self.suppress_exc = suppress_exc
        super(DbContext, self).__init__(
            *args,
            autocommit=False,
            bind=self.engine,
            autoflush=False,
            # expire_on_commit=False,
            **kwargs,
        )

    async def __aenter__(self) -> AsyncSession:
        """
        :return: SQLAlchemy session object for context manager to operate on.
        """
        # _session_maker = async_sessionmaker(
        #     autocommit=False,
        #     bind=self.engine,
        # )
        # self.session = _session_maker()
        self.session = self
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if any((exc_type, exc_val, exc_tb)):
            if exc_type == HTTPException:
                raise exc_val  # Suppressing rest of session due to HTTP exc
            logger.opt(lazy=True).exception(exc_val)
            logger.debug("Rolling back session")
            await self.session.rollback()
            logger.debug("Closing DB session")
            await self.session.close()
            self.json = {
                "exc_type": str(exc_type),
                "exc_val": str(exc_val),
                "exc_tb": str(exc_tb),
            }
            if self.suppress_exc:
                logger.opt(lazy=True).debug(
                    "Suppressing exception because suppress={x}",
                    x=lambda: self.suppress_exc,
                )
                return self.suppress_exc  # gracefully suppressing if True
            raise Exception(self.json)
            # raise CustomDatabaseException
        try:
            await self.session.commit()
        except Exception:
            raise Exception
        # except IntegrityError as exc:
        #     raise CustomDatabaseException
        await self.session.close()

    async def close(self):
        await self.engine.dispose()


async def get_session():
    async with DbContext() as db:
        yield db


DBSessionDep = Annotated[AsyncSession, Depends(get_session)]

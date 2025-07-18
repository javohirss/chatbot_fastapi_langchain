from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


from config import settings

uri = settings.db_url

async_engine = create_async_engine(uri)

async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)


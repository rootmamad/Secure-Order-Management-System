from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from config import settings


engine = create_engine(settings.URl_Database,echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
Base.metadata.create_all(bind=engine)

def get_session():
    with SessionLocal() as session:
        try:
            yield session  
            session.commit() 
        except Exception as e:
            session.rollback() 
            raise e
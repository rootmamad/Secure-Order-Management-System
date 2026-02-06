from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

URl_Database = "postgresql://order_login:53638487@127.0.0.1:5432/order_management"

engine = create_engine(URl_Database,echo=True)
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
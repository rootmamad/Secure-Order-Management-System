from celery import Celery
from database import SessionLocal
from models import AuditLog
from datetime import datetime,timedelta
from models import Order,OrderItem
from celery.schedules import crontab


app = Celery("orders_task",broker="amqp://guest:guest@localhost:5672//")

@app.task()
def audit_log(user_id,action,detail):
    db = SessionLocal()
    try:
        log = AuditLog(user_id=user_id,action=action,detail=detail)
        db.add(log)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Failed to save audit log: {e}")
    finally:
        db.close()

@app.task()
def delete_old_orders():
    db = SessionLocal()
    time_delta = datetime.now() - timedelta(days=7)

    try:
        
        orders = db.query(Order).filter(Order.created_at <= time_delta,Order.status=="pending").all()

        order_ids = [order.id for order in orders]
        if order_ids:
            db.query(OrderItem).filter(OrderItem.order_id.in_(order_ids)).delete(synchronize_session=False)
            db.query(Order).filter(Order.id.in_(order_ids)).delete(synchronize_session=False)
            

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"error: {e}")
    finally:
        db.close()
    


    
app.conf.beat_schedule = {
    "delete-week-old-orders-every-midnight": {
        "task": "celery_worker.delete_old_orders", 
        "schedule": crontab(hour=20, minute=20), 
    }
}
app.conf.timezone = 'Asia/Tehran'
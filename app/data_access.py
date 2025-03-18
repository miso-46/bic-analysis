import pandas as pd
from db import SessionLocal
from models import User, Reception

# 店舗情報を取得して表示させるための関数
def get_data(store, cat_id):
    session = SessionLocal()
    try:
        results = session.query(User, Reception).join(Reception, User.id == Reception.user_id).filter(User.store_id == store, Reception.category_id == cat_id).all()
        rows = []
        for user, reception in results:
            rows.append({
                "user_id": user.id,
                "store_id": user.store_id,
                "reception_id": reception.id,
                "category_id": reception.category_id,
                "time": reception.time
            })
        return pd.DataFrame(rows)
    finally:
        session.close()

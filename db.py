from models import SessionLocal, Reception, User
import pandas as pd

# Reception テーブルから user_id と category_id でデータを取得し、DataFrame に変換
def get_data(store_id, category_id):
    session = SessionLocal()
    try:
        # Reception と User を結合し、User.store_id と Reception.category_id でフィルタ
        results = session.query(Reception).join(User, Reception.user_id == User.id).filter(
            User.store_id == store_id,
            Reception.category_id == category_id
        ).all()

        # 取得したオブジェクトを DataFrame に変換
        df = pd.DataFrame([{
            "id": r.id,
            "user_id": r.user_id,
            "category_id": r.category_id,
            "time": r.time
        } for r in results])
    finally:
        session.close()

    return df



# auth_utils.py
import bcrypt
import streamlit as st
from db import SessionLocal
from models import Store

def hash_password(plain_password: str) -> str:
    # bcryptでパスワードをハッシュ化
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # 平文パスワードをbcryptハッシュと比較
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def login_page():
    st.title("店舗ログイン")
    store_name = st.text_input("店舗名")
    plain_password = st.text_input("パスワード", type="password")

    if st.button("ログイン"):
        session = SessionLocal()
        try:
            store_obj = session.query(Store).filter_by(name=store_name).first()
            if not store_obj:
                st.error("店舗が見つかりません。")
            else:
                if verify_password(plain_password, store_obj.password):
                    st.session_state["logged_in"] = True
                    st.experimental_rerun()  # スクリプトを再実行し、ログイン済みの画面に切り替え
                else:
                    st.error("パスワードが間違っています。")
        except Exception as e:
            st.error(f"ログイン処理中にエラーが発生しました: {e}")
        finally:
            session.close()
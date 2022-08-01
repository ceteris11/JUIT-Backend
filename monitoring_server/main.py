import streamlit as st
import pandas as pd
from db.db_model import session_scope, UserInfo
from sqlalchemy import func
from datetime import datetime


# 일일 가입자 수 확인
def load_daily_new_user():
    with session_scope() as session:
        sql_query = session.query(func.substr(UserInfo.beg_dtim, 1, 8).label('date'), func.count(1).label('cnt')). \
            filter(UserInfo.login_type == 'mobile',
                   UserInfo.end_dtim == '99991231235959').\
            group_by(func.substr(UserInfo.beg_dtim, 1, 8)).\
            order_by(func.substr(UserInfo.beg_dtim, 1, 8).desc())
        daily_new_user = pd.read_sql(sql_query.statement, session.bind)

    return daily_new_user


st.title('JUIT Monitoring Dashboard')

# 가입자 추이 확인
st.header('가입자 추이')
h1 = '일일 가입자 수'
h2 = '누적 가입자 수'
# 가입자 수 load
new_user_df = load_daily_new_user()
new_user_df.index = pd.to_datetime(new_user_df['date'], format='%Y%m%d')
new_user_df = new_user_df['cnt']
# 당일 가입자 수
today_df = new_user_df[new_user_df.index == datetime.strptime(datetime.now().strftime("%Y%m%d"), "%Y%m%d")]
if len(today_df) == 0:
    today_count = 0
else:
    today_count = today_df[0]
st.write(f'오늘 가입자 수: {today_count}명({datetime.now().strftime("%Y.%m.%d")})')
# 라디오 버튼
selected_item = st.radio('데이터 구분', (h1, h2))
if selected_item == h1:
    st.subheader(h1)
    st.bar_chart(new_user_df)
elif selected_item == h2:
    st.subheader(h2)
    st.line_chart(new_user_df.sort_index().cumsum())

# 스크래핑 오류 확인

from consumer.update_portfolio import *

def test_update_single_stock_portfolio():
    user_code = 215
    begin_date = "20210801"
    account_number = "5521993510"
    securities_code = "KIWOOM"
    stock_cd = "005930"

    update_single_stock_portfolio(user_code, begin_date, account_number, securities_code, stock_cd)

    query_user_portfolio = f"select * from user_portfolio " \
                           f"where user_code = {user_code} " \
                           f"and stock_cd = {stock_cd}"

    print(f"query : {query_user_portfolio}")
    assert get_df_from_db(query_user_portfolio).shape[0] > 0


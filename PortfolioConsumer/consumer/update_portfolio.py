import sys
import os
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from consumer.db_connect import *
from util.util_get_country import get_country
from db_model import session_scope, DateWorkingDay
from sqlalchemy.orm import aliased

def get_receiving_transaction_list():
    return ['매수', '유상주입고', '무상주입고', '공모주입고', '타사대체입고', '대체입고', '액면분할병합입고',
            '감자입고', '회사분할입고', '배당입고', '해외주식매수']


def get_releasing_transaction_list():
    return ['매도', '타사대체출고', '대체출고', '액면분할병합출고', '감자출고', '해외주식매도']


def get_dividend_transaction_list():
    return ['배당', '배상세출금', '해외주식배당']  # 배당세 출금은 2021.06.23 현재 거래내역이 사실상 존재하지 않아 어떻게 처리될지 모른다.

def util_get_pulled_transaction_date(date):
    with session_scope() as session:
        # kr working day
        kr_working_day_1 = aliased(DateWorkingDay)
        kr_working_day_2 = aliased(DateWorkingDay)
        kr_working_day = session.query(kr_working_day_1.working_day.label('date'),
                                       kr_working_day_2.working_day.label('pulled_transaction_date')). \
            join(kr_working_day_2, kr_working_day_1.seq == kr_working_day_2.seq + 2). \
            filter(kr_working_day_1.working_day == date).first()
        session.commit()
        return kr_working_day[1]


def update_single_stock_portfolio(user_code, begin_date, account_number, securities_code, stock_cd,
                                  country=None, tmp_portfolio=False):
    # print(f'update_single_stock_portfolio - user_code: {user_code}, begin_date: {begin_date}, '
    #       f'account_number: {account_number}, securities_code: {securities_code}, stock_cd: {stock_cd}, '
    #       f'country: {country}, tmp_portfolio: {tmp_portfolio}')

    # user_portfolio, user_trading_log table 설정
    if tmp_portfolio:
        user_portfolio_table = 'tmp_user_portfolio'
    else:
        user_portfolio_table = 'user_portfolio'

    # begin_date
    begin_date = str(begin_date)

    # country 설정
    if country is None:
        country = get_country(stock_cd)

    # end_date 설정
    if country == 'KR':
        end_date = exec_query(f'select max(working_day) from date_working_day')[0][0]
    else:
        end_date = exec_query(f'select max(working_day) from us_date_working_day')[0][0]
    end_date = str(end_date)

    # begin_date가 end_date보다 크다면 함수 실행 종료
    if end_date < begin_date:
        # print('end_date < begin_date')
        return None

    # prev_date 설정
    prev_date = (datetime.strptime(begin_date, '%Y%m%d') - timedelta(days=1)).strftime('%Y%m%d')

    # 겹치는 구간 portfolio 삭제
    exec_query(f'delete '
               f'from {user_portfolio_table} '
               f'where user_code = {user_code} '
               f'and account_number = "{account_number}" '
               f'and securities_code = "{securities_code}" '
               f'and stock_cd = "{stock_cd}" '
               f'and date >= "{begin_date}" '
               f'and date <= "{end_date}" ')

    # 전일 포트폴리오 가져오기
    sql = f'select * ' \
          f'from {user_portfolio_table} ' \
          f'where 1=1 ' \
          f'and user_code = {user_code} ' \
          f'and date = {prev_date} ' \
          f'and account_number = "{account_number}" ' \
          f'and stock_cd = "{stock_cd}" '
    prev_portfolio = get_df_from_db(sql)

    # 거래내역 가져오기
    sql = f'select * ' \
          f'from user_trading_log ' \
          f'where 1=1 ' \
          f'and user_code = {user_code} ' \
          f'and account_number = "{account_number}" ' \
          f'and date >= "{begin_date}" ' \
          f'and stock_cd = "{stock_cd}" ' \
          f'and stock_type in ("domestic_stock", "domestic_etf", "domestic_etn", "us_stock")'
    trading_data = get_df_from_db(sql)
    # print(trading_data)

    # prev_portfolio가 없을 경우(최초 포트폴리오 등록일 경우 => begin_date가 20110101일 경우) begin_date, prev_date 재설정
    # 직접입력한 거래내역을 delete할 경우, prev_portfolio도 없고 user_trading_log도 없는 케이스 존재. 해당 케이스 제외 위해 trading_data 조건 추가
    if len(prev_portfolio) == 0 and len(trading_data) != 0:
        begin_date = str(min(trading_data['date']))
        # prev_date 설정
        prev_date = (datetime.strptime(begin_date, '%Y%m%d') - timedelta(days=1)).strftime('%Y%m%d')

    # 가격 가져오기
    price_begin_date = (datetime.strptime(prev_date, '%Y%m%d') - timedelta(days=7 + 1)).strftime('%Y%m%d')
    if country == 'KR':
        sql = f'select map.date as date, a.date as working_day, ' \
              f'        a.stock_cd, a.stock_nm, a.close_price ' \
              f'from date_working_day_mapping as map ' \
              f'join (select date, stock_cd, stock_nm, close_price ' \
              f'      from stock_daily_technical ' \
              f'      where 1=1 ' \
              f'      and date >= {price_begin_date} ' \
              f'      and stock_cd = "{stock_cd}" ' \
              f'      ' \
              f'      union all ' \
              f'      ' \
              f'      select date, stock_cd, stock_nm, close_price ' \
              f'      from stock_daily_etf ' \
              f'      where 1=1 ' \
              f'      and date >= {price_begin_date} ' \
              f'      and stock_cd = "{stock_cd}" ' \
              f'      ' \
              f'      union all ' \
              f'      ' \
              f'      select date, stock_cd, stock_nm, close_price ' \
              f'      from stock_daily_etn ' \
              f'      where 1=1 ' \
              f'      and date >= {price_begin_date} ' \
              f'      and stock_cd = "{stock_cd}" ) as a ' \
              f'    on map.working_day = a.date '
        price_data = get_df_from_db(sql)
    else:
        sql = f'select map.date as date, a.date as working_day, ' \
              f'        a.stock_cd, b.stock_nm, a.close_price ' \
              f'from us_date_working_day_mapping as map ' \
              f'join (select date, stock_cd, close_price ' \
              f'      from us_stock_daily_price ' \
              f'      where 1=1 ' \
              f'      and date >= {price_begin_date} ' \
              f'      and stock_cd = "{stock_cd}") as a ' \
              f'    on map.working_day = a.date ' \
              f'join (select stock_cd, stock_nm' \
              f'      from us_stock_info ' \
              f'      where stock_cd = "{stock_cd}") as b' \
              f'    on a.stock_cd = b.stock_cd '
        price_data = get_df_from_db(sql)

    # 해당 stock_cd에 대해 데이터가 존재하지 않을 경우 None 리턴하고 끝냄
    if price_data.shape[0] == 0:
        # print('price_data.shape[0] == 0')
        return None

    # date 컬럼 타입 변경
    price_data['date'] = price_data['date'].apply(lambda x: str(x))

    # 신규 컬럼 생성
    price_data['price_prev_1w'] = price_data.groupby('stock_cd')['close_price'].shift(7)

    # date_list 생성
    date_span = (datetime.strptime(end_date, '%Y%m%d') - datetime.strptime(begin_date, '%Y%m%d')).days
    date_list = [(datetime.strptime(begin_date, '%Y%m%d') + timedelta(days=i)).strftime('%Y%m%d') for i in
                 range(date_span + 1)]

    # new_portfolio, prev_portfolio 생성
    new_portfolio = prev_portfolio.copy()
    prev_row = prev_portfolio.copy()

    if prev_row.shape[0] == 0:
        tr_log = trading_data.loc[trading_data['date'] == begin_date, :]
        if tr_log.shape[0] != 0:
            tmp_stock_nm = tr_log['stock_nm'].values[0]
            tmp_unit_currency = tr_log['unit_currency'].values[0]
            tmp_country = tr_log['country'].values[0]
        else:
            tmp_stock_nm = ''
            if country == 'KR':
                tmp_unit_currency = 'KRW'
                tmp_country = 'KR'
            else:
                tmp_unit_currency = 'USD'
                tmp_country = 'US'
        tmp_df = pd.DataFrame([[user_code, prev_date, account_number, stock_cd, securities_code, tmp_stock_nm, 0, 0, 0,
                                0, 0, None, 0, 0, 0, 0, tmp_unit_currency, 0, tmp_country]])
        tmp_df.columns = prev_row.columns
        prev_row = tmp_df

    # 거래내역 목록 정의
    receiving_transaction_list = get_receiving_transaction_list()
    releasing_transaction_list = get_releasing_transaction_list()
    dividend_transaction_list = get_dividend_transaction_list()  # 배당세 출금은 2021.06.23 현재 거래내역이 사실상 존재하지 않아 어떻게 처리될지 모른다.

    # portfolio 생성
    for date in date_list:
        new_row = prev_row.copy()
        tr_log = trading_data.loc[trading_data['date'] == date, :]
        price = price_data.loc[price_data['date'] == date, :]

        # new_purchase_amount, realized_profit_loss, purchase_amount_of_stocks_to_sell 초기화
        new_row['new_purchase_amount'] = 0
        new_row['realized_profit_loss'] = 0
        new_row['purchase_amount_of_stocks_to_sell'] = 0

        # date update
        new_row['date'] = date

        # close_price, prev_1w_close_price, stock_nm update
        if price.shape[0] != 0:
            new_row['close_price'] = price['close_price'].values[0]
            new_row['prev_1w_close_price'] = price['price_prev_1w'].values[0]
            new_row['stock_nm'] = price['stock_nm'].values[0]

        # retention_period update
        if new_row['first_purchase_date'].values[0] is not None:
            new_row['retention_period'] = new_row['retention_period'].values[0] + 1

        # update_dtim update
        new_row['update_dtim'] = datetime.today().strftime('%Y%m%d%H%M%S')

        # 매매기록이 있을 경우 데이터 업데이트
        for i, r in tr_log.iterrows():
            tmp_row = new_row.copy()

            # stock_nm update
            new_row['stock_nm'] = r['stock_nm']

            # 매도거래내역의 경우, 기존 holding quantity가 충분한지 확인
            if r['transaction_type'] in releasing_transaction_list:
                tmp_holding_quantity = tmp_row['holding_quantity'].values[0]
                if tmp_holding_quantity == 0:  # 매도할 내역 없으면 패스
                    continue
                elif tmp_holding_quantity - r['transaction_quantity'] < 0:  # 매도할 내역 부족하면 거래내역을 줄여준다.
                    r['transaction_fee'] = r['transaction_fee'] * (
                                tmp_holding_quantity / r['transaction_quantity'])  # 비율 맞춰 처리해줌
                    r['transaction_tax'] = r['transaction_tax'] * (tmp_holding_quantity / r['transaction_quantity'])
                    r['transaction_quantity'] = tmp_holding_quantity

            # holding_quantity update
            if r['transaction_type'] in receiving_transaction_list:
                new_row['holding_quantity'] = tmp_row['holding_quantity'] + r['transaction_quantity']
            elif r['transaction_type'] in releasing_transaction_list:
                new_row['holding_quantity'] = tmp_row['holding_quantity'] - r['transaction_quantity']
            elif r['transaction_type'] in dividend_transaction_list:
                pass
            elif r['transaction_type'] == '주식합병출고':
                # 주식합병출고 거래내역이 있으면, 해당 거래내역이 존재하는 날부터 포트폴리오에 포함되지 않도록 보유수량을 0으로 바꿔줌
                new_row['holding_quantity'] = 0
            elif r['transaction_type'] == '주식합병입고':
                new_row['holding_quantity'] = tmp_row['holding_quantity'] + r['transaction_quantity']
            else:
                raise Exception

            # avg_purchase_price update
            if r['transaction_type'] in receiving_transaction_list:
                # (기존 매입금액 + 신규 매입금액 + 수수료/세금) / (기존 매입주수 + 신규 매입주수)
                new_row['avg_purchase_price'] = \
                    ((tmp_row['avg_purchase_price'] * tmp_row['holding_quantity']) +
                     (r['transaction_quantity'] * r['transaction_unit_price']) +
                     (r['transaction_fee'] + r['transaction_tax'])) / \
                    (tmp_row['holding_quantity'] + r['transaction_quantity'])
            elif r['transaction_type'] == '주식합병입고':
                # 피합병 종목의 거래내역을 가지고 와서 평균매입단가, 최초매입일자, 보유기간을 계산한다.
                # 같은 날 주식합병출고된 종목 = 피합병종목으로 본다.
                # 2영업일 이전 날짜 구하기(주식합병출고는 2영업일 이전 처리되고, 입고는 당일처리되므로, 2영업일 전 날짜로 검색해야함)
                pulled_transaction_date = util_get_pulled_transaction_date(date)

                # 주식합병출고 확인
                sql = f'select * ' \
                      f'from user_trading_log ' \
                      f'where 1=1 ' \
                      f'and user_code = {user_code} ' \
                      f'and account_number = "{account_number}" ' \
                      f'and date = {pulled_transaction_date} ' \
                      f'and transaction_type = "주식합병출고" ' \
                      f'and stock_type in ("domestic_stock", "domestic_etf", "domestic_etn", "us_stock")'
                merged_company = get_df_from_db(sql)
                # print(merged_company)
                # 같은 날 주식합병출고된 종목이 1개가 아닐 경우, 에러를 뱉는다.
                if merged_company.shape[0] != 1:
                    raise Exception

                # 종목코드 추출
                merged_stock_cd = merged_company['stock_cd'].values[0]

                sql = f'select * ' \
                      f'from user_trading_log ' \
                      f'where 1=1 ' \
                      f'and user_code = {user_code} ' \
                      f'and account_number = "{account_number}" ' \
                      f'and stock_cd = "{merged_stock_cd}" ' \
                      f'and stock_type in ("domestic_stock", "domestic_etf", "domestic_etn", "us_stock")'
                merged_corp_tr_log = get_df_from_db(sql)
                # print(merged_corp_tr_log)

                mc_holding_quantity = 0
                mc_avg_purchase_price = 0
                mc_first_purchase_date = None
                for j, mc_tr in merged_corp_tr_log.iterrows():
                    # print(mc_tr)

                    if mc_holding_quantity == 0 and \
                            mc_tr['transaction_type'] in receiving_transaction_list:
                        mc_first_purchase_date = mc_tr['date']

                    if mc_tr['transaction_type'] in receiving_transaction_list:
                        mc_avg_purchase_price = ((mc_avg_purchase_price * mc_holding_quantity) +
                                                 (mc_tr['transaction_unit_price'] * mc_tr['transaction_quantity']) +
                                                 mc_tr['transaction_fee'] + mc_tr['transaction_tax']) / \
                                                (mc_holding_quantity + mc_tr['transaction_quantity'])
                        mc_holding_quantity = mc_holding_quantity + mc_tr['transaction_quantity']
                    elif mc_tr['transaction_type'] in releasing_transaction_list:
                        mc_holding_quantity = mc_holding_quantity - mc_tr['transaction_quantity']

                    if mc_holding_quantity <= 0:
                        mc_holding_quantity = 0
                        mc_avg_purchase_price = 0
                        mc_first_purchase_date = None

                # 최초매입일자가 None이면 합병일자를 넣어준다.
                if mc_first_purchase_date is None:
                    mc_first_purchase_date = date
                # 피합병 holding_quantity와 mc_holding_quantity가 동일하면 계산한 값을 사용한다.
                if mc_holding_quantity == merged_company['transaction_quantity'].values[0]:
                    new_row['first_purchase_date'] = mc_first_purchase_date
                    new_row['retention_period'] = \
                        (datetime.strptime(date, '%Y%m%d') - datetime.strptime(mc_first_purchase_date, '%Y%m%d')).days + 1
                    new_row['avg_purchase_price'] = (mc_avg_purchase_price * mc_holding_quantity) / r['transaction_quantity']
                else:
                    new_row['first_purchase_date'] = mc_first_purchase_date
                    new_row['retention_period'] = 1
                    new_row['avg_purchase_price'] = r['transaction_unit_price']

            # first_purchase_date / retention_period update
            if new_row['first_purchase_date'].values[0] is None and r['transaction_type'] in receiving_transaction_list:
                new_row['first_purchase_date'] = date
                new_row['retention_period'] = 1

            # new_purchase_amount update
            if r['transaction_type'] in receiving_transaction_list:
                new_row['new_purchase_amount'] = tmp_row['new_purchase_amount'] + \
                                                 (r['transaction_quantity'] * r['transaction_unit_price']) + \
                                                 (r['transaction_fee'] + r['transaction_tax'])

            # realized_profit_loss update
            if r['transaction_type'] in (releasing_transaction_list + dividend_transaction_list):
                new_row['realized_profit_loss'] = \
                    tmp_row['realized_profit_loss'] + (r['transaction_quantity'] * r['transaction_unit_price']) - \
                    (r['transaction_fee'] + r['transaction_tax'])

            # purchase_amount_of_stocks_to_sell
            if r['transaction_type'] in releasing_transaction_list:
                new_row['purchase_amount_of_stocks_to_sell'] = \
                    tmp_row['purchase_amount_of_stocks_to_sell'] + \
                    (r['transaction_quantity'] * tmp_row['avg_purchase_price'])

            # 청약 케이스: close_price 설정
            if new_row['close_price'].values[0] == 0:
                new_row['close_price'] = r['transaction_unit_price']

        # total_value update
        new_row['total_value'] = new_row['holding_quantity'].values[0] * new_row['close_price'].values[0]

        # portfolio 상에서 종목 보유 내역이 0 이하일 경우, 0으로 바꿔줌.
        if new_row['holding_quantity'].values[0] <= 0:
            new_row['holding_quantity'] = 0

        # 종목 보유량이 0이고, 실현 손익도 없다면 portfolio에 저장하지 않음.
        if new_row['holding_quantity'].values[0] == 0 and new_row['realized_profit_loss'].values[0] == 0:
            new_row['first_purchase_date'] = None
            pass
        else:
            new_portfolio = pd.concat([new_portfolio, new_row])

        # prev_row update
        prev_row = new_row

    # portfolio 데이터 업데이트
    # print(f'update_single_stock_portfolio - new_portfolio: {new_portfolio}')
    insert_data(new_portfolio, user_portfolio_table)
    # print('Done')

def update_single_stock_portfolio_old(user_code, begin_date, account_number, securities_code, stock_cd,
                                  country=None, tmp_portfolio=False):
    # print(f'update_single_stock_portfolio - user_code: {user_code}, begin_date: {begin_date}, '
    #       f'account_number: {account_number}, securities_code: {securities_code}, stock_cd: {stock_cd}, '
    #       f'country: {country}')

    # user_portfolio, user_trading_log table 설정
    if tmp_portfolio:
        user_portfolio_table = 'tmp_user_portfolio'
    else:
        user_portfolio_table = 'user_portfolio'

    # begin_date
    begin_date = str(begin_date)

    # country 설정
    if country is None:
        country = get_country(stock_cd)
    # print(f'country: {country}')

    # end_date 설정
    if country == 'KR':
        end_date = exec_query(f'select max(working_day) from date_working_day')[0][0]
    else:
        end_date = exec_query(f'select max(working_day) from us_date_working_day')[0][0]
    end_date = str(end_date)

    # begin_date가 end_date보다 크다면 함수 실행 종료
    if end_date < begin_date:
        # print('end_date < begin_date')
        return None

    # prev_date 설정
    prev_date = (datetime.strptime(begin_date, '%Y%m%d') - timedelta(days=1)).strftime('%Y%m%d')

    # 겹치는 구간 portfolio 삭제
    exec_query(f'delete '
               f'from {user_portfolio_table} '
               f'where user_code = {user_code} '
               f'and account_number = "{account_number}" '
               f'and securities_code = "{securities_code}" '
               f'and stock_cd = "{stock_cd}" '
               f'and date >= "{begin_date}" '
               f'and date <= "{end_date}" ')

    # 전일 포트폴리오 가져오기
    sql = f'select * ' \
          f'from {user_portfolio_table} ' \
          f'where 1=1 ' \
          f'and user_code = {user_code} ' \
          f'and date = {prev_date} ' \
          f'and account_number = "{account_number}" ' \
          f'and stock_cd = "{stock_cd}" '
    prev_portfolio = get_df_from_db(sql)

    # 거래내역 가져오기
    sql = f'select * ' \
          f'from user_trading_log ' \
          f'where 1=1 ' \
          f'and user_code = {user_code} ' \
          f'and account_number = "{account_number}" ' \
          f'and date >= "{begin_date}" ' \
          f'and stock_cd = "{stock_cd}" ' \
          f'and stock_type in ("domestic_stock", "domestic_etf", "domestic_etn", "us_stock")'
    trading_data = get_df_from_db(sql)

    # 가격 가져오기
    price_begin_date = (datetime.strptime(prev_date, '%Y%m%d') - timedelta(days=7 + 1)).strftime('%Y%m%d')
    if country == 'KR':
        sql = f'select map.date as date, a.date as working_day, ' \
              f'        a.stock_cd, a.stock_nm, a.close_price ' \
              f'from date_working_day_mapping as map ' \
              f'join (select date, stock_cd, stock_nm, close_price ' \
              f'      from stock_daily_technical ' \
              f'      where 1=1 ' \
              f'      and date >= {price_begin_date} ' \
              f'      and stock_cd = "{stock_cd}" ' \
              f'      ' \
              f'      union all ' \
              f'      ' \
              f'      select date, stock_cd, stock_nm, close_price ' \
              f'      from stock_daily_etf ' \
              f'      where 1=1 ' \
              f'      and date >= {price_begin_date} ' \
              f'      and stock_cd = "{stock_cd}" ' \
              f'      ' \
              f'      union all ' \
              f'      ' \
              f'      select date, stock_cd, stock_nm, close_price ' \
              f'      from stock_daily_etn ' \
              f'      where 1=1 ' \
              f'      and date >= {price_begin_date} ' \
              f'      and stock_cd = "{stock_cd}" ) as a ' \
              f'    on map.working_day = a.date '
        price_data = get_df_from_db(sql)
    else:
        sql = f'select map.date as date, a.date as working_day, ' \
              f'        a.stock_cd, b.stock_nm, a.close_price ' \
              f'from us_date_working_day_mapping as map ' \
              f'join (select date, stock_cd, close_price ' \
              f'      from us_stock_daily_price ' \
              f'      where 1=1 ' \
              f'      and date >= {price_begin_date} ' \
              f'      and stock_cd = "{stock_cd}") as a ' \
              f'    on map.working_day = a.date ' \
              f'join (select stock_cd, stock_nm' \
              f'      from us_stock_info ' \
              f'      where stock_cd = "{stock_cd}") as b' \
              f'    on a.stock_cd = b.stock_cd '
        price_data = get_df_from_db(sql)

    # 해당 stock_cd에 대해 데이터가 존재하지 않을 경우 None 리턴하고 끝냄
    if price_data.shape[0] == 0:
        # print('price_data.shape[0] == 0')
        return None

    # date 컬럼 타입 변경
    price_data['date'] = price_data['date'].apply(lambda x: str(x))

    # 신규 컬럼 생성
    price_data['price_prev_1w'] = price_data.groupby('stock_cd')['close_price'].shift(7)

    # date_list 생성
    date_span = (datetime.strptime(end_date, '%Y%m%d') - datetime.strptime(begin_date, '%Y%m%d')).days
    date_list = [(datetime.strptime(begin_date, '%Y%m%d') + timedelta(days=i)).strftime('%Y%m%d') for i in
                 range(date_span + 1)]

    # new_portfolio, prev_portfolio 생성
    new_portfolio = prev_portfolio.copy()
    prev_row = prev_portfolio.copy()

    if prev_row.shape[0] == 0:
        tr_log = trading_data.loc[trading_data['date'] == begin_date, :]
        if tr_log.shape[0] != 0:
            tmp_stock_nm = tr_log['stock_nm'].values[0]
            tmp_unit_currency = tr_log['unit_currency'].values[0]
            tmp_country = tr_log['country'].values[0]
        else:
            tmp_stock_nm = ''
            if country == 'KR':
                tmp_unit_currency = 'KRW'
                tmp_country = 'KR'
            else:
                tmp_unit_currency = 'USD'
                tmp_country = 'US'
        tmp_df = pd.DataFrame([[user_code, prev_date, account_number, stock_cd, securities_code, tmp_stock_nm, 0, 0, 0,
                                0, 0, None, 0, 0, 0, 0, tmp_unit_currency, 0, tmp_country]])
        tmp_df.columns = prev_row.columns
        prev_row = tmp_df

    # portfolio 생성
    for date in date_list:
        new_row = prev_row.copy()
        tr_log = trading_data.loc[trading_data['date'] == date, :]
        price = price_data.loc[price_data['date'] == date, :]

        # new_purchase_amount, realized_profit_loss, purchase_amount_of_stocks_to_sell 초기화
        new_row['new_purchase_amount'] = 0
        new_row['realized_profit_loss'] = 0
        new_row['purchase_amount_of_stocks_to_sell'] = 0

        # date update
        new_row['date'] = date

        # close_price, prev_1w_close_price, stock_nm update
        if price.shape[0] != 0:
            new_row['close_price'] = price['close_price'].values[0]
            new_row['prev_1w_close_price'] = price['price_prev_1w'].values[0]
            new_row['stock_nm'] = price['stock_nm'].values[0]

        # retention_period update
        if new_row['first_purchase_date'].values[0] is not None:
            new_row['retention_period'] = new_row['retention_period'].values[0] + 1

        # update_dtim update
        new_row['update_dtim'] = datetime.today().strftime('%Y%m%d%H%M%S')

        receiving_transaction_list = get_receiving_transaction_list()
        releasing_transaction_list = get_releasing_transaction_list()
        dividend_transaction_list = get_dividend_transaction_list()  # 배당세 출금은 2021.06.23 현재 거래내역이 사실상 존재하지 않아 어떻게 처리될지 모른다.

        # 매매기록이 있을 경우 데이터 업데이트
        for i, r in tr_log.iterrows():
            tmp_row = new_row.copy()

            # stock_nm update
            new_row['stock_nm'] = r['stock_nm']

            # 매도거래내역의 경우, 기존 holding quantity가 충분한지 확인
            if r['transaction_type'] in releasing_transaction_list:
                tmp_holding_quantity = tmp_row['holding_quantity'].values[0]
                if tmp_holding_quantity == 0:  # 매도할 내역 없으면 패스
                    continue
                elif tmp_holding_quantity - r['transaction_quantity'] < 0:  # 매도할 내역 부족하면 거래내역을 줄여준다.
                    r['transaction_fee'] = r['transaction_fee'] * (
                                tmp_holding_quantity / r['transaction_quantity'])  # 비율 맞춰 처리해줌
                    r['transaction_tax'] = r['transaction_tax'] * (tmp_holding_quantity / r['transaction_quantity'])
                    r['transaction_quantity'] = tmp_holding_quantity

            # holding_quantity update
            if r['transaction_type'] in receiving_transaction_list:
                new_row['holding_quantity'] = tmp_row['holding_quantity'] + r['transaction_quantity']
            elif r['transaction_type'] in releasing_transaction_list:
                new_row['holding_quantity'] = tmp_row['holding_quantity'] - r['transaction_quantity']
            elif r['transaction_type'] in dividend_transaction_list:
                pass
            elif r['transaction_type'] == '주식합병출고':
                # 주식합병출고 거래내역이 있으면, 해당 거래내역이 존재하는 날부터 포트폴리오에 포함되지 않도록 보유수량을 0으로 바꿔줌
                new_row['holding_quantity'] = 0
            elif r['transaction_type'] == '주식합병입고':
                new_row['holding_quantity'] = tmp_row['holding_quantity'] + r['transaction_quantity']
            else:
                raise Exception

            # avg_purchase_price update
            if r['transaction_type'] in receiving_transaction_list:
                # (기존 매입금액 + 신규 매입금액 + 수수료/세금) / (기존 매입주수 + 신규 매입주수)
                new_row['avg_purchase_price'] = \
                    ((tmp_row['avg_purchase_price'] * tmp_row['holding_quantity']) +
                     (r['transaction_quantity'] * r['transaction_unit_price']) +
                     (r['transaction_fee'] + r['transaction_tax'])) / \
                    (tmp_row['holding_quantity'] + r['transaction_quantity'])
            elif r['transaction_type'] == '주식합병입고':
                # 피합병 종목의 거래내역을 가지고 와서 평균매입단가, 최초매입일자, 보유기간을 계산한다.
                # 같은 날 주식합병출고된 종목 = 피합병종목으로 본다.
                sql = f'select * ' \
                      f'from user_trading_log ' \
                      f'where 1=1 ' \
                      f'and user_code = {user_code} ' \
                      f'and account_number = "{account_number}" ' \
                      f'and date = {date} ' \
                      f'and transaction_type = "주식합병출고" ' \
                      f'and stock_type in ("domestic_stock", "domestic_etf", "domestic_etn", "us_stock")'
                merged_company = get_df_from_db(sql)
                # print(merged_company)
                # 같은 날 주식합병출고된 종목이 여러개일 경우, 에러를 뱉는다.
                if merged_company.shape[0] > 1:
                    raise Exception

                # 종목코드 추출
                merged_stock_cd = merged_company['stock_cd'].values[0]

                sql = f'select * ' \
                      f'from user_trading_log ' \
                      f'where 1=1 ' \
                      f'and user_code = {user_code} ' \
                      f'and account_number = "{account_number}" ' \
                      f'and stock_cd = "{merged_stock_cd}" ' \
                      f'and stock_type in ("domestic_stock", "domestic_etf", "domestic_etn", "us_stock")'
                merged_corp_tr_log = get_df_from_db(sql)
                # print(merged_corp_tr_log)

                mc_holding_quantity = 0
                mc_avg_purchase_price = 0
                mc_first_purchase_date = None
                for j, mc_tr in merged_corp_tr_log.iterrows():
                    # print(mc_tr)

                    if mc_holding_quantity == 0 and \
                            mc_tr['transaction_type'] in receiving_transaction_list:
                        mc_first_purchase_date = mc_tr['date']

                    if mc_tr['transaction_type'] in receiving_transaction_list:
                        mc_avg_purchase_price = ((mc_avg_purchase_price * mc_holding_quantity) +
                                                 (mc_tr['transaction_unit_price'] * mc_tr['transaction_quantity']) +
                                                 mc_tr['transaction_fee'] + mc_tr['transaction_tax']) / \
                                                (mc_holding_quantity + mc_tr['transaction_quantity'])
                        mc_holding_quantity = mc_holding_quantity + mc_tr['transaction_quantity']
                    elif mc_tr['transaction_type'] in releasing_transaction_list:
                        mc_holding_quantity = mc_holding_quantity - mc_tr['transaction_quantity']

                    if mc_holding_quantity <= 0:
                        mc_holding_quantity = 0
                        mc_avg_purchase_price = 0
                        mc_first_purchase_date = None

                # 최초매입일자가 None이면 합병일자를 넣어준다.
                if mc_first_purchase_date is None:
                    mc_first_purchase_date = date
                # 피합병 holding_quantity와 mc_holding_quantity가 동일하면 계산한 값을 사용한다.
                if mc_holding_quantity == merged_company['transaction_quantity'].values[0]:
                    new_row['first_purchase_date'] = mc_first_purchase_date
                    new_row['retention_period'] = \
                        (datetime.strptime(date, '%Y%m%d') - datetime.strptime(mc_first_purchase_date, '%Y%m%d')).days + 1
                    new_row['avg_purchase_price'] = (mc_avg_purchase_price * mc_holding_quantity) / r['transaction_quantity']
                else:
                    new_row['first_purchase_date'] = mc_first_purchase_date
                    new_row['retention_period'] = 1
                    new_row['avg_purchase_price'] = r['transaction_unit_price']

            # first_purchase_date / retention_period update
            if new_row['first_purchase_date'].values[0] is None and r['transaction_type'] in receiving_transaction_list:
                new_row['first_purchase_date'] = date
                new_row['retention_period'] = 1

            # new_purchase_amount update
            if r['transaction_type'] in receiving_transaction_list:
                new_row['new_purchase_amount'] = tmp_row['new_purchase_amount'] + \
                                                 (r['transaction_quantity'] * r['transaction_unit_price']) + \
                                                 (r['transaction_fee'] + r['transaction_tax'])

            # realized_profit_loss update
            if r['transaction_type'] in (releasing_transaction_list + dividend_transaction_list):
                new_row['realized_profit_loss'] = \
                    tmp_row['realized_profit_loss'] + (r['transaction_quantity'] * r['transaction_unit_price']) - \
                    (r['transaction_fee'] + r['transaction_tax'])

            # purchase_amount_of_stocks_to_sell
            if r['transaction_type'] in releasing_transaction_list:
                new_row['purchase_amount_of_stocks_to_sell'] = \
                    tmp_row['purchase_amount_of_stocks_to_sell'] + \
                    (r['transaction_quantity'] * tmp_row['avg_purchase_price'])

            # 청약 케이스: close_price 설정
            if new_row['close_price'].values[0] == 0:
                new_row['close_price'] = r['transaction_unit_price']

        # total_value update
        new_row['total_value'] = new_row['holding_quantity'].values[0] * new_row['close_price'].values[0]

        # portfolio 상에서 종목 보유 내역이 0 이하일 경우, 0으로 바꿔줌.
        if new_row['holding_quantity'].values[0] <= 0:
            new_row['holding_quantity'] = 0

        # 종목 보유량이 0이고, 실현 손익도 없다면 portfolio에 저장하지 않음.
        if new_row['holding_quantity'].values[0] == 0 and new_row['realized_profit_loss'].values[0] == 0:
            new_row['first_purchase_date'] = None
            pass
        else:
            new_portfolio = pd.concat([new_portfolio, new_row])

        # prev_row update
        prev_row = new_row

    # portfolio 데이터 업데이트
    # print(f'update_single_stock_portfolio - new_portfolio: {new_portfolio}')
    insert_data(new_portfolio, user_portfolio_table)
    # print('Done')

from sqlalchemy import create_engine, Column, Integer, String, Float, DECIMAL
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import time
from contextlib import contextmanager
from config.config_manager import get_config

# sqlalchemy 설정
engine = create_engine(f"mysql+pymysql://{get_config()['user']}:{get_config()['pwd']}@{get_config()['url']}:{get_config()['port']}/sauvignon" \
                       f'?autocommit=true&charset=utf8mb4')

Session = sessionmaker(bind=engine)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


class UserSecuritiesInfo(Base):
    __tablename__ = 'user_securities_info'

    user_code = Column(Integer, primary_key=True)
    securities_code = Column(String, nullable=True)
    securities_id = Column(String, nullable=True)
    securities_pw = Column(String, nullable=True)
    valid_flag = Column(Integer, nullable=True)
    message = Column(String, nullable=True)
    lst_update_dtim = Column(String, nullable=True)

    def __init__(self, user_code, securities_code=None, securities_id=None, securities_pw=None, valid_flag=None,
                 message=None, lst_update_dtim=time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))):
        self.user_code = user_code
        self.securities_code = securities_code
        self.securities_id = securities_id
        self.securities_pw = securities_pw
        self.valid_flag = valid_flag
        self.message = message
        self.lst_update_dtim = lst_update_dtim


class UserTradingLog(Base):
    __tablename__ = 'user_trading_log'

    user_code = Column(Integer, primary_key=True)
    begin_date = Column(String, primary_key=True)
    end_date = Column(String, primary_key=True)
    account_number = Column(String, primary_key=True)
    stock_cd = Column(String, primary_key=True)
    seq = Column(Integer, primary_key=True)
    stock_type = Column(String, nullable=True)
    securities_code = Column(String, nullable=False)
    stock_nm = Column(String, nullable=True)
    holding_quantity = Column(Float, nullable=True)
    avg_purchase_price = Column(Float, nullable=True)
    transaction_type = Column(String, nullable=True)
    transaction_detail_type = Column(String, nullable=True)
    transaction_quantity = Column(Float, nullable=True)
    transaction_unit_price = Column(Float, nullable=True)
    transaction_fee = Column(Float, nullable=True)
    transaction_tax = Column(Float, nullable=True)
    unit_currency = Column(String, nullable=True)
    update_dtim = Column(String, nullable=True)
    country = Column(String, nullable=True)

    def __init__(self, user_code, begin_date, end_date, account_number, stock_cd, seq, stock_type, securities_code,
                 stock_nm=None, holding_quantity=None, avg_purchase_price=None, transaction_type=None,
                 transaction_detail_type=None, transaction_quantity=None, transaction_unit_price=None,
                 transaction_fee=None, transaction_tax=None, unit_currency=None, update_dtim=None, country=None):
        self.user_code = user_code
        self.begin_date = begin_date
        self.end_date = end_date
        self.account_number = account_number
        self.stock_cd = stock_cd
        self.seq = seq
        self.stock_type = stock_type
        self.securities_code = securities_code
        self.stock_nm = stock_nm
        self.holding_quantity = holding_quantity
        self.avg_purchase_price = avg_purchase_price
        self.transaction_type = transaction_type
        self.transaction_detail_type = transaction_detail_type
        self.transaction_quantity = transaction_quantity
        self.transaction_unit_price = transaction_unit_price
        self.transaction_fee = transaction_fee
        self.transaction_tax = transaction_tax
        self.unit_currency = unit_currency
        self.update_dtim = update_dtim
        self.country = country


class UserPortfolio(Base):
    __tablename__ = 'user_portfolio'

    user_code = Column(Integer, primary_key=True)
    date = Column(Integer, primary_key=True)
    account_number = Column(String, primary_key=True)
    stock_cd = Column(String, primary_key=True)
    securities_code = Column(String, nullable=False)
    stock_nm = Column(String, nullable=True)
    holding_quantity = Column(Float, nullable=True)
    avg_purchase_price = Column(Float, nullable=True)
    close_price = Column(Float, nullable=True)
    prev_1w_close_price = Column(Float, nullable=True)
    total_value = Column(Float, nullable=True)
    first_purchase_date = Column(String, nullable=True)
    retention_period = Column(Integer, nullable=True)
    new_purchase_amount = Column(Float, nullable=True)
    realized_profit_loss = Column(Float, nullable=True)
    purchase_amount_of_stocks_to_sell = Column(Float, nullable=True)
    unit_currency = Column(String, nullable=True)
    update_dtim = Column(String, nullable=True)

    def __init__(self, user_code, date, account_number, stock_cd, securities_code,
                 stock_nm=None, holding_quantity=None, avg_purchase_price=None, prev_close_price=None,
                 prev_1w_close_price=None, total_value=None, first_purchase_date=None, retention_period=None,
                 new_purchase_amount=None, realized_profit_loss=None, purchase_amount_of_stocks_to_sell=None,
                 unit_currency=None, update_dtim=None):
        self.user_code = user_code
        self.date = date
        self.account_number = account_number
        self.stock_cd = stock_cd
        self.securities_code = securities_code
        self.stock_nm = stock_nm
        self.holding_quantity = holding_quantity
        self.avg_purchase_price = avg_purchase_price
        self.prev_close_price = prev_close_price
        self.prev_1w_close_price = prev_1w_close_price
        self.total_value = total_value
        self.first_purchase_date = first_purchase_date
        self.retention_period = retention_period
        self.new_purchase_amount = new_purchase_amount
        self.realized_profit_loss = realized_profit_loss
        self.purchase_amount_of_stocks_to_sell = purchase_amount_of_stocks_to_sell
        self.unit_currency = unit_currency
        self.update_dtim = update_dtim


class StockDailyTechnical(Base):
    __tablename__ = 'stock_daily_technical'

    date = Column(String, primary_key=True)
    stock_cd = Column(String, primary_key=True)
    stock_nm = Column(String, nullable=True)
    open_price = Column(Integer, nullable=True)
    high_price = Column(Integer, nullable=True)
    low_price = Column(Integer, nullable=True)
    close_price = Column(Integer, nullable=True)
    trading_volume = Column(Integer, nullable=True)
    transaction_amount = Column(Integer, nullable=True)
    market_capitalization = Column(Integer, nullable=True)
    share_of_market_cap = Column(Float, nullable=True)
    num_of_listed_stocks = Column(Integer, nullable=True)
    foreign_own_quantity = Column(Integer, nullable=True)
    share_of_foreign_own = Column(Float, nullable=True)

    def __init__(self, date, stock_cd, stock_nm, open_price, high_price, low_price, close_price,
                 trading_volume, transaction_amount, market_capitalization, share_of_market_cap,
                 num_of_listed_stocks, foreign_own_quantity, share_of_foreign_own):
        self.date = date
        self.stock_cd = stock_cd
        self.stock_nm = stock_nm
        self.open_price = open_price
        self.high_price = high_price
        self.low_price = low_price
        self.close_price = close_price
        self.trading_volume = trading_volume
        self.transaction_amount = transaction_amount
        self.market_capitalization = market_capitalization
        self.share_of_market_cap = share_of_market_cap
        self.num_of_listed_stocks = num_of_listed_stocks
        self.foreign_own_quantity = foreign_own_quantity
        self.share_of_foreign_own = share_of_foreign_own


class StockDailyEtf(Base):
    __tablename__ = 'stock_daily_etf'

    date = Column(String, primary_key=True)
    stock_cd = Column(String, primary_key=True)
    stock_nm = Column(String, nullable=True)
    open_price = Column(Integer, nullable=True)
    high_price = Column(Integer, nullable=True)
    low_price = Column(Integer, nullable=True)
    close_price = Column(Integer, nullable=True)
    trading_volume = Column(Integer, nullable=True)
    transaction_amount = Column(Integer, nullable=True)
    nav = Column(Integer, nullable=True)
    base_index_nm = Column(String, nullable=True)
    base_index = Column(Float, nullable=True)

    def __init__(self, date, stock_cd, stock_nm, open_price, high_price, low_price, close_price,
                 trading_volume, transaction_amount, nav, base_index_nm, base_index):
        self.date = date
        self.stock_cd = stock_cd
        self.stock_nm = stock_nm
        self.open_price = open_price
        self.high_price = high_price
        self.low_price = low_price
        self.close_price = close_price
        self.trading_volume = trading_volume
        self.transaction_amount = transaction_amount
        self.nav = nav
        self.base_index_nm = base_index_nm
        self.base_index = base_index


class StockDailyEtn(Base):
    __tablename__ = 'stock_daily_etn'

    date = Column(String, primary_key=True)
    isin_cd = Column(String, primary_key=True)
    stock_cd = Column(String, primary_key=True)
    stock_nm = Column(String, nullable=True)
    open_price = Column(Integer, nullable=True)
    high_price = Column(Integer, nullable=True)
    low_price = Column(Integer, nullable=True)
    close_price = Column(Integer, nullable=True)
    trading_volume = Column(Integer, nullable=True)
    transaction_amount = Column(Integer, nullable=True)
    iv = Column(Integer, nullable=True)
    base_index = Column(Float, nullable=True)

    def __init__(self, date, isin_cd, stock_cd, stock_nm, open_price, high_price, low_price, close_price,
                 trading_volume, transaction_amount, iv, base_index):
        self.date = date
        self.isin_cd = isin_cd
        self.stock_cd = stock_cd
        self.stock_nm = stock_nm
        self.open_price = open_price
        self.high_price = high_price
        self.low_price = low_price
        self.close_price = close_price
        self.trading_volume = trading_volume
        self.transaction_amount = transaction_amount
        self.iv = iv
        self.base_index = base_index


class DartFinancialStatements(Base):
    __tablename__ = 'dart_financial_statements'

    stock_cd = Column(String, primary_key=True)
    quarter = Column(String, primary_key=True)
    first_rcept_date = Column(String, primary_key=True)
    rcept_date = Column(String, nullable=False)
    next_first_rcept_date = Column(String, nullable=False)
    base_currency = Column(String, nullable=False)
    current_assets = Column(Integer, nullable=True)
    cash_and_cash_equivalents = Column(Integer, nullable=True)
    short_term_trade_receivable = Column(Integer, nullable=True)
    noncurrent_assets = Column(Integer, nullable=True)
    property_plant_and_equipment = Column(Integer, nullable=True)
    intangible_assets = Column(Integer, nullable=True)
    assets = Column(Integer, nullable=True)
    current_liabilities = Column(Integer, nullable=True)
    shortterm_borrowings = Column(Integer, nullable=True)
    noncurrent_liabilities = Column(Integer, nullable=True)
    long_term_borrowings_gross = Column(Integer, nullable=True)
    liabilities = Column(Integer, nullable=True)
    non_controlling_interests_equity = Column(Integer, nullable=True)
    equity = Column(Integer, nullable=True)
    revenue = Column(Integer, nullable=True)
    cost_of_sales = Column(Integer, nullable=True)
    gross_profit = Column(Integer, nullable=True)
    total_selling_general_administrative_expenses = Column(Integer, nullable=True)
    operating_income_loss = Column(Integer, nullable=True)
    finance_costs = Column(Integer, nullable=True)
    profit_loss_before_tax = Column(Integer, nullable=True)
    income_tax_expense_continuing_operations = Column(Integer, nullable=True)
    profit_loss_from_continuing_operations = Column(Integer, nullable=True)
    profit_loss_from_discontinued_operations = Column(Integer, nullable=True)
    profit_loss = Column(Integer, nullable=True)
    controlling_interests_profit_loss = Column(Integer, nullable=True)
    noncontrolling_interests_profit_loss = Column(Integer, nullable=True)
    cash_flows_from_used_in_operating_activities = Column(Integer, nullable=True)
    cash_flows_from_used_in_investing_activities = Column(Integer, nullable=True)
    cash_flows_from_used_in_financing_activities = Column(Integer, nullable=True)

    def __init__(self, stock_cd, quarter, first_rcept_date, rcept_date, next_first_rcept_date, base_currency,
                 current_assets, cash_and_cash_equivalents, short_term_trade_receivable, noncurrent_assets,
                 property_plant_and_equipment, intangible_assets_other_than_goodwill, assets, current_liabilities,
                 shortterm_borrowings, noncurrent_liabilities, long_term_borrowings_gross, liabilities,
                 non_controlling_interests_equity, equity, revenue, cost_of_sales, gross_profit,
                 total_selling_general_administrative_expenses, operating_income_loss, finance_costs,
                 profit_loss_before_tax, income_tax_expense_continuing_operations,
                 profit_loss_from_continuing_operations, profit_loss_from_discontinued_operations, profit_loss,
                 controlling_interests_profit_loss, noncontrolling_interests_profit_loss,
                 cash_flows_from_used_in_operating_activities,
                 cash_flows_from_used_in_investing_activities, cash_flows_from_used_in_financing_activities):
        self.stock_cd = stock_cd
        self.quarter = quarter
        self.first_rcept_date = first_rcept_date
        self.rcept_date = rcept_date
        self.next_first_rcept_date = next_first_rcept_date
        self.base_currency = base_currency
        self.current_assets = current_assets
        self.cash_and_cash_equivalents = cash_and_cash_equivalents
        self.short_term_trade_receivable = short_term_trade_receivable
        self.noncurrent_assets = noncurrent_assets
        self.property_plant_and_equipment = property_plant_and_equipment
        self.intangible_assets_other_than_goodwill = intangible_assets_other_than_goodwill
        self.assets = assets
        self.current_liabilities = current_liabilities
        self.shortterm_borrowings = shortterm_borrowings
        self.noncurrent_liabilities = noncurrent_liabilities
        self.long_term_borrowings_gross = long_term_borrowings_gross
        self.liabilities = liabilities
        self.non_controlling_interests_equity = non_controlling_interests_equity
        self.equity = equity
        self.revenue = revenue
        self.cost_of_sales = cost_of_sales
        self.gross_profit = gross_profit
        self.total_selling_general_administrative_expenses = total_selling_general_administrative_expenses
        self.operating_income_loss = operating_income_loss
        self.finance_costs = finance_costs
        self.profit_loss_before_tax = profit_loss_before_tax
        self.income_tax_expense_continuing_operations = income_tax_expense_continuing_operations
        self.profit_loss_from_continuing_operations = profit_loss_from_continuing_operations
        self.profit_loss_from_discontinued_operations = profit_loss_from_discontinued_operations
        self.profit_loss = profit_loss
        self.controlling_interests_profit_loss = controlling_interests_profit_loss
        self.noncontrolling_interests_profit_loss = noncontrolling_interests_profit_loss
        self.cash_flows_from_used_in_operating_activities = cash_flows_from_used_in_operating_activities
        self.cash_flows_from_used_in_investing_activities = cash_flows_from_used_in_investing_activities
        self.cash_flows_from_used_in_financing_activities = cash_flows_from_used_in_financing_activities


class DartFinancialStatementsBlacklist(Base):
    __tablename__ = 'dart_financial_statements_blacklist'

    stock_cd = Column(String, primary_key=True)
    quarter = Column(String, primary_key=True)

    def __init__(self, stock_cd, quarter):
        self.stock_cd = stock_cd
        self.quarter = quarter


class DartSimpleFinancialStatements(Base):
    __tablename__ = 'dart_simple_financial_statements'

    stock_cd = Column(String, primary_key=True)
    quarter = Column(String, primary_key=True)
    first_rcept_date = Column(String, primary_key=True)
    rcept_date = Column(String, nullable=False)
    next_first_rcept_date = Column(String, nullable=False)
    base_currency = Column(String, nullable=False)
    current_assets = Column(Integer, nullable=True)
    noncurrent_assets = Column(Integer, nullable=True)
    assets = Column(Integer, nullable=True)
    current_liabilities = Column(Integer, nullable=True)
    noncurrent_liabilities = Column(Integer, nullable=True)
    liabilities = Column(Integer, nullable=True)
    capital = Column(Integer, nullable=True)
    retained_earnings = Column(Integer, nullable=True)
    equity = Column(Integer, nullable=True)
    revenue = Column(Integer, nullable=True)
    operating_income_loss = Column(Integer, nullable=True)
    profit_loss_before_tax = Column(Integer, nullable=True)
    profit_loss = Column(Integer, nullable=True)
    cum_revenue = Column(Integer, nullable=True)
    cum_operating_income_loss = Column(Integer, nullable=True)
    cum_profit_loss_before_tax = Column(Integer, nullable=True)
    cum_profit_loss = Column(Integer, nullable=True)

    def __init__(self, stock_cd, quarter, first_rcept_date, rcept_date, next_first_rcept_date, base_currency,
                 current_assets, noncurrent_assets, assets, current_liabilities, noncurrent_liabilities, liabilities,
                 capital, retained_earnings, equity, revenue, operating_income_loss, profit_loss_before_tax, profit_loss,
                 cum_revenue, cum_operating_income_loss, cum_profit_loss_before_tax, cum_profit_loss):
        self.stock_cd = stock_cd
        self.quarter = quarter
        self.first_rcept_date = first_rcept_date
        self.rcept_date = rcept_date
        self.next_first_rcept_date = next_first_rcept_date
        self.base_currency = base_currency
        self.current_assets = current_assets
        self.noncurrent_assets = noncurrent_assets
        self.assets = assets
        self.current_liabilities = current_liabilities
        self.noncurrent_liabilities = noncurrent_liabilities
        self.liabilities = liabilities
        self.capital = capital
        self.retained_earnings = retained_earnings
        self.equity = equity
        self.revenue = revenue
        self.operating_income_loss = operating_income_loss
        self.profit_loss_before_tax = profit_loss_before_tax
        self.profit_loss = profit_loss
        self.cum_revenue = cum_revenue
        self.cum_operating_income_loss = cum_operating_income_loss
        self.cum_profit_loss_before_tax = cum_profit_loss_before_tax
        self.cum_profit_loss = cum_profit_loss


class UserPortfolioInfo(Base):
    __tablename__ = 'user_portfolio_info'

    user_code = Column(Integer, primary_key=True)
    portfolio_code = Column(Integer, primary_key=True)
    portfolio_nm = Column(String, primary_key=False)
    portfolio_order = Column(Integer, primary_key=False)
    lst_update_dtim = Column(String, primary_key=False)

    def __init__(self, user_code, portfolio_code, portfolio_nm, portfolio_order, lst_update_dtim):
        self.user_code = user_code
        self.portfolio_code = portfolio_code
        self.portfolio_nm = portfolio_nm
        self.portfolio_order = portfolio_order
        self.lst_update_dtim = lst_update_dtim


class UserPortfolioMap(Base):
    __tablename__ = 'user_portfolio_map'

    user_code = Column(Integer, primary_key=True)
    account_number = Column(String, primary_key=True)
    stock_cd = Column(String, primary_key=True)
    portfolio_code = Column(Integer, primary_key=True)
    securities_code = Column(String, nullable=False)
    lst_update_dtim = Column(String, nullable=True)

    def __init__(self, user_code, account_number, stock_cd, portfolio_code, securities_code,
                 lst_update_dtim=time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))):
        self.user_code = user_code
        self.account_number = account_number
        self.stock_cd = stock_cd
        self.portfolio_code = portfolio_code
        self.securities_code = securities_code
        self.lst_update_dtim = lst_update_dtim


class SecuritiesCode(Base):
    __tablename__ = 'securities_code'

    begin_date = Column(String, primary_key=True)
    end_date = Column(String, primary_key=True)
    securities_code = Column(String, primary_key=True)
    securities_nm = Column(String, nullable=False)

    def __init__(self, begin_date, end_date, securities_code, securities_nm):
        self.begin_date = begin_date
        self.end_date = end_date
        self.securities_code = securities_code
        self.securities_nm = securities_nm


class UsStockDailyPrice(Base):
    __tablename__ = 'us_stock_daily_price'

    date = Column(Integer, primary_key=True)
    stock_cd = Column(String, primary_key=True)
    open_price = Column(DECIMAL, nullable=True)
    high_price = Column(DECIMAL, nullable=True)
    low_price = Column(DECIMAL, nullable=True)
    close_price = Column(DECIMAL, nullable=True)
    adj_close_price = Column(DECIMAL, nullable=True)
    trading_volume = Column(Integer, nullable=True)
    unadjusted_trading_volume = Column(Integer, nullable=True)

    def __init__(self, date, stock_cd, open_price, high_price, low_price, close_price, adj_close_price,
                 trading_volume, unadjusted_trading_volume):
        self.date = date
        self.stock_cd = stock_cd
        self.open_price = open_price
        self.high_price = high_price
        self.low_price = low_price
        self.close_price = close_price
        self.adj_close_price = adj_close_price
        self.trading_volume = trading_volume
        self.unadjusted_trading_volume = unadjusted_trading_volume


class UsStockInfo(Base):
    __tablename__ = 'us_stock_info'

    stock_cd = Column(String, primary_key=True)
    begin_date = Column(Integer, primary_key=True)
    end_date = Column(Integer, primary_key=True)
    stock_nm = Column(String, nullable=True)
    market = Column(String, nullable=True)
    lst_update_date = Column(String, nullable=True)

    def __init__(self,  stock_cd, begin_date, end_date, stock_nm, market, lst_update_date):
        self.stock_cd = stock_cd
        self.begin_date = begin_date
        self.end_date = end_date
        self.stock_nm = stock_nm
        self.market = market
        self.lst_update_date = lst_update_date


class UsStockRealtimePrice(Base):
    __tablename__ = 'us_stock_realtime_price'

    dtim = Column(Integer, primary_key=True)
    stock_cd = Column(String, primary_key=True)
    open_price = Column(DECIMAL, nullable=True)
    high_price = Column(DECIMAL, nullable=True)
    low_price = Column(DECIMAL, nullable=True)
    close_price = Column(DECIMAL, nullable=True)
    trading_volume = Column(Integer, nullable=True)

    def __init__(self, dtim, stock_cd, open_price, high_price, low_price, close_price, trading_volume):
        self.dtim = dtim
        self.stock_cd = stock_cd
        self.open_price = open_price
        self.high_price = high_price
        self.low_price = low_price
        self.close_price = close_price
        self.trading_volume = trading_volume


class TmpUsStockRealtimePrice(Base):
    __tablename__ = 'tmp_us_stock_realtime_price'

    dtim = Column(Integer, primary_key=True)
    stock_cd = Column(String, primary_key=True)
    open_price = Column(DECIMAL, nullable=True)
    high_price = Column(DECIMAL, nullable=True)
    low_price = Column(DECIMAL, nullable=True)
    close_price = Column(DECIMAL, nullable=True)
    trading_volume = Column(Integer, nullable=True)

    def __init__(self, dtim, stock_cd, open_price, high_price, low_price, close_price, trading_volume):
        self.dtim = dtim
        self.stock_cd = stock_cd
        self.open_price = open_price
        self.high_price = high_price
        self.low_price = low_price
        self.close_price = close_price
        self.trading_volume = trading_volume


class PushNotiAcctStatus(Base):
    __tablename__ = 'push_noti_acct_status'

    user_code = Column(Integer, primary_key=True)
    account_number = Column(String, primary_key=True)
    sync_complete_flag = Column(Integer, nullable=False)
    fcm_token = Column(String, nullable=True)
    lst_update_dtim = Column(String, nullable=False)

    def __init__(self, user_code, account_number, sync_complete_flag, fcm_token, lst_update_dtim):
        self.user_code = user_code
        self.account_number = account_number
        self.sync_complete_flag = sync_complete_flag
        self.fcm_token = fcm_token
        self.lst_update_dtim = lst_update_dtim


class TmpUserPortfolio(Base):
    __tablename__ = 'tmp_user_portfolio'

    user_code = Column(Integer, primary_key=True)
    date = Column(Integer, primary_key=True)
    account_number = Column(String, primary_key=True)
    stock_cd = Column(String, primary_key=True)
    securities_code = Column(String, nullable=False)
    stock_nm = Column(String, nullable=True)
    holding_quantity = Column(Float, nullable=True)
    avg_purchase_price = Column(Float, nullable=True)
    close_price = Column(Float, nullable=True)
    prev_1w_close_price = Column(Float, nullable=True)
    total_value = Column(Integer, nullable=True)
    first_purchase_date = Column(String, nullable=True)
    retention_period = Column(Integer, nullable=True)
    new_purchase_amount = Column(Integer, nullable=True)
    realized_profit_loss = Column(Integer, nullable=True)
    purchase_amount_of_stocks_to_sell = Column(Integer, nullable=True)
    unit_currency = Column(String, nullable=True)
    update_dtim = Column(String, nullable=False)
    country = Column(String, nullable=True)

    def __init__(self, user_code, date, account_number, stock_cd, securities_code, stock_nm, holding_quantity,
                 avg_purchase_price, close_price, prev_1w_close_price, total_value, first_purchase_date, retention_period,
                 new_purchase_amount, realized_profit_loss, purchase_amount_of_stocks_to_sell, unit_currency,
                 update_dtim, country):
        self.user_code = user_code
        self.date = date
        self.account_number = account_number
        self.stock_cd = stock_cd
        self.securities_code = securities_code
        self.stock_nm = stock_nm
        self.holding_quantity = holding_quantity
        self.avg_purchase_price = avg_purchase_price
        self.close_price = close_price
        self.prev_1w_close_price = prev_1w_close_price
        self.total_value = total_value
        self.first_purchase_date = first_purchase_date
        self.retention_period = retention_period
        self.new_purchase_amount = new_purchase_amount
        self.realized_profit_loss = realized_profit_loss
        self.purchase_amount_of_stocks_to_sell = purchase_amount_of_stocks_to_sell
        self.unit_currency = unit_currency
        self.update_dtim = update_dtim
        self.country = country


class UserInfo(Base):
    __tablename__ = 'user_info'

    user_code = Column(Integer, primary_key=True)
    login_type = Column(String, nullable=False)
    login_key = Column(String, nullable=False)
    beg_dtim = Column(String, nullable=False)
    end_dtim = Column(String, nullable=False)
    passwd = Column(String, nullable=False)
    salt = Column(String, nullable=False)
    user_name = Column(String, nullable=True)
    user_birth = Column(String, nullable=True)
    user_sex = Column(String, nullable=True)
    user_foreign = Column(String, nullable=True)
    user_phone_number = Column(String, nullable=True)

    def __init__(self, user_code, login_type, login_key, beg_dtim, end_dtim, passwd, salt,
                 user_name, user_birth, user_sex, user_foreign, user_phone_number):
        self.user_code = user_code
        self.login_type = login_type
        self.login_key = login_key
        self.beg_dtim = beg_dtim
        self.end_dtim = end_dtim
        self.passwd = passwd
        self.salt = salt
        self.user_name = user_name
        self.user_birth = user_birth
        self.user_sex = user_sex
        self.user_foreign = user_foreign
        self.user_phone_number = user_phone_number

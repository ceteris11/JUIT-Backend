import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from fcmpush.fcmpushpublisher import send_fcm_push
import firebase_admin
from db.db_model import session_scope, PushNotiAcctStatus, TmpUserPortfolio
from sqlalchemy import func
import pandas as pd
import time
from datetime import datetime
import logging


# logger 설정
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# log 출력 형식
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# log 출력
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
# 로거에 핸들러가 없을 경우에만 핸들러를 붙여준다.
if len(logger.handlers) == 0:
    logger.addHandler(stream_handler)


def run_push_sender():
    logger.info('system start')
    while True:
        with session_scope() as session:
            # push 보낼 대상 불러오기
            push_list_query = session.query(PushNotiAcctStatus.user_code,
                                            func.min(PushNotiAcctStatus.sync_complete_flag).label('min_flag'),
                                            func.max(PushNotiAcctStatus.lst_update_dtim).label('max_update_dtim'),
                                            func.max(PushNotiAcctStatus.fcm_token).label('fcm_token')) \
                .group_by(PushNotiAcctStatus.user_code)
            push_list = pd.read_sql(push_list_query.statement, session.bind)
            session.commit()

            for i, r in push_list.iterrows():
                # print(r)
                # 조건 확인
                time_diff = datetime.now() - datetime.strptime(r['max_update_dtim'], '%Y%m%d%H%M%S')

                # 모든 연동이 완료되고, 가장 최근 업데이트 일시로부터 30초 이상 지난 경우 push 발송
                # <- 연동이 완료되었더라도 다음 연동 건이 존재할지 모르기 때문에, 30초 대기
                if r['min_flag'] == 1 and time_diff.seconds > 30:
                    # tmp_user_portfolio 확인: tmp_user_portfolio에 row가 있을 경우 연동 진행중으로, push 보내지 않고 continue
                    tmp_portfolio = session.query(TmpUserPortfolio). \
                        filter(TmpUserPortfolio.user_code == int(r['user_code'])). \
                        first()
                    session.commit()
                    if tmp_portfolio is not None:
                        # tmp_portfolio가 있을 경우, 현재 포트폴리오 업데이트 진행중으로 lst_update_dtim을 현재 시간으로 업데이트 해 준다.
                        push_status = session.query(PushNotiAcctStatus). \
                            filter(PushNotiAcctStatus.user_code == int(r['user_code'])). \
                            first()
                        push_status.lst_update_dtim = datetime.now().strftime('%Y%m%d%H%M%S')
                        session.commit()
                        continue

                    # 만약 업데이트가 진행 중인데 공교롭게도 그때 tmp_user_portfolio가 없어서 위 조건에 걸리지 않았다면 어쩔 수 없다.
                    # 그냥 push 보낸다. 이런 케이스는 거의 없을 것으로 보인다.

                    # push 발송
                    try:
                        # push 보내기
                        send_fcm_push(r['fcm_token'], title='신규 증권사 등록 완료!', body='JUIT에서 수익률을 확인해보세요')
                    except firebase_admin._messaging_utils.ThirdPartyAuthError as e:
                        # 인증 오류 날 경우 다음 반복 시 재시도
                        logger.info(e)
                        continue
                    except firebase_admin._messaging_utils.UnregisteredError as e:
                        # 존재하지 않는 토큰에 대해 메시지 발송할 경우 삭제 처리
                        logger.info(e)
                        pass

                    # 데이터 삭제
                    delete_query = session.query(PushNotiAcctStatus). \
                        filter(PushNotiAcctStatus.user_code == int(r['user_code'])). \
                        delete()
                    session.commit()
                    logger.info(f'send message: {r}')
                elif time_diff.seconds > 600:  # 가장 최근 연동 건이 시작된지 600초 이상 되었을 경우 데이터 초기화
                    # 데이터 삭제
                    delete_query = session.query(PushNotiAcctStatus). \
                        filter(PushNotiAcctStatus.user_code == int(r['user_code'])). \
                        delete()
                    session.commit()
                    logger.info(f'delete old data: {r}')

        # time sleep
        time.sleep(1)


if __name__ == '__main__':
    run_push_sender()

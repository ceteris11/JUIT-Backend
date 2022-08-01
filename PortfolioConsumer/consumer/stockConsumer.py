from kafka import KafkaConsumer, OffsetAndMetadata, TopicPartition
import redis
import argparse
from update_portfolio import *
import time
from logger_util import *
import traceback

clogger = create_logger("consumer")
rlogger = create_logger("redis_logger")


def update_portfolio(msg_dict):
    user_code = msg_dict["user_code"]
    stock_cd = msg_dict["stock_code"]
    begin_date = msg_dict["begin_date"]
    account_number = msg_dict["account_number"]
    securities_code = msg_dict["securities_code"]
    country = msg_dict["country"]
    tmp_portfolio = bool(msg_dict["tmp_portfolio"])

    update_single_stock_portfolio(user_code, begin_date, account_number, securities_code, stock_cd, country, tmp_portfolio)

    return {"user_code": user_code, "stock_cd": stock_cd, "account_number": account_number, "securities_code": securities_code,
            "country": country, "timestamp": msg_dict["timestamp"]}

def consume_mode(consumer:KafkaConsumer):
    while 1:
        msg_pack = consumer.poll(timeout_ms=500)
        ## 한 topic - partition 에 들어온 msg 는 여러개임을 가정한다.
        cnt=0
        for tp, msgs in msg_pack.items():
            print(f"topic: {tp.topic} , partition: {tp.partition}, msg_count: {len(msgs)}")

            for msg in msgs:
                update_portfolio(msg.value)
                cnt+=1


        print(f"---------- end {cnt}--------------")
        consumer.position(tp.partition)
        consumer.commit()
        break

def consume2(consumer, redis_client):

    for data in consumer:
        start = time.time()
        msg_value={}
        end = time.time()
        try:
            msg_value = update_portfolio(data.value)
            end = time.time()
        except Exception as e:
            error_msg = create_msg("consume", f"error occured while processing kafka inflow data {traceback.format_exc()}")
            clogger.error(error_msg)

        tp = TopicPartition(data.topic, data.partition)
        consumer.commit({
            tp: OffsetAndMetadata(data.offset+1, None)
        })
        msg = f"user_code: {msg_value['user_code']}, stock_cd: {msg_value['stock_cd']}, " \
              f"accountNumber: {msg_value['account_number']}, securities_code: {msg_value['securities_code']}, " \
              f"country: {msg_value['country']}, timestamp: {msg_value['timestamp']}, elapsed: {end-start}"

        clog_msg = create_msg("consume", msg)
        clogger.info(clog_msg)

        try:
            publish_channel = f"partition{data.partition}"
            redis_client.publish(publish_channel, data.offset+1)

        except Exception as e:
            redis_error_msg = create_msg("redis", f"redis error : {e}")
            rlogger.error(redis_error_msg)
        else:
            redis_msg = create_msg("redis", f" user_code: {msg_value['user_code']}, stock_cd: {msg_value['stock_cd']} "
                                            f"sent to redis {publish_channel} at offset({data.offset+1})")
            rlogger.info(redis_msg)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    kafka_host = os.environ.get("KAFKA_HOST")
    kafka_port = os.environ.get("KAFKA_PORT")
    redis_host = str(os.environ.get("REDIS_HOST"))
    final_kafka_url = kafka_host+":"+kafka_port
    topic_name = str(os.environ.get("TOPIC_NAME"))

    consumer = KafkaConsumer(topic_name, bootstrap_servers=final_kafka_url, enable_auto_commit=False,
                             auto_offset_reset='earliest', group_id = "consumer1",
                             value_deserializer=lambda m: json.loads(m.decode("utf-8")))

    REDIS = redis.StrictRedis(host=redis_host, port=6379, db=0)

    consume2(consumer, REDIS)



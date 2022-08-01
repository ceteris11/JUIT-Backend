import json
import os
import redis
from kafka import KafkaProducer, KafkaConsumer, TopicPartition
import argparse
import numpy as np
from time import sleep
from datetime import datetime

global_status={}

class TradeLog:
    def __init__(self, user_code, stock_code):
        self.user_code = user_code
        self.stock_code = stock_code
        self.begin_date = "20210801"
        self.account_number = "5521993510"
        self.securities_code = "KIWOOM"
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def print_log(self):
        print(f"[{self.timestamp}] : stock_cd - {self.stock_code} begin_date - {self.begin_date} "
              f"account_no-{self.account_number} securities_cd : {self.securities_code}")

    def to_json(self):
        dictform = {"user_code": self.user_code, "stock_code":self.stock_code,
                    "begin_date": self.begin_date, "account_number":self.account_number,
                    "securities_code": self.securities_code, "timestamp": self.timestamp}
        return json.dumps(dictform).encode("utf-8")


def publish(topic_name, tradeLog: TradeLog, produ, lowSec, upSec ):
    # partitionNumer = tradeLog.stock_code
    partitionNumber = int(np.random.randint(0,9, size=1)[0])
    produ.send(topic=topic_name, value = tradeLog.to_json(), partition=partitionNumber).add_callback(on_send_success).add_errback(on_send_error)
    sleep(np.random.randint(low=lowSec, high=upSec, size=1)[0])


def on_send_error(excp):
    print(f"ERROR : {excp}" )

def on_send_success(record_metadata):
    global_status[f"partition{record_metadata.partition}"] = record_metadata.offset+1
    print(f"sent data - topic:, {record_metadata.topic} partition: {record_metadata.partition}, offset: {record_metadata.offset+1}")



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--topicname")

    args = parser.parse_args()

    topic_name = str(args.topicname)
    kafka_host = os.environ.get("KAFKA_HOST")
    kafka_port = os.environ.get("KAFKA_PORT")
    final_kafka_url = kafka_host+":"+kafka_port

    redis_host = str(os.environ.get("REDIS_HOST"))
    print(f"REDIS host : {redis_host}")


    PRODUCER = KafkaProducer(bootstrap_servers=[final_kafka_url])
    redis_client = redis.StrictRedis(host=redis_host, port=6379, db=0)
    subscriber = redis_client.pubsub()

    subscriber.psubscribe(f"partition*")

    cnt = 0
    PAUSE = False

    for item in subscriber.listen():
        item_channel = item['channel'].decode("utf-8")
        print(item)

        if item_channel in global_status.keys() and global_status[item_channel] <= int(item['data']):
            print(
                f"item {item['channel'].decode('utf-8')} - data {int(item['data'])} & {global_status[item['channel'].decode('utf-8')]}")
            cnt += 1

        if PAUSE == False:
            for st_cd in ("005930", "142760", "241840", "014680", "120110", "101730"):
                trade_data = TradeLog(215, st_cd)
                publish(topic_name, trade_data, PRODUCER, 1, 3)
            PAUSE = True
            print(global_status)
            PRODUCER.flush()

        if cnt == len(global_status.keys()):
           print("## process end")
           break

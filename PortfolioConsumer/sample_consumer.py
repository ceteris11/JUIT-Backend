

from kafka import KafkaConsumer, OffsetAndMetadata, TopicPartition
import json

if __name__ == '__main__':
    topic_name = "stock_test2"
    final_kafka_url = "10.100.176.80:9094"
    consumer = KafkaConsumer(topic_name, bootstrap_servers=final_kafka_url, enable_auto_commit=False,
                             auto_offset_reset='earliest', group_id="consumer1",
                             value_deserializer=lambda m: json.loads(m.decode("utf-8")))

    for data in consumer:
        msg_value = json.dumps(data.value).encode("utf-8")
        print("Topic: {}, Partition: {}, Offset: {}, Key: {}, Value: {}".format(data.topic, data.partition, data.offset,
                                                                                data.key, msg_value))
        print(f"---- msg_value ----{type(msg_value)}")
        print(msg_value)

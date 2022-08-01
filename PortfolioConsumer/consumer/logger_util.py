import logstash
import os
import logging
import sys
from logging.handlers import RotatingFileHandler

formatter = logging.Formatter('%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)s] >> %(message)s')

class JuitTcpLogStashHandler(logstash.TCPLogstashHandler):
    def __init__(self, host, port=5959, message_type='logstash', tags=None, fqdn=False, version=0):
        super(logstash.TCPLogstashHandler, self).__init__(host, port)

    def makePickle(self, record):
        return self.formatter.format(record)




def create_logger(logger_name):
    file_handler = RotatingFileHandler('../consumer.log', maxBytes=1024 * 1024 * 100, backupCount=5)
    file_handler.setFormatter(formatter)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)

    # logstash_handler = logstash.TCPLogstashHandler(logstash_host, logstash_port, version=1)
    # logstash_handler.setFormatter(formatter)

    custom_logger = logging.getLogger(logger_name)

    if len(custom_logger.handlers) > 0:
        return custom_logger

    custom_logger.addHandler(stdout_handler)
    custom_logger.addHandler(file_handler)

    log_level = os.environ.get("LOGLEVEL")


    if log_level == "info":
        custom_logger.setLevel(logging.INFO)
    elif log_level == "error":
        custom_logger.setLevel(logging.ERROR)
    elif log_level == "debug":
        custom_logger.setLevel(logging.DEBUG)
    else:
        custom_logger.setLevel(logging.INFO)

    custom_logger.propagate=False

    return custom_logger

def create_msg(api, msg):
    return f"@{api}@ {msg}"

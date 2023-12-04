
#!/usr/bin/env python
# Author: rex.cheny
# E-mail: rex.cheny@outlook.com
 
import time
import random
import sys
 
from kafka import KafkaProducer
from kafka.errors import KafkaError, KafkaTimeoutError
import json
    
class Producer(object):
    def __init__(self, KafkaServerList=['127.0.0.1:9092'], ClientId="Procucer01", Topic='Test'):
        self._kwargs = {
            "bootstrap_servers": KafkaServerList,
            "client_id": ClientId,
            "acks": 1,
            "buffer_memory": 33554432,
            'compression_type': None,
            "retries": 3,
            "batch_size": 1048576,
            "linger_ms": 100,
            "key_serializer": lambda m: json.dumps(m).encode('utf-8'),
            "value_serializer": lambda m: json.dumps(m).encode('utf-8'),
        }
        self._topic = Topic
        try:
            self._producer = KafkaProducer(**self._kwargs)
        except Exception as err:
            print(err)
 
 
    def _onSendSucess(self, record_metadata):
        """
        异步发送成功回调函数，也就是真正发送到kafka集群且成功才会执行。发送到缓冲区不会执行回调方法。
        :param record_metadata:
        :return:
        """
        print("发送成功")
        print("被发往的主题：", record_metadata.topic)
        print("被发往的分区：", record_metadata.partition)
        print("队列位置：", record_metadata.offset)  # 这个偏移量是相对偏移量，也就是相对起止位置，也就是队列偏移量。
 
 
    def _onSendFailed(self):
        print("发送失败")
 
 
    def sendMessage(self, value=None, partition=None):
        if not value:
            return None
 
        # 发送的消息必须是序列化后的，或者是字节
        # message = json.dumps(msg, encoding='utf-8', ensure_ascii=False)
 
        kwargs = {
            "value": value, # value 必须必须为字节或者被序列化为字节，由于之前我们初始化时已经通过value_serializer来做了，所以我上面的语句就注释了
            "key": None,  # 与value对应的键，可选，也就是把一个键关联到这个消息上，KEY相同就会把消息发送到同一分区上，所以如果有这个要求就可以设置KEY，也需要序列化
            "partition": partition # 发送到哪个分区，整型。如果不指定将会自动分配。
        }
 
        try:
            # 异步发送，发送到缓冲区，同时注册两个回调函数，一个是发送成功的回调，一个是发送失败的回调。
            # send函数是有返回值的是RecordMetadata，也就是记录的元数据，包括主题、分区、偏移量
            future = self._producer.send(self._topic, **kwargs).add_callback(self._onSendSucess).add_errback(self._onSendFailed)
            print("发送消息:", value)
            # 注册回调也可以这样写，上面的写法就是为了简化
            # future.add_callback(self._onSendSucess)
            # future.add_errback(self._onSendFailed)
        except KafkaTimeoutError as err:
            print(err)
        except Exception as err:
            print(err)
 
    def closeConnection(self, timeout=None):
        # 关闭生产者，可以指定超时时间，也就是等待关闭成功最多等待多久。
        self._producer.close(timeout=timeout)
 
    def sendNow(self, timeout=None):
        # 调用flush()函数可以放所有在缓冲区的消息记录立即发送，即使ligner_ms值大于0.
        # 这时候后台发送消息线程就会开始立即发送消息并且阻塞在这里，等待消息发送成功，当然是否阻塞取决于acks的值。
        # 如果不调用flush函数，那么什么时候发送消息取决于ligner_ms或者batch任意一个条件满足就会发送。
        try:
            self._producer.flush(timeout=timeout)
        except KafkaTimeoutError as err:
            print(err)
        except Exception as err:
            print(err)
 
 
def main():
    p = Producer(KafkaServerList=["172.16.42.156:9092"], ClientId="Procucer01", Topic="TESTTOPIC")
    for i in range(10):
        time.sleep(1)
        closePrice = random.randint(1, 500)
        msg = {
            "Publisher": "Procucer01",
            "股票代码": 60000 + i,
            "昨日收盘价": closePrice,
            "今日开盘价": 0,
            "今日收盘价": 0,
        }
        p.sendMessage(value=msg)
    # p.sendNow()
    p.closeConnection()
 
if __name__ == "__main__":
    try:
        main()
    finally:
        sys.exit()

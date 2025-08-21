from kafka import KafkaProducer as kkp
from kafka import KafkaConsumer as kkc
from kafka.structs import TopicPartition as ktp
import json
# from .. import Lg
import msgpack
import typing
from .. import Funcs, Time

#print("load " + '/'.join(__file__.split('/')[-2:]))

# kafka中，Topic是一个存储消息的逻辑概念，可认为为一个消息的集合。物理上，不同Topic的消息分开存储，每个Topic可划分多个partition，同一个Topic下的不同的partition包含不同消息。每个消息被添加至分区时，分配唯一offset，以此保证partition内消息的顺序性。
# kafka中，以broker区分集群内服务器，同一个topic下，多个partition经hash到不同的broker。

class kafkaProducer():
    def __init__(self, topic:str, servers:str|list, value_serializer:str, compression_type:str=None):
        """
        This is a constructor function that initializes an object with specified parameters for Kafka
        producer.
        
        :param topic: The name of the Kafka topic to which messages will be produced
        :type topic: str
        :param servers: The `servers` parameter is a string or list of strings that specifies the Kafka
        broker(s) to connect to. The format of the string should be `host:port` for each broker,
        separated by commas if there are multiple brokers. For example, `"localhost:9092"` or `["
        :type servers: str|list
        :param value_serializer: The value_serializer parameter is used to specify the serializer to be
        used for serializing the values of messages that will be sent to the Kafka topic. The serializer
        is responsible for converting the data into a format that can be transmitted over the network
        and stored in Kafka. Common serializers include JSON, Avro,
        :type value_serializer: str
        :param compression_type: The compression type to use for messages. It can be set to "gzip",
        "snappy", "lz4", or None (default). If set to None, no compression will be used
        :type compression_type: str
        """
        self.kp = kkp(bootstrap_servers=servers, compression_type=compression_type)
        self.topic = topic
        self.value_serializer = value_serializer
    
    def Send(self, data:dict|list|bytes|str):
        """
        The Send function sends data to a Kafka topic, with support for different data types and
        serializers.
        注意这个函数是异步的, 来保证调用的速度, 所以如果Send之后程序立刻退出则数据不会被发送. 
        
        :param data: The `data` parameter can be of type `dict`, `list`, `bytes`, or `str`
        :type data: dict|list|bytes|str
        """
        if self.value_serializer == None:
            if type(data) == bytes:
                self.kp.send(self.topic, data)
            elif type(data) == str:
                self.kp.send(self.topic, data.encode())
            else:
                self.kp.send(self.topic, str(data).encode())
        elif self.value_serializer == "json":
            self.kp.send(self.topic, json.dumps(data).encode())
        elif self.value_serializer == "msgpack":
            self.kp.send(self.topic, msgpack.packb(data, use_bin_type=True))

class kafkaMessage():
    def __init__(self) -> None:
        self.Topic:str = None 
        self.Partition:int = None 
        self.Offset:int = None 
        self.Timestamp:float = None 
        self.Value:dict|list|str|bytes = None 
        self.TimestampType:int = None 
        self.Key = None 
        self.Headers:list = None 
        self.Checksum = None 
        self.SerializedKeySize:int = None 
        self.SerializedValueSize:int = None 
        self.SerializedHeaderSize:int = None 

    def __repr__(self):
        return f"kafkaMessage(Topic={self.Topic} Partition={self.Partition} Offset={self.Offset} Timestamp={self.Timestamp} Value={self.Value} TimestampType={self.TimestampType} Key={self.Key} Headers={self.Headers} Checksum={self.Checksum} SerializedKeySize={self.SerializedKeySize} SerializedValueSize={self.SerializedValueSize} SerializedHeaderSize={self.SerializedHeaderSize})"

    def __str__(self):
        return self.__repr__()

class kafkaConsumer():
    def __init__(self, topic:str, servers:str|list, value_serializer:str, group_id:str=None):
        if group_id == None:
            group_id = Funcs.UUID()

        self.kc = kkc(bootstrap_servers=servers, group_id=group_id)
        # self.kc.subscribe(topic)
        self.offset:dict = {}
        self.topic:str = topic
        self.value_serializer:str = value_serializer
        # Lg.Trace(self.value_serializer)

        self._assignPartition()
        self._tell()
    
    def _assignPartition(self):
        # import ipdb
        # ipdb.set_trace()
        while self.kc.partitions_for_topic(self.topic) == None:
            Time.Sleep(1)

        partitions = []
        for partition in self.kc.partitions_for_topic(self.topic):
            partitions.append(ktp(self.topic, partition))
        self.kc.assign(partitions)
    
    def _tell(self):
        """
        This function retrieves the current offset position for each partition of a given topic.
        """
        for partition in self.kc.partitions_for_topic(self.topic):
            tp = ktp(self.topic, partition)
            # self.kc.assign([tp])
            self.offset[partition] = self.kc.position(tp)

        # print(self.offset)
            
    def Tell(self) -> dict:
        # print(self.offset)
        return self.offset 
    
    def Seek(self, offset:dict):
        """
        The function seeks to a specific offset in a Kafka topic partition.
        
        :param offset: The parameter "offset" is a dictionary that contains the partition number as the key
        and the offset value as the value. This function is used to seek to a specific offset for each
        partition in a Kafka topic. The "kc" object is assumed to be an instance of a KafkaConsumer class
        :type offset: dict
        """
        for pn in offset:
            self.kc.seek(ktp(self.topic, pn), offset[pn]) 
    
    def SeekAllParationByOffset(self, offset:int):
        """
        This function seeks to a specific offset in a Kafka topic's partitions.
        
        :param offset: The offset parameter is an integer value that determines the position in the
        Kafka topic partition where the consumer should start reading messages from. If the offset is 0,
        the consumer will start reading from the beginning of the partition. If the offset is -1, the
        consumer will start reading from the end of
        :type offset: int
        """
        if offset == 0:
            self.kc.seek_to_beginning()
        elif offset == -1:
            self.kc.seek_to_end()
        else:
            for pn in list(self.kc.partitions_for_topic(self.topic)):
                self.kc.seek(ktp(self.topic, pn), offset)
        
        self._tell()
    
    def SeekAllParationByTime(self, timestamp:float):
        """
        This function seeks all partitions of a Kafka topic to a specific timestamp.
        
        :param timestamp: The `timestamp` parameter is a float value representing a Unix timestamp in
        seconds. It is used to seek to a specific offset in a Kafka topic partition based on the
        timestamp of the message. The function seeks to the offset of the first message with a timestamp
        greater than or equal to the specified timestamp
        :type timestamp: float
        """
        for pn in list(self.kc.partitions_for_topic(self.topic)):
            self.kc.seek(
                ktp(self.topic, pn), 
                self.kc.offsets_for_times({
                    ktp(self.topic, pn): int(timestamp * 1000),
                })[ktp(self.topic, pn)].offset
            )

        self._tell()

    def Get(self) -> kafkaMessage:
        """
        This function fetches a message from Kafka and returns its value.
        :return: A dictionary containing the message fetched from Kafka.
        """
        # Lg.Trace("Fetching message from kafka")
        msg = next(self.kc)
        # Lg.Trace(msg)
        self.offset[msg.partition] = msg.offset + 1
        # msgv = json.loads(msg.value.decode())
        msgv = msg.value

        # Lg.Trace(self.value_serializer)
        if self.value_serializer == "json":
            msgv = json.loads(msgv)
        elif self.value_serializer == 'msgpack':
            msgv = msgpack.unpackb(msgv, raw=False)

        kmsg = kafkaMessage()
        kmsg.Topic = msg.topic 
        kmsg.Partition = msg.partition
        kmsg.Offset = msg.offset
        kmsg.Timestamp = msg.timestamp / 1000
        kmsg.Value = msgv 
        kmsg.TimestampType = msg.timestamp_type 
        kmsg.Key = msg.key 
        kmsg.Headers = msg.headers 
        kmsg.Checksum = msg.checksum 
        kmsg.SerializedKeySize = msg.serialized_key_size 
        kmsg.SerializedValueSize = msg.serialized_value_size 
        kmsg.SerializedHeaderSize = msg.serialized_header_size

        return kmsg 

    def __iter__(self) -> typing.Iterator[kafkaMessage]:
        while True:
            try:
                yield self.Get()
            except StopIteration:
                return 

class Kafka():
    def __init__(self, topic:str, servers:str|list, serializer:str="msgpack", compression_type:str="lz4"):
        """
        This function initializes the Kafka object with the topic and servers
        server 可以是字符串也可以是列表, 例如"192.168.168.70:9092"或者["192.168.168.70:9092", "192.168.168.71:9092"]
        serializer可以是None, json或者msgpack, 默认msgpack.
        注意:
            1. 当serializer选择为json的时候发送和接收字符串可能会有问题.
            2. 当serializer选择为None的时候发送和接收出来的都是原始的字节bytes而不是字符串str
        
        :param topic: The topic to which the message will be published
        :type topic: str
        :param servers: A list of Kafka servers to connect to
        :type servers: str|list
        """
        self.topic = topic
        self.servers = servers 
        self.serializer = serializer
        self.compression_type = compression_type
        # Lg.Trace(self.serializer)
    
    def Producer(self) -> kafkaProducer:
        return kafkaProducer(self.topic, self.servers, self.serializer, self.compression_type)

    def Consumer(self, group_id:str=None) -> kafkaConsumer:
        # Lg.Trace(self.serializer)
        return kafkaConsumer(self.topic, self.servers, group_id=group_id, value_serializer=self.serializer)

if __name__ == "__main__":
    import time 
    import sys

    kafka = Kafka("test", '192.168.10.62:9092')
    if sys.argv[1] == 'p':
        p = kafka.Producer()
        while True:
            p.Send({"time": time.time()})
            time.sleep(1)
            
    elif sys.argv[1] == 'c':
        c = kafka.Consumer()
        c.SeekAllParationByOffset(0)
        print("Get one:", c.Get())
        for i in c:
            print("Get with for loop:", i)
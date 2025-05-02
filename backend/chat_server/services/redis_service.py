import redis

class RedisService:
    #def __init__(self, host ='localhost',port = 6379 , db = 0):
    def __init__(self, host ='redis',port = 6379 , db = 0):
        #Establish Redis Connection
        self.r = redis.StrictRedis(host=host, port=port, db=db)

    def store_message(self, room, message):
        """Store message in Redis for perticular room"""
        self.r.rpush(f"room:{room}:messages", message)
        print(f"Message stored in room: {room}")

    def get_messages(self, room):
        """Retrieve message for the specific room"""
        message = self.r.lrange(f"room:{room}:messages", 0, -1)
        print(f"Retrieving message from room;{room}")
        return [msg.decode('utf-8') for msg in message]
    
    def publish_message(self, room, message):
        """Publish a message to the room's Redis channel using Pub/Sub"""
        print(f"Publishing message to room:{room}")
        self.r.publish(f"chat:{room}",message)
    
    def subscribe_to_room(self,rooms):
        """Subscribe to the rooms Redis Channel using Pub/Sub"""
        pubsub = self.r.pubsub()
        for room in rooms:
            pubsub.subscribe(f"chat:{room}")
        print(f"Subscribe to rooms: {','.join(rooms)}")

        # Listen for incoming messages and print them
        for message in pubsub.listen():
            if message['type'] == 'message':
                print(f"Received message: {message['data'].decode('utf-8')}")

        return pubsub
    
    def stop(self):
        """"Close Redis Connection"""
        self.r.connection_pool.disconnect()


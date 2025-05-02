import redis

class RedisService:
    def __init__(self, host='localhost', port=6379, db=0):
        # Establish Redis connection
        self.r = redis.StrictRedis(host=host, port=port, db=db)

    def get_messages(self, room):
        """Retrieve messages from Redis for the given room"""
        messages = self.r.lrange(f"room:{room}:messages", 0, -1)
        return [msg.decode('utf-8') for msg in messages]

    def stop(self):
        """Close Redis connection"""
        self.r.connection_pool.disconnect()

if __name__ == "__main__":
    # Initialize Redis service
    redis_service = RedisService()

    # Specify the room name you want to fetch messages for
    room_name = "room1"

    # Get and print messages from Redis
    messages = redis_service.get_messages(room_name)
    print(f"Messages in {room_name}:")
    for message in messages:
        print(message)

    # Close the Redis connection
    redis_service.stop()

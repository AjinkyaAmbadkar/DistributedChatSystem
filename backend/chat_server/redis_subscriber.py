import redis

#Initialize the redis
r = redis.StrictRedis(host='localhost' , port= 6379, db= 0)

#Subscribe to a room
pubsub = r.pubsub()
pubsub.subscribe("chat:room1")
pubsub.subscribe("chat:room2")
pubsub.subscribe("chat:room3")
pubsub.subscribe("chat:room4")

# Listen for incoming messages and print them
for message in pubsub.listen():
    if message['type'] == 'message':
        print(f"Received message: {message['data'].decode('utf-8')}")
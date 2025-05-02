import logging
import threading
import time
from flask import Flask, request, jsonify
from services.redis_service import RedisService
from services.zookeeper_service import ZookeeperService

app = Flask(__name__)

import os

# Read from env (more flexible), defaulting to the standard in‑cluster names:
zk_hosts   = os.getenv("ZK_SERVERS",   "zookeeper:2181")
redis_host = os.getenv("REDIS_HOST",    "redis")
redis_port = int(os.getenv("REDIS_PORT", "6379"))

zk_service    = ZookeeperService(hosts=zk_hosts)
redis_service = RedisService( host=redis_host, port=redis_port )


#zk_service = ZookeeperService(hosts='localhost:30001')  # Use port 30001 for Minikube NodePort 
#redis_service = RedisService(host='localhost', port='6379')

@app.route('/')
def home():
    return "Hello, World!"

@app.route("/send_message", methods=["POST"])
def send_message():
    data = request.json
    room = data['room']
    message = data['message']
    logging.info(f"Received message for room: {room}, message: {message}")
    # Acquire lock for room
    lock = zk_service.acquire_lock(room)

    def on_leader():
        """Leader callback that handles message operations."""
        print(f"Leader elected for room: {room}")

        # Store message in Redis
        redis_service.store_message(room, message)

        # Publish message to all clients in the room
        redis_service.publish_message(room, message)

        # Simulate leader task stopping after some time 
        #time.sleep(5)

        #print(f"Leader task stopping for room: {room}")
        #zk_service.zk.stop()

    try:
        # Ensure ZooKeeper is connected before attempting leader election
        zk_service.reconnect_if_needed()

        # Attempt to elect leader and pass on_leader callback
        zk_service.elect_leader(room, on_leader)

        # Start the subscriber in a separate thread
        threading.Thread(target=redis_service.subscribe_to_room, args=(room,)).start()

        # Return success response
        return jsonify({"status": "success", "message": "Message sent successfully"}), 200

    finally:
        # Release the lock
        zk_service.release_lock(lock)

@app.route("/get_messages", methods=["GET"])
def get_messages():
    room = request.args.get("room")
    messages = redis_service.get_messages(room)
    return jsonify({"room": room, "messages": messages}), 200

@app.route("/create_room", methods=["POST"])
def create_room():
    data = request.json
    room = data['room']

    # Create a room dynamically
    redis_service.store_message(room, 'Room Created')

    # Optionally: Register room with ZooKeeper
    zk_service.create_server_node(room)

    return jsonify({"status": "success", "message": f"Room {room} created successfully!"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)

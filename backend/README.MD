# Distributed Chat System with ZooKeeper and Redis

### Project Overview

**Developer**: Ajinkya Dilip Ambadkar

This project aims to build a **distributed chat system** that uses **ZooKeeper** for leader election and coordination, and **Redis** for fast in-memory message storage and real-time communication. The goal is to create a system where multiple chat rooms are handled by different pods, and only one server pod (the leader) manages the critical operations of each room at any given time.

By utilizing **ZooKeeper** for synchronization, we ensure that no two servers can modify the room data (like storing messages in Redis) simultaneously, preventing conflicts and ensuring consistency. **Redis**, being an in-memory database, is used to store messages and enable real-time message broadcasting via the Pub/Sub model. This combination of ZooKeeper and Redis ensures a highly responsive and scalable chat system.

---

### Key Features

1. **ZooKeeper Leader Election**:  
   ZooKeeper is used to elect a leader for each chat room. The leader pod handles critical operations such as room moderation, message storage, and broadcasting. Only the leader pod can perform these actions to avoid race conditions and maintain the consistency of the room.

2. **Real-Time Messaging with Redis**:  
   Redis is leveraged to store messages in real-time for each chat room. Using Redis' Pub/Sub functionality, all subscribed clients are instantly notified whenever a new message is published, enabling real-time communication.

3. **StatefulSets for Room-Based Servers**:  
   The chat system is deployed using Kubernetes **StatefulSets**, with each pod handling a specific chat room. This ensures that each chat room is managed by a specific pod that has a stable network identity, even across restarts.

4. **Fault Tolerance & Automatic Recovery**:  
   If a pod handling a specific room fails, ZooKeeper automatically re-elects a new leader, and the chat system continues to function without downtime. This ensures that the chat rooms remain operational even when failures occur.

---

### How It Works

1. **Leader Election with ZooKeeper**:  
   When a chat room is created, ZooKeeper initiates a leader election. The leader pod for the room takes on the responsibility of handling critical operations, such as storing messages in Redis and moderating the chat room. Only one pod can hold the leadership role at any time, ensuring that there is no conflict between different pods.

2. **Message Storage and Publishing**:  
   Once the leader is elected, the pod stores the incoming message in Redis and publishes it to the corresponding Redis channel using **Pub/Sub**. All other pods that have subscribed to this channel will receive the message in real-time. This allows for a smooth, low-latency communication experience.

3. **Message Retrieval**:  
   Redis not only stores the real-time messages but also keeps a history of messages for each room, ensuring that users can retrieve past messages. The messages are stored in Redis lists and are accessible through Redis commands.

4. **Pod Management with Kubernetes**:  
   Each chat room is handled by a specific pod in Kubernetes, and these pods are deployed using **StatefulSets**. StatefulSets ensure that the pods have a stable identity and can persist room-specific data.
   
   **Zookeeper** and **Redis** are deployed as services in the same Kubernetes cluster to allow internal communication between the pods.

5. **Pod Communication**:  
   Each pod in the StatefulSet represents a chat room. The pods communicate with each other via Kubernetes service names (`zookeeper` for ZooKeeper and `redis` for Redis).  
   When a message is received, the leader pod for the chat room stores it in Redis and publishes it to the Redis channel for that room. Other pods that are subscribed to the Redis channel for that room receive the message in real-time.

---

### Key Technologies Used

1. **ZooKeeper**:
   - Used for leader election and ensuring synchronization across multiple pods managing chat rooms.
   - Handles fault tolerance by re-electing a leader if a pod crashes or becomes unreachable.

2. **Redis**:
   - A fast, in-memory key-value store used for storing messages in real-time.
   - Redis' Pub/Sub functionality is used to broadcast messages across all subscribed clients.

3. **Kubernetes**:
   - Manages the deployment of pods using StatefulSets, ensuring stable identities for each chat room.
   - Handles scaling, resource management, and fault tolerance.

4. **Flask**:
   - A lightweight web framework used to build the chat application's REST API.
   - Handles user interactions, message publishing, and managing chat rooms.

---

### How to Run the Application Locally or in Kubernetes

1. **Running Locally**:
   - Make sure **ZooKeeper** and **Redis** are running locally on your machine (or use Docker containers for them).
   - Set the appropriate `ZOOKEEPER_HOST` and `REDIS_HOST` environment variables in your Flask app.
   - Run the Flask app locally using:

     ```bash
     python server.py
     ```

2. **Running in Kubernetes**:
   - Deploy **ZooKeeper** and **Redis** using Kubernetes.
   - Update the Flask app's connection settings to use the Kubernetes service names for ZooKeeper and Redis (`zookeeper:2181`, `redis:6379`).
   - Deploy the Flask app as a StatefulSet in Kubernetes, ensuring that each pod represents a different chat room.

---

### Testing the Chat System

Once deployed, you can test the system using the following steps:

1. **Create a Chat Room**:  
   Use the `/create_room` API to create a new chat room.

2. **Send a Message**:  
   Use the `/send_message` API to send a message to a specific chat room. Messages will be stored in Redis and published to the room's Redis channel.

3. **Subscribe to a Room**:  
   Use the `/subscribe` API to subscribe to a chat room and receive messages in real-time via Redis Pub/Sub.

---

### Future Improvements

- **User Authentication**:  
  Implement user authentication to allow users to join rooms, send private messages, and more.

- **Scalability**:  
  Optimize the system to handle thousands of chat rooms and users simultaneously.

- **Error Handling and Logging**:  
  Improve error handling, logging, and monitoring for better debugging and production readiness.

- **UI Development**:  
  Build a front-end interface (e.g., React.js) to interact with the chat system and display messages in real-time.

---

### Conclusion

This project represents a highly scalable, fault-tolerant, and real-time chat system that leverages the power of **ZooKeeper** for coordination and synchronization and **Redis** for fast message storage and real-time communication. By using **StatefulSets** in Kubernetes for each chat room, we ensure that the system is resilient, scalable, and easy to manage. ZooKeeper handles leader election and synchronous execution, while Redis manages real-time messaging and message storage. The architecture provides a robust and efficient foundation for building a distributed chat system that can handle real-time interactions and scale as needed.

---


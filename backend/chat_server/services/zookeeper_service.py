from kazoo.client import KazooClient
from kazoo.recipe.lock import Lock
from kazoo.recipe.election import Election
import logging
import time
import threading

class ZookeeperService:
    #def __init__(self, hosts='zookeeper:2181'):
    def __init__(self, hosts='zookeeper:2181'):    
        """Establish connection with ZooKeeper server"""
        self.zk = KazooClient(hosts=hosts)
        self.zk.add_listener(self._zk_listener)
        self.zk.start()
        self.max_retries = 5  # Increased retries for more robust handling of temporary disconnects
        self.election_lock = threading.Lock()  # Synchronize leader election

    def _zk_listener(self, state):
        """Listener to log ZooKeeper connection state"""
        if state == "SUSPENDED":
            print("ZooKeeper connection suspended")
            logging.warning("ZooKeeper connection suspended.")
        elif state == "LOST":
            print("ZooKeeper connection lost")
            logging.error("ZooKeeper connection lost.")
        elif state == "CONNECTED":
            print("ZooKeeper connection established")
            logging.info("ZooKeeper connection established.")
        else:
            print(f"ZooKeeper state changed: {state}")
            logging.info(f"ZooKeeper state changed: {state}")

    def reconnect(self):
        """Reconnect to ZooKeeper if the connection is lost"""
        retries = 0
        while retries < self.max_retries:
            try:
                print("Attempting to reconnect to ZooKeeper...")
                self.zk.stop()  # Ensure previous session is properly closed
                self.zk.start()  # Reconnect to ZooKeeper
                if self.zk.connected:
                    print("Reconnected to ZooKeeper.")
                    return
            except Exception as e:
                retries += 1
                print(f"Reconnection attempt {retries} failed, retrying in {2**retries}s...")
                time.sleep(2 ** retries)  # Exponential backoff
        print("Failed to reconnect to ZooKeeper after multiple attempts.")
        logging.error("Failed to reconnect to ZooKeeper after multiple attempts.")

    def reconnect_if_needed(self):
        """Reconnect to ZooKeeper if the connection is lost"""
        if not self.zk.connected:
            print("ZooKeeper connection lost. Reconnecting...")
            self.reconnect()

    def wait_for_zookeeper(self):
        """Wait until ZooKeeper is fully connected"""
        while not self.zk.connected:
            print("Waiting for ZooKeeper to be fully connected...")
            time.sleep(2)  # Sleep and retry until ZooKeeper is connected
        print("ZooKeeper is now ready.")

    def create_server_node(self, server_name):
        """Register Server in ZooKeeper for service discovery"""
        server_node = f"/chat/servers/{server_name}"
        if not self.zk.exists('/chat/servers'):
            self.zk.create('/chat/servers', b"", makepath=True)  # Create the parent path if it doesn't exist

        if not self.zk.exists(server_node):
            self.zk.create(server_node, b"")
            print(f"Server {server_name} registered in ZooKeeper.")

    def acquire_lock(self, room):
        """Acquire lock for the given room using ZooKeeper"""
        lock = Lock(self.zk, f"/locks/{room}")
        print(f"Acquiring lock on room {room}")
        lock.acquire()
        print(f"Acquired lock on room {room}")
        return lock

    def release_lock(self, lock):
        """Release a lock for a room"""
        try:
            if self.zk.connected:
                lock.release()
                print("Lock released")
            else:
                print("ZooKeeper connection lost. Cannot release lock.")
        except Exception as e:
            print(f"Error while releasing lock: {str(e)}")


    def elect_leader(self, room, on_leader):
        """Elect a leader for a room, with automatic re‐entry on session loss."""
        # 1) Remember these args so we can re‐run on session LOST
        self.election_args = {'room': room, 'on_leader': on_leader}

        # 2) Build & ensure the election znode
        election_path = f"/chat/rooms/{room}/election"
        self.wait_for_zookeeper()
        self.zk.ensure_path(election_path)

        # 3) Try to elect up to max_retries times
        retries = 0
        while retries < self.max_retries:
            if not self.zk.connected:
                print("ZooKeeper not connected; reconnecting before election…")
                self.reconnect_if_needed()
                time.sleep(2)
                retries += 1
                continue

            try:
                with self.election_lock:
                    print(f"Electing leader for room: {room}")
                    election = Election(self.zk, election_path)
                    election.run(on_leader)   # blocks until you become leader, then calls on_leader()
                    print("Leader elected successfully.")
                    return
            except Exception as e:
                print(f"Error during leader election: {e}")
                self.reconnect_if_needed()
                time.sleep(2)
                retries += 1

        print("✖ Leader election process completed (no leader elected).")

    

    def stop(self):
        """Close the ZooKeeper connection"""
        self.zk.stop()

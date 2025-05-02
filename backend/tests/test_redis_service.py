import unittest
from redis_service import RedisService

class TestRedisService(unittest.TestCase):
    def setUp(self):
        self.redis_service = RedisService(host='localhost' , port=6379)

    def test_store_message(self):
        room = 'room1'
        message = 'Hello, Room1!'
        self.redis_service.store_message(room,message)
        messages = self.redis_service.get_message(room)
        self.assertIn(message,messages)


    def test_publish_messages(self):
        room = 'room1'
        message = 'Real Time Message!'
        pubsub = self.redis_service.subscribe_to_room(room)
        self.redis_service.publish_message(room,message)
        for msg in pubsub.listen():
            if msg['type'] == 'message':
                self.assertEqual(msg['data'].decode('utf-8'),message)
                break

if __name__ == "__main__":
    unittest.main()
    


    
import requests

rooms = ["room1", "room2", "room3", "room4"]
message = "Test message from Python script"

for room in rooms:
    response = requests.post(
        "http://127.0.0.1:5050/send_message",
        json={"room": room, "message": message}
    )
    print(f"Sent message to {room}: {response.json()}")

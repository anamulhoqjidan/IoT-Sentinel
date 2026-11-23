
import paho.mqtt.client as mqtt

# MQTT broker configuration
BROKER = "localhost"
PORT = 1883
TOPIC = "iot/device01/traffic"


# Called when the client connects to the broker
def on_connect(client, userdata, flags, reason_code, properties):
    print("Connected to MQTT Broker!")

    # Subscribe to our IoT traffic topic
    client.subscribe(TOPIC)
    print(f"Subscribed to: {TOPIC}")


# Called whenever a message arrives
def on_message(client, userdata, msg):
    print("\nReceived IoT Event:")
    print(f"Topic: {msg.topic}")
    print(f"Message: {msg.payload.decode('utf-8')}")


# Create MQTT client (Paho MQTT 2.x)
client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    client_id="netshieldx_subscriber"
)

# Register callbacks
client.on_connect = on_connect
client.on_message = on_message

# Connect to Mosquitto
client.connect(BROKER, PORT, 60)

print("Starting MQTT Subscriber...")
client.loop_forever()

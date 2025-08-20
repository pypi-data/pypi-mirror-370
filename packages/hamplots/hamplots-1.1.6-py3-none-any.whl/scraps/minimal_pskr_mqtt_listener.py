import paho.mqtt.client as mqtt
import ast
import datetime

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    for i in range(5,10):
        for j in range(0,10):
            rxsq = f"IO{i}{j}"
            topic1 = 'pskr/filter/v2/+/+/+/+/+/' + rxsq + '/+/#';
            client.subscribe(topic1)

def on_message(client, userdata, msg):
    d = ast.literal_eval(msg.payload.decode())
    t = datetime.datetime.fromtimestamp(d['t'])
    f.write(f"{str(t).replace(' ','_')} {d['f']/1e6} {d['md']} "
           +f"{d['rp']} {d['sc']} {d['sl']} {d['rc']} {d['rl']}\n")

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect("mqtt.pskreporter.info", 1883, 60)
f = open("decodes.txt","w")
mqttc.loop_forever()

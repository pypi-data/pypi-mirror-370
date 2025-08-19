import paho.mqtt.client as mqtt
import ast
import datetime
import time

def str_to_list(myStr):
    return [o.strip() for o in myStr.split(",")]

class pskr_listener:
    def __init__(self, squares, bands="20m", modes="FT8", TxRx = "Rx", to_file=""):
        self.decodes = []
        self.squares = str_to_list(squares)
        self.bands = str_to_list(bands)
        self.modes = str_to_list(modes)
        self.TxRx = TxRx
        self.mqtt_cl = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id = f"subscribe-{self.TxRx}")
        self.mqtt_cl.on_connect = self.subscribe
        self.mqtt_cl.on_message = self.add_decode
        self.mqtt_cl.connect("mqtt.pskreporter.info", 1883, 60)
        self.to_file = to_file

    def loop_for_time(self, time_seconds):
        if(time_seconds > 3600):
            self.mqtt_cl.loop_forever()
        else:
            self.mqtt_cl.loop_start()
            time.sleep(time_seconds)
            self.mqtt_cl.loop_stop()

    def loop_forever(self):
        self.mqtt_cl.loop_forever()

    def disconnect(self):
        self.mqtt_cl.disconnect()  

    def subscribe(self, client, userdata, flags, reason_code, properties):
        # pskr/filter/v2/{band}/{mode}/{sendercall}/{receivercall}/{senderlocator}/{receiverlocator}/{sendercountry}/{receivercountry}
        print(f"Connected: {reason_code}")
        for sq in self.squares:
            for b in self.bands:
                for md in self.modes:
                    print(f"Subscribe to {self.TxRx} in {sq} on {b} {md}")
                    tailstr = f"+/+/{sq}/+/+/#" if self.TxRx == "Tx" else f"+/+/+/{sq}/+/#"
                    client.subscribe(f"pskr/filter/v2/{b}/{md}/{tailstr}")

    def add_decode(self, client, userdata, msg):
        d = ast.literal_eval(msg.payload.decode())
        d['sl'] = d['sl'].upper()
        d['rl'] = d['rl'].upper()
        d.update({'TxRx':self.TxRx})
        d.update({'hc':  d['rc'] if self.TxRx =="Rx" else d['sc']})
        d.update({'hl':  d['rl'] if self.TxRx =="Rx" else d['sl']})
        d.update({'ha':  d['ra'] if self.TxRx =="Rx" else d['sa']})
        d.update({'oc':  d['sc'] if self.TxRx =="Rx" else d['rc']})
        d.update({'ol':  d['sl'] if self.TxRx =="Rx" else d['rl']})
        d.update({'oa':  d['sa'] if self.TxRx =="Rx" else d['ra']})
        if(self.to_file !=""):
            with open(self.to_file, 'a') as f:
                ebfm = f"{d['t']}, {d['b']}, {d['f']}, {d['md']}, "
                spot = f"{d['hc']}, {d['hl']}, {d['ha']}, {d['TxRx']}, {d['oc']}, {d['ol']}, {d['oa']}, {d['rp']}\n"
                f.write(ebfm+spot)
                f.flush()





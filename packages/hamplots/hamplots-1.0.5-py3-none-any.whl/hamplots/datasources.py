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
        self.mqtt_cl.loop_start()
        time.sleep(time_seconds)
        self.mqtt_cl.loop_stop()

    def loop_forever(self):
        self.mqtt_cl.loop_forever()

    def get_decodes(self):    
        return self.decodes

    def disconnect(self):
        self.mqtt_cl.disconnect()  

    def purge_decodes(self, epoch):
        n1 = len(self.decodes)
        self.decodes = [d for d in self.decodes if int(d["t"]) >= epoch]
        n2 = len(self.decodes)
        print(f"Purged {n1-n2} decodes of {n1}")

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
        else:
            self.decodes.append(d)

    def write_csv(self, decodes = None, filepath = ""):
        if(decodes == None):
            decodes = self.decodes
        if(filepath == ""):
            filepath =  f"{self.TxRx}_decodes.csv"
        print(f"Writing {len(decodes)} decodes to {filepath}")
        with open(filepath, "w") as f:
            for d in decodes:
                ebfm = f"{d['t']}, {d['b']}, {d['f']}, {d['md']}, "
                spot = f"{d['hc']}, {d['hl']}, {d['ha']}, {d['TxRx']}, {d['oc']}, {d['ol']}, {d['oa']}, {d['rp']}\n"
                f.write(ebfm+spot)
            f.flush()





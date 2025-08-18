
import StealthContest as sc

mySquares = "IO80,IO81,IO82,IO90,IO91,IO92,JO01,JO02,JO03"
listener = sc.pskr_listener(mySquares)

for i in range(30):
    listener.loop(2)

listener.write_csv()


myBands = "20m,15m"
myModes = "FT8,FT4"
parallel_listener = sc.pskr_listener(mySquares,  direction = "Tx")
for i in range(30):
    listener.loop(2)
    parallel_listener.loop(1)
    rx_decodes = listener.get_decodes()
    tx_decodes = parallel_listener.get_decodes()
    listener.write_csv(decodes = rx_decodes + tx_decodes, filepath="demo_combined.csv")


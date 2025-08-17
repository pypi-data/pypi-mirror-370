
import StealthContest as sc

mySquares = "IO80,IO81,IO82,IO90,IO91,IO92,JO01,JO02,JO03"
listener = sc.pskr_listener(mySquares, bands="2m")

while(True):
    for i in range(30):
        listener.loop(2)
    listener.write_csv()





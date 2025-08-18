def str_to_epoch(t_str):
    import datetime
    yy = int(t_str[0:4])
    m = int(t_str[5:7])
    dd = int(t_str[8:10])
    hh = int(t_str[11:13])
    mm = int(t_str[14:16])
    ss = int(t_str[17:19])
    return datetime.datetime(yy,m,dd,hh,mm,ss).timestamp()

with open("../decodes.csv") as f:
    lines = f.readlines()
    for i, l in enumerate(lines):
        t = int(str_to_epoch(l.split(", ")[0]))
        lnew = l.split(", ")
        lnew[0] = f"{t}"
        lines[i] = ", ".join(lnew)

with open("../decodes2.csv","w") as f:
    for l in lines:
        f.write(l)
        

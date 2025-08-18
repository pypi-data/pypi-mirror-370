
class wsjt:
    """
        not used currently so needs a lot of checking
    """
    
    def parse_line_datetime(line):
        ## includes kludge to convert to BST
         return datetime.datetime(2000+int(line[0:2]),int(line[2:4]),int(line[4:6]),
                                 (int(line[7:9])+1) % 24, int(line[9:11]), int(line[11:13]) ).timestamp()

    def parse_line(line):
        import re
        dt = parse_line_datetime(line)
        ls = line.split()
        if len(ls) == 10:
            sq = ls[9]
            if(re.search("[A-R][A-R][0-9][0-9]",sq) and sq != "RR73"):            
                return {
                    "dt": dt,
                    "f": float(ls[1])*1e6,
                    "sc": ls[8],
                    "rc": "G1OJS",
                    "rp": float(ls[4]),
                    "sl": ls[9],
                    "rl": "IO90",
                    "km": None,
                    "deg":None
                }
            
    def read_ALLTXT(fpath, dt_first, home_square):
       # print(f"{fpath}")
        with open(fpath) as f:
            lines = f.readlines()
        decodes_all = []

        km = {}
        deg = {}
        nrecs = 0
        for l in lines:
            if(len(l)>100):
                continue
            dt = parse_line_datetime(l)
            if(dt < dt_first):
                continue
            decode = parse_line(l)
            if decode:
                sc = decode["sc"]
                if(sc not in km):
                    kmdeg = sq_km_deg(decode["sl"], home_square)
                    if(kmdeg):
                        km[sc], deg[sc] = kmdeg
                decodes_all.append(decode)
                nrecs += 1
      #    print(f"Read {len(lines)} lines with {nrecs} decodes in session time window\n")
        return decodes_all


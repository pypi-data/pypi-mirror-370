import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os.path

def str_to_list(myStr):
    return [o.strip() for o in myStr.split(",")]


def tabulate_reports(remote_calls, homecall_reports):
    # flatten nested dict
    records = []
    for hc, rc_dict in homecall_reports.items():
        for rc, rplist in rc_dict.items():
            for rp in rplist:
                records.append((rc, hc, int(rp)))

    df = pd.DataFrame(records, columns=["remote", "home", "report"])
    # pivot to table of max report for each home callsign
    pivot = df.groupby(["remote", "home"])["report"].max().unstack(fill_value=-30)
    pivot = pivot.reindex(index=remote_calls, columns=homecall_reports.keys(), fill_value=-30)

    return pivot.index.tolist(), pivot.columns.tolist(), pivot.values.tolist()


def build_connectivity_info(decodes, start_epoch = 0, bands = "20m", modes = "FT8"):
    """
        returns:
         calls[callsign] = nSpots
         spots[homecall] = [reports]
    """
    remote_calls = {}
    homecall_reports = {}
    bands = str_to_list(bands)
    modes = str_to_list(modes)

    for d in decodes:
        if(int(d['t']) < start_epoch or d['b'] not in bands or d['md'] not in modes):
            continue
        homecall_reports.setdefault(d['hc'],{})
        homecall_reports[d['hc']].setdefault(d['oc'],[]).append(d['rp'])
        remote_calls.setdefault(d['oc'],0)
        remote_calls[d['oc']] += 1
    return remote_calls, homecall_reports

        
def cover_home_calls(calls, spots):
    """
    calls: dict {remote_call: count_of_reports}
    spots: dict {home_call: {remote_call: [reports...]}}
    
    Returns: list of remote calls needed to cover all home calls,
             or False if impossible.
    """
    # sort remotes by number of reports (descending)
    sorted_calls = sorted(calls, key=calls.get, reverse=True)
    
    # set of home calls that still need coverage
    uncovered = set(spots.keys())
    needed = []
    
    for rc in sorted_calls:
        # check which home calls this remote covers
        covers = {hc for hc, rcs in spots.items() if rc in rcs}
        if not covers:
            continue
        needed.append(rc)
        uncovered -= covers
        if not uncovered:  # all home calls covered
            return needed
    
    return False  # some home calls never got covered


def read_csv(filepath =  "decodes.csv", start_epoch = 0):
    if (not os.path.isfile(filepath)):
        return False
    
    decodes = []
    with open(filepath, "r") as f:
        for l in f.readlines():
            if('\x00' in l):
                continue
            ls=l.strip().split(", ")
            if(len(ls) == 12):
                d = {'t':ls[0], 'b':ls[1], 'f':ls[2], 'md':ls[3], 'hc':ls[4], 'hl':ls[5], 'ha':ls[6], 'TxRx':ls[7], 'oc':ls[8], 'ol':ls[9], 'oa':ls[10], 'rp':ls[11]}
                if(int(d['t']) < start_epoch):
                    continue
                decodes.append(d)
            
    print(f"Read {len(decodes)} decodes from {filepath}")
    return decodes









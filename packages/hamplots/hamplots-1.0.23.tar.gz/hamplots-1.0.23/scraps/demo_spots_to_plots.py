
import StealthContest as sc
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

cs_colors={}
def get_color_for_callsign(cs):
    if cs not in cs_colors:
        # pick a color from matplotlib's tab20 palette, cycling if needed
        all_colors = list(mcolors.TABLEAU_COLORS.values())
        cs_colors[cs] = all_colors[len(cs_colors) % len(all_colors)]
    return cs_colors[cs]


listener = sc.pskr_listener("IO80,IO81,IO82,IO90,IO91,IO92,JO01,JO02,JO03")

fig, ax = plt.subplots()
plt.ion()

while(True):
    for i in range(5):
        listener.loop(1)

    decodes = listener.get_decodes()
    decodes_by_homecall = {}
    for i, d in enumerate(decodes):
        decodes_by_homecall.setdefault(d['hc'],[]).append({'oc':d['oc'],'rp':d['rp']})
    print("home calls:")
    for c in sorted(decodes_by_homecall):
        print(c)

    decodes_by_homecall_sorted = sorted(decodes_by_homecall, key=lambda hc: max(rp['rp'] for rp in decodes_by_homecall[hc]), reverse=True)
    
    x_vals = []
    y_vals = []
    cols = []
    for i, hc in enumerate(decodes_by_homecall_sorted):
        for d in decodes_by_homecall[hc]:
            x_vals.append(hc)
            y_vals.append(d['rp'])
            cols.append(get_color_for_callsign(d['oc']))

    plt.cla()
    ax.scatter(x_vals, y_vals, c = cols, alpha=0.7)

    ax.tick_params("x", rotation=90, labelsize=6)


    plt.pause(5)




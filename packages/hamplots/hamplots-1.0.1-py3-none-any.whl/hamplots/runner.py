import argparse
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.image import NonUniformImage
import numpy as np
import time
import hamplots as hp
import os
import datetime

def my_pcolor(ax, fig, rowheads, colheads, cells):
    nx=len(colheads)
    ny=len(rowheads)
    x = np.arange(0.5,nx+0.5)
    y = np.arange(0.5,ny+0.5)
    xfs = max(4,min(12,0.7*72*fig.get_figwidth() / nx))
    ax.set_xticks(x, labels=colheads, rotation="vertical", fontsize = xfs)
    yfs = max(4,min(12,0.7*72*fig.get_figheight() / ny))
    ax.set_yticks(y, labels=rowheads, rotation="horizontal", fontsize = yfs)
    ax.pcolor(cells)
    ax.tick_params(top=True, bottom=False, labeltop=True, labelbottom=False)

mySquares = "IO80,IO81,IO82,IO90,IO91,IO92,JO01,JO02,JO03"
myBands = "40m, 20m, 15m, 10m, 2m"
myModes = "FT8, FT4"
    
def start_rx(runsecs):
    rx_listener = hp.pskr_listener(mySquares, modes = myModes, bands = myBands, TxRx = "Rx", to_file = "Rx_decodes.csv")
    rx_listener.loop_for_time(runsecs);
    rx_listener.disconnect();

def start_tx(runsecs):
    tx_listener = hp.pskr_listener(mySquares, modes = myModes, bands = myBands, TxRx = "Tx", to_file = "Tx_decodes.csv")
    tx_listener.loop_for_time(runsecs);
    tx_listener.disconnect();

def do_plots():
    for RxTx in ["Rx","Tx"]:
        decodes = hp.read_csv(f"{RxTx}_decodes.csv")
        if(not decodes):
            continue
        
        for band in myBands.split(", "):
            for mode in myModes.split(", "):
                print(f"Rx_{band}_{mode}")

                remote_calls, homecall_reports = hp.build_connectivity_info(decodes, bands=band, modes=mode)
                remote_calls = hp.cover_home_calls(remote_calls, homecall_reports)
                
                if remote_calls:
                    if(len(remote_calls) < 3):
                        continue
                    rowheads, colheads, cells = hp.tabulate_reports(remote_calls, homecall_reports)

                    # build DataFrame
                    import pandas as pd
                    cells = pd.DataFrame(cells, index=rowheads, columns=colheads)
                    
                    # sort
                    nRemotes_in_row = cells.replace(-30, np.nan).count(axis=1)
                    nRemotes_in_column = cells.replace(-30, np.nan).count(axis=0)
                   # mean_snr_in_column = cells.mean(axis=0)
                    cells = cells.loc[nRemotes_in_row.sort_values(ascending=True).index,
                                    nRemotes_in_column.sort_values(ascending=False).index]
                    cells = cells.replace(-30, -70)

                    # plot
                    timestr = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                    fig, axs = plt.subplots()
                    remote_action = "Transmitting" if RxTx == "Rx" else "Receiving"
                    home_entities = "receivers" if RxTx == "Rx" else "transmitters"
                    axs.set_ylabel(f"{remote_action} callsign")
                    axs.set_title(f"SNR Heatmap for home {home_entities} on {band} {mode}\n{timestr}")
                    
                    my_pcolor(axs,fig, rowheads, colheads, cells)
                    plt.tight_layout()
                 
                    if not os.path.exists("plots"):
                        os.makedirs("plots")
                    plt.savefig(f"plots/{RxTx}_{band}_{mode}.png")
                    plt.close()


def get_args_and_run():
    from importlib.metadata import version
    try:
        __version__ = version("hamplots")
    except:
        __version__ = ""
    print(f"Hamplots {__version__} by Dr Alan Robinson")
    parser = argparse.ArgumentParser()
    parser.add_argument('action', type=str)
    parser.add_argument('--runsecs', type=str, default = "30")
    args = parser.parse_args()
    print(f"args.action = .{args.action}.")
    if(args.action == "start_rx"):
        start_rx(int(args.runsecs))
    if(args.action == "start_tx"):
        start_tx(int(args.runsecs))
    if(args.action == "do_plots"):
        do_plots()
        

# if run from an IDE:
if __name__ == "__main__":
    print("Edit the lines below this to run what you need")
   # start_tx()
   # start_rx()
    do_plots()





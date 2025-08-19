import argparse
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
import time
import hamplots as hp
import os
import datetime
import subprocess

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
    print("Start Rx")
    rx_listener = hp.pskr_listener(mySquares, modes = myModes, bands = myBands, TxRx = "Rx", to_file = "Rx_decodes.csv")
    rx_listener.loop_for_time(runsecs);
    print("Disconnect Rx")
    rx_listener.disconnect();

def start_tx(runsecs):
    print("Start Tx")
    tx_listener = hp.pskr_listener(mySquares, modes = myModes, bands = myBands, TxRx = "Tx", to_file = "Tx_decodes.csv")
    tx_listener.loop_for_time(runsecs);
    print("Disconnect Tx")
    tx_listener.disconnect();

def do_plots(timewin_start_offset_secs):
    for RxTx in ["Rx","Tx"]:
        decodes = hp.read_csv(f"{RxTx}_decodes.csv")
        if(not decodes):
            continue

        timewin_start = time.time() - timewin_start_offset_secs
        for band in myBands.split(", "):
            for mode in myModes.split(", "):
                print(f"Rx_{band}_{mode}")

                remote_calls, homecall_reports = hp.build_connectivity_info(decodes, start_epoch = timewin_start, bands=band, modes=mode)
                remote_calls = hp.cover_home_calls(remote_calls, homecall_reports)

                # plot setup
                timestr = datetime.datetime.now().strftime("%d/%m/%Y %H:%M UTC")
                fig, axs = plt.subplots()
                remote_action = "Transmitting" if RxTx == "Rx" else "Receiving"
                home_entities = "Receivers'" if RxTx == "Rx" else "Transmitters'"
                axs.set_ylabel(f"{remote_action} callsign")
                plt.suptitle(f"Activity over last {timewin_start_offset_secs/60:.0f} minutes\n to/from {mySquares}")
                axs.set_title(f"{home_entities} SNR on {band} {mode}, to {timestr}")
                
                if remote_calls:
                    rowheads, colheads, cells = hp.tabulate_reports(remote_calls, homecall_reports)
                    print(f" ... analysing {len(rowheads)} by {len(colheads)}")
                    
                    # build DataFrame
                    import pandas as pd
                    cells = pd.DataFrame(cells, index=rowheads, columns=colheads)
                    
                    # sort criteria
                    nRemotes_in_row = cells.replace(-30, np.nan).count(axis=1)
                    nRemotes_in_column = cells.replace(-30, np.nan).count(axis=0)
                   # mean_snr_in_column = cells.mean(axis=0)

                    # do sort
                    cells = cells.loc[nRemotes_in_row.sort_values(ascending=True).index,
                                    nRemotes_in_column.sort_values(ascending=False).index]
                    cells = cells.replace(-30, -70)
                
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
    parser.add_argument('action', type=str, help = "start_rx|start_tx|--runsecs nsecs|--plotsecs nsecs")
    parser.add_argument('--runsecs', type=str, default = "30", help = "Run mqtt listener for runsecs seconds")
    parser.add_argument('--plotsecs', type=str, default = "600", help = "Create plots covering now to now minus plotsecs seconds")
    args = parser.parse_args()
    print(f"args.action = .{args.action}.")
    if(args.action == "start_rx"):
        start_rx(int(args.runsecs))
    if(args.action == "start_tx"):
        start_tx(int(args.runsecs))
    if(args.action == "do_plots"):
        do_plots(int(args.plotsecs))
    if(args.action == "do_all"):
        start_rx(int(args.runsecs))
        start_tx(int(args.runsecs))
        do_plots(int(args.plotsecs))
    if(args.action == "start_local_capture"):
        subprocess.Popen("hamplots start_rx --runsecs 1000000", creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.Popen("hamplots start_tx --runsecs 1000000", creationflags=subprocess.CREATE_NO_WINDOW)







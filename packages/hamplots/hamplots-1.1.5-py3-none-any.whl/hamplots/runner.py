import argparse
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
import time
import hamplots as hp
import os
import datetime
import subprocess

global myBands, myModes, mySquares

def get_cfg():
    global myBands, myModes, mySquares
    with open("hamplots.cfg","r") as f:
        lines = f.readlines()
    mySquares = [e.strip() for e in lines[0].split(",")]
    myBands = [e.strip() for e in lines[1].split(",")]
    myModes = [e.strip() for e in lines[2].split(",")]
    print(f"mySquares {mySquares}")
    print(f"myBands {myBands}")
    print(f"myModes {myModes}")


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

def start_all(refreshsecs, plotwinsecs):
    print("Starting Rx listener")
    subprocess.Popen(["hamplots", "start_rx", "--runsecs", "1000000"], creationflags=subprocess.CREATE_NO_WINDOW)
    print("Starting Tx listener")
    subprocess.Popen(["hamplots", "start_tx", "--runsecs", "1000000"], creationflags=subprocess.CREATE_NO_WINDOW)
    print(f"Starting Uploader with period {refreshsecs} secs and plot window {plotwinsecs} secs")
    while (True):
        time.sleep(refreshsecs)
        repo_dir = r"C:\Users\drala\Documents\Projects\GitHub\hamplots"
        subprocess.run(["hamplots", "do_plots", "--plotwinsecs", str(plotwinsecs)], cwd = repo_dir)
        subprocess.run(["git", "add", "-f", "./plots/*.png"], cwd=repo_dir)
        subprocess.run(["git", "add", "-f", "./plots/timestamp"], cwd=repo_dir)
        subprocess.run(["git", "commit", "-m", "upload local data"], cwd=repo_dir)
        subprocess.run(["git", "pull"], cwd=repo_dir)
        subprocess.run(["git", "clean", "-f"], cwd=repo_dir)
        subprocess.run(["git", "push", "-f"], cwd=repo_dir)
        subprocess.run(["git", "reset"], cwd=repo_dir)

def timestamp_plots():
    t = int(time.time())
    with open("plots/timestamp","w") as f:
        f.write(f"{t}\n")

def check_plots_are_old(refresh_secs):
    print(f"Checking age of existing plots")

    # if existing plots are younger than one refresh cycle, leave as-is
    if os.path.exists("plots/timestamp"):
        with open("plots/timestamp","r") as f:
            t = int(f.readline())
        age = int(time.time()- t)
        print(f"Existing plots were created {age} seconds ago (refresh cycle is {refresh_secs} secs)")
    else:
        print("No timestamp found: assuming plots are old")
        age = 1000000
    return (age > refresh_secs)
 

def do_plots(timewin_start_offset_secs):
    print(f"Starting plots with time window {timewin_start_offset_secs} secs")

    for RxTx in ["Rx","Tx"]:
        decodes = hp.read_csv(f"{RxTx}_decodes.csv")
        if(not decodes):
            continue

        timewin_start = time.time() - timewin_start_offset_secs
        for band in myBands:
            for mode in myModes:
                print(f"Rx_{band}_{mode}")

                remote_calls, homecall_reports = hp.build_connectivity_info(decodes, start_epoch = timewin_start, bands=band, modes=mode)
                remote_calls = hp.cover_home_calls(remote_calls, homecall_reports)

                # plot setup
                timestr = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
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
    parser.add_argument('action', type=str, help = "start_rx|start_tx|do_plots|start_all|--runsecs nsecs|--plotwinsecs nsecs|--refreshsecs nsecs")
    parser.add_argument('--runsecs', type=str, default = "30", help = "Run mqtt listener for runsecs seconds")
    parser.add_argument('--plotwinsecs', type=str, default = "600", help = "Create plots covering now to now minus plotwinsecs seconds")
    parser.add_argument('--refreshsecs', type=str, default = "600", help = "Upload to github every refreshsecs seconds")
 
    args = parser.parse_args()
    get_cfg()

    print(f"args.action = .{args.action}.")
    if(args.action == "start_rx"):
        start_rx(int(args.runsecs))
    if(args.action == "start_tx"):
        start_tx(int(args.runsecs))
    if(args.action == "do_plots"):
        if check_plots_are_old(int(args.refreshsecs)):
            do_plots(int(args.plotwinsecs))
            timestamp_plots()
    if(args.action == "do_all"):
        if check_plots_are_old(int(args.refreshsecs)):
            start_rx(int(args.runsecs))
            start_tx(int(args.runsecs))
            do_plots(int(args.plotwinsecs))
            timestamp_plots()
    if(args.action == "start_uploader"):
        do_periodic_uploads(int(args.refreshsecs))

    if(args.action == "start_all"):
        start_all(int(args.refreshsecs), int(args.plotwinsecs))




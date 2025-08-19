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

def do_plots(timewin_start_offset_secs, refresh_secs):
    print(f"Starting plots with refresh {refresh_secs} secs, time window {timewin_start_offset_secs} secs")

    # if existing plots are younger than one refresh cycle, leave as-is
    random_plot = os.path.join("plots", os.listdir("plots")[0])
    age = int(time.time()- os.path.getmtime(random_plot))
    print(f"Existing plots were created {age} seconds ago")
    if (age < refresh_secs):
        print("Leaving these in place")
        return

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
    global mySquares, myBands, myModes
    
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
    parser.add_argument('--bands', type=str, default = "40m, 20m, 15m, 10m, 2m", help = "Bands to scan")
    parser.add_argument('--modes', type=str, default = "FT8, FT4", help = "Modes to scan")
    parser.add_argument('--squares', type=str, default = "IO80,IO81,IO82,IO90,IO91,IO92,JO01,JO02,JO03", help = "Squares to define home")

    args = parser.parse_args()
    mySquares = args.squares
    myBands = args.bands
    myModes = args.modes

    print(f"args.action = .{args.action}.")
    if(args.action == "start_rx"):
        start_rx(int(args.runsecs))
    if(args.action == "start_tx"):
        start_tx(int(args.runsecs))
    if(args.action == "do_plots"):
        do_plots(int(args.plotwinsecs), int(args.refreshsecs))
    if(args.action == "do_all"):
        start_rx(int(args.runsecs))
        start_tx(int(args.runsecs))
        do_plots(int(args.plotwinsecs), int(args.refreshsecs))
    if(args.action == "start_uploader"):
        do_periodic_uploads(int(args.refreshsecs))

    if(args.action == "start_all"):
        print("Starting Rx listener")
        subprocess.Popen(["hamplots", "start_rx", "--runsecs", "1000000"], creationflags=subprocess.CREATE_NO_WINDOW)
        print("Starting Tx listener")
        subprocess.Popen(["hamplots", "start_tx", "--runsecs", "1000000"], creationflags=subprocess.CREATE_NO_WINDOW)
        refreshsecs = int(args.refreshsecs)
        plotwinsecs = int(args.plotwinsecs)
        print(f"Starting Uploader with period {refreshsecs} secs and plot window {plotwinsecs} secs")
        while (True):
            time.sleep(refreshsecs)
            repo_dir = r"C:\Users\drala\Documents\Projects\GitHub\hamplots"
            subprocess.run(["hamplots", "do_plots", "--plotwinsecs", str(plotwinsecs)], cwd = repo_dir)
            subprocess.run(["git", "add", "-f", "./plots/*.png"], cwd=repo_dir)
            subprocess.run(["git", "commit", "-m", "upload local data"], cwd=repo_dir)
            subprocess.run(["git", "pull"], cwd=repo_dir)
            subprocess.run(["git", "clean", "-f"], cwd=repo_dir)
            subprocess.run(["git", "push", "-f"], cwd=repo_dir)





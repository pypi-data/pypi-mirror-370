import argparse
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import time
import hamplots as hp
import os


mySquares = "IO80,IO81,IO82,IO90,IO91,IO92,JO01,JO02,JO03"
myBands = "40m, 20m, 15m, 10m, 2m"
myModes = "FT8, FT4"
    
def start_rx():
    rx_listener = hp.pskr_listener(mySquares, modes = myModes, bands = myBands, TxRx = "Rx", to_file = "Rx_decodes.csv")
    rx_listener.loop_for_time(30);
    rx_listener.disconnect();

def start_tx():
    tx_listener = hp.pskr_listener(mySquares, modes = myModes, bands = myBands, TxRx = "Tx", to_file = "Tx_decodes.csv")
    tx_listener.loop_for_time(30);
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
            #    remote_calls_needed = hp.cover_home_calls(remote_calls, homecall_reports)
                remote_calls_needed = remote_calls
                
                if remote_calls_needed:
                    rowheads, colheads, rows = hp.tabulate_reports(remote_calls_needed, homecall_reports)

                    # build DataFrame
                    import pandas as pd
                    data = pd.DataFrame(rows, index=rowheads, columns=colheads)
                    
                    # sort by counts
                    row_counts = data.replace(-30, np.nan).count(axis=1)
                    col_counts = data.replace(-30, np.nan).count(axis=0)
                    data = data.loc[row_counts.sort_values(ascending=False).index,
                                    col_counts.sort_values(ascending=False).index]

                    # mask missing values
                    mask = data == -30

                    # plot seaborn heatmap
                    plt.figure(figsize=(max(6, len(colheads)*0.5), max(4, len(rowheads)*0.5)))
                    sns.heatmap(data, mask=mask, annot=True, fmt="d", cmap="hot",
                                cbar_kws={"label":"SNR (dB)"})
                    plt.xlabel("Home stations")
                    plt.ylabel("Remote stations")
                    plt.title(f"{RxTx} {band} {mode}")
                    plt.xticks(rotation=90)
                    plt.yticks(rotation=0)
                  #  ax.xaxis.tick_top()
                  #  ax.xaxis.set_label_position('top')

                    timestamp = datetime.now().strftime("created on %y/%m/%d %H:%M")
                    fig.text(0.99, 0.01, timestamp,
                             ha='right', va='bottom',
                             fontsize=8, color='gray')
                    
                    plt.tight_layout()
                    if not os.path.exists("plots"):
                        os.makedirs("plots")
                    plt.savefig(f"plots/{RxTx}_{band}_{mode}.png")
                    plt.close()


def get_args_and_run():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', type=str)
    args = parser.parse_args()
    
    if(args.action == "start_rx"):
        start_rx()
    if(args.action == "start_tx"):
        start_tx()
    if(args.action == "do_plots"):
        do_plots()
        
if __name__ == "__main__":
    get_args_and_run()

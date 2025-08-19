import matplotlib.pyplot as plt


from matplotlib import cm
import numpy as np

def my_pcolor(ax, rowheads, colheads, cells):
    nx=len(colheads)
    ny=len(rowheads)
    x = np.arange(0.5,nx+0.5)
    y = np.arange(0.5,ny+0.5)
    xfs = max(6,min(18,0.8*72*fig.get_figwidth() / nx))
    ax.set_xticks(x, labels=colheads, rotation="vertical", fontsize = xfs)
    yfs = max(6,min(18,0.8*72*fig.get_figheight() / ny))
    ax.set_yticks(y, labels=rowheads, rotation="horizontal", fontsize = yfs)
    ax.pcolor(cells)
    ax.tick_params(top=True, bottom=False, labeltop=True, labelbottom=False)

fig, ax = plt.subplots()
rowheads = ["A","B","C"]
colheads = ["D","E","F"]
cells = [[0,0,0],[0,1,0],[1,1,0]]
my_pcolor(ax, rowheads, colheads, cells)

ax.set_title("title")

plt.show()

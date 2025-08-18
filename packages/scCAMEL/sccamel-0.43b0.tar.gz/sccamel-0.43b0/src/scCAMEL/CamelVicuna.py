# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from __future__ import annotations
import datetime
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn import manifold
from collections import defaultdict
#from mpl_toolkits.mplot3d import Axes3D
import math
import sklearn
import scipy
import openpyxl
from matplotlib.collections import PatchCollection
import os
import sys
import numpy as np
import pandas as pd
import anndata
from scipy import sparse
import gc
#imports
import pandas as pd
import pickle as pickle
from scipy.spatial.distance import cdist, pdist, squareform
#import backspinpy
#from backspinpy import fit_CV
#from backspinpy.Cef_tools import *
import numpy as np
import pandas as pd
import scanpy as sc
from anndata import AnnData
from typing import Sequence, Union, Iterable
from tqdm import trange  # Add at the top
#from __future__ import division
import pandas as pd
from sklearn.linear_model import LogisticRegression, LogisticRegressionCV
#from sklearn.cross_validation import StratifiedShuffleSplit
from collections import defaultdict
from sklearn import preprocessing
import matplotlib.patches as mpatches
from sklearn.decomposition import PCA
import umap
import scipy
from scipy import sparse
from sklearn.metrics import pairwise_distances
# with pickle
import logging
from scipy.sparse import issparse, coo_matrix
import pickle
import random

import seaborn as sns

import datetime
import seaborn as sns
import pandas as pd
import pickle as pickle
from scipy.spatial.distance import cdist, pdist, squareform
#import backspinpy
import pandas as pd
from sklearn.linear_model import LogisticRegression, LogisticRegressionCV
from sklearn.model_selection import StratifiedShuffleSplit
from collections import defaultdict
from sklearn import preprocessing
import matplotlib.patches as mpatches
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches
from scipy.spatial import distance
from scipy.cluster import hierarchy
import seaborn as sns
import torch
import torch.nn as nn
from torch.autograd import Variable
import torch.utils.data as Data
import torchvision
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import torch.utils.data as data_utils
from matplotlib import cm
import numpy as np
import pandas as pd
import pickle as pickle
from scipy.spatial.distance import cdist, pdist, squareform
#import backspinpy
import pandas as pd
from sklearn.linear_model import LogisticRegression, LogisticRegressionCV
from sklearn.model_selection import StratifiedShuffleSplit
from collections import defaultdict
from sklearn import preprocessing
import matplotlib.patches as mpatches
import torch.nn.functional as F
import math
from scipy.stats import ranksums
#import gpytorch

from scipy import sparse
import urllib.request
import os.path
from scipy.io import loadmat
from math import floor
#from matplotlib.legend_handler import Handler

def package_version():
    alllist=[]
    for m in globals().values():
        if getattr(m, '__version__', None):
            alllist.append(f'{m.__name__}=={m.__version__}')
    return alllist




import scanpy as sc
import umap
import numpy as np
from sklearn.preprocessing import LabelEncoder

import numpy as np
import pandas as pd
import random
from matplotlib.colors import to_hex

def add_color2(datax, clustername="Cluster", colorcode="color", predef=pd.Series()):
    """
    Input:
    datax: AnnData object, a data matrix with annotation, where the row index is the cell barcode, and the columns are the gene names and cell annotations
    clustername: str, the name of the column in the annotation that contains the cell cluster information
    colorcode: str, the name of the new column to be added to the annotation, which contains the color code for each cell
    predef: pd.Series, optional argument, a pre-defined dictionary with cluster name as key and color code as value
    Output:
    datax: AnnData object, a data matrix with annotation, where the row index is the cell barcode, and the columns are the gene names and cell annotations,
    with a new column added that contains the color code for each cell
    Functionality:

    This function adds a new column to the annotation of the data matrix, which contains the color code for each cell based on the cluster information in the specified column.
    If a pre-defined dictionary is provided, the function uses that to assign color codes to each cluster instead of generating a new color code.
    The color codes are added as a new column to the data matrix and stored in the uns field with the key "refcolor_dict".
    """
    if not colorcode in datax.obs.columns:
        color_dict = {}
        wanted_order = list(set(datax.obs[clustername]))

        # Use predefined colors if provided, else generate a random color
        for item in wanted_order:
            if item in predef:
                color_dict[item] = np.array(predef[item])
            else:
                color_dict[item] = np.array(random.sample(range(0, 255), 3))

        # Apply the colors to the cells
        colorlist = []
        for item in datax.obs[clustername]:
            colorlist.append(color_dict[item] / 255.0)

        # Convert RGB to HEX
        clist = []
        for item in colorlist:
            clist.append(to_hex(item))

        datax.obs[colorcode] = clist
        datax.uns["refcolor_dict"] = color_dict

    return datax


def UMAPtrain2(datax,
               NN=25,
               mdist=0.6,
               rd=173,
               n_comp=2,
               supervised=False,
               label_col="Cluster"):
    """
    Perform UMAP embedding (supervised or unsupervised) on the provided AnnData object.

    Parameters:
    - datax (AnnData): The AnnData object containing PCA-transformed data and optionally cluster labels.
    - NN (int, optional): Number of neighbors for UMAP (default=25).
    - mdist (float, optional): Minimum distance parameter for UMAP (default=0.6).
    - rd (int, optional): Random seed for reproducibility (default=173).
    - n_comp (int, optional): Number of UMAP components (default=2).
    - supervised (bool, optional): Whether to perform supervised UMAP using labels (default=False).
    - label_col (str, optional): Column name in `adata.obs` containing cluster labels (default="Cluster").

    Returns:
    - datax (AnnData): Updated AnnData object with UMAP embeddings.
    - umaptrain (UMAP): Trained UMAP model.
    """

    # Ensure 'X_pca' is present in obsm
    if "X_pca" not in datax.obsm:
        raise ValueError("PCA coordinates not found in datax.obsm['X_pca']. Please run PCA first.")

    # Extract PCA data
    XX = datax.obsm["X_pca"].astype(np.float32)

    # Initialize UMAP with desired parameters
    umaptrain = umap.UMAP(
        n_neighbors=NN,
        min_dist=mdist,
        spread=1,
        negative_sample_rate=5,
        init='spectral',
        random_state=rd,
        n_components=n_comp
    )

    # Perform supervised or unsupervised UMAP
    if supervised:
        # Check if label column exists
        if label_col not in datax.obs:
            raise ValueError(f"Label column '{label_col}' not found in datax.obs.")

        # Retrieve cluster labels
        labels = datax.obs[label_col].astype(str)

        # Encode string labels to integers
        le = LabelEncoder()
        y = le.fit_transform(labels)

        # Perform supervised UMAP by passing labels 'y'
        embedding = umaptrain.fit_transform(XX, y)
    else:
        # Perform unsupervised UMAP
        embedding = umaptrain.fit_transform(XX)

    # Assign the embedding to multiple obsm fields as per original code
    datax.obsm['X_umap'] = embedding
    datax.obsm['X_draw_graph_fr'] = embedding
    datax.obsm['X_CAMELumap'] = embedding

    return datax, umaptrain

def EnrichScore_Ranksum(adata, foldchange=1, meanthreshold=0.05, pvalue=0.1):
    """
    Input:
    adata: AnnData object containing the count matrix and cell metadata information
    foldchange: fold change threshold for differential expression analysis (default = 1)
    meanthreshold: mean expression threshold for differential expression analysis (default = 0.05)
    pvalue: p-value threshold for differential expression analysis (default = 0.1)
    Output:

    dfmk: DataFrame containing the differentially expressed genes for each cluster,
    along with the cluster name and the number of other clusters in which the gene is differentially expressed
    Functionality:
    This function performs differential expression analysis using ranksum test and generates a list of differentially expressed genes for each cluster based on the specified thresholds for fold change, mean expression, and p-value.
    It returns a DataFrame containing the differentially expressed genes for each cluster,
     along with the cluster name and the number of other clusters in which the gene is differentially expressed.
    """
    cluslist = list(set(adata.obs["Cluster"]))
    dfgrp = pd.DataFrame(adata.X.T, index=adata.var.index, columns=adata.obs.index).T
    dfgrp["Cluster"] = adata.obs["Cluster"]
    # dfgrp.shape
    markers = defaultdict(set)
    mkdict = {}
    sys.stdout.write("[%s]" % "Processing")
    sys.stdout.flush()
    sys.stdout.write("\b" * (50 + 1))  # return to start of line, after '['
    perc = len(cluslist)
    for ct in cluslist:
        temp = {}
        for num in range(min(2, int(len(cluslist) / 4) + 1), len(cluslist)):
            temp[num] = []
        dftemp1 = dfgrp.loc[dfgrp["Cluster"] == ct]
        # y=0

        itemindex = cluslist.index(ct)
        # setup toolbar

        sys.stdout.write("-%s%%-" % int(itemindex * 100 / perc))
        sys.stdout.flush()
        for mk in dfgrp.columns[:-1]:
            x = 0
            # y = 0
            dfgrpmk = dfgrp[[mk, "Cluster"]]
            for ct2 in list(set(cluslist) - set([ct])):
                dftemp2 = dfgrpmk.loc[dfgrpmk["Cluster"] == ct2]
                # pval = scipy.stats.ttest_ind(dftemp1[mk], dftemp2[mk], equal_var=False).pvalue

                score, pval = ranksums(dftemp1[mk], dftemp2[mk])
                fc = (dftemp1[mk].mean() + 0.0001) / (dftemp2[mk].mean() + 0.0001)
                # if (score10.loc[mk,ct] >= float(score10.loc[mk,ct2])) & (EScore.loc[mk,ct] >= float(EScore.loc[mk,ct2]))&(ratiovalue.loc[mk,ct]>0.9)& (score10.loc[mk,ct] > 1) & (EScore.loc[mk,ct] > 1) :
                if (fc > foldchange) & (dftemp1[mk].mean() > meanthreshold) & (pval < pvalue):
                    x = x + 1
                # if (score10.loc[mk, ct] * fc < float(score10.loc[mk, ct2])) & (
                #      EScore.loc[mk, ct] * fc < float(EScore.loc[mk, ct2])):
                # if (score10.loc[mk,ct] < float(score10.loc[mk,ct2])) & (EScore.loc[mk,ct] < float(EScore.loc[mk,ct2])) &(ratiovalue.loc[mk,ct]<0.1)& (EScore.loc[mk,ct] < 0.1):
                # y = y + 1
            if x in list(range(min(2, int(len(cluslist) / 4) + 1), len(cluslist))):
                temp[x].append(mk)
            # if y in list(range(min(3, int(len(df_fold.columns) / 4) + 1), len(df_fold.columns))):
            #  temp[y].append(mk)
            # markers[ct2] -= set([mk])
        # for num in range(2,len(df_fold.columns)-1):
        mkdict[ct] = temp
    genelist = []
    grouplist = []
    numberlist = []
    for num in range(min(2, int(len(cluslist) / 4) + 2), len(cluslist)):
        for ct in cluslist:
            genelist.extend(mkdict[ct][num])
            grouplist.extend([ct] * len(mkdict[ct][num]))
            numberlist.extend([num] * len(mkdict[ct][num]))
    print("Camel...Running: Marker is coming out...")
    dfmk = pd.DataFrame([genelist, grouplist, numberlist])
    dfmk.columns = dfmk.iloc[0, :]
    dfmk = dfmk.T
    dfmk.columns = ["Gene", "Group", "Num"]
    return dfmk


import numpy as np
import pandas as pd
import anndata
from scipy import sparse
import gc


def DataScalingLogMinMax(datax):
    """
    Inputs:
        datax: an AnnData object containing the raw gene expression data
    Outputs:
        An AnnData object with scaled gene expression data
    Functionality:
        1. Normalizes the raw data by counts per cell.
        2. Applies a log₂(x + 1) transformation.
        3. Performs scaling on each gene such that the maximum becomes 1 and
           the minimum is retained as a percentage (r_min/r_max) of the maximum.
    """
    import numpy as np
    import pandas as pd

    # Create a DataFrame with genes as rows and cells as columns.
    dfdev = pd.DataFrame(datax.X, index=datax.obs.index, columns=datax.var.index).T

    # Compute counts per cell (i.e. per column).
    CountsPerCell = dfdev.sum()
    CountsPerCell = np.ravel(CountsPerCell).copy()

    # Convert data to numpy array with cells as rows and genes as columns.
    data = dfdev.values.T
    if issubclass(data.dtype.type, (int, np.integer)):
        data = data.astype(np.float32)

    # Calculate median value of non-zero counts for scaling.
    CountsPerCell = np.asarray(CountsPerCell)
    mdvalue = np.median(CountsPerCell[CountsPerCell > 0], axis=0)
    # Avoid division by zero.
    CountsPerCell += (CountsPerCell == 0)
    norm_factors = CountsPerCell / mdvalue

    # Normalize the data by dividing each cell's values by its scaling factor.
    normalized_data = np.divide(data, norm_factors[:, None], out=data)

    # Create a DataFrame with genes as rows and cells as columns from the normalized data.
    df_norm = pd.DataFrame(normalized_data.T, index=dfdev.index, columns=dfdev.columns)

    # Apply log2 transformation: log2(x + 1)
    df_log = np.log2(df_norm + 1)

    # Define the custom scaling function per gene.
    def scale_row(row):
        r_min = row.min()
        r_max = row.max()
        # If the maximum is zero, return the row as is.
        if r_max == 0:
            return row
        # If all values are identical, set them to 1.
        if r_max == r_min:
            return pd.Series(1, index=row.index)
        # Apply linear scaling such that:
        # - when x = r_min -> scaled = r_min/r_max
        # - when x = r_max -> scaled = 1
        return ((row - r_min) / (r_max - r_min)) * (1 - (r_min / r_max)) + (r_min / r_max)

    # Apply scaling for each gene (i.e. each row).
    df_scaled = df_log.apply(scale_row, axis=1)

    # Update the AnnData object's X with the scaled data,
    # transposing back to have cells as rows and genes as columns.s
    df_scaled.values.T

    # Optionally, store the normalization factors in datax if needed.
    # datax.uns['norm_factors'] = norm_factors

    return datax




def patch_violinplot():
    from matplotlib.collections import PolyCollection
    ax = plt.gca()
    for art in ax.get_children():
        if isinstance(art, PolyCollection):
            art.set_edgecolor((0.6, 0.6, 0.6))


from matplotlib import pyplot
from matplotlib import gridspec

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from anndata import AnnData

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from anndata import AnnData



def save_load_model(filename, modelname=None, type="save"):
    if type=="save":
        pickle.dump(modelname, open(filename, 'wb'))
    elif type=="load":
        loaded_model = pickle.load((open(filename, 'rb')))
        return loaded_model

def rgb2hex(r,g,b):
    return "#{:02x}{:02x}{:02x}".format(r,g,b)

import numpy as np
import pandas as pd
import random
from matplotlib.colors import to_hex

def addcolor(datax, clustername="Cluster", colorcode="color", predef=pd.Series()):
    """
    Input:
    datax: AnnData object, a data matrix with annotation, where the row index is the cell barcode, and the columns are the gene names and cell annotations
    clustername: str, the name of the column in the annotation that contains the cell cluster information
    colorcode: str, the name of the new column to be added to the annotation, which contains the color code for each cell
    predef: pd.Series, optional argument, a pre-defined dictionary with cluster name as key and color code as value
    Output:
    datax: AnnData object, a data matrix with annotation, where the row index is the cell barcode, and the columns are the gene names and cell annotations,
    with a new column added that contains the color code for each cell
    Functionality:

    This function adds a new column to the annotation of the data matrix, which contains the color code for each cell based on the cluster information in the specified column.
    If a pre-defined dictionary is provided, the function uses that to assign color codes to each cluster instead of generating a new color code.
    The color codes are added as a new column to the data matrix and stored in the uns field with the key "refcolor_dict".
    """
    if not colorcode in datax.obs.columns:
        color_dict = {}
        wanted_order = list(set(datax.obs[clustername]))

        # Use predefined colors if provided, else generate a random color
        for item in wanted_order:
            if item in predef:
                color_dict[item] = np.array(predef[item])
            else:
                color_dict[item] = np.array(random.sample(range(0, 255), 3))

        # Apply the colors to the cells
        colorlist = []
        for item in datax.obs[clustername]:
            colorlist.append(color_dict[item] / 255.0)

        # Convert RGB to HEX
        clist = []
        for item in colorlist:
            clist.append(to_hex(item))

        datax.obs[colorcode] = clist
        datax.uns["refcolor_dict"] = color_dict

    return datax


def UMAP_plot(datax,clustername="Cluster", colorcode="color",legendOnPlot=False,Ncol=2,
              legendshow=True,figuresize=(10,10),alphavalue=0.8, lwvalue=0.1, markervalue=".",
             dotsize=200,lengendfont=20, legendloc=2,bbox_to_anchorvalues=(1.15, 1.2)):
    """
    This function takes a scanpy object and generates a UMAP plot based on the computed UMAP coordinates of the cells in the object. It also allows coloring of the cells based on a specified categorical variable in the object, and adds a legend to the plot.

    Inputs:
    datax: A scanpy object containing the data to plot
    clustername: The name of the categorical variable to use for coloring the cells (default: "Cluster")
    colorcode: The name of the new column to add to the object to store the cell colors (default: "color")
    legendOnPlot: If True, shows the legend on the plot itself (default: False)
    Ncol: Number of columns to use for the legend if it is shown on the plot (default: 2)
    legendshow: If True, shows the legend (default: True)
    figuresize: A tuple specifying the size of the plot in inches (default: (10,10))
    alphavalue: Alpha value for the cells (default: 0.8)
    lwvalue: Line width for the cells (default: 0.1)
    markervalue: Marker style for the cells (default: ".")
    dotsize: Size of the cells in the plot (default: 200)
    lengendfont: Font size for the legend (default: 20)
    legendloc: Location of the legend on the plot (default: 2)
    bbox_to_anchorvalues: Tuple specifying the location of the legend box on the plot (default: (1.15, 1.2))
    Output:
    datax: The scanpy object with the added color column
    ax: The plot axis object
    """
    #groups=list(set(df["Cluster"]))
    #annot=dfref["Cluster"].values
    #fname="uMAP_GBM"
    #title=''
    #prefix='uMAP'
    #colorlist=[]
    #for item in df["Cluster"].values:
    if not colorcode in datax.obs.columns:
        color_dict = {}
        wanted_order=list(set(datax.obs[clustername]))
        for item in wanted_order:
            color_dict[item] = (np.array(random.sample(range(0, 499), 3))/500).tolist()
        colorlist=[]
        for item in datax.obs[clustername]:
            colorlist.append(color_dict[item])
        datax.obs[colorcode]=colorlist
    fig=plt.figure(figsize=figuresize, facecolor='w')
    ax = fig.add_subplot(111)
    ax.scatter(datax.obsm["X_umap"][:,0],datax.obsm["X_umap"][:,1],c=datax.obs[colorcode],
               alpha=alphavalue, lw=lwvalue,
                marker=markervalue, s=dotsize)
    plt.grid(False)
    plt.axis("off")
    if legendshow==True:
        recs = []
        dfc = datax.obs[[clustername, colorcode]]
        dfc.index = dfc[clustername]
        dfc = dfc[~dfc.index.duplicated(keep='first')]
        xwanted_order = sorted(list(set(datax.obs[clustername])))
        for item in xwanted_order:
            recs.append(mpatches.Rectangle((0,0),1,1,fc=dfc.loc[item,colorcode]))
        ax.legend(recs,xwanted_order, ncol=Ncol,loc=legendloc,bbox_to_anchor=bbox_to_anchorvalues, prop={'size': lengendfont})
        #xwanted_order=list(set(dfref["Cluster"]))
        #for item in xwanted_order:
         #   recs.append(mpatches.Rectangle((0,0),1,1,fc=color_dict2[item]))
        #plt.legend(recs,xwanted_order, loc=2,bbox_to_anchor=(1.15, 1.2), prop={'size': 25})
    if legendOnPlot==True:
        dfposi=pd.DataFrame(datax.obsm["X_umap"], index=datax.obs.index, columns=["UMAP_X", "UMAP_Y"]).astype(float)
        dfposi[clustername]=datax.obs[clustername]
        textpositionLv = dfposi.groupby([clustername]).mean()
        for i in range(textpositionLv.shape[0]):
            plt.text(textpositionLv.iloc[i, 0], textpositionLv.iloc[i, 1], textpositionLv.index[i], fontsize=lengendfont)
    return datax, ax


def UMAPplotRefPred(DataRef, DataPdt, refClusterName,pdtClusterName, refColorCode, pdtColorCode,figuresize=(10, 10),
                    RefAlphaValue=0.8, RefLwValue=0.1, RefMarkerValue="x", RefDotSize=200,
                    PdtAlphaValue=0.8, PdtLwValue=0.1, PdtMarkerValue=".", PdtDotSize=200,
                    lengendfont=20, RefLegendloc=2, PdtLegendloc=3, Refbbox_to_anchorvalues=(1.15, 1.2),
                    Pdtbbox_to_anchorvalues=(1.15, 0.05)):
    """
    Inputs:
    DataRef: Reference dataset (an AnnData object) to be plotted on UMAP.
    DataPdt: Predicted dataset (an AnnData object) to be plotted on UMAP.
    refClusterName: The column name of the cluster labels of the reference dataset.
    pdtClusterName: The column name of the cluster labels of the predicted dataset.
    refColorCode: The column name of the colors assigned to each cluster in the reference dataset.
    pdtColorCode: The column name of the colors assigned to each cluster in the predicted dataset.
    figuresize: A tuple specifying the figure size (default: (10,10)).
    RefAlphaValue: The alpha value of the markers for the reference dataset (default: 0.8).
    RefLwValue: The line width value for the reference dataset (default: 0.1).
    RefMarkerValue: The marker value for the reference dataset (default: "x").
    RefDotSize: The dot size value for the reference dataset (default: 200).
    PdtAlphaValue: The alpha value of the markers for the predicted dataset (default: 0.8).
    PdtLwValue: The line width value for the predicted dataset (default: 0.1).
    PdtMarkerValue: The marker value for the predicted dataset (default: ".").
    PdtDotSize: The dot size value for the predicted dataset (default: 200).
    lengendfont: The font size of the legend (default: 20).
    RefLegendloc: The location of the legend for the reference dataset (default: 2).
    PdtLegendloc: The location of the legend for the predicted dataset (default: 3).
    Refbbox_to_anchorvalues: The anchor values for the reference legend box (default: (1.15, 1.2)).
    Pdtbbox_to_anchorvalues: The anchor values for the predicted legend box (default: (1.15, 0.05)).
    Outputs:
    DataRef: The reference dataset (an AnnData object).
    DataPdt: The predicted dataset (an AnnData object).
    ax: The matplotlib axes object containing the UMAP plot.
    """
    # groups=list(set(df["Cluster"]))
    # annot=dfref["Cluster"].values
    # fname="uMAP_GBM"
    # title=''
    # prefix='uMAP'
    # colorlist=[]
    # for item in df["Cluster"].values:
    import matplotlib
    if not refColorCode in DataRef.obs.columns:
        color_dict = {}
        wanted_order = list(set(DataRef.obs[refClusterName]))
        for item in wanted_order:
            color_dict[item] = (np.array(random.sample(range(0, 999), 3))/1000).tolist()
        colorlist = []
        for item in DataRef.obs[refClusterName]:
            colorlist.append(color_dict[item])
        DataRef.obs[refColorCode] = colorlist
    if not pdtColorCode in DataPdt.obs.columns:
        color_dict = {}
        wanted_order = list(set(DataPdt.obs[pdtClusterName]))
        for item in wanted_order:
            color_dict[item] = (np.array(random.sample(range(0, 999), 3))/1000).tolist()
        colorlist = []
        for item in DataPdt.obs[pdtClusterName]:
            colorlist.append(color_dict[item])
        DataPdt.obs[pdtColorCode] = colorlist

    fig = plt.figure(figsize=figuresize, facecolor='w')
    ax = fig.add_subplot(111)
    ax.scatter(DataRef.obsm["X_umap"][:, 0], DataRef.obsm["X_umap"][:, 1], c=DataRef.obs[refColorCode],
               alpha=RefAlphaValue,
               lw=RefLwValue,
               marker=RefMarkerValue, s=RefDotSize)
    ax.scatter(DataPdt.obsm["X_umap"][:, 0], DataPdt.obsm["X_umap"][:, 1], c=DataPdt.obs[pdtColorCode],
               alpha=PdtAlphaValue,
               lw=PdtLwValue,
               marker=PdtMarkerValue, s=PdtDotSize)
    plt.grid(False)
    plt.axis("off")

    recs = []
    dfc = DataRef.obs[[refClusterName, refColorCode]]
    dfc.index = dfc[refClusterName]
    dfc = dfc[~dfc.index.duplicated(keep='first')]
    xwanted_order = list(set(DataRef.obs[refClusterName]))
    for item in xwanted_order:
        recs.append(mpatches.Rectangle((0, 0), 1, 1, fc=dfc.loc[item, refColorCode]))
    legend1 = ax.legend(recs, xwanted_order, loc=RefLegendloc, bbox_to_anchor=Refbbox_to_anchorvalues,
                        prop={'size': lengendfont})

    recs2 = []
    dfcPdt = DataPdt.obs[[pdtClusterName, pdtColorCode]]
    dfcPdt.index = dfcPdt[pdtClusterName]
    dfcPdt = dfcPdt[~dfcPdt.index.duplicated(keep='first')]
    mwanted_order = list(set(DataPdt.obs[pdtClusterName]))
    for item in mwanted_order:
        recs2.append(matplotlib.patches.Circle((2, 2), radius=1, fc=dfcPdt.loc[item, pdtColorCode]))
    ax.legend(recs2, mwanted_order, loc=PdtLegendloc, bbox_to_anchor=Pdtbbox_to_anchorvalues,
              prop={'size': lengendfont})
    plt.gca().add_artist(legend1)
# xwanted_order=list(set(dfref["Cluster"]))
# for item in xwanted_order:
#   recs.append(mpatches.Rectangle((0,0),1,1,fc=color_dict2[item]))
# plt.legend(recs,xwanted_order, loc=2,bbox_to_anchor=(1.15, 1.2), prop={'size': 25})
    return DataRef, DataPdt, ax

def indices_distancesDensematrix(D, n_neighbors):
    sample_range = np.arange(D.shape[0])[:, None]
    indices = np.argpartition(D, n_neighbors-1, axis=1)[:, :n_neighbors]
    indices = indices[sample_range, np.argsort(D[sample_range, indices])]
    distances = D[sample_range, indices]
    return indices, distances
def sparse_matrixindicesDistances(indices, distances, nobs, n_neighbors):
    n_nonzeros = nobs * n_neighbors
    indptr = np.arange(0, n_nonzeros + 1, n_neighbors)
    D = scipy.sparse.csr_matrix((distances.copy().ravel(),  # must do copy here
                                indices.copy().ravel(),
                                indptr),
                                shape=(nobs, nobs))
    D.eliminate_zeros()
    return D

def connectivities_to_igraph(adjacency, directed=None):
    """Get igraph graph from adjacency matrix."""
    """
    The function connectivities_to_igraph takes an adjacency matrix and returns a graph object from the igraph library.

    Input:
    adjacency: A square, symmetric matrix representing the pairwise similarities or distances between observations.
    directed: A boolean indicating whether the graph should be directed or undirected (default is None).
    Output:
    gph: An igraph Graph object.
   
    np.nonzero(): Returns the indices of the elements that are non-zero.
    zip(): Returns an iterator of tuples, where the i-th tuple contains the i-th element from each of the argument sequences or iterables.
    igraph.Graph.add_vertices(): Adds vertices to the graph.
    igraph.Graph.add_edges(): Adds edges to the graph.
    igraph.EdgeSeq.es: Property that returns the sequence of edges of a graph.
    warn() (from the logging module): Logs a warning message.
    Note: The function tries to set the weights of the edges using the weight attribute of gph.es. If this fails, it silently ignores the error."""
    try:
        import igraph as ig
    except ImportError:
        raise ImportError(
            'Please install igraph!'
        )
    sources, targets = adjacency.nonzero()
    weights = adjacency[sources, targets]
    if isinstance(weights, np.matrix):
        weights = weights.A1
    gph = ig.Graph(directed=directed)
    gph.add_vertices(adjacency.shape[0])  # this adds adjacency.shap[0] vertices
    gph.add_edges(list(zip(sources, targets)))
    try:
        gph.es['weight'] = weights
    except:
        pass
    if gph.vcount() != adjacency.shape[0]:
        logging.warn('The constructed graph has only {} nodes. '
                  'Your adjacency matrix contained redundant nodes.'
                  .format(gph.vcount()))
    return gph

def UMAPindices_distancesTosparseMatrix(knn_indices, knn_dists, n_obs, n_neighbors):
    """
    This function takes in the indices and distances of the k-nearest neighbors (knn_indices, knn_dists),
    the total number of observations (n_obs), and the number of neighbors used to calculate the distances (n_neighbors),
    and returns a sparse matrix in CSR format representing the pairwise distances between the observations.

    Input:
    knn_indices: array-like, shape (n_obs, n_neighbors)
    The indices of the k-nearest neighbors for each observation.
    knn_dists: array-like, shape (n_obs, n_neighbors)
    The distances to the k-nearest neighbors for each observation.
    n_obs: int
    The total number of observations.
    n_neighbors: int
    The number of neighbors used to calculate the distances.
    Output:
    result: scipy.sparse.csr_matrix, shape (n_obs, n_obs)
    A sparse matrix in CSR format representing the pairwise distances between the observations.
    """
    rows = np.zeros((n_obs * n_neighbors), dtype=np.int64)
    cols = np.zeros((n_obs * n_neighbors), dtype=np.int64)
    vals = np.zeros((n_obs * n_neighbors), dtype=np.float64)

    for i in range(knn_indices.shape[0]):
        for j in range(n_neighbors):
            if knn_indices[i, j] == -1:
                continue  # We didn't get the full knn for i
            if knn_indices[i, j] == i:
                val = 0.0
            else:
                val = knn_dists[i, j]

            rows[i * n_neighbors + j] = i
            cols[i * n_neighbors + j] = knn_indices[i, j]
            vals[i * n_neighbors + j] = val

    result = coo_matrix((vals, (rows, cols)),
                                      shape=(n_obs, n_obs))
    result.eliminate_zeros()
    return result.tocsr()

def _compute_connectivities_umapXX(
    knn_indices,
    knn_dists,
    n_obs,
    n_neighbors,
    set_op_mix_ratio=1.0,
    local_connectivity=1.0,
):
    """
    credits go to Scanpy, with modifications
    Given a set of data X, a neighborhood size, and a measure of distance
    compute the fuzzy simplicial set (here represented as a fuzzy graph in
    the form of a sparse matrix) associated to the data. This is done by
    locally approximating geodesic distance at each point, creating a fuzzy
    simplicial set for each such point, and then combining all the local
    fuzzy simplicial sets into a global one via a fuzzy union.
    """
#    with warnings.catch_warnings():
        # umap 0.5.0
#        warnings.filterwarnings("ignore", message=r"Tensorflow not installed")
    from umap.umap_ import fuzzy_simplicial_set

    X = coo_matrix(([], ([], [])), shape=(n_obs, 1))
    connectivities = fuzzy_simplicial_set(
        X,
        n_neighbors,
        None,
        None,
        knn_indices=knn_indices,
        knn_dists=knn_dists,
        set_op_mix_ratio=set_op_mix_ratio,
        local_connectivity=local_connectivity,
    )

    if isinstance(connectivities, tuple):
        # In umap-learn 0.4, this returns (result, sigmas, rhos)
        connectivities = connectivities[0]

    distances = UMAPindices_distancesTosparseMatrix(
        knn_indices, knn_dists, n_obs, n_neighbors
    )

    return distances, connectivities.tocsr()

def SWAPLINE_dist(datax, n_neighbors=50, metric = 'euclidean'):
    """
    Inputs:
    datax: an AnnData object containing cell type scores.
    n_neighbors (optional, default=50): an integer value for the number of nearest neighbors to be used in the pairwise distance calculation.
    metric (optional, default='euclidean'): a string value for the metric used to calculate pairwise distances.
    Outputs:
    datax: an AnnData object with updated connectivities and distances.
    Function description:
    This function calculates the pairwise distances between cell type scores in the input data, and then calculates the connectivities and distances using the UMAP algorithm.
    The resulting connectivities and distances are stored in the output AnnData object.
    The number of nearest neighbors to be used in the pairwise distance calculation and the metric used to calculate pairwise distances can be customized by the user.
    """
    #n_pcs = 30, n_neighbors = len(dfnn.index),  metric = 'euclidean'
    ####
    # must be np.float32
    ####
    XX = datax.obsm["Celltype_Score"].astype(np.float32)

    #pca_ = PCA(n_components=n_pcs, svd_solver='arpack', random_state=0)
    #X_pca = pca_.fit_transform(X)
    PariDistances = pairwise_distances(XX, metric=metric)
    knn_indices, knn_distances = indices_distancesDensematrix(PariDistances, n_neighbors)
    logging.info('Camel...Running: distance calculating.....')
    #_distances = sparse_matrixindicesDistances(knn_indices, knn_distances, XX.shape[0], n_neighbors)
    #dftestdist = pd.DataFrame(knn_distances)
    #dftest = 0
    #dftestindex = pd.DataFrame(knn_indices)
    # dfnn=df.T
    # dfnn.shape
    #dftestindex.index = dfnn.index
    _distances, _connectivities = _compute_connectivities_umapXX(
        knn_indices, knn_distances, XX.shape[0], n_neighbors)
    datax.obsp["connectivities"]=_connectivities
    datax.obsp["distances"] = _distances
    #logging.info('Camel...Running: connectivity calculating.....')
    #neighbors_distances = _distances
    #neighbors_connectivities = _connectivities
    #adjacency = _connectivities
    #neighbors_connectivities = _connectivities
    logging.info('Camel...Running: finish.....')
    return datax

def clusterfinder(datax,Th_value =1, method="Louvain"):
    """
    Inputs:

    datax: AnnData object containing the gene expression data and UMAP coordinates
    Th_value: Resolution parameter value for the clustering algorithm. Default is 1.
    method: Clustering algorithm to use. Two options are available: "Louvain" (default) or "Leiden".
    Outputs:

    Returns an AnnData object with a new observation-level column "Assigned_Celltype" containing the cell cluster assignments generated by the chosen clustering algorithm.
    Functionality:
    This function performs clustering on the gene expression data and UMAP coordinates contained in an AnnData object. The user can choose between two clustering algorithms:
    Louvain or Leiden. The resolution parameter for the clustering algorithm can be set by the user (default is 1).
    The function returns the original AnnData object with a new observation-level column containing the cluster assignments generated by the chosen algorithm.

    """

    buildgraph = connectivities_to_igraph(adjacency=datax.obsp["connectivities"], directed=True)
    if method=="Louvain":

        from natsort import natsorted
        try:
            import louvain
        except ImportError:
            raise ImportError(
                'Please install the louvain!.'
            )

        logging.info('Camel...Running: Louvain clustering')

        parttern = louvain.find_partition(
            buildgraph,
            partition_type=louvain.RBConfigurationVertexPartition,
            resolution_parameter=Th_value,
            #**partition_kwargs
        )
        # output clusters
        clustergroups = np.array(parttern.membership)
        cellcluster = pd.Categorical(
            values=clustergroups.astype('U'),
            categories=natsorted(np.unique(clustergroups).astype('U')),
        )

    elif method=="Leiden":
        from natsort import natsorted
        try:
            #import louvain
            import leidenalg
        except ImportError:
            raise ImportError(
                'Please install leidenalg!'
            )
        #partition_kwargs = dict(partition_kwargs)

        print('Camel...Running: Leiden clustering')
        parttern = leidenalg.find_partition(
            buildgraph,
            partition_type = leidenalg.RBConfigurationVertexPartition,
            resolution_parameter=Th_value,
            )
        # output clusters
        clustergroups = np.array(parttern.membership)
        cellcluster = pd.Categorical(
            values=clustergroups.astype('U'),
            categories=natsorted(np.unique(clustergroups).astype('U')),
        )
    datax.obs["Assigned_Celltype"]=cellcluster
    return datax

def transfer_learning(UMAPmodel, datapdt, datax,clustername, colorcode, n_neighbors=50):
    """
    Input:

    UMAPmodel: a trained UMAP model
    datapdt: a scanpy AnnData object containing the predicted cell type scores
    datax: a scanpy AnnData object containing the original data with known cell type annotations
    clustername: a string representing the name of the cluster column in both datapdt and datax
    colorcode: a string representing the name of the column containing cell colors in datax
    n_neighbors: an integer representing the number of neighbors to use in the K-nearest neighbors classifier
    Output:

    datapdt: a scanpy AnnData object with predicted cell types and colors
    Function description: The function uses transfer learning to predict cell types and colors for new data based on a trained model.
     It first uses a UMAP model to transform the predicted cell type scores in datapdt into two-dimensional UMAP coordinates.
     It then trains a K-nearest neighbors classifier on the cell type scores and cluster annotations in datax.
     Finally, it predicts cell types for the cells in datapdt using the trained classifier and assigns colors based on the colorcode column in datax if available. T
    the function returns the modified datapdt object.

    """
    try:
        from sklearn.neighbors import KNeighborsClassifier
    except ImportError:
        raise ImportError(
            'Please install sklearn!'
        )
    X_rTest = UMAPmodel.transform(datapdt.obsm["Celltype_Score"])
    datapdt.obsm['X_umap'] = X_rTest
    # dfg = pd.DataFrame(X_r)
    #dfgTest.index = dfpcaTest.index
    #dfgTest.columns=["UMAP_X","UMAP_Y"]
    #dfpdtTest = dfgTest.join(dfclusTest["Cluster"], how="inner")
    neigh = KNeighborsClassifier(n_neighbors=n_neighbors, metric="euclidean")
    neigh.fit(datax.obsm["Celltype_Score"].astype(np.float32), datax.obs[clustername])
    datapdt.obs[clustername] = neigh.predict(datapdt.obsm["Celltype_Score"].astype(np.float32))
    if colorcode in datax.obs.columns:
        dfc = datax.obs[[clustername, colorcode]]
        dfc.index = dfc[clustername]
        dfc = dfc[~dfc.index.duplicated(keep='first')]
        colorlist=[]
        for item in  datapdt.obs[clustername]:
            colorlist.append(dfc.loc[item,colorcode])
        datapdt.obs[colorcode]=colorlist
    return datapdt


def patch_violinplot():
    from matplotlib.collections import PolyCollection
    ax = plt.gca()
    for art in ax.get_children():
        if isinstance(art, PolyCollection):
            art.set_edgecolor((0.6, 0.6, 0.6))



def scaling_data(datax, LogMinMax=False):
    """
    Input:
    datax: AnnData object containing the raw expression data
    LogMinMax (optional): Boolean, default False. If True, apply log normalization followed by min-max scaling.
    Output:
    datax: AnnData object with the scaled expression data in the "Scaled_Matrix" layer.
    Functionality:
    The function scales the input expression data by dividing
    each cell's expression values by the median expression value across all cells,
    and then scaling to a total count of 100,000. If LogMinMax is True,
    the function first applies log normalization (log10(x+1)) followed by min-max scaling to values between 0 and 1.
    The scaled expression matrix is stored in the "Scaled_Matrix" layer of the input AnnData object.
    """
    XX = datax.X
    countsInEachCell = np.ravel(XX.astype(float).sum(1)).copy()
    # XX = XXV.copy()
    if issubclass(XX.dtype.type, (int, np.integer)):
        XX = XX.astype(np.float32)  # np.float32
    countsInEachCell = np.asarray(countsInEachCell)
    after = np.median(countsInEachCell[countsInEachCell > 0], axis=0)
    countsInEachCell += (countsInEachCell == 0)
    countsInEachCell = countsInEachCell / after
    np.divide(XX, countsInEachCell[:, None], out=XX)
    XX = (XX.T / XX.sum(1)).T * 100000
    if LogMinMax == True:
        XX = np.log10(XX + 1)
        XX = ((XX.T - XX.min(1)) / XX.max(1)).T

    XX = np.nan_to_num(XX)
    datax.layers["Scaled_Matrix"] = XX

    return datax


def MarkerGenePlot(datax, genelist, nrow=2,fc=12,colormapopt="cividis"):
    """
    Inputs:
    datax: AnnData object containing gene expression data and UMAP coordinates.
    genelist: list of genes to plot.
    nrow: number of rows in the plot. Default value is 2.
    fc: font size of the plot titles. Default value is 12.
    colormapopt: colormap option to use in the plot. Default value is "cividis".
    Outputs: fig: matplotlib figure object containing the scatterplots of the gene expression levels in the UMAP space for each gene in the genelist.
    """
    import math
    dfexpr = pd.DataFrame(datax.layers['Scaled_Matrix'].T, index=datax.var.index, columns=datax.obs.index)
    dfexpr = dfexpr.T
    dfexpr["UMAPX"] = datax.obsm["X_umap"][:, 0]
    dfexpr["UMAPY"] = datax.obsm["X_umap"][:, 1]
    fig = plt.figure(figsize=(15, 15), facecolor='w')
    for i in range(1, len(genelist) + 1):
        genename = genelist[i - 1]
        plt.subplot(nrow, int(math.ceil(len(genelist) / nrow + 0.5)), i)
        dfe = dfexpr.sort_values(genename)
        plt.scatter(dfe["UMAPX"], dfe["UMAPY"], lw=0.1, edgecolor="grey", c=dfe[genename], s=int(80 / nrow),
                    cmap="cividis")
        plt.title(genename, fontsize=fc)
        plt.axis("off")
    return fig







def writedataraw(adatax,filename,filepath=""):
    adatax.X= sparse.csr_matrix(adatax.X)
    adatax.write(os.path.join(filepath, filename))

#import scipy.sparse as sparse
def write_data(adatax,filename,filepath=""):
    """
    Inputs:
    df_dev: a pandas DataFrame containing gene expression data. Each row represents a gene, and each column represents a sample.
    FeatureGenes: a list of gene names for which to calculate the feature enrichment score.
    controlnumber: the number of control genes to use when calculating the score (default is 50).
    cuts: the number of quantiles to divide the gene expression distribution into (default is 25).
    Outputs:
    FeatureScore: a numpy array of feature enrichment scores, with one score for each gene in FeatureGenes.
    """
    if type(adatax.X) != sparse.csr_matrix:
        adatax.X= sparse.csr_matrix(adatax.X)
    if 'ConstrualValue_DeepLift' in adatax.obsm:
        if type(adatax.obsm['ConstrualValue_DeepLift']) != sparse.csr_matrix:
            adatax.obsm['ConstrualValue_DeepLift']= sparse.csr_matrix(adatax.obsm['ConstrualValue_DeepLift'])
    if 'ConstrualValue_DeepLift' in adatax.obsm:
        if type(adatax.obsm['NormalizedMatrix']) != sparse.csr_matrix:
            adatax.obsm['NormalizedMatrix']= sparse.csr_matrix(adatax.obsm['NormalizedMatrix'])
    adatax.write(os.path.join(filepath, filename))


def enrichmentscoreBETA(dfpfcclus, df_dev, fc=3, pvalcutoff=0.1, shortcut=True):
    """
    dfpfcclus: a pandas DataFrame containing the cluster labels for each cell in the gene expression data
    df_dev: a pandas DataFrame containing the gene expression data for each cell
    fc: a fold change threshold used for the enrichment score calculation
    pvalcutoff: a p-value cutoff used for the enrichment score calculation
    shortcut: a boolean value indicating whether to use a shortcut method for the calculation or not
    The function first joins the two input DataFrames on the common cells and clusters, and then calculates the mean expression for each gene in each cluster. It then calculates the fold change of gene expression between each cluster and a control group (computed as the mean expression of all cells), and multiplies it by the ratio of the number of cells with non-zero expression of the gene in the cluster and control group. The resulting value is the enrichment score for each gene in each cluster.

    If shortcut is set to True, the function uses a simplified method for the calculation, which involves calculating the fold change of gene expression between each cluster and the control group and filtering genes based on fold change and median expression values.

    The function returns a pandas DataFrame containing the enriched genes for each cluster, along with their enrichment scores and gene expression values.

    """
    # dfpfcclus = dfpfcclus, df_dev = df_dev, fc = 1.25, shortcut = True
    dfgrp = df_dev.T.astype(float).join(dfpfcclus.T, how="inner")
    dfmean = dfgrp.groupby(['Cluster']).mean()
    dfmedian = dfgrp.groupby(['Cluster']).median().T
    df_means = df_dev.mean(1)
    if shortcut == False:
        print("Camel...Running: clusteringValue1...")
        TotalNzCount = np.sum(dfgrp.iloc[:, :-1] >  0)
        grpNzCount = dfgrp.groupby(['Cluster']).agg(lambda x: x.ne(0).sum())
        print("Camel...Running: clusteringValue2...")
        RestNzCount = TotalNzCount - grpNzCount
        RatioNzCount = (grpNzCount + 0.1) / (RestNzCount + 0.1)/dfgrp.groupby(["Cluster"]).count()*1000
        dfmean = dfmean.T.loc[RatioNzCount.columns].T
        df_means = df_means.loc[RatioNzCount.columns]
        df_fold = (dfmean + 0.01).div(df_means + 0.01, axis=1) ** 0.5
        # df_fold=dfmean.div(df_means,axis=1)
        print("Camel...Running: Enrichment1...")
        EScore = df_fold[RatioNzCount.columns].fillna(0) * RatioNzCount
        EScore = EScore.T
        df_fold = df_fold.T.fillna(0)
        df_avgpos = df_means
        df_avgpos = df_avgpos.fillna(0.0)
        score00 = df_fold
        score10 = df_fold.multiply(df_avgpos, axis=0)
        # keep NumPy, but wrap the result back into a DataFrame
        order = np.argsort(score00.to_numpy(), axis=0)  # ndarray
        ix00 = pd.DataFrame(order, index=score00.index, columns=score00.columns)
        # ix05 = np.argsort( score05 , 0)
        order = np.argsort(score10.to_numpy(), axis=0)  # ndarray
        ix10 = pd.DataFrame(order, index=score10.index, columns=score10.columns)
        markers = defaultdict(set)
        N = int(len(df_fold.index) / len(df_fold.columns) * 3)
        N= min(len(df_fold.index), N)
        print("Camel...Running: CrossChecking...")
        for ct in df_fold.columns:
            markers[ct] |= set(df_fold.index[ix00.loc[:, ct][::-1]][:N])
            markers[ct] |= set(df_fold.index[ix10.loc[:, ct][::-1]][:N])

        RatioNzCount = RatioNzCount.T
        # RatioNzCount = RatioNzCount.T
        mkdict = {}
        sys.stdout.write("[%s]" % "Processing")
        sys.stdout.flush()
        sys.stdout.write("\b" * (50 + 1))  # return to start of line, after '['
        perc = len(df_fold.columns)
        for ct in df_fold.columns:
            temp = {}
            for num in range(min(3, int(len(df_fold.columns) / 4) + 1), len(df_fold.columns)):
                temp[num] = []
            dftemp1 = dfgrp.loc[dfgrp["Cluster"] == ct]
            # y=0

            itemindex = df_fold.columns.tolist().index(ct)
            # setup toolbar

            sys.stdout.write("-%s%%-" % int(itemindex * 100 / perc))
            sys.stdout.flush()
            for mk in markers[ct]:
                x = 0
                # y = 0
                dfgrpmk = dfgrp[[mk, "Cluster"]]
                for ct2 in list(set(df_fold.columns) - set([ct])):
                    dftemp2 = dfgrpmk.loc[dfgrpmk["Cluster"] == ct2]
                    pval = scipy.stats.ttest_ind(dftemp1[mk], dftemp2[mk], equal_var=False).pvalue
                    # if (score10.loc[mk,ct] >= float(score10.loc[mk,ct2])) & (EScore.loc[mk,ct] >= float(EScore.loc[mk,ct2]))&(ratiovalue.loc[mk,ct]>0.9)& (score10.loc[mk,ct] > 1) & (EScore.loc[mk,ct] > 1) :
                    if (score10.loc[mk, ct] >= float(score10.loc[mk, ct2]) * fc / 2) & (
                            EScore.loc[mk, ct] >= float(EScore.loc[mk, ct2]) * fc) & (pval < pvalcutoff):
                        x = x + 1
                    # if (score10.loc[mk, ct] * fc < float(score10.loc[mk, ct2])) & (
                    #      EScore.loc[mk, ct] * fc < float(EScore.loc[mk, ct2])):
                    # if (score10.loc[mk,ct] < float(score10.loc[mk,ct2])) & (EScore.loc[mk,ct] < float(EScore.loc[mk,ct2])) &(ratiovalue.loc[mk,ct]<0.1)& (EScore.loc[mk,ct] < 0.1):
                    # y = y + 1
                if x in list(range(min(3, int(len(df_fold.columns) / 4) + 1), len(df_fold.columns))):
                    temp[x].append(mk)
                # if y in list(range(min(3, int(len(df_fold.columns) / 4) + 1), len(df_fold.columns))):
                #  temp[y].append(mk)
                # markers[ct2] -= set([mk])
            # for num in range(2,len(df_fold.columns)-1):
            mkdict[ct] = temp
        genelist = []
        grouplist = []
        numberlist = []
        for num in range(min(3, int(len(df_fold.columns) / 4) + 2), len(df_fold.columns)):
            for ct in df_fold.columns:
                genelist.extend(mkdict[ct][num])
                grouplist.extend([ct] * len(mkdict[ct][num]))
                numberlist.extend([num] * len(mkdict[ct][num]))
        print("Camel...Running: Marker is coming out...")
        dfmk = pd.DataFrame([genelist, grouplist, numberlist])
        dfmk.columns = dfmk.iloc[0, :]
        dfmk = dfmk.T
        dfmk.columns = ["Gene", "Group", "Num"]
        dftest = EScore.loc[dfmk.index]
        dftest = dfmk.iloc[:, 1:].T.append(dftest.T)
        dftest = dftest.T.sort_values(by=['Group', 'Num'], ascending=[True, False])
        collist = []
        for item in score10.columns:
            collist.append("Expr_%s" % item)
        score10.columns = collist
        dftestnew = dftest.join(score10, how="inner")
        # list_genes = list(set(dftestnew.index))
        return dftestnew
    elif shortcut == True:
        # df_fold=(dfmean+0.01).div(df_means+0.01,axis=1)**0.5
        print("Camel...Running: clusteringValue1...")
        df_fold = dfmean.div(df_means, axis=1)
        # dfmean=dfgrp.groupby(['Cluster']).mean()
        # df_means = df_dev.mean(1)
        # df_fold=dfmean.div(df_means,axis=1)
        df_fold = df_fold.T.dropna()
        df_avgpos = df_means
        df_avgpos = df_avgpos.fillna(0)
        score00 = df_fold
        score10 = df_fold.multiply(df_avgpos, axis=0)
        print("Camel...Running: clusteringValue2...")

        # keep NumPy, but wrap the result back into a DataFrame
        order = np.argsort(score00.to_numpy(), axis=0)  # ndarray
        ix00 = pd.DataFrame(order, index=score00.index, columns=score00.columns)
        # ix05 = np.argsort( score05 , 0)
        order = np.argsort(score10.to_numpy(), axis=0)  # ndarray
        ix10 = pd.DataFrame(order, index=score10.index, columns=score10.columns)
        markers = defaultdict(set)
        N = int(len(df_fold.index) / len(df_fold.columns) * 3)
        N = min(len(df_fold.index), N)
        print(N)
        sys.stdout.write("[%s]" % "Processing")
        sys.stdout.flush()
        sys.stdout.write("\b" * (50 + 1))  # return to start of line, after '['
        perc = len(df_fold.columns)
        for ct in df_fold.columns:
            markers[ct] |= set(df_fold.index[ix00.loc[:, ct][::-1]][:N])
            markers[ct] |= set(df_fold.index[ix10.loc[:, ct][::-1]][:N])
        print(len(markers))
        print("Camel...Running: CrossChecking...")
        genelist = []
        for ct in df_fold.columns:
            for mk in markers[ct]:
                for ct2 in list(set(df_fold.columns) - set([ct])):
                    if (score10.loc[mk, ct] >= float(score10.loc[mk, ct2])* fc) & (
                            score00.loc[mk, ct] >= float(score00.loc[mk, ct2])* fc ) & (dfmedian.loc[mk, ct] > 0):
                        genelist.append(mk)
                    #elif (score10.loc[mk, ct] < float(score10.loc[mk, ct2])) & (
                     #       score00.loc[mk, ct] < float(score00.loc[mk, ct2])) & (dfmedian.loc[mk, ct] <= 0):
                      #  genelist.append(mk)
            itemindex = df_fold.columns.tolist().index(ct)
            # setup toolbar

            sys.stdout.write("-%s%%-" % int(itemindex * 100 / perc))
            sys.stdout.flush()
        print("Camel...Running: output genelist...")
        return genelist




def FeatureEnrichScoreNew(df_dev, FeatureGenes, controlnumber=50, cuts=25):
    """
    Inputs:
    df_dev: a pandas DataFrame containing gene expression data. Each row represents a gene, and each column represents a sample.
    FeatureGenes: a list of gene names for which to calculate the feature enrichment score.
    controlnumber: the number of control genes to use when calculating the score (default is 50).
    cuts: the number of quantiles to divide the gene expression distribution into (default is 25).
    Outputs:
    FeatureScore: a numpy array of feature enrichment scores, with one score for each gene in FeatureGenes.
    """

    var_names = df_dev.index
    gene_list = FeatureGenes

    obs_avg = df_dev.mean(1)
    obs_avg = obs_avg[np.isfinite(obs_avg)]
    n_items = int(np.round(len(obs_avg) / cuts))
    obs_cut = obs_avg.rank(method='min') // n_items

    ctrl_size = controlnumber
    control_genes = set()
    for cut in np.unique(obs_cut.loc[gene_list]):
        r_genes = np.array(obs_cut[obs_cut == cut].index)
        np.random.shuffle(r_genes)
        control_genes.update(set(r_genes[:ctrl_size]))
    control_genes = list(control_genes - set(gene_list))
    gene_list = list(gene_list)
    X_list = df_dev.loc[gene_list].T.values
    X_control = df_dev.loc[control_genes].mean().values
    FeatureScore = np.nanmean(X_list, axis=1) - X_control
    return FeatureScore




__all__ = ["FeatureEnrichScore", "compute_feature_scores"]


# -----------------------------------------------------------------------------
# High‑level convenience wrapper – many replicates + active cell call
# -----------------------------------------------------------------------------

def FeatureEnrichScore(df_dev: pd.DataFrame,
                       FeatureGenes: Sequence[str],
                       *,
                       controlnumber: int = 500,
                       cuts: int = 20, ):
    """
    Inputs:
    df_dev: a pandas DataFrame containing gene expression data. Each row represents a gene, and each column represents a sample.
    FeatureGenes: a list of gene names for which to calculate the feature enrichment score.
    controlnumber: the number of control genes to use when calculating the score (default is 50).
    cuts: the number of quantiles to divide the gene expression distribution into (default is 25).
    Outputs:
    FeatureScore: a numpy array of feature enrichment scores, with one score for each gene in FeatureGenes.
    """

    var_names = df_dev.index
    gene_list = FeatureGenes

    obs_avg = df_dev.mean(1)
    obs_avg = obs_avg[np.isfinite(obs_avg)]
    n_items = int(np.round(len(obs_avg) / cuts))
    obs_cut = obs_avg.rank(method='min') // n_items

    ctrl_size = controlnumber
    control_genes = set()
    for cut in np.unique(obs_cut.loc[gene_list]):
        r_genes = np.array(obs_cut[obs_cut == cut].index)
        np.random.shuffle(r_genes)
        control_genes.update(set(r_genes[:ctrl_size]))
    control_genes = list(control_genes - set(gene_list))
    gene_list = list(gene_list)
    X_list = df_dev.loc[gene_list].T.values
    X_control = df_dev.loc[control_genes].mean().values
    FeatureScore = np.nanmean(X_list, axis=1) - X_control
    return FeatureScore


def compute_feature_scores(
        adata: AnnData,
        feature_genes: Sequence[str] | Iterable[str],
        *,
        n_iter: int = 500,
        n_top_genes: int = 5000,
        batch_key: str | None = None,
        controlnumber: int = 500,
        cuts: int = 20,
        layer: str | None = None,
        key: str = "feature",
        random_state: int | None = 0,
        pvalue: float = 0.01
) -> pd.DataFrame:
    """Run *n_iter* replicates of `FeatureEnrichScore` and annotate active cells.

    The workflow replicates the original notebook logic:
    1. Keep highly‑variable genes (*n_top_genes* per batch if *batch_key*).
    2. Restrict expression matrix to those genes **plus** the provided
       `feature_genes`.
    3. Run Monte‑Carlo sampling (`n_iter` replicates).
    4. Call a cell *active* if *mean(score) > 0* **and** 5‑th percentile > 0.
    5. Store results in `adata.obs` under the given *key*.

    Returns
    -------
    pd.DataFrame
        Summary per cell with columns `[score, active]` (indexed by cell IDs).
    """
    rng = np.random.default_rng(random_state)

    # 1. Highly‑variable genes ------------------------------------------------
    adata_var = adata.var.copy()
    if "MVgene" not in adata_var.columns:
        adata_var["MVgene"] = False  # init
    sc.pp.highly_variable_genes(
        adata,
        n_top_genes=n_top_genes,
        batch_key=batch_key,
        inplace=True,
    )
    adata_var["MVgene"] |= adata.var["highly_variable"].to_numpy()

    # 2. Ensure feature genes always kept
    feature_genes = list(set(feature_genes))
    present = set(feature_genes) & set(adata.var_names)
    if not present:
        raise ValueError("None of the feature_genes are present in adata.var_names")
    adata_var.loc[list(present), "MVgene"] = True

    # 3. Build expression DataFrame (genes × cells)
    adata_sub = adata[:, adata_var["MVgene"]].copy()
    X = adata_sub.layers[layer] if layer is not None else adata_sub.X
    df_dev = pd.DataFrame(X.T, index=adata_sub.var.index, columns=adata_sub.obs.index)

    # 4. Monte‑Carlo replicates ----------------------------------------------
    from tqdm import trange  # Import here for notebooks, or put at top
    scores = np.empty((n_iter, df_dev.shape[1]), dtype=np.float32)
    for i in trange(n_iter, desc="Monte-Carlo replicates", leave=True):
        scores[i] = FeatureEnrichScore(
            df_dev,
            present,
            controlnumber=controlnumber,
            cuts=cuts,
        )

    # 5. Summaries & active call ---------------------------------------------
    score_mean = scores.mean(axis=0)
    score_median = np.median(scores, axis=0)
    score_p = np.quantile(scores, pvalue, axis=0)
    value = np.sqrt(score_mean * score_median)
    select = ((score_mean > 0) & (score_p > 0)).astype(int)
    active_value = value * select

    result = pd.DataFrame(
        {
            f"{key}_Value": value,
            f"{key}_Select": select,
            f"{key}_ActiveValue": active_value,
        },
        index=adata_sub.obs.index,
    )
    # 6. Attach to adata.obs --------------------------------------------------
    adata.obs = adata.obs.drop(columns=result.columns, errors="ignore")
    adata.obs = adata.obs.join(result, how="left")
    return result


import pandas as pd
import anndata as ad

def flag_genes_by_celltype(
        adata: ad.AnnData,
        gene_ct_df: pd.DataFrame,
        gene_col: str = "GeneName",
        ct_col: str = "CellType",
        fill_value: bool = False
) -> None:
    """
    Annotate adata.var with Boolean flags showing for which cell types
    each gene is listed in the supplied catalogue.

    After running, `adata.var` will contain one column per unique cell type,
    named exactly as in `gene_ct_df[ct_col]`.

    Parameters
    ----------
    adata
        Your AnnData object (genes = rows of `adata.var`).
    gene_ct_df
        A DataFrame with at least two columns:
            * `gene_col` – gene symbols (must match `adata.var_names`)
            * `ct_col`   – the cell-type label for that gene
    gene_col, ct_col
        Column names (change only if your DataFrame uses other labels).
    fill_value
        What to write for genes that are *not* listed for a cell type
        (defaults to `False`).
    """
    # ------------------------------------------------------------------ #
    # 1 .  normalise input                                                #
    # ------------------------------------------------------------------ #
    gene_ct_df = gene_ct_df[[gene_col, ct_col]].dropna().copy()
    gene_ct_df[gene_col] = gene_ct_df[gene_col].astype(str)
    gene_ct_df[ct_col]   = gene_ct_df[ct_col].astype(str)

    # keep only genes present in adata
    gene_ct_df = gene_ct_df[gene_ct_df[gene_col].isin(adata.var_names)]

    # ------------------------------------------------------------------ #
    # 2 .  build a boolean indicator matrix: genes × cell-types           #
    # ------------------------------------------------------------------ #
    # pivot → rows = genes, columns = cell types, True where listed
    ind_mat = (
        pd.crosstab(
            gene_ct_df[gene_col],
            gene_ct_df[ct_col]
        )
        .astype(bool)            # 1/0 → True/False
        .reindex(index=adata.var_names, columns=None)  # keep same gene index
        .fillna(fill_value)
    )

    # ------------------------------------------------------------------ #
    # 3 .  merge into adata.var                                           #
    # ------------------------------------------------------------------ #
    for col in ind_mat.columns:
        adata.var[col] = ind_mat[col]

    # store provenance for reproducibility
    adata.uns.setdefault("var_gene_celltype_flags", {})["source_shape"] = \
        gene_ct_df.shape



import numpy as np
import pandas as pd
from scipy import sparse
import anndata as ad

def build_escore_adata(
    adata: ad.AnnData,
    cluster_key: str = "Cluster",
    layer: str | None = None,
    shortcut: bool = False,
    scale: float = 1_000.0,
    pseudo_expr: float = 0.01,
    pseudo_count: float = 0.1,
) -> ad.AnnData:
    """
    Compute the gene-cluster enrichment score (EScore) and return it
    as a *new* AnnData object with
        obs = clusters    (rows)
        var = genes       (columns)
        X   = EScore[c, g]

    Parameters
    ----------
    adata
        Original single-cell data set (cells × genes).
        `adata.obs[cluster_key]` must contain cluster labels.
    cluster_key
        Column in `adata.obs` that holds the cluster annotation.
    layer
        If you keep normalised counts in a layer (e.g. 'log1p'), give its name.
        By default the function uses `adata.X`.
    shortcut
        When *True* we skip the non-zero–ratio weighting and simply
        return the cluster means; otherwise we reproduce your
        full “Camel…Running” logic.
    scale, pseudo_expr, pseudo_count
        Hyper-parameters exactly like in your original snippet.

    Returns
    -------
    AnnData
        clusters × genes EScore matrix
    """
    # ------------------------------------------------------------------ #
    # 1 .  prepare an expression DataFrame                                #
    # ------------------------------------------------------------------ #
    X = adata.layers[layer] if layer is not None else adata.X
    if sparse.issparse(X):
        X = X.toarray()

    # cell × gene expression table
    df_cells = pd.DataFrame(
        X,
        index=adata.obs_names,
        columns=adata.var_names,
        dtype=float,
    )

    # cluster labels
    df_clusters = adata.obs[[cluster_key]].rename(columns={cluster_key: "Cluster"})
    # join → cell × (genes … , Cluster)
    df_grp = df_cells.join(df_clusters)

    # ------------------------------------------------------------------ #
    # 2 .  cluster means + global means                                   #
    # ------------------------------------------------------------------ #
    df_mean   = df_grp.groupby("Cluster").mean()      # clusters × genes
    gene_mean = df_cells.mean(axis=0)                 #   1       × genes

    # ------------------------------------------------------------------ #
    # 3 .  optional non-zero weighting                                    #
    # ------------------------------------------------------------------ #
    if not shortcut:
        total_nz = (df_grp.iloc[:, :-1] > 0).sum()                    # genes
        grp_nz   = df_grp.groupby("Cluster").agg(lambda x: x.ne(0).sum())  # clusters × genes
        rest_nz  = total_nz - grp_nz                                  # clusters × genes

        ratio_nz = (
            (grp_nz + pseudo_count) /
            (rest_nz + pseudo_count) /
            df_grp.groupby("Cluster").size().values[:, None] * scale  # broadcasting
        )

        df_fold = (df_mean + pseudo_expr).div(gene_mean + pseudo_expr, axis=1) ** 0.5
        escore  = (df_fold * ratio_nz).fillna(0.0)                    # clusters × genes
    else:
        escore = df_mean.copy()

    # ------------------------------------------------------------------ #
    # 4 .  wrap into a fresh AnnData                                      #
    # ------------------------------------------------------------------ #
    esc_adata = ad.AnnData(
        X   = escore.values.astype(np.float32),
        obs = pd.DataFrame(index=escore.index),
        var = pd.DataFrame(index=escore.columns),
    )
    esc_adata.uns["escore_params"] = dict(
        cluster_key = cluster_key,
        layer       = layer,
        shortcut    = shortcut,
        scale       = scale,
        pseudo_expr = pseudo_expr,
        pseudo_count= pseudo_count,
    )

    return esc_adata


import numpy as np
import pandas as pd

def lr_score_between_two_clusters(
        adata,
        EScore,          # genes × clusters  (DataFrame)
        lr_df,           # ligand–receptor catalogue
        cluster1: str,
        cluster2: str,
        use_var_filter: bool = True,
        missing_value: float = 0.0,
        include_all_pairs: bool = True,
        agg_duplicate: str = "mean",  # how to collapse duplicates
):
    """
    Return a 2-column DataFrame with scores for
        cluster1-ligand → cluster2-receptor   and
        cluster2-ligand → cluster1-receptor.
    Every pair in `lr_df` is kept; un-scored ones are `missing_value`.
    """

    # ---------- 1. prepare gene sets -----------------------------------
    if use_var_filter and cluster1 in adata.var and cluster2 in adata.var:
        lig1 = set(adata.var.index[adata.var[cluster1].astype(bool)])
        lig2 = set(adata.var.index[adata.var[cluster2].astype(bool)])
    else:
        lig1 = lig2 = set(EScore.index)

    rec1, rec2 = lig1, lig2       # we treat the same set for receptors

    # ---------- 2. make EScore index unique if necessary ---------------
    if EScore.index.has_duplicates:
        EScore = EScore.groupby(EScore.index).agg(agg_duplicate)

    # ---------- 3. helper that CAN see lr_df via closure ---------------
    def _directed_scores(lig_cluster, rec_cluster,
                         lig_set, rec_set, col_name):
        """score one direction and return a Series"""
        pairs = (
            lr_df[
                lr_df["ligand_symbol"].isin(lig_set) &
                lr_df["receptor_symbol"].isin(rec_set)
            ]
            .drop_duplicates(subset=["ligand_symbol", "receptor_symbol"])
            .reset_index(drop=True)
        )

        if pairs.empty:
            return pd.Series(dtype=float, name=col_name)

        lig_vals = EScore.loc[pairs["ligand_symbol"], lig_cluster].to_numpy()
        rec_vals = EScore.loc[pairs["receptor_symbol"], rec_cluster].to_numpy()

        s = pd.Series(
            lig_vals * rec_vals,
            index=pairs["ligand_symbol"] + "-" + pairs["receptor_symbol"],
            name=col_name,
        )
        # collapse duplicated pair names, default = mean
        return getattr(s.groupby(level=0), agg_duplicate)()

    # ---------- 4. two directions --------------------------------------
    col_fw = f"{cluster1}(lig)-{cluster2}(rec)"
    col_rv = f"{cluster2}(lig)-{cluster1}(rec)"

    s_fw = _directed_scores(cluster1, cluster2, lig1, rec2, col_fw)
    s_rv = _directed_scores(cluster2, cluster1, lig2, rec1, col_rv)

    lr_mat = pd.concat([s_fw, s_rv], axis=1)

    # ---------- 5. guarantee full index, fill missing with 0 ----------
    if include_all_pairs:
        full_index = (
            lr_df["ligand_symbol"].astype(str) + "-" +
            lr_df["receptor_symbol"].astype(str)
        ).unique()

        lr_mat = (
            lr_mat.groupby(level=0).first()          # ensure unique index
                  .reindex(full_index)
                  .fillna(missing_value)             # zeros for absent pairs
        )

    return lr_mat

import itertools
import pandas as pd

def lr_matrix_all_pairs(
        adata,
        EScore,              # genes × clusters  (DataFrame)
        lr_df,               # ligand–receptor catalogue
        celltype_cols=None,  # list/tuple of cell-type columns in adata.var
        use_var_filter=True,
        missing_value=0.0,
        include_all_pairs=True,
        verbose=True,
):
    """
    Compute directed ligand-receptor scores for *every* ordered cluster pair
    (A→B, with A ≠ B) and merge them into one DataFrame.

    Parameters
    ----------
    adata, EScore, lr_df
        Same objects you already use.
    celltype_cols
        If *None* we take **all** columns in `adata.var`.
        Otherwise give an explicit list of cluster names to include.
    use_var_filter, missing_value, include_all_pairs
        Passed straight to `lr_score_between_two_clusters`.
    verbose
        Print progress every N pairs.

    Returns
    -------
    pd.DataFrame
        Index  : every ligand-receptor pair that appears in `lr_df`
        Columns: one column per ordered pair, named
                 "ClusterA(lig)-ClusterB(rec)"
                 (no self-pairs).
    """
    # ---------------------------------------------------------------
    # 0. which clusters do we have?
    # ---------------------------------------------------------------
    if celltype_cols is None:
        clusters = list(adata.var.columns)
    else:
        clusters = list(celltype_cols)

    if len(clusters) < 2:
        raise ValueError("Need at least two cell-type columns in adata.var")

    # ---------------------------------------------------------------
    # 1. iterate over all A ≠ B
    # ---------------------------------------------------------------
    matrices = []
    total = len(clusters) * (len(clusters) - 1)
    for i, (c1, c2) in enumerate(itertools.permutations(clusters, 2), 1):
        if verbose and (i % 20 == 0 or i == total):
            print(f"[lr-matrix] processed {i:>4}/{total} pairs …", end="\r")

        mat_pair = lr_score_between_two_clusters(
            adata            = adata,
            EScore           = EScore,
            lr_df            = lr_df,
            cluster1         = c1,
            cluster2         = c2,
            use_var_filter   = use_var_filter,
            missing_value    = missing_value,
            include_all_pairs= include_all_pairs,
            # helper’s defaults for other args
        )

        matrices.append(mat_pair)

    if verbose:
        print("")  # newline after progress bar

    # ---------------------------------------------------------------
    # 2. merge all columns  (outer join → guarantees full row index)
    # ---------------------------------------------------------------
    lr_all = (
        pd.concat(matrices, axis=1)
          .fillna(missing_value)
          .astype(float)
    )

    return lr_all


import numpy as np
import pandas as pd
import anndata as ad
import re


def lr_dataframe_to_adata(lr_df: pd.DataFrame,
                          row_delim: str = "-",
                          col_delim: str = "-",
                          lig_tag: str = "(lig)",
                          rec_tag: str = "(rec)") -> ad.AnnData:
    """
    Convert a ligand-receptor score matrix into an AnnData object.

    lr_df
        rows    = "LigandGene-ReceptorGene"
        columns = "ClusterA(lig)-ClusterB(rec)"
    """

    # ------------------------------------------------------------------
    # 1 .  var = information about each ligand-receptor GENE pair
    # ------------------------------------------------------------------
    row_ser = lr_df.index.to_series().astype(str)
    split_row = row_ser.str.split(row_delim, n=1, expand=True)
    split_row.columns = ["Ligand_gene", "Receptor_gene"]
    var = split_row

    # ------------------------------------------------------------------
    # 2 .  obs = information about each CLUSTER pair (direction)
    # ------------------------------------------------------------------
    col_ser = pd.Series(lr_df.columns.astype(str), index=lr_df.columns)
    split_col = col_ser.str.split(col_delim, n=1, expand=True)
    split_col.columns = ["Ligand_cluster_raw", "Receptor_cluster_raw"]

    strip = lambda s, tag: re.sub(re.escape(tag) + r"\s*$", "", s)
    obs = pd.DataFrame({
        "Ligand"  : split_col["Ligand_cluster_raw"].map(lambda s: strip(s, lig_tag)),
        "Receptor": split_col["Receptor_cluster_raw"].map(lambda s: strip(s, rec_tag)),
    })

    # ------------------------------------------------------------------
    # 3 .  transpose so rows = obs, cols = var
    # ------------------------------------------------------------------
    X = lr_df.T.to_numpy(dtype=np.float32)

    # ------------------------------------------------------------------
    # 4 .  build AnnData
    # ------------------------------------------------------------------
    adata_lr = ad.AnnData(
        X   = X,
        obs = obs,
        var = var,
    )
    adata_lr.uns["source"] = "ligand-receptor score matrix (rows = cluster pairs, cols = LR pairs)"

    return adata_lr

import itertools
import pandas as pd
import numpy as np


def lr_score_cross_datasets(
    adata_L, EScore_L,           # ligand data set (genes × clusters)
    adata_R, EScore_R,           # receptor data set (genes × clusters)
    lr_df,                       # catalogue with 'ligand_symbol', 'receptor_symbol'
    clusters_L=None, clusters_R=None,
    use_var_filter=True,
    missing_value=0.0,
    include_all_pairs=True,
    agg_duplicate="mean",
    verbose=True,
):
    """
    Compute directed ligand-receptor interaction scores for *every*
    ligand-cluster in `adata_L` against *every* receptor-cluster in `adata_R`.

    Parameters
    ----------
    adata_L, adata_R
        AnnData objects that hold the Boolean flag columns in `.var`.
    EScore_L, EScore_R
        DataFrames : rows = genes, columns = clusters (enrichment scores).
    lr_df
        Two-column catalogue with 'ligand_symbol', 'receptor_symbol'.
    clusters_L, clusters_R
        Optional lists of cluster names to use; default = all columns of
        the corresponding `EScore_*`.
    use_var_filter
        If *True* a gene acts as ligand (or receptor) for a cluster only
        when the Boolean flag in the respective `adata.var[cluster]` is True.
    missing_value
        Value inserted when either gene is absent; default = 0.
    include_all_pairs
        Keep every row from `lr_df` in the final matrix (fill with
        `missing_value` when a score is missing).
    agg_duplicate
        How to collapse duplicated gene symbols (`"mean"`, `"max"`, ...).
    verbose
        Print a tiny progress counter.

    Returns
    -------
    pd.DataFrame
        Index  : ligand-receptor pairs (same order as in `lr_df`)
        Columns: f"{clusterL}(lig)-{clusterR}(rec)"
    """

    # ------------------------------------------------------------------
    # 0 . Which clusters are we working with?
    # ------------------------------------------------------------------
    if clusters_L is None:
        clusters_L = list(EScore_L.columns)
    if clusters_R is None:
        clusters_R = list(EScore_R.columns)

    if not clusters_L or not clusters_R:
        raise ValueError("At least one cluster needed in each data set")

    # ------------------------------------------------------------------
    # 1 . Ensure unique gene symbols inside each EScore matrix
    # ------------------------------------------------------------------
    if EScore_L.index.has_duplicates:
        EScore_L = EScore_L.groupby(EScore_L.index).agg(agg_duplicate)
    if EScore_R.index.has_duplicates:
        EScore_R = EScore_R.groupby(EScore_R.index).agg(agg_duplicate)

    # ------------------------------------------------------------------
    # 2 . Pre-compute gene sets per cluster (optional filter)
    # ------------------------------------------------------------------
    if use_var_filter:
        L_sets = {
            c: set(adata_L.var.index[adata_L.var[c].astype(bool)])
            for c in clusters_L
        }
        R_sets = {
            c: set(adata_R.var.index[adata_R.var[c].astype(bool)])
            for c in clusters_R
        }
    else:
        all_L_genes = set(EScore_L.index)
        all_R_genes = set(EScore_R.index)
        L_sets = {c: all_L_genes for c in clusters_L}
        R_sets = {c: all_R_genes for c in clusters_R}

    # ------------------------------------------------------------------
    # 3 . Helper that scores ONE ordered pair (clusterL → clusterR)
    # ------------------------------------------------------------------
    def _score_one_pair(cL, cR):
        # catalogue lines that survive the two gene sets
        pairs = (
            lr_df[
                lr_df["ligand_symbol"].isin(L_sets[cL]) &
                lr_df["receptor_symbol"].isin(R_sets[cR])
            ]
            .drop_duplicates(subset=["ligand_symbol", "receptor_symbol"])
            .reset_index(drop=True)
        )
        if pairs.empty:
            return pd.Series(dtype=float, name=f"{cL}(lig)-{cR}(rec)")

        lig_vals = EScore_L.loc[pairs["ligand_symbol"], cL].to_numpy()
        rec_vals = EScore_R.loc[pairs["receptor_symbol"], cR].to_numpy()

        s = pd.Series(
            lig_vals * rec_vals,
            index=pairs["ligand_symbol"] + "-" + pairs["receptor_symbol"],
            name=f"{cL}(lig)-{cR}(rec)",
        )
        return getattr(s.groupby(level=0), agg_duplicate)()

    # ------------------------------------------------------------------
    # 4 . Iterate over the Cartesian product of clusters
    # ------------------------------------------------------------------
    columns = []
    total = len(clusters_L) * len(clusters_R)
    for i, (cL, cR) in enumerate(itertools.product(clusters_L, clusters_R), 1):
        if verbose and (i % 50 == 0 or i == total):
            print(f"[cross-LR] processed {i:>4}/{total} pairs …", end="\r")
        columns.append(_score_one_pair(cL, cR))
    if verbose:
        print("")

    lr_mat = pd.concat(columns, axis=1)

    # ------------------------------------------------------------------
    # 5 . Guarantee full row index & fill missing with zeros
    # ------------------------------------------------------------------
    if include_all_pairs:
        full_index = (
            lr_df["ligand_symbol"].astype(str) + "-" +
            lr_df["receptor_symbol"].astype(str)
        ).unique()
        lr_mat = (
            lr_mat.groupby(level=0).first()   # unique index
                  .reindex(full_index)
                  .fillna(missing_value)
                  .astype(float)
        )

    return lr_mat

def merge_obs_clusters(
    adata,
    cluster_key: str = "Cluster",
    old_labels  : tuple[str, str] = ("PEP1.1.a", "PEP1.1.b"),
    new_label   : str = "PEP1.1",
    keep_old    : bool = False,
):
    """
    Replace the two old cluster names with `new_label` in adata.obs[cluster_key].
    Set keep_old=True if you prefer writing to a new column
    '<cluster_key>_merged' instead of overwriting.
    """
    col = f"{cluster_key}_merged" if keep_old else cluster_key

    # make sure the working column exists
    if keep_old:
        adata.obs[col] = adata.obs[cluster_key]
    # ------------------------------------------------------------------
    # map the old labels to the new one
    mapping = {old_labels[0]: new_label, old_labels[1]: new_label}
    adata.obs[col] = (
        adata.obs[col]
        .replace(mapping)
        .astype("category")            # keep Scanpy happy
    )
    # remove the now-unused categories (no 'inplace' parameter anymore)
    adata.obs[col] = adata.obs[col].cat.remove_unused_categories()


import sys
import numpy as np
import pandas as pd
import scipy.stats
from collections import defaultdict

# ---------------------------------------------------------------------
def CellTypeGeneFinder(
    dfpfcclus,
    df_dev,
    fc: float = 3,
    pvalcutoff: float = 0.1,
    shortcut: bool = True,
):
    """
    Parameters
    ----------
    dfpfcclus : pd.Series or DataFrame
        Cluster labels per cell (index must match df_dev columns).
    df_dev    : pd.DataFrame (genes × cells)
        Expression matrix (float).
    fc, pvalcutoff, shortcut
        Same meaning as in the original function.

    Returns
    -------
    pd.DataFrame or list
        See original docstring.
    """
    # --------------------------------------------------------------- #
    # 0 .  prepare joint table                                        #
    # --------------------------------------------------------------- #
    dfgrp    = df_dev.T.astype(float).join(dfpfcclus.T, how="inner")
    dfmean   = dfgrp.groupby(["Cluster"]).mean()
    dfmedian = dfgrp.groupby(["Cluster"]).median().T
    df_means = df_dev.mean(1)

    # --------------------------------------------------------------- #
    # 1 .  LONG route (no shortcut)                                   #
    # --------------------------------------------------------------- #
    if not shortcut:
        print("Camel...Running: clusteringValue1...")
        total_nz = (dfgrp.iloc[:, :-1] > 0).sum()
        grp_nz   = dfgrp.groupby(["Cluster"]).agg(lambda x: x.ne(0).sum())

        print("Camel...Running: clusteringValue2...")
        rest_nz  = total_nz - grp_nz
        ratio_nz = (
            (grp_nz + 0.1) / (rest_nz + 0.1) / dfgrp.groupby(["Cluster"]).count() * 1_000
        )

        dfmean   = dfmean.T.loc[ratio_nz.columns].T
        df_means = df_means.loc[ratio_nz.columns]
        df_fold  = (dfmean + 0.01).div(df_means + 0.01, axis=1) ** 0.5

        print("Camel...Running: Enrichment1...")
        escore   = (df_fold[ratio_nz.columns].fillna(0) * ratio_nz).T
        df_fold  = df_fold.T.fillna(0)

        df_avgpos = df_means.fillna(0.0)
        score00   = df_fold
        score10   = df_fold.multiply(df_avgpos, axis=0)

        # ---------- sorting indices (NumPy keeps speed) --------------
        order00 = np.argsort(score00.to_numpy(), axis=0)
        ix00    = pd.DataFrame(order00, index=score00.index, columns=score00.columns)
        order10 = np.argsort(score10.to_numpy(), axis=0)
        ix10    = pd.DataFrame(order10, index=score10.index, columns=score10.columns)

        N = min(len(df_fold.index),
                int(len(df_fold.index) / len(df_fold.columns) * 3))
        markers = defaultdict(set)

        print("Camel...Running: CrossChecking...")
        for ct in df_fold.columns:
            markers[ct].update(df_fold.index[ix00.loc[:, ct][::-1][:N]])
            markers[ct].update(df_fold.index[ix10.loc[:, ct][::-1][:N]])

        ratio_nz = ratio_nz.T
        mkdict   = {}

        sys.stdout.write("[Processing]")
        sys.stdout.flush()
        sys.stdout.write("\b" * (50 + 1))

        perc = len(df_fold.columns)
        for ct in df_fold.columns:
            temp = {num: [] for num in range(
                min(3, int(len(df_fold.columns) / 4) + 1), len(df_fold.columns))
            }
            dftemp1 = dfgrp.loc[dfgrp["Cluster"] == ct]

            itemindex = df_fold.columns.get_loc(ct)
            sys.stdout.write(f"-{int(itemindex * 100 / perc)}%-")
            sys.stdout.flush()

            for mk in markers[ct]:
                x = 0
                dfgrpmk = dfgrp[[mk, "Cluster"]]
                for ct2 in set(df_fold.columns) - {ct}:
                    dftemp2 = dfgrpmk.loc[dfgrpmk["Cluster"] == ct2]
                    pval = scipy.stats.ttest_ind(
                        dftemp1[mk], dftemp2[mk], equal_var=False
                    ).pvalue
                    if (
                        score10.loc[mk, ct] >= score10.loc[mk, ct2] * fc / 2
                        and escore.loc[mk, ct] >= escore.loc[mk, ct2] * fc
                        and pval < pvalcutoff
                    ):
                        x += 1
                if x in temp:
                    temp[x].append(mk)
            mkdict[ct] = temp

        # ------------- flatten dictionary into a long DataFrame --------
        genelist, grouplist, numberlist = [], [], []
        for num in range(min(3, int(len(df_fold.columns) / 4) + 2),
                         len(df_fold.columns)):
            for ct in df_fold.columns:
                genelist.extend(mkdict[ct][num])
                grouplist.extend([ct] * len(mkdict[ct][num]))
                numberlist.extend([num] * len(mkdict[ct][num]))

        print("Camel...Running: Marker is coming out...")
        dfmk = pd.DataFrame({"Gene": genelist, "Group": grouplist, "Num": numberlist},
                             index=genelist)

        dftest = escore.loc[dfmk.index]

        # ---- pandas ≥2.0 compatible replacement for .append ----------
        dftest = pd.concat([dfmk[["Group", "Num"]].T, dftest.T])
        dftest = dftest.T.sort_values(by=["Group", "Num"],
                                      ascending=[True, False])

        score10.columns = [f"Expr_{c}" for c in score10.columns]
        dftestnew = dftest.join(score10, how="inner")
        return dftestnew

    # --------------------------------------------------------------- #
    # 2 .  SHORTCUT route                                             #
    # --------------------------------------------------------------- #
    else:
        print("Camel...Running: clusteringValue1...")
        df_fold = dfmean.div(df_means, axis=1).T.dropna()
        df_avgpos = df_means.fillna(0)

        score00 = df_fold
        score10 = df_fold.multiply(df_avgpos, axis=0)

        print("Camel...Running: clusteringValue2...")
        order00 = np.argsort(score00.to_numpy(), axis=0)
        ix00    = pd.DataFrame(order00, index=score00.index, columns=score00.columns)
        order10 = np.argsort(score10.to_numpy(), axis=0)
        ix10    = pd.DataFrame(order10, index=score10.index, columns=score10.columns)

        N = min(len(df_fold.index),
                int(len(df_fold.index) / len(df_fold.columns) * 3))
        markers = defaultdict(set)

        sys.stdout.write("[Processing]")
        sys.stdout.flush()
        sys.stdout.write("\b" * (50 + 1))

        perc = len(df_fold.columns)
        for ct in df_fold.columns:
            markers[ct].update(df_fold.index[ix00.loc[:, ct][::-1][:N]])
            markers[ct].update(df_fold.index[ix10.loc[:, ct][::-1][:N]])

            itemindex = df_fold.columns.get_loc(ct)
            sys.stdout.write(f"-{int(itemindex * 100 / perc)}%-")
            sys.stdout.flush()

        print("Camel...Running: CrossChecking...")
        genelist = []
        for ct in df_fold.columns:
            for mk in markers[ct]:
                for ct2 in set(df_fold.columns) - {ct}:
                    if (
                        score10.loc[mk, ct] >= score10.loc[mk, ct2] * fc
                        and score00.loc[mk, ct] >= score00.loc[mk, ct2] * fc
                        and dfmedian.loc[mk, ct] > 0
                    ):
                        genelist.append(mk)

        print("Camel...Running: output genelist...")
        return genelist



import itertools
import pandas as pd
import numpy as np


def lr_score_cross_datasets(
    adata_L, EScore_L,           # ligand  (genes × clusters)
    adata_R, EScore_R,           # receptor
    lr_df,                       # catalogue with 'ligand_symbol', 'receptor_symbol'
    clusters_L=None, clusters_R=None,
    use_var_filter=True,
    missing_value=0.0,
    include_all_pairs=True,
    agg_duplicate="mean",
    verbose=True,
):
    # ------------------------------------------------------------------
    # 0 .  which clusters?
    # ------------------------------------------------------------------
    clusters_L = list(EScore_L.columns) if clusters_L is None else list(clusters_L)
    clusters_R = list(EScore_R.columns) if clusters_R is None else list(clusters_R)
    if not clusters_L or not clusters_R:
        raise ValueError("Need at least one cluster in each data set")

    # ------------------------------------------------------------------
    # 1 .  collapse duplicate gene names (optional)
    # ------------------------------------------------------------------
    if EScore_L.index.has_duplicates:
        EScore_L = EScore_L.groupby(EScore_L.index).agg(agg_duplicate)
    if EScore_R.index.has_duplicates:
        EScore_R = EScore_R.groupby(EScore_R.index).agg(agg_duplicate)

    # ------------------------------------------------------------------
    # 2 .  gene sets per cluster, but *do not* crash if the
    #      Boolean flag column is missing
    # ------------------------------------------------------------------
    def _get_gene_set(adata, cluster_name, default_set):
        """Return flagged genes for a cluster, or default_set if flag column absent."""
        if (
            use_var_filter
            and cluster_name in adata.var.columns
            and adata.var[cluster_name].dtype == bool
        ):
            return set(adata.var.index[adata.var[cluster_name]])
        return default_set

    all_L_genes = set(EScore_L.index)
    all_R_genes = set(EScore_R.index)

    L_sets = {c: _get_gene_set(adata_L, c, all_L_genes) for c in clusters_L}
    R_sets = {c: _get_gene_set(adata_R, c, all_R_genes) for c in clusters_R}

    # ------------------------------------------------------------------
    # 3 .  helper: score one ordered pair (cL → cR)
    # ------------------------------------------------------------------
    def _score_one_pair(cL, cR):
        pairs = (
            lr_df[
                lr_df["ligand_symbol"].isin(L_sets[cL])
                & lr_df["receptor_symbol"].isin(R_sets[cR])
            ]
            .drop_duplicates(subset=["ligand_symbol", "receptor_symbol"])
            .reset_index(drop=True)
        )
        if pairs.empty:
            return pd.Series(dtype=float, name=f"{cL}(lig)-{cR}(rec)")

        lig_vals = EScore_L.loc[pairs["ligand_symbol"], cL].to_numpy()
        rec_vals = EScore_R.loc[pairs["receptor_symbol"], cR].to_numpy()

        s = pd.Series(
            lig_vals * rec_vals,
            index=pairs["ligand_symbol"] + "-" + pairs["receptor_symbol"],
            name=f"{cL}(lig)-{cR}(rec)",
        )
        return getattr(s.groupby(level=0), agg_duplicate)()

    # ------------------------------------------------------------------
    # 4 .  Cartesian product of clusters
    # ------------------------------------------------------------------
    columns = []
    total = len(clusters_L) * len(clusters_R)
    for i, (cL, cR) in enumerate(itertools.product(clusters_L, clusters_R), 1):
        if verbose and (i % 50 == 0 or i == total):
            print(f"[cross-LR] processed {i:>4}/{total} pairs …", end="\r")
        columns.append(_score_one_pair(cL, cR))
    if verbose:
        print("")  # newline

    lr_mat = pd.concat(columns, axis=1)

    # ------------------------------------------------------------------
    # 5 .  guarantee full index and fill missing with zeros
    # ------------------------------------------------------------------
    if include_all_pairs:
        full_index = (
            lr_df["ligand_symbol"].astype(str) + "-" + lr_df["receptor_symbol"].astype(str)
        ).unique()
        lr_mat = (
            lr_mat.groupby(level=0).first()
                  .reindex(full_index)
                  .fillna(missing_value)
                  .astype(float)
        )

    return lr_mat



import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm

def cellcomm_dotplot(
    adata_lr,
    agg="sum",
    standard_scale=None,     # 'var', 'group', or None
    log=False,
    cmap="seismic",
    dot_max=0.8,             # fraction (0–1) passed to scatter sizing
    dot_min=0.01,
    figsize=None,
    var_names=None,
    edgecolors="none",
    size_exponent=1.0,
    **kwargs
):
    # 1. Construct the aggregated matrix
    df = pd.DataFrame({
        "Ligand": adata_lr.obs["Ligand"].values,
        "Receptor": adata_lr.obs["Receptor"].values,
        "Score": adata_lr.X.sum(axis=1)
    })
    mat = df.pivot_table(
        index="Ligand", columns="Receptor", values="Score",
        aggfunc=agg, fill_value=0.0, observed=False
    ).astype(float)

    if var_names is not None:
        mat = mat.loc[var_names]

    if log:
        mat = np.log1p(mat)

    # 2. Standard-scale rows or columns
    if standard_scale == "var":
        mins = mat.min(axis=1).to_numpy().reshape(-1, 1)
        maxs = mat.max(axis=1).to_numpy().reshape(-1, 1)
        mat = (mat - mins) / (maxs - mins + 1e-9)
    elif standard_scale == "group":
        mins = mat.min(axis=0)
        maxs = mat.max(axis=0)
        mat = (mat - mins) / (maxs - mins + 1e-9)

    # 3. Convert to long-form
    long = mat.stack().reset_index()
    long.columns = ["Ligand", "Receptor", "Score"]

    # 4. Plot
    fig, ax = plt.subplots(figsize=figsize or (0.6 * mat.shape[1], 0.6 * mat.shape[0]))
    norm = plt.Normalize(vmin=long["Score"].min(), vmax=long["Score"].max())
    cmap_obj = cm.get_cmap(cmap)

    receivers = mat.columns.tolist()
    ligands = mat.index.tolist()
    max_val = norm.vmax

    for r in long.itertuples(index=False):
        frac = r.Score / max_val if max_val != 0 else 0
        size = (frac ** size_exponent) * (dot_max - dot_min) + dot_min
        ax.scatter(
            receivers.index(r.Receptor),
            ligands.index(r.Ligand),
            s=size * (fig.dpi * 3),
            c=[cmap_obj(norm(r.Score))],
            edgecolors=edgecolors,
            **kwargs
        )

    ax.set_xticks(range(len(receivers)))
    ax.set_xticklabels(receivers, rotation=90)
    ax.set_yticks(range(len(ligands)))
    ax.set_yticklabels(ligands)
    ax.set_xlabel("Receiver")
    ax.set_ylabel("Ligand")

    sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap_obj)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, pad=0.02)
    cbar.set_label("Score")

    plt.tight_layout()
    plt.show()
    return fig, ax


# ---------------------------------------------------------------
#  colour utility
# ---------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.path import Path
from matplotlib.patches import PathPatch


# ───────────────── helpers ─────────────────
def _polar(r, th):  # Cartesian
    return np.array([r * np.cos(th), r * np.sin(th)])


def _hex2rgb(h):
    return tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))


def _pick_colors(n):
    """Return n visually-distinct RGB tuples (0-1)."""
    if n <= 20:
        cmap = cm.get_cmap('tab20', n)
        return [cmap(i)[:3] for i in range(n)]
    # >20 → cycle through tab20, tab20b, tab20c
    maps = [cm.get_cmap(nm, 20) for nm in ('tab20', 'tab20b', 'tab20c')]
    cols = (maps[i // 20](i % 20)[:3] for i in range(n))
    return list(cols)


# ───────────────── arc / ribbon primitives (same as before, but internal) ──────────
CHORDLW = .01


def _ideogram(a, b, r=1, w=.15, col=(1, 0, 0), ax=None):
    if a > b: a, b = b, a
    a, b = np.deg2rad([a, b]);
    ri = r * (1 - w)
    opt = 4 / 3 * np.tan((b - a) / 4) * r
    vs = [_polar(r, a),
          _polar(r, a) + _polar(opt, a + .5 * np.pi),
          _polar(r, b) + _polar(opt, b - .5 * np.pi),
          _polar(r, b),
          _polar(ri, b),
          _polar(ri, b) + _polar(opt * (1 - w), b - .5 * np.pi),
          _polar(ri, a) + _polar(opt * (1 - w), a + .5 * np.pi),
          _polar(ri, a),
          _polar(r, a)]
    codes = ([Path.MOVETO] + [Path.CURVE4] * 3 +
             [Path.LINETO] + [Path.CURVE4] * 3 + [Path.CLOSEPOLY])
    ax.add_patch(PathPatch(Path(vs, codes),
                           facecolor=col + (0.45,),
                           edgecolor=col + (0.40,),
                           lw=CHORDLW))


# inner ribbon between two nodes
def _ribbon(a1, b1, a2, b2, r=1, cw=.25, col=(1, 0, 0), ax=None, alpha=.7, lw=1):
    a1, b1, a2, b2 = map(np.deg2rad, [a1, b1, a2, b2])
    opt1 = 4 / 3 * np.tan((b1 - a1) / 4) * r
    opt2 = 4 / 3 * np.tan((b2 - a2) / 4) * r
    ri = r
    vs = [_polar(r, a1),
          _polar(r, a1) + _polar(opt1, a1 + .5 * np.pi),
          _polar(r, b1) + _polar(opt1, b1 - .5 * np.pi),
          _polar(r, b1),
          _polar(ri - cw, b1),
          _polar(ri - cw, a2),
          _polar(r, a2),
          _polar(r, a2) + _polar(opt2, a2 + .5 * np.pi),
          _polar(r, b2) + _polar(opt2, b2 - .5 * np.pi),
          _polar(r, b2),
          _polar(ri - cw, b2),
          _polar(ri - cw, a1),
          _polar(r, a1)]
    ax.add_patch(PathPatch(Path(vs, [Path.MOVETO] + [Path.CURVE4] * 12),
                           facecolor=col + (alpha,),
                           edgecolor=col + (alpha,),
                           lw=CHORDLW * lw))


# ───────────────── main drawing routine ─────────────────
def _draw_chord(mat, names, colors, ax,
                pad=2, rim=.12, cw=.25, alpha=.75):
    n = len(names)
    # handle zero rows
    row_sum = mat.sum(1);
    total = row_sum.sum()
    eps = total * 1e-9
    row_sum[row_sum == 0] = eps
    seg = row_sum / row_sum.sum() * (360 - pad * n)

    arcs, pos = [], {}
    cur = 0
    for i, ang in enumerate(seg):
        arcs.append((cur, cur + ang))
        step = mat[i] / row_sum[i] * ang
        c = cur
        for j, w in enumerate(step):
            pos[(i, j)] = (c, c + w)
            c += w
        cur += ang + pad

    # outer arcs
    for i, (s, e) in enumerate(arcs):
        _ideogram(s, e, r=1, w=rim, col=colors[i], ax=ax)

    max_w = mat.max() if mat.max() > 0 else 1
    for i in range(n):
        for j in range(i + 1, n):
            if mat[i, j] == mat[j, i] == 0: continue
            col = colors[j] if mat[i, j] <= mat[j, i] else colors[i]
            weight = mat[i, j] + mat[j, i]
            _ribbon(*pos[(i, j)], *pos[(j, i)], r=1 - rim, w=0,
                    cw=cw, col=col, ax=ax,
                    alpha=alpha, scale=(weight / max_w) * 3)

    # label coords
    lbl = []
    for s, e in arcs:
        mid = (s + e) / 2
        th = np.deg2rad(mid)
        angle = mid - 90 if -30 <= mid <= 210 else mid - 270
        lbl.append((*_polar(1 + rim + .25, th), angle))
    return lbl


def _pick_colors_auto(n):
    """Return ≥ n distinct RGB triples (0-1) cycling tab20 → tab20b → tab20c."""
    base = ['tab20', 'tab20b', 'tab20c']
    out = []
    for i in range(n):
        cmap = plt.colormaps.get_cmap(base[(i // 20) % 3])  # works on any MPL
        out.append(cmap(i % 20)[:3])
    return out


# ---------------------------------------------------------------
#  main plotter with “colors_dict” option
# ---------------------------------------------------------------
def MakeChordPlot(
        adata_lr,
        order=None,
        keep_unlisted=True,
        colors_dict=None,  # <-- NEW
        figsize=(10, 10),
        arc_width=.15,
        chord_width=.25,
        pad_deg=3,
        min_weight=0,
        label_r=.24,
        label_angle_shift=0,
        label_fontsize=9):
    """
    colors_dict : dict / Series  cell-type → colour
                  • values can be 3-tuple floats (0-1) or hex '#rrggbb'
                  • any node missing in the dict gets an automatic colour
    """

    # 1 · aggregate ------------------------------------------------------
    df = pd.DataFrame({
        "Ligand": adata_lr.obs["Ligand"].values,
        "Receptor": adata_lr.obs["Receptor"].values,
        "Score": adata_lr.X.sum(axis=1)
    })
    mat = (df.pivot_table(index="Ligand", columns="Receptor", values="Score",
                          aggfunc="sum", fill_value=0.0, observed=False)
           .astype(float))

    all_nodes = mat.index.union(mat.columns).tolist()
    nodes = (order or []) + ([] if keep_unlisted else [])
    if order is None:
        nodes = all_nodes
    else:
        nodes = [n for n in order if n in all_nodes]
        if keep_unlisted:
            nodes += [n for n in all_nodes if n not in nodes]

    mat = mat.reindex(index=nodes, columns=nodes, fill_value=0)
    mat = mat + mat.T
    X = mat.to_numpy()

    # 2 · colours --------------------------------------------------------
    from matplotlib import colors as mcolors  # import once at top

    auto_cols = _pick_colors_auto(len(nodes))
    color_map = {n: auto_cols[i] for i, n in enumerate(nodes)}

    if colors_dict is not None:
        for k, v in colors_dict.items():
            if k not in color_map:  # node absent from diagram
                continue

            # --- normalise --------------------------------------------------
            if isinstance(v, str):
                # hex '#rrggbb' or named colour
                v_rgb = mcolors.to_rgb(v)  # → 0-1 tuple
            elif isinstance(v, (tuple, list)) and len(v) == 3:
                if all(isinstance(x, int) for x in v):
                    # 0-255 ints
                    v_rgb = tuple(c / 255. for c in v)
                else:
                    # assume already 0-1 floats
                    v_rgb = tuple(float(c) for c in v)
            else:
                raise ValueError(f"Unrecognised colour format for '{k}': {v}")

            color_map[k] = v_rgb  # overwrite

    colors = [color_map[n] for n in nodes]

    # 3 · geometry -------------------------------------------------------
    row = X.sum(1);
    total = row.sum();
    eps = total * 1e-9
    row[row == 0] = eps
    seg = row / row.sum() * (360 - pad_deg * len(nodes))

    # 4 · draw -----------------------------------------------------------
    fig, ax = plt.subplots(figsize=figsize)
    ax.axis('off');
    ax.set_xlim(-1.3, 1.3);
    ax.set_ylim(-1.3, 1.3)

    arcs, pos, cursor = [], {}, 0
    for i, ang in enumerate(seg):
        arcs.append((cursor, cursor + ang))
        step = X[i] / row[i] * ang
        c = cursor
        for j, w in enumerate(step):
            pos[(i, j)] = (c, c + w)
            c += w
        cursor += ang + pad_deg

    for i, (a0, a1) in enumerate(arcs):
        _ideogram(a0, a1, r=1, w=arc_width, col=colors[i], ax=ax)

    max_w = X.max() or 1
    for i in range(len(nodes)):
        for j in range(len(nodes)):
            if i == j or X[i, j] < min_weight: continue
            _ribbon(*pos[(i, j)], *pos[(j, i)],
                    r=1 - arc_width, cw=chord_width,
                    col=colors[j],
                    alpha=.6,
                    lw=(X[i, j] + X[j, i]) / max_w, ax=ax)

    # labels
    for (a0, a1), name in zip(arcs, nodes):
        mid = (a0 + a1) / 2
        th = np.deg2rad(mid)
        angle = (mid - 90 if -30 <= mid <= 210 else mid - 270) + label_angle_shift
        x, y = _polar(1 + arc_width + label_r, th)
        ax.text(x, y, name.replace('_', '\n'),
                rotation=angle, ha='center', va='center',
                fontsize=label_fontsize, color=color_map[name])

    plt.tight_layout();
    plt.show()
    return fig, ax


# -------------------------------------------------------------------
# 1.  extract interactions for a ligand ± receptor filter
# -------------------------------------------------------------------
def _interactions_for_gene(adata_lr, target_gene, target_receptor=None):
    """Return tidy DF with only positive-score rows for the requested
       ligand gene (and, if given, receptor gene)."""
    var = adata_lr.var

    mask = var["Ligand_gene"] == target_gene
    if target_receptor is not None:
        mask &= var["Receptor_gene"] == target_receptor

    if not mask.any():
        return pd.DataFrame()           # nothing to plot

    # slice X to selected columns
    Xsel = adata_lr[:, mask].X
    if isinstance(Xsel, np.ndarray):
        Xsel = Xsel.copy()

    long = (pd.DataFrame(Xsel, index=adata_lr.obs_names,
                         columns=adata_lr.var_names[mask])
              .stack()
              .reset_index(name="Score"))
    long.columns = ["obs_id", "interaction_pair", "Score"]
    long = long.query("Score > 0")
    if long.empty:
        return pd.DataFrame()

    obs_meta = adata_lr.obs.loc[long["obs_id"]].reset_index(drop=True)
    var_meta = var.loc[long["interaction_pair"]].reset_index()

    return pd.DataFrame({
        "Ligand_Cluster"    : obs_meta["Ligand"].values,
        "LigandName"        : var_meta["Ligand_gene"].values,
        "ReceptorName"      : var_meta["Receptor_gene"].values,
        "ReceptorCluster"   : obs_meta["Receptor"].values,
    })


# -------------------------------------------------------------------
# 2.  end-user one-liner  – now `target_receptor` aware
# -------------------------------------------------------------------
def sankey_for_ligand(
        adata_lr,
        target_gene,
        color_map,
        *,
        target_receptor = None,     # ← NEW
        font_labels     = 15,
        font_titles     = 20,
        min_weight      = 1,
        figsize         = (6, 12),
        **sankey_kw):

    # 1 · extract interactions with the new helper
    df_long = _interactions_for_gene(
        adata_lr, target_gene, target_receptor)
    if df_long.empty:
        tag = f"{target_gene}->{target_receptor}" if target_receptor else target_gene
        raise ValueError(f"No positive interactions for '{tag}'")

    # 2 · collapse to three-column table expected by CAMELsanky
    flows = (df_long
             .groupby(["Ligand_Cluster", "ReceptorCluster"])
             .size()
             .reset_index(name="Weight")
             .query("Weight > @min_weight"))

    # 3 · pad with ZZZ rows so every node is present
    senders    = flows["Ligand_Cluster"].unique().tolist()
    receivers  = flows["ReceptorCluster"].unique().tolist()
    missing_s  = set(senders)   ^ set(flows["Ligand_Cluster"])
    missing_r  = set(receivers) ^ set(flows["ReceptorCluster"])

    for s in missing_s:
        flows.loc[len(flows)] = [s, "ZZZemptyR", 1]
    for r in missing_r:
        flows.loc[len(flows)] = ["ZZZemptyL", r, 1]

    sankey_df = flows[["Weight", "Ligand_Cluster", "ReceptorCluster"]]
    sankey_df.columns = ["Weight", "Sending_Cells", "Recieving_Cells"]

    # 4 · colour map → hex strings
    cmap_hex = {k: (v if isinstance(v, str) and v.startswith("#")
                    else "#{:02x}{:02x}{:02x}".format(*v))
                for k, v in color_map.items()}
    cmap_hex["ZZZemptyL"] = cmap_hex["ZZZemptyR"] = "#ffffff"

    # 5 · draw
    fig = plt.figure(figsize=figsize)
    CAMELsanky(
        sankey_df,
        colors       = cmap_hex,
        titles_color = "black",
        labels_size  = font_labels,
        titles_size  = font_titles,
        node_sizes   = False,
        labels_color = "k",
        **sankey_kw
    )
    subtitle = f"{target_gene}→{target_receptor}" if target_receptor else target_gene
    plt.title(f"Ligand: {subtitle} : Receptor", y=1.05, fontsize=font_titles+5)
    return fig, plt.gca()



def DrawFlow(start, end, width, left, right, color):
    """
    Draw a single flow, from "left" to "right", with y going from "start" to
    "end", width "width" and color "color".
    Input:

    start: float
    end: float
    width: float
    left: float
    right: float
    color: str
    Output: None

    Functionality:

    Draws a single flow with specified start and end points, width, and color using a Path object and adds it to the current axis.
     The flow is curved at the top and bottom, with the width increasing from the start to the middle, and decreasing from the middle to the end.
    """
    space = right - left

    verts = np.zeros(shape=(9, 2), dtype='float')
    verts[:, 1] = start
    verts[2:6, 1] = end
    verts[4:, 1] += width

    verts[:, 0] = left
    verts[1:7, 0] += space / 2
    verts[3:5, 0] += space / 2

    codes = [Path.MOVETO,
             Path.CURVE4,
             Path.CURVE4,
             Path.CURVE4,
             Path.LINETO,
             Path.CURVE4,
             Path.CURVE4,
             Path.CURVE4,
             Path.CLOSEPOLY
             ]

    path = Path(verts, codes)

    patch = matplotlib.patches.PathPatch(path, facecolor=color, lw=0, alpha=.4)
    plt.gca().add_patch(patch)


def _node_text(start, size, node_sizes):
    if node_sizes is True:
        node_sizes = '{label} ({size})'
    # Allow for formatting specs:
    elif '{label' not in node_sizes:
        size = node_sizes.format(size)
        node_sizes = '{label} {size}'
    return node_sizes.format(label=start, size=size)



# Share of total width left empty (same in each phase):
GAPS = .1

# Location of bounds (if a phase is drawn from 0 to 1).
LEFT = .1
RIGHT = .9
def CAMELsanky(data,  # cmap=plt.get_cmap('jet_r'),
               colors=None,
               flows_color=None,
               labels_color='black', titles_color='black', labels_size=20,
               titles_size=20, node_sizes=False, sort_flows_by_nodes=False):
    """
    CAMELsanky function for generating a Sankey diagram.

    Args:
    data (pd.DataFrame): Input data for the diagram.
    colors (dict, optional): A dictionary mapping labels to colors.
    flows_color (str, optional): Color for flows between nodes.
    labels_color (str, optional): Color for node labels.
    titles_color (str, optional): Color for titles.
    labels_size (int, optional): Font size for node labels.
    titles_size (int, optional): Font size for titles.
    node_sizes (bool, optional): If True, display node sizes in the diagram.
    sort_flows_by_nodes (bool, optional): If True, sort flows by nodes.
    """

    data = pd.DataFrame(data)

    # One column is for the weights, the remaining n+1 limits define n phases:
    phases = data.shape[1] - 2

    # all_labels = data.iloc[:, 1:].stack().unique()

    # colors = dict(zip(all_labels,
    #                  cmap(np.arange(0, len(all_labels))/len(all_labels))))

    # Actual scale from flow/block width to drawn width:
    factor = (1 - GAPS) / data.iloc[:, 0].sum()

    # The first column always contains weights:
    var_weight = data.columns[0]
    for phase in range(phases):
        # ... while the columns containing variables shift at each phase:
        var_left = data.columns[phase + 1]
        var_right = data.columns[phase + 2]

        # Compute total weight for each label:
        l_sizes = data.groupby(var_left)[var_weight].sum()
        r_sizes = data.groupby(var_right)[var_weight].sum()

        # Drop empty cats (https://github.com/pandas-dev/pandas/issues/8559):
        l_sizes, r_sizes = (s.pipe(lambda x: x[x > 0]) for s in (l_sizes, r_sizes))

        # Map weights to drawn sizes:
        l_shares = l_sizes * factor
        r_shares = r_sizes * factor

        # Distribute gap space among gaps:
        l_gaps = GAPS / max((len(l_shares) - 1), 1)
        r_gaps = GAPS / max((len(r_shares) - 1), 1)

        # Compute blocks positions, including gaps:
        l_starts = (l_shares + l_gaps).cumsum().shift().fillna(0)
        r_starts = (r_shares + r_gaps).cumsum().shift().fillna(0)

        for (pos, l, w, starts, shares) in (
                ('right', phase + RIGHT, 1 - RIGHT, r_starts, r_shares),
                ('left', phase, LEFT, l_starts, l_shares)):
            if pos == 'right' and phase < phases - 1:
                # Center text for full width:
                text_x = l + w
            elif pos == 'left' and phase:
                # Do not draw text - it will be drawn by next phase:
                text_x = -1
            else:
                # Center text for half width (first or last extreme):
                text_x = l + 0.5 * w

            for idx, start in enumerate(starts.index):

                # Draw blocks:
                bottom = starts.loc[start]
                p = matplotlib.patches.Rectangle((l, 1 - bottom - shares.loc[start]),
                                      w, shares.loc[start],
                                      fill=False, clip_on=False)
                # if text not in ["ZZZemptyL","ZZZemptyR"]:
                pc = PatchCollection([p], facecolor=colors[start], alpha=.75)
                # else:
                #   pc = PatchCollection([p], facecolor=colors[start], alpha=0)
                plt.gca().add_collection(pc)

                # Draw labels text:
                if text_x != -1 and labels_color is not None:
                    if node_sizes is not False:
                        if phase == 0 and pos == 'left':
                            size = l_sizes.iloc[idx]
                        else:
                            size = r_sizes.iloc[idx]
                        text = _node_text(start, size, node_sizes)
                    else:
                        text = f"{start}"
                    if text not in ["ZZZemptyL", "ZZZemptyR"]:
                        plt.gca().text(text_x,
                                       1 - bottom - 0.5 * shares.loc[start],
                                       text,
                                       horizontalalignment='center',
                                       verticalalignment='center',
                                       fontsize=labels_size, color=labels_color)

            # Draw titles:
            if text_x != -1 and titles_color is not None:
                plt.gca().text(text_x,
                               1,
                               var_left if pos == 'left' else var_right,
                               horizontalalignment='center',
                               verticalalignment='bottom',
                               fontsize=titles_size, color=titles_color)

        # Draw flows:
        flows_list = data[[var_weight,
                           var_left,
                           var_right]]
        if sort_flows_by_nodes:
            # Avoid (probably unjustified - we're working on entire columns)
            # SettingWithCopyWarning:
            flows_list = flows_list.copy()
            for a_var, starts in (var_left, l_starts), (var_right, r_starts):
                dtype = pd.CategoricalDtype(categories=starts.index,
                                            ordered=True)
                flows_list[a_var] = flows_list[a_var].astype(dtype)
            flows_list = flows_list.sort_values([var_left, var_right])

        for idx, (weight, start, end) in flows_list.iterrows():
            if start not in ["ZZZemptyL", "ZZZemptyR"]:
                if end not in ["ZZZemptyL", "ZZZemptyR"]:
                    width = weight * factor
                    l = l_starts.loc[start]
                    r = r_starts.loc[end]
                    DrawFlow(1 - l_starts.loc[start] - width,
                               1 - r_starts.loc[end] - width, width,
                               phase + LEFT, phase + RIGHT,
                               flows_color or colors[start])
                    l_starts.loc[start] += width
                    r_starts.loc[end] += width

    plt.xlim(0, phases)
    plt.axis('off')


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import anndata as ad
from typing import Optional, Tuple

def plot_lr_heatmap(
    adata_lr: ad.AnnData,
    ligand_gene   : Optional[str] = None,
    receptor_gene : Optional[str] = None,
    *,
    cmap: str = "rocket_r",
    figsize: Tuple[int, int] = (10, 4),
    vmax: float | None = None,
    vmin: float = 0.0,
    annot: bool = False,
):
    """
    Draw a heat-map of (cluster-pair × LR-pair) scores for the requested
    ligand and/or receptor gene.

    Parameters
    ----------
    adata_lr       : AnnData
        The LR-score matrix created by `lr_dataframe_to_adata`
        (rows = cluster pairs, cols = LR pairs).
    ligand_gene    : str | None
        Select only ligand–receptor pairs whose ligand gene equals this
        string.  If *None* the ligand is not filtered.
    receptor_gene  : str | None
        Analogous filter on the receptor gene.
    cmap, figsize, vmax, vmin, annot
        Styling options forwarded to `seaborn.heatmap`.

    Returns
    -------
    (fig, ax, df)
        • `fig`, `ax` – the Matplotlib objects
        • `df`        – the DataFrame that was plotted
    """
    # ------------------------------------------------------------------
    # 1. pick LR columns that match the requested gene(s)
    # ------------------------------------------------------------------
    mask = pd.Series(True, index=adata_lr.var_names)
    if ligand_gene is not None:
        mask &= adata_lr.var["Ligand_gene"].eq(ligand_gene)
    if receptor_gene is not None:
        mask &= adata_lr.var["Receptor_gene"].eq(receptor_gene)

    if not mask.any():
        raise ValueError("No LR pairs match the given gene filters")

    # ------------------------------------------------------------------
    # 2. keep only rows (cluster pairs) with a positive score
    #    for any of the selected LR pairs
    # ------------------------------------------------------------------
    Xsel = adata_lr[:, mask].X
    if isinstance(Xsel, np.ndarray):
        row_keep = Xsel.sum(axis=1) > 0
    else:                                  # sparse
        row_keep = np.asarray(Xsel.sum(1)).flatten() > 0

    # slice AnnData
    ad_sel = adata_lr[row_keep, mask]

    # ------------------------------------------------------------------
    # 3. convert to tidy DataFrame  (your original two-liner)
    # ------------------------------------------------------------------
    df = pd.DataFrame(
        ad_sel.X,
        index  = ad_sel.obs.index,   # cluster-pair labels
        columns= ad_sel.var.index    # ‘LigandGene-ReceptorGene’
    ).T

    # ------------------------------------------------------------------
    # 4. plot
    # ------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(
        df,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        annot=annot,
        linewidths=.5,
        linecolor="0.9",
        cbar_kws={"label": "Interaction score"},
        ax=ax,
    )
    ax.set_xlabel("Ligand-cluster ➜ Receptor-cluster")
    ax.set_ylabel("LigandGene-ReceptorGene")
    title_bits = []
    if ligand_gene:   title_bits.append(f"ligand = {ligand_gene}")
    if receptor_gene: title_bits.append(f"receptor = {receptor_gene}")
    ax.set_title("Cell-cell interaction heat-map\n" + ", ".join(title_bits))

    plt.tight_layout()
    plt.show()
    return fig, ax, df
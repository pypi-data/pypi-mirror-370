# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import datetime
import matplotlib.pyplot as plt
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

def shannon_entropy(S, mode="discrete"):
    """
    https://stackoverflow.com/questions/42683287/python-numpy-shannon-entropy-array
    """
    S = np.asarray(S)
    pS = S / S.sum()
    # Remove zeros
    if mode == "continuous":
        return -np.sum(pS*np.log2(S))
    if mode == "discrete":
        pS = pS[np.nonzero(pS)[0]]
        return -np.sum(pS*np.log2(pS))



def PurityEstimationLearningScore(datax, clusterlist,  elbow=True, figureplot=True):

    """
    The function first calculates the Shannon entropy for each cluster based on their PCA scores,
    and then calculates the Shannon entropy for each cluster after shuffling the PCA scores.
    The ratio of these two values, normalized by the number of PCA dimensions, is used as a measure of purity.
    The function returns a pandas dataframe sorted by the purity scores, with an optional elbow plot if figureplot is True.

    Input:

    datax: Single-cell RNAseq dataset
    clusterlist: String indicating the name of the cluster column
    elbow: Boolean indicating whether to perform elbow analysis to determine the optimal number of clusters
    figureplot: Boolean indicating whether to plot the result
    Output:

    dfsort: Pandas dataframe sorted by purity scores, with an optional elbow plot if figureplot is True.
    """
    cluslist = list(set(datax.obs[clusterlist]))
    entropyValue1=[]
    for item in cluslist:
        scpd1 = datax[datax.obs[clusterlist] == item]
        X_pcavalue=np.array(scpd1.obsm['Celltype_Score'])
        v0 = shannon_entropy(
            (X_pcavalue[:, 0] - X_pcavalue[:, 0].min()) / (X_pcavalue[:, 0].max() - X_pcavalue[:, 0].min()))
        v0=v0/scpd1.shape[0]
        num=X_pcavalue.shape[1]
        for i in range(1, num):
            vtemp = shannon_entropy(
                (X_pcavalue[:, i] - X_pcavalue[:, i].min()) / (X_pcavalue[:, i].max() - X_pcavalue[:, i].min()))
            vtemp=vtemp/scpd1.shape[0]
            v0 = v0 * vtemp
        entropyValue1.append(v0 ** (-1 / num))
    entropyValue2=[]
    for item in cluslist:
        scpd1 = datax[datax.obs[clusterlist] == item]
        X_pcavalueAll=np.array(scpd1.obsm['Celltype_Score'])
        orishape=X_pcavalueAll.shape
        arr=X_pcavalueAll.flatten()
        np.random.shuffle(arr)
        X_pcavalue=arr.reshape(orishape)
        #datax.obsm["PCAall"]=X_pcavalueAllnew
        v0 = shannon_entropy(
            (X_pcavalue[:, 0] - X_pcavalue[:, 0].min()) / (X_pcavalue[:, 0].max() - X_pcavalue[:, 0].min()))
        v0=v0/scpd1.shape[0]
        num=X_pcavalue.shape[1]
        for i in range(1, num):
            vtemp = shannon_entropy(
                (X_pcavalue[:, i] - X_pcavalue[:, i].min()) / (X_pcavalue[:, i].max() - X_pcavalue[:, i].min()))
            vtemp=vtemp/scpd1.shape[0]
            v0 = v0 * vtemp
        entropyValue2.append(v0 ** (-1 / num))
    entropyValue=np.array(entropyValue2)/np.array(entropyValue1)-1
    dfsort = pd.DataFrame([cluslist, entropyValue]).T
    dfsort.columns = ["Name", "Values"]
    dfsort = dfsort.sort_values(["Values"], ascending=False)
    dfsort["Purity"] = [1] * dfsort.shape[0]
    if elbow==True:
        from kneed import KneeLocator
        kn = KneeLocator(range(0, dfsort.shape[0]), dfsort["Values"], curve='convex', direction='decreasing')
        dfsort["Purity"][:(kn.knee + 1)] = 0
    if figureplot:
        fig = plt.figure()
        fig, ax = plt.subplots(figsize=(7, 7))
        plt.scatter(dfsort["Name"], dfsort["Values"], s=100)
        plt.xticks(rotation=70, fontsize=15)
        plt.yticks(rotation=0, fontsize=15)
        if elbow==True:
            plt.axvline(dfsort["Name"].values[kn.knee], c='r', alpha=0.8, linestyle='dashed')
        plt.ylabel('LearningScore_Normalized Purity', position=(0, 0.5), color=(0.2, 0.2, 0.2),
                   alpha=0.8, fontsize=20)
        plt.xlabel("Cell Types", fontsize=20)
        ax.spines.right.set_visible(False)
        ax.spines.top.set_visible(False)
        plt.grid(False)
    return dfsort

def PurityEstimationPCA(datax, clusterlist, PCnum=10, elbow=True, figureplot=True):
    """
    Inputs:

    datax: AnnData object, input data to perform PCA on
    clusterlist: str, name of column in data.obs that contains cluster information
    PCnum: int, number of principal components to use in entropy calculation, default=10
    elbow: bool, whether to use elbow method to determine cutoff for low purity clusters, default=True
    figureplot: bool, whether to generate a scatter plot of purity values, default=True
    Outputs:

    dfsort: pandas DataFrame with columns "Name", "Values", and "Purity". "Name" contains cluster names, "Values" contains normalized purity values, and "Purity" indicates whether the cluster is considered high (1) or low (0) purity based on cutoff determined by elbow method or not used if elbow=False.
    Functionality:

    Calculates the normalized entropy values for each cluster based on the specified number of principal components.
    Calculates the normalized entropy values for each cluster after shuffling the principal component values, which serves as a null model.
    Calculates the purity value for each cluster by subtracting the normalized entropy value of the null model from the original normalized entropy value, and dividing by the original normalized entropy value.
    Sorts the clusters by decreasing purity values.
    Uses the elbow method to determine the cutoff for low purity clusters if elbow=True.
    Returns a pandas DataFrame with cluster names, normalized purity values, and high/low purity status. Also generates a scatter plot of cluster purity values if figureplot=True.
    """
    num = PCnum
    cluslist = list(set(datax.obs[clusterlist]))
    X = datax.X
    pca_ = PCA(n_components=min(datax.shape[0], num), svd_solver='auto', random_state=0)
    PCAmodel = pca_.fit(X)
        # X_cca,Y_cca=cca_.fit_transform(X,Y)
    X_pcavalueAll = abs(PCAmodel.transform(X))
    datax.obsm["PCAall"]=X_pcavalueAll
    entropyValue1 = []
    for item in cluslist:
        scpd1 = datax[datax.obs[clusterlist] == item]
        X_pcavalue=scpd1.obsm["PCAall"]
        v0 = shannon_entropy(
            (X_pcavalue[:, 0] - X_pcavalue[:, 0].min()) / (X_pcavalue[:, 0].max() - X_pcavalue[:, 0].min()))
        v0=v0/scpd1.shape[0]
        for i in range(1, num):
            vtemp = shannon_entropy(
                (X_pcavalue[:, i] - X_pcavalue[:, i].min()) / (X_pcavalue[:, i].max() - X_pcavalue[:, i].min()))
            vtemp=vtemp/scpd1.shape[0]
            v0 = v0 * vtemp
        entropyValue1.append(v0 ** (-1 / num))
    orishape=X_pcavalueAll.shape
    arr=X_pcavalueAll.flatten()
    np.random.shuffle(arr)
    X_pcavalueAllnew=arr.reshape(orishape)
    datax.obsm["PCAall"]=X_pcavalueAllnew
    entropyValue2=[]
    for item in cluslist:
        scpd1 = datax[datax.obs[clusterlist] == item]
        X_pcavalue=scpd1.obsm["PCAall"]
        v0 = shannon_entropy(
            (X_pcavalue[:, 0] - X_pcavalue[:, 0].min()) / (X_pcavalue[:, 0].max() - X_pcavalue[:, 0].min()))
        v0=v0/scpd1.shape[0]
        for i in range(1, num):
            vtemp = shannon_entropy(
                (X_pcavalue[:, i] - X_pcavalue[:, i].min()) / (X_pcavalue[:, i].max() - X_pcavalue[:, i].min()))
            vtemp=vtemp/scpd1.shape[0]
            v0 = v0 * vtemp
        entropyValue2.append(v0 ** (-1 / num))
    entropyValue=np.array(entropyValue2)/np.array(entropyValue1)-1
    dfsort = pd.DataFrame([cluslist, entropyValue]).T
    dfsort.columns = ["Name", "Values"]
    dfsort = dfsort.sort_values(["Values"], ascending=False)
    dfsort["Purity"] = [1] * dfsort.shape[0]
    if elbow==True:
        from kneed import KneeLocator
        kn = KneeLocator(range(0, dfsort.shape[0]), dfsort["Values"], curve='convex', direction='decreasing')
        dfsort["Purity"][:(kn.knee + 1)] = 0
    if figureplot:
        fig = plt.figure()
        fig, ax = plt.subplots(figsize=(7, 7))
        plt.scatter(dfsort["Name"], dfsort["Values"], s=100)
        plt.xticks(rotation=70, fontsize=15)
        plt.yticks(rotation=0, fontsize=15)
        if elbow==True:
            plt.axvline(dfsort["Name"].values[kn.knee], c='r', alpha=0.8, linestyle='dashed')
        plt.ylabel('%sPCs_Normalized Purity'%PCnum, position=(0, 0.5), color=(0.2, 0.2, 0.2),
                   alpha=0.8, fontsize=20)
        plt.xlabel("Cell Types", fontsize=20)
        ax.spines.right.set_visible(False)
        ax.spines.top.set_visible(False)
        plt.grid(False)
    return dfsort

def PurityEstimation(datax, clusterlist, PCnum=10, figureplot=True):
    """
    Inputs
    datax: an AnnData object
    clusterlist: a string representing the column name in the datax.obs dataframe that contains the cell type cluster assignments
    PCnum: an integer specifying the number of principal components to use for entropy estimation
    figureplot: a boolean indicating whether to generate a plot or not (default is True)
    Outputs:
    dfsort: a pandas dataframe with columns "Name" (cell type names), "Values" (entropy values), and "Purity" (0 for impure and 1 for pure cell types)
    Functionality:

    For each cell type in clusterlist, it performs PCA on the subset of data in datax that is assigned to that cell type, and estimates entropy based on the first PCnum principal components.
    It calculates the product of the entropy values and raises it to the power of -1/PCnum to obtain a "purity score" for the cell type.
    It sorts the cell types by their purity scores and assigns a purity label (0 or 1) based on the "knee point" in the sorted list (determined using the kneed package).
    It generates a scatter plot of the entropy values for each cell type and marks the knee point with a vertical dashed line.
    """
    entropyValue = []
    num = PCnum
    cluslist = list(set(datax.obs[clusterlist]))
    for item in cluslist:
        scpd1 = datax[datax.obs[clusterlist] == item]
        X = scpd1.X
        pca_ = PCA(n_components=min(scpd1.shape[0], num), svd_solver='auto', random_state=0)
        PCAmodel = pca_.fit(X)
        # X_cca,Y_cca=cca_.fit_transform(X,Y)
        X_pcavalue = abs(PCAmodel.transform(X))
        v0 = shannon_entropy(
            (X_pcavalue[:, 0] - X_pcavalue[:, 0].min()) / (X_pcavalue[:, 0].max() - X_pcavalue[:, 0].min()))
        for i in range(1, num):
            vtemp = shannon_entropy(
                (X_pcavalue[:, i] - X_pcavalue[:, i].min()) / (X_pcavalue[:, i].max() - X_pcavalue[:, i].min()))
            v0 = v0 * vtemp
        # v1=shannon_entropy((X_pcavalue[:,0]-X_pcavalue[:,0].min())/(X_pcavalue[:,0].max()-X_pcavalue[:,0].min()), mode="discrete", verbose=False)
        # v2=shannon_entropy((X_pcavalue[:,1]-X_pcavalue[:,1].min())/(X_pcavalue[:,1].max()-X_pcavalue[:,1].min()), mode="discrete", verbose=False)
        # v1=shannon_entropy((X_pcavalue.std(1)-X_pcavalue.std(1).min())/(X_pcavalue.std(1).max()-X_pcavalue.std(1).min()), mode="discrete", verbose=False)
        entropyValue.append(v0 ** (-(1 / num)))
    dfsort = pd.DataFrame([cluslist, entropyValue]).T
    dfsort.columns = ["Name", "Values"]
    dfsort = dfsort.sort_values(["Values"], ascending=False)
    from kneed import KneeLocator
    kn = KneeLocator(range(0, dfsort.shape[0]), dfsort["Values"], curve='convex', direction='decreasing')
    dfsort["Purity"] = [1] * dfsort.shape[0]
    dfsort["Purity"][:(kn.knee + 1)] = 0
    if figureplot:
        fig = plt.figure()
        fig, ax = plt.subplots(figsize=(7, 7))
        plt.scatter(dfsort["Name"], dfsort["Values"], s=100)
        plt.xticks(rotation=70, fontsize=15)
        plt.yticks(rotation=0, fontsize=15)
        plt.axvline(dfsort["Name"].values[kn.knee], c='r', alpha=0.8, linestyle='dashed')
        plt.ylabel('Normalized Entropy', position=(0, 0.5), color=(0.2, 0.2, 0.2),
                   alpha=0.8, fontsize=20)
        plt.xlabel("Cell Types", fontsize=20)
        ax.spines.right.set_visible(False)
        ax.spines.top.set_visible(False)
        plt.grid(False)
    return dfsort


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

def UMAPtrain(datax,NN=25,mdist=0.6, rd=173, n_comp=2):
    #XXdf, df with row cellID, with columns probability features, and the last column is clustername
    XX=datax.obsm["Celltype_Score"].astype(np.float32)
    umaptrain = umap.UMAP(n_neighbors=NN, min_dist=mdist,
                          # metric='correlation',
                          random_state=rd,
                          n_components=n_comp).fit(XX)
    datax.obsm['X_umap']= umaptrain.embedding_
    datax.obsm['X_draw_graph_fr'] = umaptrain.embedding_
    datax.obsm['X_CAMELumap'] = umaptrain.embedding_
    #dfg = pd.DataFrame(X_r)
    #dfg.index = XXdf.index
    #dfg2 = dfg.join(XXdf.iloc[:,-1:], how="inner")
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


def MergeObjectValue3(DatasetName, filelist, filepath, templateGenelist):
    ann_data_list = {}
    for jname in set(DatasetName):
        print(jname)
        all_dataframes = []
        scorearray = None
        for item in filelist:
            if item.startswith(jname):
                sctemp = anndata.read(filepath + item)
                sctemp.obsm['NormalizedMatrix'] = sctemp.X
                if type(sctemp.obsm['NormalizedMatrix']) == sparse.csr.csr_matrix:
                    norm_matrix = sctemp.obsm['NormalizedMatrix'].toarray()
                else:
                    norm_matrix = sctemp.obsm['NormalizedMatrix']
                sctemp.X = norm_matrix
                sctemp = DataScalingLogMinMax(sctemp)
                df = pd.DataFrame(sctemp.X.T, index=sctemp.var.index, columns=sctemp.obs.index)
                df["GeneCount"] = 1
                df = df.reindex(templateGenelist).fillna(0)
                all_dataframes.append(df)

                # Accumulate scorearray if needed
                if 'Celltype_Score' in sctemp.obsm:
                    scorearray = np.concatenate((scorearray, sctemp.obsm['Celltype_Score']),
                                                axis=1) if scorearray is not None else sctemp.obsm['Celltype_Score']

                # Free memory
                del norm_matrix, df
                gc.collect()

        # Sum the dataframes
        df_combined = pd.concat(all_dataframes).groupby(level=0).sum()

        # Create an AnnData object
        ad = anndata.AnnData(df_combined.iloc[:, :-1].T)
        ad.obs = sctemp.obs  # Assuming obs is same for all files
        ad.obsm = sctemp.obsm  # Assuming obsm is same for all files
        ad.uns = sctemp.uns  # Assuming uns is same for all files
        ad.obs["Dataset"] = [jname] * ad.shape[0]
        if scorearray is not None:
            ad.obsm['PCAraw0'] = scorearray
        del ad.obsm["NormalizedMatrix"]
        ann_data_list[jname] = ad

        # Free memory
        del sctemp, all_dataframes, df_combined, scorearray
        gc.collect()

    # Concatenate all Anndata objects
    adatax = anndata.concat([ann_data_list[jname] for jname in set(DatasetName)])
    # adatax = adatax[:, adatax.X.T.sum(1) > 0]

    return adatax


def ConsistantAssign(datax,dfsig,outputfilepath=None,outputPlot=True ):
    """
    Inputs:

    datax: AnnData object containing the scRNA-seq data with cell type scores
    dfsig: Pandas dataframe containing signature matrix for cell type scores
    outputfilepath: Path to output file for cells with inconsistent cluster assignment (default=None)
    outputPlot: Boolean to control whether to plot the consistency score (default=True)
    Outputs:

    datax: AnnData object with additional columns "PredictCluster" and "ClusterConsistanceScore"
    If outputfilepath is provided, a tab-separated file with cells with inconsistent cluster assignment will be saved to the specified path
    If outputPlot is set to True, a bar plot showing the percentage of consistently assigned cells for each cluster will be displayed
    Functionality:

    Calculates the consistency score for each cell by comparing its true cluster assignment with its predicted cluster assignment based on the highest cell type score
    Adds the predicted cluster assignment and the consistency score as new columns in the AnnData object
    Optionally saves a file with cells that have inconsistent cluster assignment
    Optionally displays a bar plot showing the percentage of consistently assigned cells for each cluster
    """
    dfprob=pd.DataFrame(datax.obsm['Celltype_Score'], index=datax.obs.index,columns=datax.uns['Celltype_Score_RefCellType'])
    dfprob1=dfprob-dfsig.quantile(0.95)
    dfprob1[dfprob1<0]=0
    dfprob1neg=dfprob1.loc[dfprob1.sum(1)==0]
    dfprob1posi=dfprob1.loc[dfprob1.sum(1)>0]
    cluslist=[]
    colname=dfprob1posi.columns
    for i in range(dfprob1posi.shape[0]):
        temp=dfprob1posi.iloc[i,:]
        cluslist.append(colname[temp.tolist().index(max(temp))])
    dfprob1posi["PredictCluster"]=cluslist
    dfprob1neg["PredictCluster"]=["NoPrediction"]*dfprob1neg.shape[0]
    dfprob1=dfprob1posi.append(dfprob1neg)
    dfprob1=dfprob1.loc[datax.obs.index]
    datax.obs["PredictCluster"]=dfprob1["PredictCluster"]
    sumlist=[]
    for item in datax.obs.index:
        if datax.obs.loc[item,"Cluster"]==datax.obs.loc[item,"PredictCluster"]:
            sumlist.append(1)
        else:
            sumlist.append(0)
    datax.obs["ClusterConsistanceScore"]=sumlist
    if outputfilepath!=None:
        dfoutput=datax.obs.loc[datax.obs["ClusterConsistanceScore"]==0][["Cluster","PredictCluster"]].sort_values(["Cluster"])
        dfoutput.to_csv(outputfilepath,sep="\t")
    if outputPlot==True:
        Percent0=datax.obs.groupby(["Cluster"])["ClusterConsistanceScore"].sum()/datax.obs.groupby(["Cluster"])["ClusterConsistanceScore"].count()
        Percent75=1-Percent0
        PercentDf=[Percent0,Percent75]
        PercentSum=pd.DataFrame(PercentDf,index=["Consistent","Inconsistent"])*100

        plt.figure(figsize=(25,10))

        cmap = plt.cm.bwr
        percfig=PercentSum.T.plot.bar(stacked=True, legend=False, figsize=(20, 10),yticks = range(0,101,10),color=cmap(np.linspace(0, 1, 2)),alpha=0.95)
        plt.xticks(rotation=90,
                   #horizontalalignment='center',
                   verticalalignment='top', position=(0,-0.05), fontsize=20)
        plt.yticks(rotation=0, verticalalignment='top', position=(0,0), fontsize=20)
        percfig.set_ylim(ymin=0, ymax=100)
        #percfig.grid(False)
        plt.ylabel('Percentage of consistently assigned cells (%)', fontsize=25, position=(0,0.5), color=(0.2,0.2,0.2), alpha=0.95)
        plt.xlabel("",position=(0,-0.5), fontsize=15)
        percfig.spines.right.set_visible(False)
        percfig.spines.top.set_visible(False)
        recs2 = []
        for i in range(len(PercentSum.index.tolist())):
            recs2.append(mpatches.Rectangle((0,0),1,1, alpha=0.95,edgecolor="Grey", fc=cmap(np.linspace(0, 1, 2))[i]))

        percfig.legend(recs2,PercentSum.index.tolist(),loc=2,bbox_to_anchor=(1.01, 1.1), prop={'size':25})
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


def CellTypeSimilarityViolinPlot(
        datax, dataref, fontsizevalue: int = 15, bw_adjust: float = .4):
    """
    Produce a grid of width‑normalised violin plots of Celltype_Score.
    """
    import numpy as np, pandas as pd, seaborn as sns, matplotlib.pyplot as plt
    from matplotlib import gridspec, pyplot

    sns.set_style("white")          #  ← add here
    plt.rcParams["axes.grid"] = False
    ref_types = np.sort(dataref.obs["Cluster"].unique())
    qry_types = np.sort(datax.obs["Cluster"].unique())

    # ------------------------------------------------------------------ build
    dfprob = pd.DataFrame(
        datax.obsm["Celltype_Score"],
        index=datax.obs.index,
        columns=datax.uns["Celltype_Score_RefCellType"]
    )
    dfmk = dfprob.astype(float).join(datax.obs["Cluster"], how="inner").T

    # ------------------------------------------------------------------ colours
    refcolor_dict = pd.Series(dataref.uns["refcolor_dict"])
    colors = refcolor_dict.map(lambda rgb: np.asarray(rgb) / 255.)

    # ------------------------------------------------------------------ canvas
    fig = pyplot.figure(figsize=(int(len(ref_types) / 2), len(qry_types)))
    outer = gridspec.GridSpec(len(qry_types), 1, hspace=.05)

    for r, qtype in enumerate(qry_types):
        ax_row = fig.add_subplot(outer[r, 0])
        inner = gridspec.GridSpecFromSubplotSpec(
            1, len(ref_types), subplot_spec=outer[r], wspace=.02)

        # background bars (purely cosmetic)
        x = np.arange(.5, len(ref_types) + .5)
        ax_row.bar(x, [100]*len(ref_types), width=.95, color="white", alpha=.4)
        ax_row.set_xlim(0, len(ref_types)); ax_row.set_ylim(0, 100)
        ax_row.set_ylabel(qtype, rotation=0, labelpad=90, fontsize=fontsizevalue)
        ax_row.set_xticks(x, labels=ref_types, rotation=90,
                          ha="center", fontsize=fontsizevalue)
        if r < len(qry_types) - 1:
            ax_row.set_xticklabels([])
        ax_row.spines[['right', 'top']].set_visible(False)

        # ------------------------------------------------------------ violins
        dftemp = dfmk.T.loc[dfmk.loc["Cluster"] == qtype]
        dftest = dftemp.drop(columns="Cluster").astype(float)

        for c, ref in enumerate(ref_types):
            base = fig.add_subplot(inner[0, c]); base.axis("off")
            ax = base.twinx();  ax.set_ylim(-.01, 100);  ax.axis("off")

            data_long = dftest.join(dftemp["Cluster"])
            sns.violinplot(
                y=ref, data=data_long, ax=ax,
                density_norm="width",   # constant width
                bw_adjust=bw_adjust,
                common_norm=False,      # <‑‑ key difference
                cut=2, gridsize=500, width=.9,
                color=colors[ref],      # RGB in 0‑1
                inner="box", edgecolor=None, saturation=1,
            )
            plt.setp(ax.collections, alpha=.5)

    fig.tight_layout()
    return dfprob



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

def MergeCluster(adatax, reflist=[], NewName=None):
    newlist=[]
    adatax.obs[ 'Origin_Assigned_Celltype']=adatax.obs[ 'Assigned_Celltype']
    for item in adatax.obs[ 'Assigned_Celltype']:
        if item in reflist:
            newlist.append(NewName)
        else:
            newlist.append(item)
    adatax.obs[ 'Assigned_Celltype']=newlist
    return adatax

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

def prediction(datax, mcolor_dict,net,learninggroup="train", radarplot=True, fontsizeValue=35,
              datarefplot=None,
               ncolnm=1, bbValue=(1.1, 1.05)):
    #mwanted_order = mwanted_order, mclasses_names = mclasses_names, mprotogruop = dfpfcclus.loc["Cluster"].values,
    #mdf_train_set = mdf_train_set, figsizeV = 18, mtrain_index = mtrain_index, net = net, mreorder_ix = mreorder_ix,
    #mcolor_dict = refcolor_dict, learninggroup = "test"
    """
    Inputs:

    datax: an AnnData object containing gene expression data
    mcolor_dict: a dictionary mapping cell type names to colors
    net: a trained neural network model
    learninggroup: a string indicating whether to perform the prediction on the "train" or "test" set
    radarplot: a boolean indicating whether to generate a radar plot of the results
    fontsizeValue: an integer specifying the font size of the radar plot labels
    datarefplot: an AnnData object containing reference gene expression data (only used if learninggroup is "test")
    ncolnm: an integer specifying the number of columns in the radar plot
    bbValue: a tuple of two floats specifying the scaling factor for the radar plot axes
    Outputs:

    datax: an AnnData object containing the predicted cell type scores
    (if radarplot is True):
    axm: the Matplotlib axis object for the radar plot
    dfclRef: a Pandas DataFrame containing the coordinates of the cell type scores in the radar plot
    Function description: This function predicts cell type scores using a trained neural network model,
    either on the train or test set of gene expression data stored in an AnnData object.
    If radarplot is True, it generates a radar plot of the predicted scores.
    """

    mcolor_dict=pd.Series(mcolor_dict)
    if  learninggroup=="train":
        mdf_train_set = pd.DataFrame(datax.obsm["train_set_values"].T, index=datax.uns["train_set_gene"],
                                     columns=datax.obs.index)
        mtrain_index = datax.obs["mtrain_index"].values
        mwanted_order = datax.uns["mwanted_order"]
        mclasses_names = datax.uns["mclasses_names"]
        mprotogruop = datax.obs["Cluster"].values
        dfpfcclus = datax.obs["Cluster"]
        mreorder_ix = [list(mclasses_names).index(i) for i in mwanted_order]
        mbool00 = np.in1d( mclasses_names[mtrain_index],  mwanted_order )
        if (np.sum(mcolor_dict ==None)!=0) or (np.sum(mcolor_dict.index.isin(mwanted_order))!=len(mwanted_order)):
            mcolor_dict={}
            for item in mwanted_order:
                mcolor_dict[item] = (np.array(random.sample(range(0, 999), 3)) / 1000).tolist()
        else:
            mcolor_dict = mcolor_dict.map(lambda x: list(map(lambda y: y/255., x)))
        #color_dict
        #mcolor_dict = mcolor_dict.map(lambda x: list(map(lambda y: y/255., x)))
        #rcParams['savefig.dpi'] = 500
        #mnewcolors = array(list(mcolor_dict[mprotogruop].values))
        normalizer = 0.9*mdf_train_set.values.max(1)[:,np.newaxis]
        ####
        # must be np.float32
        ####
        refdataLR=net.predict_proba((mdf_train_set.values/ normalizer).astype(np.float32).T)

        todaytime=f"{datetime.datetime.now():%Y%m%d%I%M%p}"

        dataRef= refdataLR[:,mreorder_ix]
        mreordername=[]
        for i in mreorder_ix:
            mreordername.append(list(mclasses_names)[i])
        dfprobCL=pd.DataFrame(dataRef*100, index=mdf_train_set.columns,columns=mreordername)
        #dfnewcl=pd.DataFrame(array([xtest,ytest]).T, index=mdf_train_set.columns)
        datax.obsm["Celltype_Score"]=dfprobCL.values
        datax.uns["Celltype_Score_RefCellType"]=dfprobCL.columns.tolist()
        datax.uns["Celltype_OrderNumber"]=mreorder_ix
        if radarplot ==True:
            axm, dfclRef = RadarVisualization(refdataLR=refdataLR, mreorder_ix=mreorder_ix,
                                              #fontsizeValue=fontsizeValue,
                                              Ncolm=ncolnm, bbValue=bbValue,
                                                        mtrain_index=mtrain_index,
                                                        mclasses_names=mclasses_names,
                                              mcolor_dict=mcolor_dict,
                                              dataclpn=None, learninggroup=learninggroup,
                                                        mdf_train_set=mdf_train_set,
                                                        mwanted_order=mwanted_order,
                                                        mprotogruop=mprotogruop,
                                              fontsizeValue=int(100/int(len(mwanted_order)**0.5))
                                              )
            datax.obsm["CelltypeScoreCoordinates"]=dfclRef.values
        return datax

    elif learninggroup=="test":
        mdf_train_set = pd.DataFrame(datax.obsm["test_set_values"].T, index=datax.uns["train_set_gene"],
                                     columns=datax.obs.index)
        mtrain_index = datax.obs["mtrain_index"].values
        mwanted_order = datax.uns["mwanted_order"]
        mclasses_names = datax.uns["mclasses_names"]
        mprotogruop = datax.obs["Cluster"].values
        dfpfcclus = datax.obs["Cluster"]
        mreorder_ix = [list(mwanted_order).index(i) for i in mwanted_order]
        if (np.sum(mcolor_dict ==None)!=0) or (np.sum(mcolor_dict.index.isin(mwanted_order))!=len(mwanted_order)):
            mcolor_dict={}
            for item in mwanted_order:
                mcolor_dict[item]=random.sample(range(0, 255), 3)
        mcolor_dict = mcolor_dict.map(lambda x: list(map(lambda y: y/255., x)))
        #mnewcolors = array(list(mcolor_dict[mprotogruop].values))
        normalizerTest=0.9*mdf_train_set.values.max(1)[:,np.newaxis]
        normalizedValue=(mdf_train_set.sub(mdf_train_set.min(1),0).div(normalizerTest,0).fillna(0).values).T

        ####
        # must be np.float32
        ####
        dataRef=net.predict_proba((normalizedValue).astype(np.float32))[:,datarefplot.uns["Celltype_OrderNumber"]]
        mreordername=[]
        for i in mreorder_ix:
            mreordername.append(list(mclasses_names)[i])
        #ollist=[datarefplot.uns['Celltype_Score_RefCellType'][i] for i in datarefplot.uns['Celltype_OrderNumber']]
        #dfprobCL=pd.DataFrame(dataRef*100,   index=mdf_train_set.columns,columns= collist)
        dfprobCL = pd.DataFrame(dataRef * 100, index=mdf_train_set.columns,
                                columns=datarefplot.uns['Celltype_Score_RefCellType'])
        #dfnewcl=pd.DataFrame(array([xtest,ytest]).T, index=mdf_train_set.columns)
        datax.obsm["Celltype_Score"]=dfprobCL.values
        datax.uns["Celltype_Score_RefCellType"]=dfprobCL.columns.tolist()
        datax.uns["Celltype_OrderNumber"]=mreorder_ix
        if radarplot ==True:
            axm, dfclRef = RadarVisualization(refdataLR=dataRef,
                                              mreorder_ix=datarefplot.uns["Celltype_OrderNumber"],
                                            mtrain_index=datarefplot.obs["mtrain_index"].values,
                                              learninggroup="test",
                                              Ncolm=ncolnm, bbValue=bbValue,
                                              mdf_train_set=mdf_train_set,
                                              mprotogruop=datax.obs["Cluster"].values,
                                                    dataclpn=dataRef,
                                                    mwanted_order=mwanted_order,
                                              mclasses_names=datarefplot.uns["mclasses_names"],
                                                    mcolor_dict=mcolor_dict,
                                              fontsizeValue=int(100/int(len(mwanted_order)**0.5)))
            datax.obsm["CelltypeScoreCoordinates"]=dfclRef.values
        return datax



        return mreordername, dfprobCL,  mcolor_dict, dataRef





def RadarPlot(data, scaling=False,start_angle=90, rotate_labels=True, labels=('one','two','three'),fontsizeV=20,
                  sides=3, label_offset=0.10, fig_args = {'figsize':(18,18),'facecolor':'white','edgecolor':'white'}):
    '''
    Inputs:

    data: array-like object of shape (N, S), where N is the number of data points and S is the number of sides/vertices of the polygon.
    scaling: boolean, whether to scale the data so that it sums to 1.
    start_angle: int, the angle in degrees of the first vertex.
    rotate_labels: boolean, whether to rotate the labels so they are perpendicular to the vertices.
    labels: array-like object of length S, the labels for the vertices.
    fontsizeV: int, the font size for the labels.
    sides: int, the number of sides/vertices of the polygon.
    label_offset: float, the offset for the label from the vertex (as a percentage of the distance from the origin).
    fig_args: dict, additional arguments for the plt.figure() function.
    Outputs:

    newdata: array of shape (N, 2), the transformed data used to plot the radar chart.
    ax: the axis object for the plot.
    '''
    pi=np.pi
    basis = np.array([[np.cos(2*i*pi/sides + start_angle*pi/180),
                    np.sin(2*i*pi/sides + start_angle*pi/180)] for i in range(sides)])
    RadialBasis=np.array([[np.cos(2*i*pi/sides + (start_angle+180/sides)*pi/180),
                    np.sin(2*i*pi/sides + (start_angle+180/sides)*pi/180)] for i in range(sides)])

    # If data is Nxsides, newdata is Nx2.
    if scaling:
        # Scales data
        newdata = np.dot((data.T / data.sum(-1)).T,basis)
    else:
        # Assumes data already sums to 1.
        newdata = np.dot(data,basis)

    fig = plt.figure(**fig_args)
    ax = fig.add_subplot(111)

    for i,l in enumerate(labels):
        if i >= sides:
            break
        basis2= np.array([[np.cos(2*i*pi/sides + (start_angle+180/sides/2)*pi/180),
                    np.sin(2*i*pi/sides + (start_angle+180/sides/2)*pi/180)] for i in range(sides)])
        x = basis2[i,0]
        y = basis2[i,1]
        if rotate_labels:
            angle = 180*np.arctan(y/x)/pi + 75
            if angle > 90 and angle <= 270:
                angle = np.mod(angle + 180,360)
        else:
            angle = 0
        if l=="Microglia":
            basis3= np.array([[np.cos(2*i*pi/sides + (start_angle+180/sides)*pi/180),
                    np.sin(2*i*pi/sides + (start_angle+180/sides)*pi/180)] for i in range(sides)])
            x = basis3[i,0]
            y = basis3[i,1]
            ax.text(
                x*(1.1 + label_offset),
                y*(1.1 + label_offset),
                l,
                horizontalalignment='center',
                verticalalignment='center',
                rotation=angle-16,
                fontsize=fontsizeV
            )
        elif l=="Cajal-Retzius":
            basis3= np.array([[np.cos(2*i*pi/sides + (start_angle+220/sides)*pi/180),
                    np.sin(2*i*pi/sides + (start_angle+220/sides)*pi/180)] for i in range(sides)])
            x = basis3[i,0]
            y = basis3[i,1]
            ax.text(
                x*(1.15 + label_offset),
                y*(1.15 + label_offset),
                l,
                horizontalalignment='center',
                verticalalignment='center',
                rotation=angle-16,
                fontsize=fontsizeV
            )
        elif len(l)>8:
            basis3= np.array([[np.cos(2*i*pi/sides + (start_angle+180/sides)*pi/180),
                    np.sin(2*i*pi/sides + (start_angle+180/sides)*pi/180)] for i in range(sides)])
            x = basis3[i,0]
            y = basis3[i,1]
            ax.text(
                x*(1.113 + label_offset),
                y*(1.113 + label_offset),
                l,
                horizontalalignment='center',
                verticalalignment='center',
                rotation=angle-16,
                fontsize=fontsizeV
            )
        elif len(l)>=5:
            basis4= np.array([[np.cos(2*i*pi/sides + (start_angle+180/sides/1.5)*pi/180),
                    np.sin(2*i*pi/sides + (start_angle+180/sides/1.5)*pi/180)] for i in range(sides)])
            x = basis4[i,0]
            y = basis4[i,1]
            ax.text(
                x*(1.03 + label_offset),
                y*(1.03 + label_offset),
                l,
                horizontalalignment='center',
                verticalalignment='center',
                rotation=angle-15,
                fontsize=fontsizeV
            )
        else:
            ax.text(
                x*(1.01 + label_offset),
                y*(1.01 + label_offset),
                l,
                horizontalalignment='center',
                verticalalignment='center',
                rotation=angle-15,
                fontsize=fontsizeV
            )
    # Clear normal matplotlib axes graphics

    ax.set_xticks(())
    ax.set_yticks(())
    ax.set_frame_on(False)

    # Plot borders
    ax.plot([basis[_,0] for _ in list(range(sides))+ [0,]], [basis[_,1] for _ in list(range(sides))+ [0,]],c='black',lw=2)
    ax.plot([basis[_,0]*0.75 for _ in list(range(sides))+ [0,]],[basis[_,1]*0.75 for _ in list(range(sides))+ [0,]],c='#B3B6B7',lw=1)
    ax.plot([basis[_,0]*0.5 for _ in list(range(sides))+ [0,]],[basis[_,1]*0.5 for _ in list(range(sides))+ [0,]],c='#B3B6B7',lw=1)
    ax.plot([basis[_,0]*0.25 for _ in list(range(sides))+ [0,]],[basis[_,1]*0.25 for _ in list(range(sides))+ [0,]],c='#B3B6B7',lw=1)
    for _ in list(range(sides)):
        ax.plot([0,RadialBasis[_,0]*0.98],[0,RadialBasis[_,1]*0.98], color='#B3B6B7', linewidth=1, linestyle='dashed')
    return newdata,ax


def RadarVisualization(refdataLR, dataclpn, mreorder_ix, fontsizeValue,bbValue,
                       mtrain_index, mwanted_order,Ncolm,
                       mprotogruop,mdf_train_set,
                       mclasses_names, mcolor_dict, learninggroup="train"):
    """
    Input:

    refdataLR: numpy array
    dataclpn: numpy array
    mreorder_ix: numpy array
    fontsizeValue: int
    bbValue: tuple
    mtrain_index: numpy array
    mwanted_order: numpy array
    Ncolm: int
    mprotogruop: numpy array
    mdf_train_set: pandas dataframe
    mclasses_names: numpy array
    mcolor_dict: dictionary
    learninggroup: string
    Output:

    axm: matplotlib axis object
    dfnewcl: pandas dataframe
    The function takes in input several arguments, including refdataLR and dataclpn which are numpy arrays, mreorder_ix,
    mtrain_index, mwanted_order, mprotogruop, and mclasses_names which are numpy arrays, mdf_train_set which is a pandas dataframe,
    mcolor_dict which is a dictionary, and fontsizeValue and Ncolm which are integers.
    t also takes a string learninggroup which specifies whether the function is being called for the train or test dataset.

    The function returns a matplotlib axis object axm and a pandas dataframe dfnewcl.
    The function plots a radar chart using the RadarPlot function,
    and then adds scatter points to the chart based on the values in mtrain_index and mwanted_order.
    If learninggroup is set to "test", the scatter points are based on dataclpn. The function also adds a legend to the chart using the mwanted_order and mcolor_dict.
    The dfnewcl dataframe is a dataframe of the x and y coordinates of the scatter points.

    """

    #refdataLR = refdataLR, dataclpn = dataclpn, mreorder_ix = mreorder_idx,
    #mtrain_index = mtrain_index, mwanted_order = wanted_orderclpn,
    #mprotogruop = dfpfcclus.loc["Cluster"].values,mdf_train_set=mdf_train_set,
    #mclasses_names = mclasses_names, mcolor_dict = color_dictclpn, learninggroup = "train"
    if learninggroup == "train":
        mnewdata, axm = RadarPlot(refdataLR[:, mreorder_ix], sides=len(mreorder_ix),
                                  fontsizeV=fontsizeValue,labels=mclasses_names[mreorder_ix])
        mbool00 = np.in1d(mclasses_names[mtrain_index], mwanted_order)
        xtest = mnewdata[mbool00, 0] * 0.99
        ytest = mnewdata[mbool00, 1] * 0.99
        alllist=[]
        for item in mprotogruop:
            alllist.append(mcolor_dict[item])
        mnewcolors = np.array(alllist)

        axm.scatter(xtest, ytest, alpha=0.8, c=mnewcolors[mbool00, :], s=200, lw=0.2)
        dfnewcl = pd.DataFrame(np.array([xtest, ytest]).T, index=mdf_train_set.columns)
        recs = []
        for item in mwanted_order:
            recs.append(mpatches.Rectangle((0, 0), 1, 1, fc=mcolor_dict[item]))
        axm.legend(recs, mwanted_order, loc=2, bbox_to_anchor=(1.05, 1.05), prop={'size': fontsizeValue})
        return axm, dfnewcl

    elif learninggroup == "test":
        #mnewdata, axm = RadarPlot(refdataLR[:, mreorder_ix], sides=len(mreorder_ix), labels=mclasses_names[mreorder_ix])
        mnewdata, axm = RadarPlot(refdataLR, sides=len(mreorder_ix), labels=mclasses_names[mreorder_ix])

        # mbool00 = in1d( mclasses_names[mtrain_index],  mwanted_order )
        sides = len(mreorder_ix)
        start_angle = 90
        pi=np.pi
        basisclpn = np.array([[np.cos(2 * i * pi / sides + start_angle * pi / 180),
                            np.sin(2 * i * pi / sides + start_angle * pi / 180)] for i in range(sides)])
        newdataclpn = np.dot(dataclpn, basisclpn)
        xtest = mnewdata[:, 0] * 0.99
        ytest = mnewdata[:, 1] * 0.99
        dfnewcl = pd.DataFrame(np.array([xtest, ytest]).T, index=mdf_train_set.columns)
        # mcolor_dict = mcolor_dict.map(lambda x: list(map(lambda y: y/255., x)))

        mnewcolors = np.array(list(mcolor_dict[mprotogruop].values))

        axm.scatter(xtest, ytest, alpha=0.8, c=mnewcolors, s=200, lw=0.2)

        recs = []
        for item in mwanted_order:
            recs.append(mpatches.Rectangle((0, 0), 1, 1, fc=mcolor_dict[item]))
        axm.legend(recs, mwanted_order, loc=2, bbox_to_anchor=bbValue,ncol=Ncolm, prop={'size': fontsizeValue})
        return axm, dfnewcl



def permutationTest(datax,net,num, plotshow=True):

    """
    Input:
    datax: AnnData object containing the count data, cell type scores, and other relevant information.
    net: Trained scDeepCluster network
    num: Number of iterations to run the permutation test
    plotshow: Boolean value indicating whether to show the violin plot or not
    Output:
    dftest0: Pandas DataFrame containing the results of the permutation test, showing the predicted cell type fractions for each iteration.
    ratiodf: Pandas DataFrame containing the fraction of iterations for which each cell type has a predicted fraction greater than or equal to a given threshold.
    Function: The permutationTest function runs a permutation test to assess the robustness of the cell type predictions made by a scDeepCluster network.
    The function generates random permutations of the count data and uses the trained network to predict the cell type fractions for each permutation.
    The resulting predicted cell type fractions are used to generate a violin plot showing the distribution of predicted fractions for each cell type.
    The function also generates a DataFrame showing the fraction of iterations for which each cell type has a predicted fraction greater than or equal to a given threshold.
    The function returns the dftest0 and ratiodf dataframes.
    """
    dfprobRef = pd.DataFrame(datax.obsm["Celltype_Score"], index=datax.obs.index,
                             columns=datax.uns["Celltype_Score_RefCellType"])
    #dfpfcclus = datax.obs[["mtrain_index", "Cluster"]].T
    #mwanted_order = datax.uns["mwanted_order"]
    mreorder_ix=datax.uns["Celltype_OrderNumber"]
    mdf_train_set = pd.DataFrame(datax.obsm["train_set_values"].T, index=datax.uns["train_set_gene"],
                                 columns=datax.obs.index)

    test = mdf_train_set.values.reshape((len(mdf_train_set.columns) * len(mdf_train_set.index)))
    test = np.random.permutation(test)
    test = test.reshape((len(mdf_train_set.index), len(mdf_train_set.columns)))
    dftest = pd.DataFrame(test).astype(float)
    xp = dftest.values
    xp -= xp.min()
    xp /= xp.ptp()
    ####
    # must be np.float32
    ####
    test0 = net.predict_proba((xp).T.astype(np.float32))[:, mreorder_ix]
    for i in range(0, num):
        test = mdf_train_set.values.reshape((len(mdf_train_set.columns) * len(mdf_train_set.index)))
        test = np.random.permutation(test)
        test = test.reshape((len(mdf_train_set.index), len(mdf_train_set.columns)))
        dftest = pd.DataFrame(test).astype(float)
        xp = dftest.values
        xp -= xp.min()
        xp /= xp.ptp()
        ####
        # must be np.float32
        ####
        dataRef2 = net.predict_proba((xp).T.astype(np.float32))[:, mreorder_ix]

        test0 = np.append(test0, dataRef2, axis=0)
        # test0=test0+dataRef2

    thresholdlist = []
    temp = []
    for threshold in np.arange(0.0, 1.0, 0.01):
        thresholdlist.append("Prob_%s%%" % int(threshold * 100))
        temp.append((np.sum(test0 > threshold, axis=0) / test0.shape[0]))

    ratiodf = pd.DataFrame(temp)
    ratiodf.index = thresholdlist
    ratiodf.columns = dfprobRef.columns
    dftest0 = pd.DataFrame(test0 * 100, columns=dfprobRef.columns)
    if plotshow== True:
        import seaborn as sns
        fig = plt.figure()
        fig, ax = plt.subplots(figsize=(15, 7))
        ax = sns.violinplot(scale="width", bw=0.4, cut=2, gridsize=100, saturation=0.9, scale_hue=False,
                            width=0.95, palette=["grey"], linewidth=0.5, split=True, data=dftest0, alpha=0.75)
        ax = sns.scatterplot(data=dftest0.quantile(0.9), c=["r"], marker="X", s=200)
        plt.axhline(50, c='b', alpha=0.8, linestyle='dashed')
        ax.set_ylim(ymin=-0.01, ymax=100)
        plt.xticks(rotation=90, fontsize=22)
        plt.yticks(
            fontsize=25)
        plt.title("Cell-Type Fractions", fontsize=25)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
    return dftest0, ratiodf




def ProbSinglePlot (datax, mcolor_dict, fs=25):
    """
    Input:

    datax: AnnData object containing the cell type probability scores for each cell
    mcolor_dict: dictionary mapping each cell type to a RGB color code
    fs: font size for the plot
    Output:

    fig: the generated matplotlib figure object
    Functionality:
    This function generates a violin plot for each cell type in datax,
    displaying the distribution of probability scores for each cell in that cell type.
    The violin plots are arranged in a grid, with one plot for each cell type.
    The x-axis displays the cell type names, and the y-axis displays the probability score (from 0 to 100%).
    Additionally, for each cell type, a bar is displayed at the top of the plot to indicate the threshold value for the probability score (set at 80%).
    The function also uses the mcolor_dict input to color each violin plot based on the corresponding cell type color.

    """
    import seaborn as sns
    #dfprobRef = dfprobRef, dfpfcclus = dfpfcclus, mwanted_order = mwanted_order, mcolor_dict = refcolor_dict
    # mdf_train_set = pd.DataFrame(datax.obsm["train_set_values"].T, index=datax.uns["train_set_gene"],
    #                             columns=datax.obs.index)
    #mtrain_index = datax.obs["mtrain_index"].values
    #mwanted_order = datax.uns["mwanted_order"]
    #mclasses_names = datax.uns["mclasses_names"]
    #mprotogruop = datax.obs["Cluster"].values
    #dfpfcclus = datax.obs["Cluster"]

    dfprobRef=pd.DataFrame(datax.obsm["Celltype_Score"], index=datax.obs.index, columns=datax.uns["Celltype_Score_RefCellType"])
    dfpfcclus = datax.obs[["mtrain_index","Cluster"]].T
    mwanted_order=datax.uns["mwanted_order"]
    mcolor_dict = mcolor_dict.map(lambda x: list(map(lambda y: y / 255., x)))
    fig = plt.figure(figsize=(50,20))
    x=np.arange(0.5, len(dfprobRef.columns)+0.5, 1)
    y=[80]*len(dfprobRef.columns)
    #plt.plot(x,100, color=array(color_dictw[dftemp.index[1]]))
    plt.bar(x, y,  width=0.95,alpha=0.65, color="w")
    plt.grid(False)
    plt.axis([0,len(dfprobRef.columns),0,101])
    plt.xticks(x, dfprobRef.columns,rotation=90,horizontalalignment='center', verticalalignment='top',
           position=(0,0),  fontsize=fs)
    plt.yticks(fontsize=fs)

    #plt.spines['top'].set_visible(False)
    #plt.axhline( 70, c='b', alpha=0.8,  linestyle='dashed')
    #dfprobRef.plot.scatter(x=dfprobRef.columns.values,y=range(0, 100))
    plt.ylabel('Probability of Cell-Type Similarity (%)',  position=(0,0.5), color=(0.2,0.2,0.2),
               alpha=0.8, fontsize=50)
    plt.xlabel("Cell Types", fontsize=50)
    sns.set_style("whitegrid")
    #plt.setp(ax.collections, alpha=.5)

    for i in range(len(dfprobRef.columns)):
        cells=dfpfcclus.T.loc[dfpfcclus.loc["Cluster"].isin([dfprobRef.columns[i]])].index
        dfprobReftemp=dfprobRef.loc[cells,dfprobRef.columns[i]]
        anum=fig.add_subplot(1,len(dfprobRef.columns),i+1)
        anum.axis([0,1,0,100])
        sns.violinplot(x=dfprobReftemp.index.name,
                       #y=dfprobReftemp.columns,
                       scale="area",bw=0.4,
                       cut=1.2,
                        gridsize=100,saturation=0.5, width=0.98,
                       color=mcolor_dict[mwanted_order[i]],
                       #palette=mcolor_dict[mwanted_order[i]] ,
                       inner= None, data=dfprobReftemp, ax=anum)
        plt.setp(anum.collections, alpha=.65)
        anum.scatter(list(np.random.random_sample(len(dfprobReftemp.index))-0.5),dfprobReftemp.values,
                    c=[mcolor_dict[mwanted_order[i]]]*len(dfprobReftemp.index), alpha=0.95,
                    s =200, edgecolors="grey", lw=2)
        anum.axis('off')

    plt.grid(False)

    # Turns off grid on the secondary (right) Axis.
    #ax.right_ax(False)

    plt.xticks(rotation=90,horizontalalignment='center', verticalalignment='top',
           position=(0,0), fontsize=fs)
    #plt.spines['top'].set_visible(False)
    #plt.axhline( 70, c='b', alpha=0.8,  linestyle='dashed')
    #dfprobRef.plot.scatter(x=dfprobRef.columns.values,y=range(0, 100))
    plt.ylabel('Probability of Cell-Type Similarity (%)', fontsize='large', position=(0,0.5), color=(0.2,0.2,0.2), alpha=0.8)
    plt.xlabel("Cell Types", fontsize=fs)
    #plt.title("Cell-Type Similarity")
    #plt.savefig("ViolinPlot %s.png"%"SOXtest4", bbox_inches="tight")

    recs = []
    for item in mwanted_order:
        recs.append(mpatches.Rectangle((0,0),1,1,fc=mcolor_dict[item]))
    plt.legend(recs,mwanted_order, loc=2,bbox_to_anchor=(1.1, 1.05), prop={'size': fs})
    #plt.savefig("GBMDGTFgenes_mDG_vs_PEgbm_wheel%sPlot.png"%cvalue,bbox_inches='tight')

        #plt.scatter(list(np.random.random_sample(len(dfprobRef.index))/3-0.16+i),dfprobRef.iloc[:,i].values.tolist(),
         #           c=array(list(mcolor_dict[mprotogruop].values)), alpha=0.9, edgecolors="grey", lw=0.3)
    return fig




def Merge_Objects(DatasetName, filelist, filepath, templateGenelist):
    ann_data_list = {}
    for jname in set(DatasetName):
        print(jname)
        all_dataframes = []
        scorearray = None
        for item in filelist:
            if item.startswith(jname):
                sctemp = anndata.read_h5ad(filepath + item)
                if type(sctemp.obsm['NormalizedMatrix']) == sparse.csr_matrix:
                    norm_matrix = sctemp.obsm['NormalizedMatrix'].toarray()
                else:
                    norm_matrix = sctemp.obsm['NormalizedMatrix']
                df = pd.DataFrame(norm_matrix.T, index=sctemp.uns["train_set_gene"], columns=sctemp.obs.index)
                df["GeneCount"] = 1
                df = df.reindex(templateGenelist).fillna(0)
                all_dataframes.append(df)

                # Accumulate scorearray if needed
                if 'Celltype_Score' in sctemp.obsm:
                    scorearray = np.concatenate((scorearray, sctemp.obsm['Celltype_Score']), axis=1) if scorearray is not None else sctemp.obsm['Celltype_Score']

                # Free memory
                del norm_matrix, df
                gc.collect()

        # Sum the dataframes
        df_combined = pd.concat(all_dataframes).groupby(level=0).sum()

        # Create an AnnData object
        ad = anndata.AnnData(df_combined.iloc[:, :-1].T)
        ad.obs = sctemp.obs  # Assuming obs is same for all files
        ad.obsm = sctemp.obsm  # Assuming obsm is same for all files
        ad.uns = sctemp.uns   # Assuming uns is same for all files
        ad.obs["Dataset"] = [jname] * ad.shape[0]
        if scorearray is not None:
            ad.obsm['PCAraw0'] = scorearray
        del ad.obsm["NormalizedMatrix"]
        del ad.obsm["ConstrualValue_DeepLift"]
        del ad.obsm["ConstrualDelta_DeepLift"]
        ann_data_list[jname] = ad

        # Free memory
        del sctemp, all_dataframes, df_combined, scorearray
        gc.collect()

    # Concatenate all Anndata objects
    adatax = anndata.concat([ann_data_list[jname] for jname in set(DatasetName)])
    #adatax = adatax[:, adatax.X.T.sum(1) > 0]

    return adatax


def patch_violinplot():
    from matplotlib.collections import PolyCollection
    ax = plt.gca()
    for art in ax.get_children():
        if isinstance(art, PolyCollection):
            art.set_edgecolor((0.6, 0.6, 0.6))

def ProbMultiPlot( datax, mcolor_dict,fs=15):

     """
        Input:

        datax: AnnData object
        mcolor_dict: dictionary containing color values for each cell type
        fs: font size for plot labels
        Output:

        fig: matplotlib figure object
        Functionality:
        This function generates a violin plot of the probability of cell type similarity for each cell in the dataset,
         along with a scatter plot of the same data points. The violin plot shows the distribution of the probability of similarity for each cell type, while the scatter plot shows the actual values for each cell.
         The color of each data point in the scatter plot corresponds to the cell type of the cell. The function also adds a legend to the plot showing the color-coding for each cell type.
        The function returns the generated matplotlib figure object.
     """
     #dfprobRef, dfpfcclus, mwanted_order, mcolor_dict
     #dfprobRef=dfprobRef, dfpfcclus=dfpfcclus, mwanted_order=mwanted_order,
                  # mcolor_dict=refcolor_dict
     mcolor_dict=pd.Series(mcolor_dict)
     mcolor_dict = mcolor_dict.map(lambda x: list(map(lambda y: y / 255., x)))
     dfprobRef = pd.DataFrame(datax.obsm["Celltype_Score"], index=datax.obs.index,
                              columns=datax.uns["Celltype_Score_RefCellType"])
     dfpfcclus = datax.obs[["mtrain_index", "Cluster"]].T
     mwanted_order = datax.uns["mwanted_order"]
     mprotogruop = datax.obs["Cluster"].values
     rdmvalue = np.random.choice(len(dfprobRef.index), 300, replace=False).tolist()
     dftemp = dfprobRef.iloc[rdmvalue, :]
     # seleColor=mnewcolors[rdmvalue]
     fig = plt.figure(figsize=(25, 10))
     fig, ax = plt.subplots()
     fig.set_size_inches(16, 8)
     sns.set_style("whitegrid")

     ax = sns.violinplot(y=dfprobRef.index.name, x=dfprobRef.columns.name, scale="width", bw=0.4, cut=2, gridsize=100,
                         saturation=0.9, width=0.98, palette=mcolor_dict[mwanted_order], inner=None, data=dfprobRef)
     plt.setp(ax.collections, alpha=.8)
     for i in range(len(dfprobRef.columns)):
         plt.scatter(list(np.random.random_sample(len(dfprobRef.index)) / 3 - 0.16 + i),
                     dfprobRef.iloc[:, i].values.tolist(), c=np.array(list(mcolor_dict[mprotogruop].values)), alpha=0.9,
                     edgecolors="grey", lw=0.3)

     # ax=sns.swarmplot(y=dftemp.index.name, x=dfprobRef.columns.name,size=5, edgecolor='gray', linewidth=0.1,palette=seleColor , data = dftemp)
     patch_violinplot()
     # plt.set_frame_on(False) #Remove both axes
     # Turns off grid on the left Axis.

     ax.set_ylim(ymin=0, ymax=100.5)
     ax.grid(False)

     # Turns off grid on the secondary (right) Axis.
     # ax.right_ax(False)

     plt.xticks(rotation=90, horizontalalignment='center', verticalalignment='top',
                position=(0, 0), fontsize=fs)
     ax.spines['top'].set_visible(False)
     # plt.axhline( 70, c='b', alpha=0.8,  linestyle='dashed')
     # dfprobRef.plot.scatter(x=dfprobRef.columns.values,y=range(0, 100))
     plt.ylabel('Probability of Cell-Type Similarity (%)', fontsize=fs,
                position=(0, 0.5), color=(0.2, 0.2, 0.2),
                alpha=0.8)
     plt.xlabel("Cell Types", fontsize=fs)
     # plt.title("Cell-Type Similarity")
     # plt.savefig("ViolinPlot %s.png"%"SOXtest4", bbox_inches="tight")

     recs = []
     for item in mwanted_order:
         recs.append(mpatches.Rectangle((0, 0), 1, 1, fc=mcolor_dict[item]))
     ax.legend(recs, mwanted_order, loc=2, bbox_to_anchor=(1.05, 1.05), prop={'size': fs})
     # plt.savefig("GBMDGTFgenes_mDG_vs_PEgbm_wheel%sPlot.png"%cvalue,bbox_inches='tight')
     return fig



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



def ConstrualValue(datax,net,filepath, ConstrualModel="DeepLift", MarkerGeneFinder=True,fcV=3, pValCutOff = 0.1):
    """
    Function name: ConstrualValue
    Input:
    datax: AnnData object containing gene expression data.
    net: PyTorch model trained for the task of interest.
    filepath: Path to save the output files.
    ConstrualModel (optional, default="DeepLift"): String indicating the attribution algorithm to be used.
    MarkerGeneFinder (optional, default=True): Boolean indicating whether to perform marker gene analysis.
    fcV (optional, default=3): Fold change cutoff for differential expression analysis.
    pValCutOff (optional, default=0.1): p-value cutoff for differential expression analysis.
    Output: Modified datax AnnData object containing the construal value scores for each sample in the dataset,
    as well as the top marker genes (if MarkerGeneFinder=True).
    """
    torch.manual_seed(0);
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print("CamelRunning with %s"%device)
    if "test_set_values" in datax.obsm:
        mdf_train_set = pd.DataFrame(datax.obsm["test_set_values"].T, index=datax.uns["train_set_gene"],
                                 columns=datax.obs.index)
    elif "train_set_values" in datax.obsm:
        mdf_train_set = pd.DataFrame(datax.obsm["train_set_values"].T, index=datax.uns["train_set_gene"],
                                     columns=datax.obs.index)
    normalizer = 0.9 * mdf_train_set.values.max(1)[:, np.newaxis]
    train = torch.tensor((mdf_train_set.values / normalizer).T.astype(np.float32))
    Refmodel = net.module_
    DataInput = Variable(train, requires_grad=True).to(device)
    if ConstrualModel=="DeepLift":
        from captum.attr import DeepLift
        algorithm = DeepLift(Refmodel)
        # attr_dl = attribute_image_features(dl, data, baselines=0)
        attrValue = algorithm.attribute(DataInput,target=0)
        datax.obsm["ConstrualValue_DeepLift"] =abs(attrValue .detach().cpu().numpy())
        #abs(attrValue .detach().cpu().numpy()),  attrValue is either neg or posi, set abs()
        #datax.uns["train_set_gene"]
    if MarkerGeneFinder==True:
        df_dev=pd.DataFrame(datax.obsm["ConstrualValue_DeepLift"].T*10000,
                             index=datax.uns["train_set_gene"], columns=datax.obs.index)
        dfpfcclus=datax.obs["Cluster"]
        dftestnew=enrichmentscoreBETA(dfpfcclus=dfpfcclus, df_dev=df_dev, fc=fcV,
                                      pvalcutoff = pValCutOff, shortcut=False)
        dfmarker=dftestnew
        with pd.ExcelWriter(filepath) as writer:
            grouplist = datax.uns['mwanted_order']
            ESmarkerlist = []
            columnlist = []
            for i in range(0, len(grouplist) + 1):
                if i == 0:
                    dfmarker.to_excel(writer, sheet_name='All_Summary', index=True, header=True)
                else:
                    dftemp = dfmarker.loc[dfmarker["Group"] == grouplist[i - 1]].sort_values([grouplist[i - 1]],
                                                                                             ascending=False)
                    dftemp.to_excel(writer, sheet_name=grouplist[i - 1], index=True, header=True)
                    ESmarkerlist.append(dftemp.index[:100].tolist())
                    ESmarkerlist.append((100 * dftemp["Num"] / len(grouplist)).astype(int)[:100].tolist())
                    columnlist.append(grouplist[i - 1])
                    columnlist.append("%s_CrossSigScore%%" % grouplist[i - 1])
            dfmk100 = pd.DataFrame(ESmarkerlist, index=columnlist).T
            dfmk100.to_csv("%s_Top100Marker.csv"%filepath,sep="\t")
            datax.uns["TopMarkerGene"]=dfmk100.values
            datax.uns["TopMarkerGene_Cluster"]=columnlist
        return datax
    else:
        return datax

def ConstrualValue22(datax,net,filepath, ConstrualModel="DeepLift", targetvalue=0,deviceDef="cpu",
                     MarkerGeneFinder=True,fcV=3, pValCutOff = 0.1):
    """
    The ConstrualValue22 function takes a scRNA-seq dataset datax,
    a neural network model net, and several optional parameters to compute the "construal value" of each gene
    in each cell of the dataset. The construal value represents the importance of each gene
    to the identity of the cell.
    The function first preprocesses the input data and normalizes it.
    Then, it uses the DeepLift algorithm from the captum library to compute the construal value of each gene.
    If the MarkerGeneFinder parameter is set to True,
    the function performs a marker gene analysis using the computed construal values.
    This analysis identifies genes that are differentially expressed between different cell clusters.
    The results of the analysis are saved to an Excel file, and the top 100 marker genes for each cluster
    are also saved to a separate CSV file. The function returns the updated datax object
    with the computed construal values and the marker gene analysis results (if applicable).

    """

    torch.manual_seed(0);
    if deviceDef=="cpu":
        device = "cpu"
    elif torch.cuda.is_available():
        device = 'cuda'
    else:
        device = "cpu"
    #device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print("CamelRunning with %s"%device)
    if "test_set_values" in datax.obsm:
        mdf_train_set = pd.DataFrame(datax.obsm["test_set_values"].T, index=datax.uns["train_set_gene"],
                                 columns=datax.obs.index)
    elif "train_set_values" in datax.obsm:
        mdf_train_set = pd.DataFrame(datax.obsm["train_set_values"].T, index=datax.uns["train_set_gene"],
                                     columns=datax.obs.index)
    normalizer = 0.9 * mdf_train_set.values.max(1)[:, np.newaxis]
    train = torch.tensor((mdf_train_set.values / normalizer).T.astype(np.float32))
    Refmodel = net.module_
    DataInput = Variable(train, requires_grad=True).to(device)
    if ConstrualModel=="DeepLift":
        from captum.attr import DeepLift
        algorithm = DeepLift(Refmodel)
        # attr_dl = attribute_image_features(dl, data, baselines=0)
        attrValue, deltav = algorithm.attribute(DataInput,target=targetvalue, return_convergence_delta=True)
        datax.obsm["ConstrualValue_DeepLift"] =abs(attrValue .detach().cpu().numpy())
        datax.obsm["ConstrualDelta_DeepLift"] =abs( deltav .detach().cpu().numpy())
        #abs(attrValue .detach().cpu().numpy()),  attrValue is either neg or posi, set abs()
        #datax.uns["train_set_gene"]
    if MarkerGeneFinder==True:
        df_dev=pd.DataFrame(datax.obsm["ConstrualValue_DeepLift"].T*10000,
                             index=datax.uns["train_set_gene"], columns=datax.obs.index)
        dfpfcclus=datax.obs["Cluster"]
        dftestnew=enrichmentscoreBETA(dfpfcclus=dfpfcclus, df_dev=df_dev, fc=fcV,
                                      pvalcutoff = pValCutOff, shortcut=False)
        dfmarker=dftestnew
        with pd.ExcelWriter(filepath) as writer:
            grouplist = datax.uns['mwanted_order']
            ESmarkerlist = []
            columnlist = []
            for i in range(0, len(grouplist) + 1):
                if i == 0:
                    dfmarker.to_excel(writer, sheet_name='All_Summary', index=True, header=True)
                else:
                    dftemp = dfmarker.loc[dfmarker["Group"] == grouplist[i - 1]].sort_values([grouplist[i - 1]],
                                                                                             ascending=False)
                    dftemp.to_excel(writer, sheet_name=grouplist[i - 1], index=True, header=True)
                    ESmarkerlist.append(dftemp.index[:100].tolist())
                    ESmarkerlist.append((100 * dftemp["Num"] / len(grouplist)).astype(int)[:100].tolist())
                    columnlist.append(grouplist[i - 1])
                    columnlist.append("%s_CrossSigScore%%" % grouplist[i - 1])
            dfmk100 = pd.DataFrame(ESmarkerlist, index=columnlist).T
            dfmk100.to_csv("%s_Top100Marker.csv"%filepath,sep="\t")
            datax.uns["TopMarkerGene"]=dfmk100.values
            datax.uns["TopMarkerGene_Cluster"]=columnlist
        return datax
    else:
        return datax


def ConstrualValueRef(datax,net,deviceset="cuda", ConstrualModelvalue="DeepLift"):
    """
    This function aims to create a reference matrix for construal value prediction using the DeepLift model. The input parameters are:
    datax: AnnData object, the dataset on which the reference matrix is to be constructed
    net: Keras model, the neural network model used for prediction
    ConstrualModelvalue: string, the type of method used for generating construal values, in this case "DeepLift"
    """
    clist=[]
    for i in datax.uns['Celltype_OrderNumber']:
        datax=ConstrualValue22(datax=datax,net=net, filepath=None,targetvalue=i,
                               ConstrualModel="DeepLift",MarkerGeneFinder=False,deviceDef=deviceset,
                               fcV=1.5, pValCutOff = 0.1)
        clist.append(datax.obsm['ConstrualValue_DeepLift'].T.sum(1).tolist())
    datax.uns['ConstrualValue_DeepLift_ClusterRef']=np.array(clist)
    #dftestx=pd.DataFrame(clist)
    #dftestx.columns=datax.uns[ 'train_set_gene']
    #dftestx.index=datax.uns[ 'mclasses_names']
    #dfprob=pd.DataFrame(datax.obsm['Celltype_Score'])
    #dfprob.index=datax.obs.index
    #dfprob.columns=datax.uns[ 'mclasses_names']
    dfsum=pd.DataFrame(np.dot(datax.obsm['Celltype_Score'],datax.uns['ConstrualValue_DeepLift_ClusterRef']))
    dfsum.columns=datax.uns[ 'train_set_gene']
    dfsum.index=datax.obs.index
    dfref=(dfsum/dfsum.max()).fillna(0)
    dfrefv=pd.DataFrame(datax.obsm[ 'train_set_values'])
    dfrefv.columns=datax.uns[ 'train_set_gene']
    dfrefv.index=datax.obs.index
    dfrefv=dfrefv/dfrefv.max()
    dfall=(dfrefv*dfref)**0.5
    datax.obsm["NormalizedMatrix"]=dfall.values
    return datax

def ConstrualValueRefmean(datax,net, deviceset="cuda",ConstrualModelvalue="DeepLift"):
    """
    This function aims to create a reference matrix for construal value prediction using the DeepLift model. The input parameters are:
    datax: AnnData object, the dataset on which the reference matrix is to be constructed
    net: Keras model, the neural network model used for prediction
    ConstrualModelvalue: string, the type of method used for generating construal values, in this case "DeepLift"
    """
    clist=[]
    for i in datax.uns['Celltype_OrderNumber']:
        datax=ConstrualValue22(datax=datax,net=net, filepath=None,targetvalue=i,
                               ConstrualModel="DeepLift",MarkerGeneFinder=False,deviceDef=deviceset,
                               fcV=1.5, pValCutOff = 0.1)
        clist.append(datax.obsm['ConstrualValue_DeepLift'].T.sum(1).tolist())
    datax.uns['ConstrualValue_DeepLift_ClusterRef']=np.array(clist)
    #dftestx=pd.DataFrame(clist)
    #dftestx.columns=datax.uns[ 'train_set_gene']
    #dftestx.index=datax.uns[ 'mclasses_names']
    #dfprob=pd.DataFrame(datax.obsm['Celltype_Score'])
    #dfprob.index=datax.obs.index
    #dfprob.columns=datax.uns[ 'mclasses_names']
    dfsum=pd.DataFrame(np.dot(datax.obsm['Celltype_Score'],datax.uns['ConstrualValue_DeepLift_ClusterRef']))
    dfsum.columns=datax.uns[ 'train_set_gene']
    dfsum.index=datax.obs.index
    dfref=(dfsum/dfsum.max()).fillna(0)
    dfrefv=pd.DataFrame(datax.obsm[ 'train_set_values']).fillna(0)
    dfrefv.columns=datax.uns[ 'train_set_gene']
    dfrefv.index=datax.obs.index
    dfrefv=dfrefv/dfrefv.max()
    dfrefv =dfrefv.fillna(0)
    dfall = (dfrefv + dfref) * 0.5
    datax.obsm["NormalizedMatrix"]=dfall.values
    return datax


def ConstrualValuePrediction(datapdt, dataref):
    # dataref.uns['ConstrualValue_DeepLift_ClusterRef']=np.array(clist)
    # dftestx=pd.DataFrame(clist)
    # dftestx.columns=datax.uns[ 'train_set_gene']
    # dftestx.index=datax.uns[ 'mclasses_names']
    # dfprob=pd.DataFrame(datax.obsm['Celltype_Score'])
    # dfprob.index=datax.obs.index
    # dfprob.columns=datax.uns[ 'mclasses_names']
    dfsum = pd.DataFrame(np.dot(datapdt.obsm['Celltype_Score'], dataref.uns['ConstrualValue_DeepLift_ClusterRef']))
    dfsum.columns = dataref.uns['train_set_gene']
    dfsum.index = datapdt.obs.index
    dfref = (dfsum / dfsum.max()).fillna(0)
    dfrefv = pd.DataFrame(datapdt.obsm['test_set_values']).fillna(0)
    dfrefv.columns = dataref.uns['train_set_gene']
    dfrefv.index = datapdt.obs.index
    dfrefv = dfrefv / dfrefv.max()
    dfrefv = dfrefv.fillna(0)
    dfall = (dfrefv * dfref) ** 0.5
    datapdt.obsm["NormalizedMatrix"] = dfall.values
    return datapdt

def ConstrualValuePredictionmean(datapdt, dataref):
    # dataref.uns['ConstrualValue_DeepLift_ClusterRef']=np.array(clist)
    # dftestx=pd.DataFrame(clist)
    # dftestx.columns=datax.uns[ 'train_set_gene']
    # dftestx.index=datax.uns[ 'mclasses_names']
    # dfprob=pd.DataFrame(datax.obsm['Celltype_Score'])
    # dfprob.index=datax.obs.index
    # dfprob.columns=datax.uns[ 'mclasses_names']
    dfsum = pd.DataFrame(np.dot(datapdt.obsm['Celltype_Score'], dataref.uns['ConstrualValue_DeepLift_ClusterRef']))
    dfsum.columns = dataref.uns['train_set_gene']
    dfsum.index = datapdt.obs.index
    dfref = (dfsum / dfsum.max()).fillna(0)
    dfrefv = pd.DataFrame(datapdt.obsm['test_set_values'])
    dfrefv.columns = dataref.uns['train_set_gene']
    dfrefv.index = datapdt.obs.index
    dfrefv = dfrefv / dfrefv.max()
    dfall = (dfrefv.fillna(0) + dfref.fillna(0)) * 0.5
    datapdt.obsm["NormalizedMatrix"] = dfall.values
    return datapdt
    
def MarkerDotPlot(datax,filepath, clustername):
    """
    Input Parameters:
    datax: AnnData object containing the gene expression data
    filepath: file path to the file containing the marker gene information
    clustername: the name of the column in the marker gene file that contains the cluster labels
    Output:
    A scatter plot visualizing the marker gene expression across the specified clusters
    """
    from mpl_toolkits.axes_grid1.inset_locator import inset_axes
    df=pd.DataFrame(datax.X.T,index=datax.var.index,columns=datax.obs.index)
    dfmk=pd.read_table(filepath,index_col=0,sep="\t")
    dfgrpref=df.loc[dfmk[clustername].dropna().values].T
    dfgrpref["Cluster"]=datax.obs["Cluster"]
    dfgrpref=dfgrpref[dfgrpref.columns[::-1]]
    dfmean=dfgrpref.groupby(["Cluster"]).mean()
    dfmean=dfmean/dfmean.sum()
    grpNzCount = dfgrpref.groupby(['Cluster']).agg(lambda x: x.ne(0).sum())/dfgrpref.groupby(["Cluster"]).count()
    xvalue=[]
    for i in range(len(dfmean.index)):
        xvalue.extend([dfmean.index[i]]*len(dfmean.columns))
    yvalue=[]
    yvalue.extend((dfmean.columns.tolist())*len(dfmean.index))
    sns.set_style(style='white')
    plt.figure(figsize=(7,30), facecolor='w')
    plt.rcParams['xtick.bottom'] = plt.rcParams['xtick.labelbottom'] = False
    plt.rcParams['xtick.top'] = plt.rcParams['xtick.labeltop'] = True

    plt.xticks(fontsize=15, rotation=90)
    plt.yticks(fontsize=15, rotation=0)
    ax=plt.scatter( xvalue,yvalue,s = (grpNzCount *250).values.flatten(),
                c=dfmean.values.flatten(),cmap="plasma",
                alpha=.95,
                lw=0.2)
    plt.title(clustername, fontsize=20)

    plt.colorbar(ax, anchor=(0.5,1),fraction=0.05)
    plt.grid("on",alpha=0.5)
    return ax


def CellTypeSimilarity(datax, labelnum=False, RowCluster=True, fontsizeWeight=0.65,
                        ColCluster=True, metricvalue='correlation', methodvalue="average"):

    """
    Inputs:

    datax: AnnData object containing the cell type scores in the obsm attribute and the cell cluster annotations in the obs attribute
    labelnum: a boolean value indicating whether to show the average cell type scores in the heatmap or not (default=False)
    RowCluster: a boolean value indicating whether to cluster rows (default=True)
    fontsizeWeight: the font scale weight for the heatmap labels (default=0.65)
    ColCluster: a boolean value indicating whether to cluster columns (default=True)
    metricvalue: the distance metric to use when clustering (default='correlation')
    methodvalue: the linkage method to use when clustering (default="average")
    Outputs:

    A heatmap visualizing the similarity of cell type scores across different cell clusters in the input AnnData object.
    """
    dfprob = pd.DataFrame(datax.obsm['Celltype_Score'], index=datax.obs.index,
                          columns=datax.uns['Celltype_Score_RefCellType'])
    dfprob["Cluster"] = datax.obs["Cluster"]
    dfpb2 = dfprob.groupby(["Cluster"]).mean()
    dfpb2 = (dfpb2 + dfpb2.T) / 2
    correlations_array = np.asarray(np.log2(dfpb2.values + 1))
    if labelnum == False:
        sns.set(font_scale=1)
        row_linkage1 = hierarchy.linkage(
            distance.pdist(correlations_array),
            method=methodvalue,
            metric=metricvalue
        )

        col_linkage1 = hierarchy.linkage(
            distance.pdist(correlations_array.T),
            method=methodvalue,
            metric=metricvalue
        )
        plt.figure(figsize=(int(dfpb2.shape[1]), int(dfpb2.shape[0])))
        sns.set_style("white")
        sns.set(font_scale=fontsizeWeight)

        cg = sns.clustermap(np.log10(dfpb2 + 1) ** 0.75,
                            row_linkage=row_linkage1,
                            col_linkage=col_linkage1,
                            method=methodvalue,
                            metric=metricvalue,
                            # z_score=0,
                            row_cluster=RowCluster, col_cluster=ColCluster,
                            figsize=(int(dfpb2.shape[1]), int(dfpb2.shape[0])),
                            cmap="cividis")
        plt.setp(cg.ax_heatmap.yaxis.get_majorticklabels(), rotation=0, fontsize=15)
        plt.setp(cg.ax_heatmap.xaxis.get_majorticklabels(), rotation=90, fontsize=15)
    elif labelnum == True:
        sns.set(font_scale=1)
        labels = dfpb2.values
        labels = labels.round(decimals=1)
        row_linkage1 = hierarchy.linkage(
            distance.pdist(correlations_array),
            method=methodvalue,
            metric=metricvalue
        )
        plt.figure(figsize=(int(dfpb2.shape[1]), int(dfpb2.shape[0])))
        sns.set_style("white")
        sns.set(font_scale=fontsizeWeight)
        col_linkage1 = hierarchy.linkage(
            distance.pdist(correlations_array.T),
            method=methodvalue,
            metric=metricvalue
        )
        cg = sns.clustermap(np.log10(dfpb2 + 1) ** 0.75,
                            row_linkage=row_linkage1,
                            col_linkage=col_linkage1,
                            annot=labels,
                            method=methodvalue,
                            metric=metricvalue,
                            # z_score=0,
                            row_cluster=RowCluster, col_cluster=ColCluster,
                            figsize=(int(dfpb2.shape[1]), int(dfpb2.shape[0])), cmap="cividis")
        plt.setp(cg.ax_heatmap.yaxis.get_majorticklabels(), rotation=0, fontsize=15)
        plt.setp(cg.ax_heatmap.xaxis.get_majorticklabels(), rotation=90, fontsize=15)

def SelfSimilarity(datax, labelnum=False, RowCluster=True,
                   ColCluster=True, metricvalue='correlation',methodvalue="average"):
    """
    datax: a Pandas dataframe containing cell type scores for each sample
    labelnum: a boolean value indicating whether to annotate the heatmap with the values of the cell type scores
    RowCluster: a boolean value indicating whether to cluster the rows of the heatmap
    ColCluster: a boolean value indicating whether to cluster the columns of the heatmap
    metricvalue: a string specifying the distance metric to be used for clustering
    methodvalue: a string specifying the clustering method to be used
    The function starts by creating a new dataframe dfprob by extracting cell type scores from the input dataframe datax and grouping them by cluster. It then calculates the average cell type score for each cluster and creates a symmetric dataframe dfpb2 by averaging the values of the cluster-cell type score matrix and its transpose.

    If labelnum is set to False, the function generates a heatmap using Seaborn's clustermap function, with the log2-transformed dfpb2 dataframe as the input. The method and metric parameters specify the clustering method and distance metric to be used, respectively. The z_score parameter normalizes the data by subtracting the mean and dividing by the standard deviation. The heatmap is then displayed with the x and y axis tick labels set to a rotation of 90 and 0 degrees, respectively.

    If labelnum is set to True, the function creates a similar heatmap with the addition of cell type score annotations. The annot parameter is set to labels, which is a rounded version of the dfpb2 dataframe values.

    """

    dfprob = pd.DataFrame(datax.obsm['Celltype_Score'], index=datax.obs.index,
                          columns=datax.uns['Celltype_Score_RefCellType'])
    dfprob["Cluster"] = datax.obs["Cluster"]
    dfpb2 = dfprob.groupby(["Cluster"]).mean()
    dfpb2 = (dfpb2 + dfpb2.T) / 2
    if labelnum==False:
        sns.set(font_scale=1)

        cg = sns.clustermap(np.log2(dfpb2 + 1), cmap="CMRmap",
                            method=methodvalue,
                            metric=metricvalue,
                            row_cluster=RowCluster, col_cluster=ColCluster,
                            z_score=1, figsize=(10, 10))
        plt.setp(cg.ax_heatmap.yaxis.get_majorticklabels(), rotation=0, fontsize=15)
        plt.setp(cg.ax_heatmap.xaxis.get_majorticklabels(), rotation=90, fontsize=15)
    elif labelnum==True:
        sns.set(font_scale=1)
        labels = dfpb2.values
        labels = labels.round(decimals=1)
        cg = sns.clustermap(np.log2(dfpb2 + 1), cmap="CMRmap",
                            method=methodvalue,
                            metric=metricvalue,
                            annot=labels,
                            row_cluster=RowCluster, col_cluster=ColCluster,
                            z_score=1, figsize=(10, 10))
        plt.setp(cg.ax_heatmap.yaxis.get_majorticklabels(), rotation=0, fontsize=15)
        plt.setp(cg.ax_heatmap.xaxis.get_majorticklabels(), rotation=90, fontsize=15)


def ConvertSparse(adata):
    if type(adata.X)==sparse.csr.csr_matrix:
        adata.X=adata.X.toarray()
    if adata.obsm['ConstrualValue_DeepLift'].size != 0:
        if type(adata.obsm['ConstrualValue_DeepLift']) == sparse.csr.csr_matrix:
            adata.obsm['ConstrualValue_DeepLift']= adata.obsm['ConstrualValue_DeepLift'].toarray()
    if adata.obsm['NormalizedMatrix'].size != 0:
        if type(adata.obsm['NormalizedMatrix']) == sparse.csr.csr_matrix:
            adata.obsm['NormalizedMatrix']= adata.obsm['NormalizedMatrix'].toarray()
    return adata



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

import sys
import numpy as np
import pandas as pd
import scipy.stats
from collections import defaultdict

# ---------------------------------------------------------------------
def enrichmentscoreBETA(
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



def FeatureEnrichScore(df_dev, FeatureGenes, controlnumber=50, cuts=25):
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


def MergeObject(DatasetName, filelist, filepath, templateGenelist):
    ann_data_list = {}
    for jname in set(DatasetName):
        print(jname)
        all_dataframes = []
        scorearray = None
        for item in filelist:
            if item.startswith(jname):
                sctemp = anndata.read(filepath + item)
                if type(sctemp.obsm['NormalizedMatrix']) == sparse.csr.csr_matrix:
                    norm_matrix = sctemp.obsm['NormalizedMatrix'].toarray()
                else:
                    norm_matrix = sctemp.obsm['NormalizedMatrix']
                df = pd.DataFrame(norm_matrix.T, index=sctemp.uns["train_set_gene"], columns=sctemp.obs.index)
                df["GeneCount"] = 1
                df = df.reindex(templateGenelist).fillna(0)
                all_dataframes.append(df)

                # Accumulate scorearray if needed
                if 'Celltype_Score' in sctemp.obsm:
                    scorearray = np.concatenate((scorearray, sctemp.obsm['Celltype_Score']),
                                                axis=1) if scorearray is not None else sctemp.obsm['Celltype_Score']

                # Free memory
                del norm_matrix, df
                gc.collect()

        # Sum the dataframes
        df_combined = pd.concat(all_dataframes).groupby(level=0).sum()

        # Create an AnnData object
        ad = anndata.AnnData(df_combined.iloc[:, :-1].T)
        ad.obs = sctemp.obs  # Assuming obs is same for all files
        ad.obsm = sctemp.obsm  # Assuming obsm is same for all files
        ad.uns = sctemp.uns  # Assuming uns is same for all files
        ad.obs["Dataset"] = [jname] * ad.shape[0]
        if scorearray is not None:
            ad.obsm['PCAraw0'] = scorearray
        del ad.obsm["NormalizedMatrix"]
        ann_data_list[jname] = ad

        # Free memory
        del sctemp, all_dataframes, df_combined, scorearray
        gc.collect()

    # Concatenate all Anndata objects
    adatax = anndata.concat([ann_data_list[jname] for jname in set(DatasetName)])
    # adatax = adatax[:, adatax.X.T.sum(1) > 0]

    return adatax

from skorch import NeuralNetClassifier
import torch
import json, pathlib, numpy as np, pandas as pd

def save_camel_model(adatax, net, out_dir="camel_checkpoints", prefix="camel_nn"):
    """Save skorch model + meta for later reload."""
    out_path = pathlib.Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # ---------- 1) build meta ---------------------------------------------
    mdf_train_set = pd.DataFrame(
        adatax.obsm["train_set_values"].T,
        index=adatax.uns["train_set_gene"],
        columns=adatax.obs.index,
    )

    meta = dict(
        input_dim   = int(mdf_train_set.shape[0]),
        hidden_dim  = int(mdf_train_set.shape[0] / 5),
        output_dim  = int(np.unique(adatax.obs["mtrain_index"]).size),

        # convert arrays to plain Python lists so JSON can handle them
        gene_order  = adatax.uns["train_set_gene"].tolist(),
        cell_labels = (
            adatax.uns["mclasses_names"].tolist()
            if "mclasses_names" in adatax.uns
            else None
        ),
    )

    meta_file = out_path / f"{prefix}_meta.json"
    with meta_file.open("w") as fh:
        json.dump(meta, fh, indent=2)

    # ---------- 2) network weights + history ------------------------------
    weight_file  = out_path / f"{prefix}_weights.pt"
    history_file = out_path / f"{prefix}_history.json"
    net.save_params(f_params=weight_file, f_history=history_file)

    return dict(meta=str(meta_file),
                weights=str(weight_file),
                history=str(history_file))


import torch.nn as nn
import torch.nn.functional as F

class Classifier3LayersToLoad(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim, dropout=0.3):
        super().__init__()
        self.hidden  = nn.Linear(input_dim,  hidden_dim)
        self.dropout = nn.Dropout(dropout)
        self.output  = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        x = F.relu(self.hidden(x))
        x = self.dropout(x)
        return F.softmax(self.output(x), dim=-1)

def load_camel_model(checkpoint_dir="./", prefix="camel_nn_GBMtest",dropoutVal=0.5, device="cpu"):
    path = pathlib.Path(checkpoint_dir)
    meta  = json.load((path / f"{prefix}_meta.json").open())
    #norm  = np.load(path / f"{prefix}_normaliser.npy")

    net = NeuralNetClassifier(
        Classifier3LayersToLoad(meta["input_dim"],
                          meta["hidden_dim"],
                          meta["output_dim"],
                          dropout=dropoutVal).float(),
        device=device
    )
    net.initialize()
    net.load_params(
        f_params  = path / f"{prefix}_weights.pt",
        f_history = path / f"{prefix}_history.json",
    )
    return net



import scanpy as sc
import umap
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt


def PCAesti2(adatax, ReadyModel=None):
    """
    Perform Principal Component Analysis (PCA) on the input AnnData object.

    Parameters:
    - adatax (AnnData): The AnnData object containing raw expression data.
    - ReadyModel (sklearn.decomposition.PCA, optional): Pre-trained PCA model. If provided, the model is used to transform the data instead of fitting a new model.

    Returns:
    - adatax (AnnData): Updated AnnData object with PCA embeddings.
    - PCAmodel (sklearn.decomposition.PCA, optional): The PCA model used for transformation. Returned only if ReadyModel is None.
    """
    # Extract the raw PCA data
    X = adatax.obsm["PCAraw0"].astype(np.float32)

    if ReadyModel is None:
        # Initialize and fit a new PCA model
        pca_ = PCA(n_components=X.shape[1] - 1, svd_solver='arpack', random_state=0)
        PCAmodel = pca_.fit(X)

        # Transform the data
        X_pcavalue = PCAmodel.transform(X)

        # Assign PCA coordinates to obsm
        adatax.obsm['X_pca'] = X_pcavalue
        adatax.obsm['Celltype_ScoreAll'] = X_pcavalue  # Assuming this is intended for downstream analysis

        # Plot explained variance ratio
        plt.figure(figsize=(5, 5))
        plt.scatter(range(1, X_pcavalue.shape[1] + 1), PCAmodel.explained_variance_ratio_)
        plt.xlabel("PC Number", fontsize=15)
        plt.ylabel("Explained Variance Ratio", fontsize=15)
        plt.title("PCA Explained Variance Ratio")
        plt.show()

        # Populate uns['pca'] with necessary parameters
        adatax.uns['pca'] = {
            'variance_ratio': PCAmodel.explained_variance_ratio_.tolist(),  # Convert to list for JSON compatibility
            'params': {
                'n_comps': X_pcavalue.shape[1],
                'zero_center': pca_.mean_ is not None,  # PCA centers data by default
                'use_highly_variable': True,  # Assuming you used highly variable genes
                'svd_solver': 'arpack',
                'random_state': 0
            }
        }

        return adatax, PCAmodel
    else:
        # Use the provided PCA model to transform the data
        X_pcavalue = ReadyModel.transform(X)

        # Assign PCA coordinates to obsm
        adatax.obsm['X_pca'] = X_pcavalue
        adatax.obsm['Celltype_ScoreAll'] = X_pcavalue  # Assuming this is intended for downstream analysis

        # Populate uns['pca'] with necessary parameters
        adatax.uns['pca'] = {
            'variance_ratio': ReadyModel.explained_variance_ratio_.tolist(),
            'params': {
                'n_comps': X_pcavalue.shape[1],
                'zero_center': ReadyModel.mean_ is not None,
                'use_highly_variable': True,  # Adjust based on your preprocessing
                'svd_solver': ReadyModel.svd_solver,
                'random_state': ReadyModel.random_state
            }
        }

        return adatax


def PCAesti(adatax,ReadyModel=None):
    """
    Input:
    adatax: AnnData object containing raw expression data and PCA coordinates.
    ReadyModel: PCA model object (optional)
    Output:
    adatax: AnnData object with updated PCA coordinates and explained variance ratio.
    PCAmodel: PCA model object (optional)
    Function description:
    This function performs principal component analysis (PCA) on the input AnnData object containing raw expression data and PCA coordinates.
    If a pre-existing PCA model is provided, the function applies the model to the input data instead of creating a new model.
     The function returns the updated AnnData object with the new PCA coordinates and explained variance ratio.
    Additionally, if a new PCA model is created, the function also returns the PCA model object.
    """
    X =adatax.obsm["PCAraw0"]
    if ReadyModel==None:
        pca_ = PCA(n_components=adatax.obsm["PCAraw0"].shape[1]-1, svd_solver='arpack', random_state=0)
        PCAmodel= pca_.fit(X)
        #X_cca,Y_cca=cca_.fit_transform(X,Y)
        X_pcavalue=PCAmodel.transform(X)
        adatax.obsm['Celltype_ScoreAll']=X_pcavalue
        plt.figure(figsize=(5,5))
        plt.scatter(list(range(0,adatax.obsm["PCAraw0"].shape[1]-1)),PCAmodel.explained_variance_ratio_)
        plt.xlabel("Comp_Num",fontsize=15)
        plt.ylabel('PCAratio',fontsize=15)
        adatax.obsm['Celltype_ScoreAll']=X_pcavalue
        adatax.obsm['X_pca']=X_pcavalue
        adatax.uns['pca']=PCAmodel.explained_variance_ratio_
        return adatax, PCAmodel
    else:
        X_pcavalue=ReadyModel.transform(X)
        adatax.obsm['Celltype_ScoreAll']=X_pcavalue
        adatax.obsm['X_pca']=X_pcavalue
        adatax.uns['pca']=ReadyModel.explained_variance_ratio_
        return adatax


def project_and_transfer(
        adata,
        adata_ref,
        PCAmodel,
        UMAPmodel,
        *,
        pcVal: int = 6,
        n_neighbors: int = 30,
        clustername: str = "Cluster",
        colorcode:   str = "color",
):
    """
    1.  Keeps a copy of the *raw* Cell-type score in `adata.obsm['PCAraw0']`.
    2.  Projects **adata** onto a pre–trained PCA model (`PCAesti2`),
        then stores the first *pcVal* components back in
        `adata.obsm['Celltype_Score']`.
    3.  Ensures the reference object (`adata_ref`) carries the same
        number of PCs in `adata_ref.obsm['Celltype_Score']`.
    4.  Runs scCamel’s transfer-learning step to map **adata** onto the
        reference UMAP space.

    Parameters
    ----------
    adata       : AnnData
        Query / target dataset you want to project and transfer.
    adata_ref   : AnnData
        Reference dataset with an existing UMAP + cluster labels.
    PCAmodel    : fitted PCA object (as produced by scCamel’s `PCAesti2`).
    UMAPmodel   : fitted UMAP object.
    pcVal       : int, default 6
        How many principal components to keep.
    n_neighbors : int, default 30
        `n_neighbors` forwarded to `transfer_learning`.
    clustername : str, default "Cluster"
        Column in `adata_ref.obs` that contains cluster labels.
    colorcode   : str, default "color"
        Column in `adata_ref.obs` that stores a hex/RGB colour per cluster.

    Returns
    -------
    adata : AnnData (the *same* object, updated in-place)
        After function ends, `adata` is embedded in the reference UMAP.
    """
    # ------------------------------------------------------------------ #
    # 1) keep a backup of the original Cell-type scores                  #
    # ------------------------------------------------------------------ #
    if "Celltype_Score" not in adata.obsm:
        raise KeyError("`adata.obsm['Celltype_Score']` is missing.")
    adata.obsm["PCAraw0"] = adata.obsm["Celltype_Score"].copy()

    # ------------------------------------------------------------------ #
    # 2) project the query dataset onto the pre-trained PCA              #
    # ------------------------------------------------------------------ #
    adata = PCAesti2(adatax=adata, ReadyModel=PCAmodel)          # ↩︎ in-place

    # keep only the leading `pcVal` components
    adata.obsm["Celltype_Score"] = adata.obsm["X_pca"][:, :pcVal]
    adata_ref.obsm["Celltype_Score"] = adata_ref.obsm["X_pca"][:, :pcVal]

    # ------------------------------------------------------------------ #
    # 3) map the query cells into the reference UMAP space               #
    # ------------------------------------------------------------------ #
    adata = transfer_learning(
        UMAPmodel=UMAPmodel,
        datapdt=adata,                    # query dataset
        datax=adata_ref,                  # reference
        clustername=clustername,
        colorcode=colorcode,
        n_neighbors=n_neighbors,
    )

    return adata
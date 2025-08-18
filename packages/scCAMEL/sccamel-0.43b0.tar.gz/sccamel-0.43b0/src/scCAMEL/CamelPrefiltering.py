import pandas as pd
import numpy as np
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
import datetime
import seaborn as sns
import pandas as pd
import pickle as pickle
from scipy.spatial.distance import cdist, pdist, squareform
#import backspinpy
import anndata as ad
import scipy
import pandas as pd
from sklearn.utils import resample
import pandas as pd
import scanpy as sc
import anndata as ad
import pandas as pd
from sklearn.utils import resample
from sklearn.linear_model import LogisticRegression, LogisticRegressionCV
from sklearn.model_selection import StratifiedShuffleSplit
from collections import defaultdict
from sklearn import preprocessing
import matplotlib.patches as mpatches
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches
from matplotlib.legend_handler import HandlerPatch
import os
import sys
#from skorch.callbacks import Callback
import torch
from torch import nn
import torch.nn.functional as F
from skorch import NeuralNetClassifier

def prefilter(datax, biasgene=True, filename=None, path=None):
    """
    Inputs:
    datax: AnnData object containing the input data
    biasgene (optional): Boolean value to specify whether to remove bias genes or not. Default is True.
    filename (optional): Name of the file containing list of bias genes. Default is None.
    path (optional): Path to the file containing list of bias genes. Default is None.
    Outputs:
    datax: AnnData object containing the pre-filtered data
    """
    # df_f = dfpfc, filename = filename, path = path
    print("CamelRunning_Prefilter......")
    df_f = pd.DataFrame(datax.X.T, index=datax.var.index, columns=datax.obs.index)
    if biasgene==True:
        dropgene = open('%s%s' % (path, filename)).read().split('\n')
        other_genes = ['HBG1', 'HBA1', 'HBA2', 'HBE1', 'HBZ', 'BLVRB', 'S100A6', 'SNAR-E', 'SNAR-A13_loc1',
                   'SNAR-C1_loc1', 'SNAR-A1_loc2', 'SNAR-A8_loc1', 'SNAR-C1_loc2', 'SNAR-A2_loc2', 'SNAR-C4',
                   'SNAR-A12_loc1', 'SNAR-C3', 'SNAR-C1_loc3', 'SNAR-G2', 'SNAR-G1', 'SNAR-A11_loc9',
                   'SNAR-A6_loc3', 'SNAR-A14_loc7', 'SNAR-A6_loc5',
                   'SNAR-A10_loc6', 'SNAR-A5_loc9', 'SNAR-A14_loc3', 'SNAR-A9_loc9', 'SNAR-A11_loc7',
                   'SNAR-B1_loc1', 'SNAR-B1_loc2', 'SNAR-D', 'SNAR-F']
        dropgene.extend(other_genes)
        dropgene = list(set(dropgene))

        df_f = df_f.loc[~np.in1d(df_f.index, dropgene)].astype(float)
    df_f = df_f.loc[np.sum(df_f >= 1, 1) >= 5, :]  # is at least 1 in 5 cells
    df_f = df_f.loc[np.sum(df_f >= 2, 1) >= 2, :]  # is at least 2 in 2 cells
    df_f = df_f.loc[np.sum(df_f >= 3, 1) >= 1, :]  # is at least 3 in 1 cells
    ftlist=np.in1d(datax.var.index, df_f.index.tolist())
    datax.var["Filter1"]=ftlist
    print("CamelRunning_Prefilter......Finished")
    return datax


def MVgenes(datax, wt=3, markerlist=[],plotfig=False, Xlow=-8.5, Xhigh=6.5, Ylow=-2, Yhigh=6.5,alphaValue=0.2, sValue=10,
           fig_args={'figsize': (8, 8), 'facecolor': 'white', 'edgecolor': 'white'}):
    """
    Inputs:
    datax: AnnData object, input data matrix
    wt: int, default 3, weight parameter for the threshold count
    markerlist: list of str, default empty, list of additional genes to include in the MVgene list
    plotfig: bool, default False, whether or not to plot the figure
    Xlow: float, default -8.5, minimum limit of x-axis in the figure
    Xhigh: float, default 6.5, maximum limit of x-axis in the figure
    Ylow: float, default -2, minimum limit of y-axis in the figure
    Yhigh: float, default 6.5, maximum limit of y-axis in the figure
    alphaValue: float, default 0.2, alpha value for the scatter plot in the figure
    sValue: float, default 10, size of the markers in the scatter plot in the figure
    fig_args: dictionary, default {'figsize': (8, 8), 'facecolor': 'white', 'edgecolor': 'white'}, dictionary containing the figure arguments
    Outputs:

    datax: AnnData object, input data matrix with additional column "MVgene" added to var
    score: numpy array, CV score for each gene
    thrs: int, threshold count for selecting MVgenes
    ax: AxesSubplot object, the figure subplot object
    Functions:

    CV_Mean(mu, cv, fit_method='SVR', svr_gamma=0.003, x0=[0.5, 0.5], verbose=False): calculates the coefficient of variation (CV) score for each gene based on the mean and standard deviation of expression values, and fits a Support Vector Regression model or exponential function to the scores
    thrscount(x, y): calculates the threshold count for selecting MVgenes based on the fitted curve and the weight parameter (wt)
    """
    # plotShow default= Ture
    print("CamelRunning_MVgenes......")
    df_f = pd.DataFrame(datax.X.T, index=datax.var.index, columns=datax.obs.index)
    df_f=df_f.loc[datax.var["Filter1"] > 0]
    mu = df_f.mean(1).values
    sigma = df_f.std(1, ddof=1).values
    cv = sigma / mu
    score, mu_linspace, cv_fit, params = CV_Mean(mu, cv, 'SVR', svr_gamma=0.003)
    mu_sorted = mu[np.argsort(score)[::-1]]
    cv_sorted = cv[np.argsort(score)[::-1]]
    y = cv_fit.tolist()
    x = mu_linspace.tolist()
    pars = thrscount(x, y)

    thrs = 0
    for i in range(len(np.log2(mu_sorted) > 0)):
        if i == 0:
            if func(np.log2(cv_sorted[i]), pars[0], pars[1], pars[2]) < np.log2(mu_sorted[i]):
                thrs = thrs + 1
        else:
            if np.log2(cv_sorted[i]) < np.log2(cv_sorted[i - 1]):
                if func(np.log2(cv_sorted[i]), pars[0], pars[1], pars[2]) < np.log2(mu_sorted[i]):
                    thrs = thrs + 1
    thrs = min(max(thrs*wt, 1000), 5000)
    # thrs=2210
    MVlist = df_f.iloc[np.argsort(score)[::-1], :].iloc[:thrs, :].index
    MVlist=list(set(MVlist.tolist()+markerlist))
    ftlist2 = np.in1d(datax.var.index, MVlist)
    datax.var["MVgene"] = ftlist2
    #mu = mu, cv = cv, mu_sorted = mu_sorted, cv_sorted = cv_sorted, thrs = thrs,
    #mu_linspace = mu_linspace, cv_fit = cv_fit,
    #Xlow = -8.5, Xhigh = 6.5, Ylow = -2, Yhigh = 6.5, alphaValue = 0.2, sValue = 10,
    if plotfig==True:
        fig = plt.figure(**fig_args)
        ax = fig.add_subplot(111)
        ax.scatter(np.log2(mu), np.log2(cv), marker='o', edgecolor='none', alpha=0.1, s=5)

        ax.scatter(np.log2(mu_sorted[thrs:]), np.log2(cv_sorted[thrs:]), marker='o', edgecolor='none', alpha=alphaValue, s=sValue,
                   c='r')
        # x.plot(mu_linspace, cv_fit*1.1,'-k', linewidth=1, label='$FitCurve$')
        # plot(linspace(-9,7), -0.5*linspace(-9,7), '-r', label='$Poisson$')
        plt.ylabel('log2 CV')
        plt.xlabel('log2 mean')
        ax.grid(alpha=0.3)
        plt.xlim(Xlow, Xhigh)
        plt.ylim(Ylow, Yhigh)
        ax.legend(loc=1, fontsize=15)
        plt.gca().set_aspect(1.2)
        plt.grid(False)
    print("CamelRunning_MVgenes......Finished")
    return datax, score,  thrs, ax

def CV_Mean(mu, cv, fit_method='SVR', svr_gamma=0.003, x0=[0.5, 0.5], verbose=False):
    ### modified from BackSPIN, (GioeleLa Manno, et al., 2016, PMID: 27716510 )
    """
    Inputs:
    mu: a numpy array representing the mean expression of genes
    cv: a numpy array representing the coefficient of variation of genes
    fit_method: a string representing the method used for curve fitting, default is 'SVR'
    svr_gamma: a float representing the gamma parameter used for SVR, default is 0.003
    x0: a list of two floats representing initial guess parameters for the exponential fit method, default is [0.5, 0.5]
    verbose: a boolean representing whether to print verbose output, default is False
    Outputs:

    score: a numpy array representing the relative position of each gene with respect to the fitted curve
    mu_linspace: a numpy array representing the x-axis values for the fitted curve
    cv_fit: a numpy array representing the y-axis values for the fitted curve
    params: a numpy array representing the parameters used for the exponential fit method, or None if using SVR
    Function description:
    This function fits a curve to the relationship between mean gene expression and coefficient of variation (CV),
    and calculates the relative position of each gene with respect to the fitted curve. The user can choose between two curve fitting methods:
    Support Vector Regression (SVR) or exponential. If using SVR, the user can specify the gamma parameter.
    If using exponential, the user can specify initial guess parameters x0. The function returns the relative position of each gene,
    the x-axis and y-axis values for the fitted curve,
    and the parameters used for the exponential fit method (or None if using SVR).
    """
    log2_m = np.log2(mu)
    log2_cv = np.log2(cv)

    if len(mu) > 1000 and 'bin' in fit_method:
        # histogram with 30 bins
        n, xi = histogram(log2_m, 30)
        med_n = percentile(n, 50)
        for i in range(0, len(n)):
            # index of genes within the ith bin
            ind = where((log2_m >= xi[i]) & (log2_m < xi[i + 1]))[0].astype(int)
            if len(ind) > med_n:
                # Downsample if count is more than median
                ind = ind[random.permutation(len(ind))]
                ind = ind[:len(ind) - int(med_n)]
                mask = ones(len(log2_m), dtype=bool)
                mask[ind] = False
                log2_m = log2_m[mask]
                log2_cv = log2_cv[mask]
            elif (around(med_n / len(ind)) > 1) and (len(ind) > 5):
                # Duplicate if count is less than median
                log2_m = r_[log2_m, tile(log2_m[ind], int(round(med_n / len(ind)) - 1))]
                log2_cv = r_[log2_cv, tile(log2_cv[ind], int(round(med_n / len(ind)) - 1))]
    else:
        if 'bin' in fit_method:
            print('More than 1000 input feature needed for bin correction.')
        pass

    if 'SVR' in fit_method:
        try:
            from sklearn.svm import SVR
            if svr_gamma == 'auto':
                svr_gamma = 1000. / len(mu)
            # Fit the Support Vector Regression
            clf = SVR(gamma=svr_gamma)
            clf.fit(log2_m[:, np.newaxis], log2_cv)
            fitted_fun = clf.predict
            score = np.log2(cv) - fitted_fun(np.log2(mu)[:, np.newaxis])
            params = None
            # The coordinates of the fitted curve
            mu_linspace = np.linspace(min(log2_m), max(log2_m))
            cv_fit = fitted_fun(mu_linspace[:, np.newaxis])
            return score, mu_linspace, cv_fit, params

        except ImportError:
            if verbose:
                print('SVR fit requires scikit-learn python library. Using exponential instead.')
            if 'bin' in fit_method:
                return fit_CV(mu, cv, fit_method='binExp', x0=x0)
            else:
                return fit_CV(mu, cv, fit_method='Exp', x0=x0)
    elif 'Exp' in fit_method:
        from scipy.optimize import minimize
        # Define the objective function to fit (least squares)
        fun = lambda x, log2_m, log2_cv: sum(abs(log2((2. ** log2_m) ** (-x[0]) + x[1]) - log2_cv))
        # Fit using Nelder-Mead algorythm
        optimization = minimize(fun, x0, args=(log2_m, log2_cv), method='Nelder-Mead')
        params = optimization.x
        # The fitted function
        fitted_fun = lambda log_mu: log2((2. ** log_mu) ** (-params[0]) + params[1])
        # Score is the relative position with respect of the fitted curve
        score = np.log2(cv) - fitted_fun(np.log2(mu))
        # The coordinates of the fitted curve
        mu_linspace = np.linspace(min(log2_m), max(log2_m))
        cv_fit = fitted_fun(mu_linspace)
        return score, mu_linspace, cv_fit, params



def thrscount(x, y):
    """
    Input:
    x: a 1D numpy array containing the x-values of the data points
    y: a 1D numpy array containing the y-values of the data points
    Output:
    pars: a 1D numpy array containing the fitted parameters of the function
    Function description:
    This function fits a function to the given data points (x,y) using curve_fit from scipy.optimize module.
    The fitted function is of the form func(x, a, b, c) = a / (1 + np.exp(-(x - b)/c)).
     The function then calculates the confidence intervals for the fitted parameters and returns them in the pars array.
    """
    from scipy.optimize import curve_fit
    from scipy.stats.distributions import t
    initial_guess = [10, 0 - x[-1], y[-1]]
    pars, pcov = curve_fit(func, x, y, p0=initial_guess)
    alpha = 0.05  # 95% confidence interval = 100*(1-alpha)

    n = len(y)  # number of data points
    p = len(pars)  # number of parameters

    dof = max(0, n - p)  # number of degrees of freedom

    # student-t value for the dof and confidence level
    tval = t.ppf(1.0 - alpha / 2., dof)
    for i, j, var in zip(range(n), pars, np.diag(pcov)):
        sigma = var ** 0.5
        #print('p{0}: {1} [{2}  {3}]'.format(i, j,
        #                                    j - sigma * tval,
        #                                    j + sigma * tval))
    return pars

def func(x, a, b, c):
    'nonlinear function in a and b to fit to data'
    return a * x * x + b * x + c



def prediction(datax, mcolor_dict,net,learninggroup="train", radarplot=False, fontsizeValue=35,
              datarefplot=None,
               ncolnm=1, bbValue=(1.1, 1.05)):
    """
    datax: a data object.
    mcolor_dict: a dictionary that maps the colors of the clusters to their names.
    net: a machine learning model.
    learninggroup: a string indicating whether the data is from the train or the test set.
    radarplot: a boolean indicating whether to generate a radar plot or not.
    fontsizeValue: an integer indicating the font size of the plot.
    datarefplot: a reference dataset object.
    ncolnm: an integer indicating the number of columns in the radar plot.
    bbValue: a tuple indicating the width and height of the radar plot.
    The function first checks if the learninggroup is "train" or "test" and initializes the appropriate variables based on that.
    The function then generates a normalization factor for the data and feeds it to the machine learning model to generate a prediction.
    The function then generates a DataFrame with the probabilities for each cell to belong to each cluster and adds it to the data object.
    If radarplot is True, the function generates a radar plot of the cell types and returns it along with the coordinates of the cell type scores.
Finally, the function returns the updated data object.
    """
    #mwanted_order = mwanted_order, mclasses_names = mclasses_names, mprotogruop = dfpfcclus.loc["Cluster"].values,
    #mdf_train_set = mdf_train_set, figsizeV = 18, mtrain_index = mtrain_index, net = net, mreorder_ix = mreorder_ix,
    #mcolor_dict = refcolor_dict, learninggroup = "test"



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

def TransSpeciesGeneName(dfm, dictfilename, path):
    # dfm=dfpfc, dictfilename=dictfilename, path=path

    with open('%s%s' % (path, dictfilename), 'rb') as f:
        mouse2human_dict = pickle.load(f, encoding='ASCII')
    # dfm=df_f
    # convert the mouse gene name in the human gene name
    mouse_translable = [i for i in dfm.index if i in mouse2human_dict]
    dfm = dfm.loc[mouse_translable, :]
    dfm.index = [mouse2human_dict[i] for i in dfm.index]
    dfm=dfm.groupby(level=0).mean()
    return dfm


def SelectFeatures(datax, clustername='Cluster', methodname='wilcoxon', numbergenes=300, folderchange=3,
                   pvalue=0.1):
    """

    Input:
    datax: Input data object that contains gene expression data and other information
    clustername (optional): Name of the column in datax.obs that contains cluster labels
    methodname (optional): Method used to select features. Possible values are 'wilcoxon' and 'Enrichment_shortcut'
    numbergenes (optional): Number of top genes to select based on their p-values when using the 'wilcoxon' method
    folderchange (optional): Fold change threshold used when selecting marker genes using the 'Enrichment_shortcut' method
    pvalue (optional): p-value threshold used when selecting marker genes using either method
    Output:
    Modified datax object that contains the selected marker genes
    Function Description:
    The SelectFeatures function selects features (genes) based on the specified method (wilcoxon or Enrichment_shortcut) and returns the modified datax object.
    If the method name is 'wilcoxon', the function ranks genes in groups using the Wilcoxon test. It then creates a DataFrame containing information about gene names,
    log fold changes, p-values, and adjusted p-values for each group. The function then selects the top numbergenes genes based on their p-values and creates a list of marker genes.
    If the method name is 'Enrichment_shortcut', the function creates a DataFrame containing expression data for genes that pass a filtering step.
     It then calls another function called enrichmentscoreBETA to calculate enrichment scores for each cluster and select marker genes based on their scores.
    Finally, the function creates a list of unique marker genes and adds it as a new column to the input data object before returning it.
    """
    # datax: This is the input data object that contains gene expression data and other information. It is modified by the function and returned as the output.
    # clustername: This is an optional parameter that specifies the name of the column in datax.obs that contains cluster labels. The default value is 'Cluster'.
    # methodname: This is an optional parameter that specifies the method used to select features. The possible values are 'wilcoxon' and 'Enrichment_shortcut'. The default value is 'wilcoxon'.
    # numbergenes: This is an optional parameter that specifies the number of top genes to select based on their p-values when using the 'wilcoxon' method. The default value is 300.
    # folderchange: This is an optional parameter that specifies the fold change threshold used when selecting marker genes using the 'Enrichment_shortcut' method. The default value is 3.
    # pvalue: This is an optional parameter that specifies the p-value threshold used when selecting marker genes using either method. However, it appears to not be used in this version of the code. The default value is 0.1.
    if methodname == 'wilcoxon':
        sc.tl.rank_genes_groups(datax, clustername, method='wilcoxon')
        result = datax.uns['rank_genes_groups']
        groups = result['names'].dtype.names
        dfgene = pd.DataFrame(
            {group + '_' + key[:1]: result[key][group]
             for group in groups for key in ['names', 'logfoldchanges', 'pvals', 'pvals_adj']})
        df100 = dfgene.iloc[:numbergenes, :]
        genelist = []
        for i in range(0, df100.shape[1], 3):
            genelist.extend(df100.iloc[:, i].values)
        dfmk = genelist
        markerlist = list(set(dfmk) & set(datax.var.index))
    elif methodname == 'Enrichment_shortcut':
        dfdev2 = pd.DataFrame(datax.X, index=datax.obs.index, columns=datax.var.index).T
        dfdev2 = dfdev2.loc[datax.var['Filter1'] == True]
        markerlist = enrichmentscoreBETA(dfpfcclus=datax.obs[clustername], df_dev=dfdev2,
                                                           fc=folderchange, shortcut=True)
        markerlist = list(set(markerlist) & set(datax.var.index))
    MVlist = list(set(markerlist))
    ftlist2 = np.in1d(datax.var.index, MVlist)
    datax.var["MVgene"] = ftlist2
    return datax

def LabelGene_Scaling(datax, commongene, mprotogruop, tftable=None, thrs=None, score=None,
                      std_scaling=False, TPTT=10000, sharedMVgenes=None,
                      learninggroup="train"):
    """
    Input:
    datax: AnnData object
    commongene: List of genes common to all samples
    mprotogruop: Series or array of cluster labels for each sample
    tftable: Path to a file containing a list of transcription factors
    thrs: Threshold to select top genes based on a score
    score: Series or array of scores for each gene
    std_scaling: Boolean flag to indicate whether to scale data using standard deviation
    TPTT: Integer value to multiply each count by
    sharedMVgenes: List of genes to include in the analysis
    learninggroup: String indicating whether the function is being called for training or testing data
    Output:
    datax: AnnData object with modified attributes
    Functionality:
    This function scales the gene expression data based on the gene labels for each sample. If the function is called for training data,
    it selects the most variable genes and transcription factors and scales the data based on standard deviation or TPTT.
     It then extracts the samples and gene labels for training the classifier. If the function is called for testing data,
    it scales the data based on the training set and extracts the samples and gene labels for testing the classifier.
    The modified attributes of the AnnData object are returned.
    """

    print("CamelRunning---GenesScaling......")
    dfpfc = pd.DataFrame(datax.X.T, index=datax.var.index, columns=datax.obs.index)
    dfpfcclus = pd.DataFrame([datax.obs["Cluster"].values.tolist(), datax.obs["Cluster"].values.tolist()],
                             index=["bk", "Cluster"], columns=datax.obs.index)
    if learninggroup == "train":

        list_genes = datax.var.index[datax.var["MVgene"]].tolist()
        if tftable==None:
            tflist=[]
        else:
            tflist = pd.read_table(tftable, index_col=0, header=0, sep="\t").index.tolist()

        if score == None:
            sharedMVgenes = list(set(list_genes + tflist))
        else:
            df_dev_rev = dfpfc.iloc[np.argsort(score)[::-1], :].iloc[max(min(-thrs, -2000), -5000):, :]
            sharedMVgenes = list(set(list_genes + tflist) - set(df_dev_rev.index))
        if np.sum(TPTT) != 0:
            dfpfc = (dfpfc / dfpfc.sum()).multiply(TPTT, axis=0).fillna(0)
        if std_scaling == True:
            scalepfc = dfpfc.div(dfpfc.std(1), axis=0).fillna(0)
        scalepfc = dfpfc.astype(float).fillna(0)
        scalepfc = dfpfc.div(dfpfc.std(1), axis=0)
        scalepfc = scalepfc.fillna(0)
        dfpfc_dev = scalepfc.loc[list(set(scalepfc.index) & set(sharedMVgenes))].dropna()
        dfpfc_dev_log = np.log2(dfpfc_dev + 1)
        dfpfc_dev_all = dfpfc_dev_log.T.join(dfpfcclus.T, how="inner").dropna()
        bool1 = mprotogruop != "nan"
        mclasses_names, mclasses_index = np.unique(mprotogruop[bool1], return_inverse=True, return_counts=False)
        mtrain_index = mclasses_index
        mdf_train_set = dfpfc_dev_log.loc[:, bool1].copy()
        # mdf_train_set = dfpfc_dev_log.copy()
        mdf_train_set = mdf_train_set.loc[mdf_train_set.sum(1) > 0]
        sharedMVgenes = mdf_train_set.index.tolist()
        # datax.uns["train_set"]=mdf_train_set
        datax.obsm["train_set_values"] = mdf_train_set.values.T
        datax.uns["train_set_gene"] = mdf_train_set.index.values
        datax.uns["mclasses_names"] = mclasses_names
        datax.obs["mtrain_index"] = mtrain_index
        refgenelist = np.in1d(datax.var.index, sharedMVgenes)
        datax.var["RefGeneList"] = refgenelist
        print("CamelRunning---TrainingGenesScaling......Finished")
        return datax
    elif learninggroup == "test":
        dfpfc = dfpfc.reindex(commongene).fillna(0).astype(float)
        if np.sum(TPTT) != 0:
            dfpfc = (dfpfc / dfpfc.sum()).multiply(TPTT, axis=0).fillna(0)

        if std_scaling == True:
            scalegbm = dfpfc.div(dfpfc.std(1), axis=0).fillna(0)
        else:
            scalegbm = dfpfc.astype(float).fillna(0)

        dfgbm_dev = scalegbm.reindex(sharedMVgenes).fillna(0)
        dfgbm_dev_log = np.log2(dfgbm_dev + 1).fillna(0)
        # df_dev_gbm = df_dev_gbm.loc[mdf_train_set.index].fillna(0)
        dfgbm_dev_all = dfgbm_dev_log.T.join(dfpfcclus.loc["Cluster"].T, how="inner").T
        # dfgbmcol = dfgbm_dev_all.iloc[-1:, :]
        # dfgbm = dfgbm_dev_all.iloc[:-1, :]
        dfclpncol = dfgbm_dev_all.iloc[-1:, :]
        dfclpn = dfgbm_dev_all.iloc[:-1, :]
        protogruop = dfclpncol.loc["Cluster"].values
        bool1 = protogruop != 'none'
        classes_names, classes_index = np.unique(protogruop[bool1], return_inverse=True, return_counts=False)
        train_index = classes_index
        # dfgbm_train_set = dfgbm_dev_log.loc[:, bool1].copy()
        # train_index = classes_index
        # dfgbm_train_set = dfgbm_train_set.loc[dfgbm_train_set.sum(1) > 0]
        dfclpn = dfclpn.loc[:, bool1].copy()
        df_train_setclpn = dfclpn.loc[dfclpn.sum(1) > 0]
        df_train_setclpn = df_train_setclpn.reindex(sharedMVgenes).fillna(0)
        datax.obsm["test_set_values"] = df_train_setclpn.values.T
        datax.uns["train_set_gene"] = df_train_setclpn.index.values
        datax.uns["mclasses_names"] = classes_names
        datax.obs["mtrain_index"] = classes_index
        testgenelist = np.in1d(datax.var.index, sharedMVgenes)
        datax.var["RefGeneList"] = testgenelist
        print("CamelRunning---TestGenesScaling......Finished")
        return datax
        # return df_train_setclpn, dfclpncol, protogruop


def balance_clusters_adata(adata, cluster_col, fold_threshold=10):
    cluster_counts = adata.obs[cluster_col].value_counts()
    max_count = cluster_counts.max()

    balanced_data = []
    balanced_obs = []

    for cluster in cluster_counts.index:
        cluster_indices = adata.obs.index[adata.obs[cluster_col] == cluster]
        cluster_adata = adata[cluster_indices]
        if len(cluster_adata) < max_count / fold_threshold:
            # Up-sample
            n_samples = int(max_count / fold_threshold)
            sampled_indices = resample(cluster_indices,
                                       replace=True,
                                       n_samples=n_samples,
                                       random_state=42)
            # Identify duplicates
            sampled_indices = cluster_indices.tolist() + sampled_indices.tolist()
            sampled_indices_df = pd.DataFrame(sampled_indices, columns=['index'])
            sampled_indices_df['is_duplicated'] = sampled_indices_df.duplicated(keep='first')

            upsampled = sampled_indices_df.set_index('index')['is_duplicated']
        else:
            # No up-sampling for clusters that do not meet the criteria
            sampled_indices = cluster_indices
            # Label non-up-sampled items
            upsampled = pd.Series(False, index=sampled_indices)

        balanced_data.append(adata[sampled_indices])
        cluster_obs = adata.obs.loc[sampled_indices].copy()
        cluster_obs['upsampled'] = upsampled
        balanced_obs.append(cluster_obs)

    balanced_adata = ad.concat(balanced_data)
    balanced_adata.obs = pd.concat(balanced_obs)

    return balanced_adata




def MVgene_Scaling(datax,score, commongene, mprotogruop,tftable,thrs,
                   std_scaling=False, TPTT=10000, sharedMVgenes=None,
                   learninggroup="train"):
    """
    Inputs:
    datax: AnnData object containing the gene expression matrix and metadata.
    score: A vector of scores for each cell in the dataset.
    commongene: A vector of genes to be used for scaling the data.
    mprotogruop: A vector of metadata containing the cluster information.
    tftable: A table containing the list of transcription factor (TF) genes.
    thrs: An integer value representing the threshold for the number of genes to be selected.
    std_scaling: A boolean value to perform standard scaling or not.
    TPTT: A numeric value for normalizing the data.
    sharedMVgenes: A list of genes to be used as features.
    learninggroup: A string value indicating whether the data is for training or testing.
    Outputs:
    An updated AnnData object containing the scaled gene expression matrix and metadata.
    Functionality:

    This function scales the gene expression matrix of the input data based on the provided parameters such as score, threshold, and common genes.
    It also performs normalization and standard scaling if specified.
    The resulting data is then used for training or testing based on the input learning group.
     The function returns an updated AnnData object containing the scaled gene expression matrix and metadata.
    """


    print("CamelRunning---GenesScaling......")
    dfpfc = pd.DataFrame(datax.X.T, index=datax.var.index, columns=datax.obs.index)
    dfpfcclus = pd.DataFrame([datax.obs["Cluster"].values.tolist(), datax.obs["Cluster"].values.tolist()],
                             index=["bk", "Cluster"], columns=datax.obs.index)
    if learninggroup == "train":

        list_genes = datax.var.index[datax.var["MVgene"]].tolist()
        df_dev_rev = dfpfc.iloc[np.argsort(score)[::-1], :].iloc[max(min(-thrs, -2000), -5000):, :]
        tflist = pd.read_table(tftable, index_col=0, header=0, sep="\t").index.tolist()
        sharedMVgenes = list(set(list_genes + tflist) - set(df_dev_rev.index))
        if  np.sum(TPTT) != 0:
            dfpfc = (dfpfc / dfpfc.sum()).multiply(TPTT, axis=0).fillna(0)
        if std_scaling == True:
            scalepfc = dfpfc.div(dfpfc.std(1), axis=0).fillna(0)
        scalepfc = dfpfc.astype(float).fillna(0)
        scalepfc = dfpfc.div(dfpfc.std(1), axis=0)
        scalepfc = scalepfc.fillna(0)
        dfpfc_dev = scalepfc.loc[set(scalepfc.index) & set(sharedMVgenes)].dropna()
        dfpfc_dev_log = np.log2(dfpfc_dev + 1)
        dfpfc_dev_all = dfpfc_dev_log.T.join(dfpfcclus.T, how="inner").dropna()
        bool1 = mprotogruop != "nan"
        mclasses_names, mclasses_index = np.unique(mprotogruop[bool1], return_inverse=True, return_counts=False)
        mtrain_index = mclasses_index
        mdf_train_set = dfpfc_dev_log.loc[:, bool1].copy()
        # mdf_train_set = dfpfc_dev_log.copy()
        mdf_train_set = mdf_train_set.loc[mdf_train_set.sum(1) > 0]
        sharedMVgenes = mdf_train_set.index.tolist()
        #datax.uns["train_set"]=mdf_train_set
        datax.obsm["train_set_values"] = mdf_train_set.values.T
        datax.uns["train_set_gene"] = mdf_train_set.index.values
        datax.uns["mclasses_names"] = mclasses_names
        datax.obs["mtrain_index"] = mtrain_index
        refgenelist = np.in1d(datax.var.index, sharedMVgenes)
        datax.var["RefGeneList"]=refgenelist
        print("CamelRunning---TrainingGenesScaling......Finished")
        return datax
    elif learninggroup == "test":
        dfpfc = dfpfc.reindex(commongene).fillna(0).astype(float)
        if np.sum(TPTT) != 0:
            dfpfc = (dfpfc / dfpfc.sum()).multiply(TPTT, axis=0).fillna(0)

        if std_scaling == True:
            scalegbm = dfpfc.div(dfpfc.std(1), axis=0).fillna(0)
        else:
            scalegbm = dfpfc.astype(float).fillna(0)

        dfgbm_dev = scalegbm.reindex(sharedMVgenes).fillna(0)
        dfgbm_dev_log = np.log2(dfgbm_dev + 1).fillna(0)
        # df_dev_gbm = df_dev_gbm.loc[mdf_train_set.index].fillna(0)
        dfgbm_dev_all = dfgbm_dev_log.T.join(dfpfcclus.loc["Cluster"].T, how="inner").T
        # dfgbmcol = dfgbm_dev_all.iloc[-1:, :]
        # dfgbm = dfgbm_dev_all.iloc[:-1, :]
        dfclpncol = dfgbm_dev_all.iloc[-1:, :]
        dfclpn = dfgbm_dev_all.iloc[:-1, :]
        protogruop = dfclpncol.loc["Cluster"].values
        bool1 = protogruop != 'none'
        classes_names, classes_index = np.unique(protogruop[bool1], return_inverse=True, return_counts=False)
        train_index = classes_index
        # dfgbm_train_set = dfgbm_dev_log.loc[:, bool1].copy()
        # train_index = classes_index
        # dfgbm_train_set = dfgbm_train_set.loc[dfgbm_train_set.sum(1) > 0]
        dfclpn = dfclpn.loc[:, bool1].copy()
        df_train_setclpn = dfclpn.loc[dfclpn.sum(1) > 0]
        df_train_setclpn = df_train_setclpn.reindex(sharedMVgenes).fillna(0)
        datax.obsm["test_set_values"] =  df_train_setclpn.values.T
        datax.uns["train_set_gene"] =  df_train_setclpn.index.values
        datax.uns["mclasses_names"] = classes_names
        datax.obs["mtrain_index"] = classes_index
        testgenelist = np.in1d(datax.var.index, sharedMVgenes)
        datax.var["RefGeneList"] = testgenelist
        print("CamelRunning---TestGenesScaling......Finished")
        return datax
        #return df_train_setclpn, dfclpncol, protogruop





def NNclassifer(datax, epochNum=100, learningRate=0.05, verbose=0,
                optimizerMmentum=0.8,deviceDef= "cpu",
                dropout=0.3):
    """
    Inputs:

    datax: Anndata object containing gene expression data
    epochNum (optional): number of epochs to train neural network, default is 100
    learningRate (optional): learning rate for optimizer, default is 0.05
    verbose (optional): verbosity level during training, default is 0
    optimizerMomentum (optional): momentum for optimizer, default is 0.8
    dropout (optional): dropout rate, default is 0.3
    Outputs:

    net: trained neural network classifier
    Function Description:
    This function takes in an Anndata object containing gene expression data, builds and trains a neural network classifier using the PyTorch library,
    and returns the trained neural network classifier. The neural network classifier has three layers: an input layer, a hidden layer, and an output layer.
    The number of neurons in the hidden layer is set to one-fifth the number of genes in the input layer.
    The number of neurons in the output layer is set to the number of unique cell types in the dataset.
    The function also allows for optional parameters to set the number of epochs, learning rate, verbosity level during training, optimizer momentum, and dropout rate.
    """
    # nist_d=mdf_train_set.shape[0],
    # hidden_d = int(mnist_d / 5),
    # output_d = len(unique(mtrain_index))):
    # from skorch import NeuralNetClassifier
    # import Classifier3Layers
    # import LossTweet
    if deviceDef=="cpu":
        deviceSel = "cpu"
    elif torch.cuda.is_available():
        deviceSel = 'cuda'
    else:
        deviceSel = "cpu"
    print("CamelRunning---NNclasffier_in_%s......."%deviceSel)
    mdf_train_set = pd.DataFrame(datax.obsm["train_set_values"].T, index=datax.uns["train_set_gene"],
                                 columns=datax.obs.index)
    mtrain_index= datax.obs["mtrain_index"]
    class Classifier3Layers(nn.Module):
        def __init__(
                self,
                input_dim=mdf_train_set.shape[0],
                hidden_dim=int(mdf_train_set.shape[0] / 5),
                output_dim=len(np.unique(mtrain_index)),
                dropout=0.3,
        ):
            super(Classifier3Layers, self).__init__()
            self.dropout = nn.Dropout(dropout)

            self.hidden = nn.Linear(input_dim, hidden_dim)
            self.output = nn.Linear(hidden_dim, output_dim)

        def forward(self, X, **kwargs):
            X = F.relu(self.hidden(X))
            X = self.dropout(X)
            X = F.softmax(self.output(X), dim=-1)
            return X


    net = NeuralNetClassifier(
        Classifier3Layers(
            input_dim=mdf_train_set.shape[0],
            hidden_dim=int(mdf_train_set.shape[0] / 5),
            output_dim=len(np.unique(mtrain_index)),
            dropout=0.5,
        ).float(),
        max_epochs=epochNum,
        lr=learningRate,
        verbose=0,
        optimizer__momentum=optimizerMmentum,
        module__dropout=dropout,
        #optimizer__nesterov=True,
        device=deviceSel,
        # callbacks=[acTweet(max_loss=0.2)]
    )

    normalizer = 0.9 * mdf_train_set.values.max(1)[:, np.newaxis]
    net.fit((mdf_train_set.values / normalizer).T.astype(np.float32), mtrain_index)
    # noticeMSG
    print("CamelRunning---NNclasffier_in_%s.......Finished" % deviceSel)
    return net

def DataScaling(datax):
    """
    Inputs:

    datax: an AnnData object containing the raw gene expression data
    Outputs:

    An AnnData object with scaled gene expression data
    Functionality:

    Scales the raw gene expression data in datax using the counts per cell
    Returns an AnnData object with the scaled gene expression data
    """
    dfdev=pd.DataFrame(datax.X,index=datax.obs.index,columns=datax.var.index).T
    #dfdev=dfdev.loc[datax.var['Filter1']==True]
    CountsPerCell =dfdev.sum()
    CountsPerCell = np.ravel(CountsPerCell).copy()
    data=dfdev.values.T
    if issubclass(data.dtype.type, (int, np.integer)):
        data = data.astype(np.float32)
    CountsPerCell = np.asarray(CountsPerCell)
    mdvalue = np.median(CountsPerCell[CountsPerCell>0], axis=0)
    CountsPerCell += (CountsPerCell == 0)
    CountsPerCell = CountsPerCell / mdvalue
    DatX = dict(
            X=  np.divide(data, CountsPerCell[:, None], out=data),
            norm_factor=CountsPerCell,
        )

    dfdev2=pd.DataFrame(DatX["X"].T)
    dfdev2.columns=dfdev.columns
    dfdev2.index=dfdev.index
    datax.X=dfdev2.values.T
    return  datax

def NNclassifer4layers(datax, epochNum=100, learningRate=0.05, verbose=0,
                optimizerMmentum=0.8,
                dropout=0.3):
    """
    Inputs:

    datax: Anndata object containing gene expression data and labels.
    epochNum: Number of epochs for training.
    learningRate: Learning rate for the optimizer.
    verbose: Whether or not to print progress during training.
    optimizerMmentum: Momentum parameter for the optimizer.
    dropout: Dropout rate for the neural network.
    Output:

    net: Trained neural network classifier.
    Functionality:

    Defines a 4-layer neural network classifier using PyTorch.
    Trains the neural network using the given data and hyperparameters.
    Returns the trained neural network classifier.
    """
    # nist_d=mdf_train_set.shape[0],
    # hidden_d = int(mnist_d / 5),
    # output_d = len(unique(mtrain_index))):
    # from skorch import NeuralNetClassifier
    # import Classifier3Layers
    # import LossTweet
    deviceSel = 'cuda' if torch.cuda.is_available() else 'cpu'
    print("CamelRunning---NNclasffier_in_%s......."%deviceSel)
    mdf_train_set = pd.DataFrame(datax.obsm["train_set_values"].T, index=datax.uns["train_set_gene"],
                                 columns=datax.obs.index)
    mtrain_index= datax.obs["mtrain_index"]
    class Classifier4Layers(nn.Module):
        def __init__(
                self,
                input_dim=mdf_train_set.shape[0],
                hidden_dim1=int(mdf_train_set.shape[0] / 5),
                hidden_dim2=int(mdf_train_set.shape[0] / 15),
                output_dim=len(np.unique(mtrain_index)),
                dropout=0.3,
        ):
            super(Classifier4Layers, self).__init__()
            self.dropout = nn.Dropout(dropout)
            self.hidden1 = nn.Linear(input_dim, hidden_dim1)
            self.hidden2 = nn.Linear(hidden_dim1, hidden_dim2)
            self.output = nn.Linear(hidden_dim2, output_dim)

        def forward(self, X, **kwargs):
            X = F.relu(self.hidden1(X))
            X = F.relu(self.hidden2(X))
            X = self.dropout(X)
            X = F.softmax(self.output(X), dim=-1)
            return X


    net = NeuralNetClassifier(
        Classifier4Layers(
            input_dim=mdf_train_set.shape[0],
            hidden_dim1=int(mdf_train_set.shape[0] / 5),
            hidden_dim2=int(mdf_train_set.shape[0] / 15),
            output_dim=len(np.unique(mtrain_index)),
            dropout=0.5,
        ).float(),
        max_epochs=epochNum,
        lr=learningRate,
        verbose=0,
        optimizer__momentum=optimizerMmentum,
        module__dropout=dropout,
        #optimizer__nesterov=True,
        device=deviceSel,
        # callbacks=[acTweet(max_loss=0.2)]
    )

    normalizer = 0.9 * mdf_train_set.values.max(1)[:, np.newaxis]
    net.fit((mdf_train_set.values / normalizer).T.astype(np.float32), mtrain_index)
    # noticeMSG
    print("CamelRunning---NNclasffier_in_%s.......Finished" % deviceSel)
    return net


def balance_clusters_adata(adata, cluster_col, fold_threshold=10):
    cluster_counts = adata.obs[cluster_col].value_counts()
    max_count = cluster_counts.max()

    balanced_data = []
    balanced_obs = []

    for cluster in cluster_counts.index:
        cluster_indices = adata.obs.index[adata.obs[cluster_col] == cluster]
        cluster_adata = adata[cluster_indices]
        if len(cluster_adata) < max_count / fold_threshold:
            # Up-sample
            n_samples = int(max_count / fold_threshold)
            sampled_indices = resample(cluster_indices,
                                       replace=True,
                                       n_samples=n_samples,
                                       random_state=42)
            # Identify duplicates
            sampled_indices = cluster_indices.tolist() + sampled_indices.tolist()
            sampled_indices_df = pd.DataFrame(sampled_indices, columns=['index'])
            sampled_indices_df['is_duplicated'] = sampled_indices_df.duplicated(keep='first')

            upsampled = sampled_indices_df.set_index('index')['is_duplicated']
        else:
            # No up-sampling for clusters that do not meet the criteria
            sampled_indices = cluster_indices
            # Label non-up-sampled items
            upsampled = pd.Series(False, index=sampled_indices)

        balanced_data.append(adata[sampled_indices])
        cluster_obs = adata.obs.loc[sampled_indices].copy()
        cluster_obs['upsampled'] = upsampled
        balanced_obs.append(cluster_obs)

    balanced_adata = ad.concat(balanced_data)
    balanced_adata.obs = pd.concat(balanced_obs)

    return balanced_adata

def AccuracyPlot( nnModel, accCutoff=0.95, Xlow=-1,Ylow=0.5, Yhigh=1,):
    """
    Inputs:

    nnModel: a neural network model object which has a history attribute containing the accuracy scores during training/validation.
    accCutoff: the threshold for the minimum acceptable accuracy score.
    Xlow: the lower limit of the x-axis range.
    Ylow: the lower limit of the y-axis range.
    Yhigh: the upper limit of the y-axis range.
    Outputs:

    ax: a matplotlib Axes object containing the accuracy plot.
    Functionality:

    This function generates a plot of the accuracy scores during training/validation of a neural network model.
    The x-axis represents the number of epochs and the y-axis represents the accuracy score.
    The function also plots a horizontal line at the specified accuracy cutoff threshold.
    The function returns a matplotlib Axes object containing the accuracy plot.
    """
    fig_args = {'figsize': (6, 3), 'facecolor': 'white', 'edgecolor': 'white'}
    #acc = net.history[:, 'valid_acc'], accCutoff = 0.95,
    #Xlow = -1, Xhigh = len(nnModel.history[:, 'valid_acc']) + 1,
    acc = nnModel.history[:, 'valid_acc']
    Xhigh = len(nnModel.history[:, 'valid_acc']) + 1
    fig = plt.figure(**fig_args)
    ax = fig.add_subplot(111)
    ax.plot(np.array([abs(i) for i in range(Xhigh-1)]),np.array( acc ), c='k', lw=2 )

    ax.axhline( accCutoff, c='b' )
    #axvline( 35 , c='r')
    plt.ylabel('Accuracy Score', fontsize=15)
    plt.xlabel('Epoches', fontsize=15)
    plt.xlim( Xlow, Xhigh)
    plt.ylim(Ylow, Yhigh)
    plt.grid(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    return ax


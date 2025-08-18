#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tacowig.py

Stepwise pipeline to generate per–cell type BigWig tracks from single-cell ATAC data.
- Reading is a separate step (read_adata), returning an AnnData object.
- TACoWig class operates on an AnnData instance (no file I/O inside).
- CLI main(): read -> (optional filter) -> prepare -> aggregate -> write BigWigs.

Usage (CLI):
  python tacowig.py \
    --input my_atac.h5ad \
    --celltype-key Cluster \
    --allow-chroms human \
    --resolve-overlaps \
    --aggregation mean \
    --scale 10 \
    --outdir bigwigs

In notebooks:
  from tacowig import read_adata, apply_obs_filter, TACoWig
  adata = read_adata("my_atac.h5ad")
  adata = apply_obs_filter(adata, "Dataset", "10X10k")
  pipe = TACoWig(adata, celltype_key="Cluster", resolve_overlaps=True, scale=10.0)
  pipe.prepare_intervals().aggregate()
  files = pipe.write_bigwigs()
"""

import os, re, warnings, argparse
from typing import Dict, List, Tuple, Optional

import numpy as np
import pandas as pd
import anndata as ad
from scipy import sparse
import pyBigWig

# Optional (.h5mu support)
try:
    import muon as mu
    _HAS_MUON = True
except Exception:
    _HAS_MUON = False

# Optional (overlap resolution)
try:
    import pyranges as pr
    _HAS_PYRANGES = True
except Exception:
    _HAS_PYRANGES = False


__all__ = ["TACoWig", "read_adata", "apply_obs_filter"]


# ----------------------------- Utilities ----------------------------- #

def _sanitize_filename(name: str) -> str:
    name = re.sub(r"[^\w\-.]+", "_", str(name).strip())
    return name or "unnamed"

def _ensure_csr(x) -> sparse.csr_matrix:
    if sparse.isspmatrix_csr(x):
        return x
    if sparse.isspmatrix(x):
        return x.tocsr()
    return sparse.csr_matrix(x)

def read_adata(path: str, modality: Optional[str] = "atac") -> ad.AnnData:
    """
    Read an AnnData (.h5ad) or MuData (.h5mu) file and return an AnnData object.
    NOTE: Only reading happens here. No filtering, no interval parsing.
    """
    if path.endswith(".h5ad"):
        return ad.read_h5ad(path)
    if path.endswith(".h5mu"):
        if not _HAS_MUON:
            raise ImportError("Reading .h5mu requires 'muon' (pip install muon).")
        mdata = mu.read_h5mu(path)
        mod = modality or "atac"
        if mod not in mdata.mod:
            raise KeyError(f"Modality '{mod}' not found. Available: {list(mdata.mod.keys())}")
        return mdata.mod[mod]
    raise ValueError("Input must end with .h5ad or .h5mu")

def apply_obs_filter(adata: ad.AnnData, key: Optional[str], value: Optional[str]) -> ad.AnnData:
    """
    Optional convenience to subset cells by obs[key] == value.
    """
    if key is None or value is None:
        return adata
    if key not in adata.obs:
        raise KeyError(f"Filter key '{key}' not found in adata.obs")
    mask = adata.obs[key].astype(str).values == str(value)
    out = adata[mask].copy()
    if out.n_obs == 0:
        raise ValueError("No cells left after filtering.")
    return out


# ----------------------------- Main class ---------------------------- #

class TACoWig:
    """
    Stepwise pipeline operating on an AnnData object:

      1) prepare_intervals()  -> parse/filter/sort peaks, optional overlap fix, reorder matrix
      2) aggregate()          -> per-celltype aggregation
      3) write_bigwigs()      -> write per-celltype BigWig files

    You can chain steps:
      TACoWig(adata,...).prepare_intervals().aggregate().write_bigwigs()
    """

    def __init__(
        self,
        adata: ad.AnnData,
        *,
        celltype_key: str = "Cluster",
        allow_chroms: Optional[List[str]] = None,
        chrom_sizes_tsv: Optional[str] = None,
        resolve_overlaps: bool = False,
        enforce_chr_prefix: bool = True,
        aggregation: str = "mean",        # "mean" | "sum" | "median"
        scale: float = 1.0,
        outdir: str = "bigwigs",
        verbose: bool = True,
    ):
        if adata is None or not isinstance(adata, ad.AnnData):
            raise TypeError("adata must be an AnnData object.")
        if adata.n_obs == 0:
            raise ValueError("adata contains zero cells.")

        self.adata = adata
        self.celltype_key = celltype_key
        self.allow_chroms = allow_chroms or [
            "chr1","chr2","chr3","chr4","chr5","chr6","chr7","chr8","chr9","chr10",
            "chr11","chr12","chr13","chr14","chr15","chr16","chr17","chr18","chr19",
            "chr20","chr21","chr22","chrX","chrY"
        ]
        self.chrom_sizes_tsv = chrom_sizes_tsv
        self.resolve_overlaps = resolve_overlaps
        self.enforce_chr_prefix = enforce_chr_prefix
        self.aggregation = aggregation
        self.scale = float(scale)
        self.outdir = outdir
        self.verbose = verbose

        # Filled by steps
        self.X: Optional[sparse.csr_matrix] = None            # cells x peaks (reordered)
        self.intervals: Optional[pd.DataFrame] = None         # chrom,start,end,peak_idx
        self.chrom_sizes: Optional[List[Tuple[str,int]]] = None
        self.agg: Optional[Dict[str, np.ndarray]] = None      # {cell_type: vector}

    # -------------------------- core steps -------------------------- #

    def prepare_intervals(self):
        """Parse intervals, filter/sort, (optionally) resolve overlaps, reorder X, compute chrom sizes."""
        if self.verbose:
            print("[PREP] Parsing peak intervals")

        intervals = self._parse_intervals_from_var(self.adata.var, self.adata.var_names)
        intervals = self._filter_and_sort_intervals(intervals, self.allow_chroms)

        if self.resolve_overlaps:
            if not _HAS_PYRANGES:
                raise ImportError("Overlap resolution requires 'pyranges' (pip install pyranges).")
            if self.verbose:
                print("[PREP] Resolving overlaps with PyRanges (shift previous end)")
            intervals = self._adjust_overlaps_with_pyranges(intervals)

        # Reorder matrix columns to match sorted intervals
        X = _ensure_csr(self.adata.X)
        X = X[:, intervals["peak_idx"].values]
        if self.verbose:
            print(f"[PREP] Reordered matrix: {X.shape}")

        # Chrom sizes (TSV or infer)
        if self.chrom_sizes_tsv:
            chrom_sizes = self._read_chrom_sizes_tsv(self.chrom_sizes_tsv)
            if self.verbose:
                print(f"[PREP] Using chrom sizes TSV ({len(chrom_sizes)} entries)")
        else:
            chrom_sizes = self._infer_chrom_sizes(intervals)
            if self.verbose:
                print(f"[PREP] Inferred chrom sizes ({len(chrom_sizes)} entries)")

        self.X = X
        self.intervals = intervals[["chrom","start","end","peak_idx"]].reset_index(drop=True)
        self.chrom_sizes = chrom_sizes
        return self

    def aggregate(self):
        """Aggregate per cell type (mean/sum/median) across cells."""
        assert self.X is not None and self.intervals is not None, "Run prepare_intervals() first."
        key = self.celltype_key
        if key not in self.adata.obs:
            raise KeyError(f"'{key}' not found in adata.obs")

        labels = self.adata.obs[key].astype(str).values
        uniq = pd.unique(labels)
        agg: Dict[str, np.ndarray] = {}

        if self.verbose:
            print(f"[AGG] Aggregation='{self.aggregation}' by '{key}' on {len(uniq)} groups")

        for ct in uniq:
            idx = np.where(labels == ct)[0]
            if idx.size == 0:
                continue
            sub = self.X[idx, :]
            if self.aggregation == "mean":
                v = np.asarray(sub.mean(axis=0)).ravel()
            elif self.aggregation == "sum":
                v = np.asarray(sub.sum(axis=0)).ravel()
            elif self.aggregation == "median":
                warnings.warn("Sparse median not implemented efficiently; using mean instead.")
                v = np.asarray(sub.mean(axis=0)).ravel()
            else:
                raise ValueError("aggregation must be one of {'mean','sum','median'}")
            agg[ct] = v

        if not agg:
            raise ValueError("No aggregates computed; check celltype_key and data.")
        self.agg = agg
        return self

    def write_bigwigs(self) -> List[str]:
        """Write one BigWig per cell type; returns list of file paths."""
        assert self.agg is not None and self.intervals is not None and self.chrom_sizes is not None, \
            "Run aggregate() after prepare_intervals()."

        os.makedirs(self.outdir, exist_ok=True)
        chroms = self.intervals["chrom"].tolist()
        starts = self.intervals["start"].astype(int).tolist()
        ends   = self.intervals["end"].astype(int).tolist()

        written = []
        for ct, vec in self.agg.items():
            fname = os.path.join(self.outdir, f"{_sanitize_filename(ct)}.bigwig")
            vals = (vec.astype(float) * self.scale).tolist()

            with pyBigWig.open(fname, "w") as bw:
                bw.addHeader(self.chrom_sizes)
                step = 2_000_000
                n = len(vals)
                if n <= step:
                    bw.addEntries(chroms, starts, ends=ends, values=vals)
                else:
                    for i in range(0, n, step):
                        bw.addEntries(chroms[i:i+step], starts[i:i+step],
                                      ends=ends[i:i+step], values=vals[i:i+step])
            written.append(fname)
            if self.verbose:
                print(f"[WRITE] {ct} -> {fname}")

        if self.verbose:
            print(f"[DONE] Wrote {len(written)} BigWig file(s) to '{self.outdir}'")
        return written

    # -------------------------- helpers -------------------------- #

    def _parse_intervals_from_var(self, var: pd.DataFrame, var_names: pd.Index) -> pd.DataFrame:
        # Prefer explicit columns if present
        for c, s, e in [("Chromosome","Start","End"), ("chrom","start","end")]:
            if c in var.columns and s in var.columns and e in var.columns:
                chrom = var[c].astype(str).values
                start = var[s].astype(int).values
                end   = var[e].astype(int).values
                break
        else:
            # Fallback parse: "chr1:100-200" or "1:100-200"
            chrom, start, end = [], [], []
            for name in var_names.astype(str).tolist():
                c, pos = name.split(":")
                s, e = pos.split("-")
                if self.enforce_chr_prefix and not c.startswith("chr"):
                    c = "chr" + c
                chrom.append(c); start.append(int(s)); end.append(int(e))
            chrom = np.array(chrom); start = np.array(start); end = np.array(end)

        df = pd.DataFrame({
            "chrom": chrom,
            "start": start,
            "end": end,
            "peak_idx": np.arange(len(chrom), dtype=int)
        })
        bad = (df["end"] <= df["start"]) | df.isna().any(axis=1)
        if bad.any():
            warnings.warn(f"Removing {bad.sum()} malformed intervals (end<=start or NA).")
            df = df.loc[~bad].copy()
        return df

    @staticmethod
    def _filter_and_sort_intervals(df: pd.DataFrame, allowlist: Optional[List[str]]) -> pd.DataFrame:
        if allowlist:
            df = df[df["chrom"].isin(allowlist)].copy()
            df["chrom"] = pd.Categorical(df["chrom"], categories=allowlist, ordered=True)
        return df.sort_values(["chrom","start","end"]).reset_index(drop=True)

    @staticmethod
    def _infer_chrom_sizes(df_sorted: pd.DataFrame) -> List[Tuple[str,int]]:
        sizes = df_sorted.groupby("chrom")["end"].max().reset_index()
        return list(sizes.itertuples(index=False, name=None))

    @staticmethod
    def _read_chrom_sizes_tsv(path: str) -> List[Tuple[str,int]]:
        cs = pd.read_csv(path, sep="\t", header=None, comment="#")
        if cs.shape[1] >= 2 and not np.issubdtype(cs.iloc[0,1], np.integer):
            cs = pd.read_csv(path, sep="\t", header=0, comment="#")
        cs = cs.iloc[:, :2]
        cs.iloc[:, 0] = cs.iloc[:, 0].astype(str)
        cs.iloc[:, 1] = cs.iloc[:, 1].astype(int)
        return list(cs.itertuples(index=False, name=None))

    def _adjust_overlaps_with_pyranges(self, df_sorted: pd.DataFrame) -> pd.DataFrame:
        """
        Cluster overlaps and shift previous 'end' to (next 'start' - 1).
        """
        gr = pr.PyRanges(df_sorted.rename(columns={"chrom":"Chromosome","start":"Start","end":"End"}))
        clusters = gr.cluster()

        def _adjust(cluster_df: pd.DataFrame) -> pd.DataFrame:
            cdf = cluster_df.sort_values(["Chromosome","Start"]).copy()
            for i in range(1, len(cdf)):
                if cdf["Start"].iloc[i] <= cdf["End"].iloc[i-1]:
                    cdf.loc[cdf.index[i-1], "End"] = cdf["Start"].iloc[i] - 1
            return cdf[cdf["End"] > cdf["Start"]]

        adjusted = clusters.apply(_adjust).df
        out = adjusted.rename(columns={"Chromosome":"chrom","Start":"start","End":"end"}).copy()

        # Try to map back to original peaks by (chrom,start) primary
        out = out.merge(
            df_sorted[["chrom","start","end","peak_idx"]],
            on=["chrom","start"],
            how="left",
            suffixes=("","_orig")
        )
        missing = out["peak_idx"].isna()
        if missing.any():
            out.loc[missing, "peak_idx"] = out.loc[missing].merge(
                df_sorted[["chrom","start","end","peak_idx"]],
                on=["chrom","start","end"], how="left"
            )["peak_idx_y"].values
        if out["peak_idx"].isna().any():
            fill = df_sorted["peak_idx"].values[:out["peak_idx"].isna().sum()]
            out.loc[out["peak_idx"].isna(), "peak_idx"] = fill

        out["peak_idx"] = out["peak_idx"].astype(int)
        return out.sort_values(["chrom","start","end"]).reset_index(drop=True)


# ------------------------------- CLI -------------------------------- #

def _parse_allow_chroms(arg: Optional[str]) -> Optional[List[str]]:
    if arg is None:
        return None
    if arg.lower() == "human":
        return ["chr"+str(i) for i in range(1,23)] + ["chrX","chrY"]
    if arg.lower() == "mouse":
        return ["chr"+str(i) for i in range(1,20)] + ["chrX","chrY"]
    # otherwise comma-separated list
    return [c.strip() for c in arg.split(",") if c.strip()]

def main():
    p = argparse.ArgumentParser(description="ATAC peaks -> per-celltype BigWig (reading is separate).")
    p.add_argument("--input", required=True, help=".h5ad or .h5mu path")
    p.add_argument("--modality", default="atac", help="MuData modality (if --input is .h5mu)")
    p.add_argument("--celltype-key", default="Cluster", help="obs column for cell types")
    p.add_argument("--filter-key", default=None, help="Optional obs key to subset cells")
    p.add_argument("--filter-value", default=None, help="Value for --filter-key")
    p.add_argument("--allow-chroms", default="human",
                   help="'human' | 'mouse' | comma-separated list (e.g. chr1,chr2,chrX)")
    p.add_argument("--chrom-sizes-tsv", default=None, help="Optional chrom sizes TSV")
    p.add_argument("--resolve-overlaps", action="store_true", help="Use PyRanges cluster/adjust")
    p.add_argument("--no-enforce-chr-prefix", action="store_true", help="Do NOT auto-add 'chr' prefix")
    p.add_argument("--aggregation", default="mean", choices=["mean","sum","median"], help="Aggregation mode")
    p.add_argument("--scale", type=float, default=1.0, help="Multiply values before writing")
    p.add_argument("--outdir", default="bigwigs", help="Output directory for .bigwig files")
    p.add_argument("--quiet", action="store_true", help="Less verbose")

    args = p.parse_args()
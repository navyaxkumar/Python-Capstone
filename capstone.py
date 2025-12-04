# capstone.py
# Author: Navya Kumar (Roll No. 2501410054)
# Campus Energy Dashboard – refactored version with simplified names

import os
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# folders
SRC_DIR = Path("data")
OUT_DIR = Path("output")
OUT_DIR.mkdir(exist_ok=True)

# common possible column names we may run into
TS_NAMES = ["timestamp", "time", "datetime", "date"]
KWH_NAMES = ["kwh", "energy", "usage", "meter"]
BLD_NAMES = ["building", "block", "facility"]


# -----------------------------
# FILE HANDLING + INITIAL LOAD
# -----------------------------
def get_all_files(folder=SRC_DIR):
    """returns all CSVs inside data folder"""
    if not folder.exists():
        print("data folder missing.")
        return []
    return list(folder.glob("*.csv"))


def safe_read(path):
    """tries reading a csv and skips garbage lines"""
    try:
        df = pd.read_csv(path, on_bad_lines="skip")
        return df
    except Exception as e:
        print(f"could not read {path}: {e}")
        return None


def fix_colnames(df, filename):
    """tries to find timestamp, kwh, building cols and normalize them"""
    df.columns = df.columns.str.strip()

    # look for timestamp column
    ts_col = None
    for c in df.columns:
        if c.lower() in TS_NAMES:
            ts_col = c
            break

    # look for kwh column
    kwh_col = None
    for c in df.columns:
        if c.lower() in KWH_NAMES:
            kwh_col = c
            break

    # look for building column
    bcol = None
    for c in df.columns:
        if c.lower() in BLD_NAMES:
            bcol = c
            break

    rename = {}
    if ts_col:
        rename[ts_col] = "timestamp"
    if kwh_col:
        rename[kwh_col] = "kwh"
    if bcol:
        rename[bcol] = "building"

    df = df.rename(columns=rename)

    # if still missing cols, try fallback logic
    if "timestamp" not in df.columns:
        df = df.rename(columns={df.columns[0]: "timestamp"})

    if "kwh" not in df.columns:
        if len(df.columns) > 1:
            df = df.rename(columns={df.columns[1]: "kwh"})
        else:
            df["kwh"] = 0

    # building name fallback from filename
    if "building" not in df.columns:
        bname = Path(filename).stem.split("_")[0]
        df["building"] = bname

    return df


def load_everything():
    """main loader: loops through csvs, fixes them, merges into one df"""
    files = get_all_files()
    if not files:
        print("No CSVs in data/. Add some first.")
        return pd.DataFrame()

    combined = []
    trash = []

    for f in files:
        raw = safe_read(f)
        if raw is None:
            trash.append(f)
            continue

        fixed = fix_colnames(raw, f)
        fixed["timestamp"] = pd.to_datetime(fixed["timestamp"], errors="coerce")
        fixed["kwh"] = pd.to_numeric(fixed["kwh"], errors="coerce")

        before = len(fixed)
        fixed = fixed.dropna(subset=["timestamp", "kwh"])
        after = len(fixed)

        if after == 0:
            trash.append(f)
            continue

        print(f"Loaded {f} ({before}->{after})")
        combined.append(fixed)

    if not combined:
        return pd.DataFrame()

    df_all = pd.concat(combined, ignore_index=True)
    df_all = df_all[["building", "timestamp", "kwh"]].sort_values("timestamp")
    return df_all.reset_index(drop=True)


# -----------------------------
# AGGREGATION LOGIC
# -----------------------------
def daily_stats(df):
    """daily totals per building"""
    x = df.set_index("timestamp")
    out = x.groupby("building").resample("D")["kwh"].sum().reset_index()
    return out


def weekly_stats(df):
    """weekly totals per building"""
    x = df.set_index("timestamp")
    out = x.groupby("building").resample("W")["kwh"].sum().reset_index()
    return out


def bld_summary(df):
    """sum, avg, min, max per building"""
    s = (df.groupby("building")["kwh"]
         .agg(total="sum", avg="mean", low="min", high="max")
         .reset_index())
    s["avg"] = s["avg"].round(2)
    return s


# -----------------------------
# OOP CLASSES
# -----------------------------
class Reading:
    def __init__(self, ts, kwh):
        self.ts = pd.to_datetime(ts)
        self.kwh = float(kwh)


class Block:
    def __init__(self, name):
        self.name = name
        self.rec = []

    def add(self, r: Reading):
        self.rec.append(r)

    def total(self):
        return sum(r.kwh for r in self.rec)

    def per_day(self):
        if not self.rec:
            return pd.DataFrame()
        df = pd.DataFrame([{"timestamp": r.ts, "kwh": r.kwh} for r in self.rec])
        df = df.set_index("timestamp").resample("D")["kwh"].sum().reset_index()
        return df

    def peak(self):
        if not self.rec:
            return None
        x = max(self.rec, key=lambda r: r.kwh)
        return x.ts, x.kwh


class BlockManager:
    def __init__(self):
        self.box = {}

    def feed(self, df):
        for _, row in df.iterrows():
            name = row["building"]
            if name not in self.box:
                self.box[name] = Block(name)
            try:
                r = Reading(row["timestamp"], row["kwh"])
                self.box[name].add(r)
            except:
                pass

    def make_summary(self):
        rows = []
        for name, blk in self.box.items():
            ts, peakv = blk.peak() if blk.peak() else (pd.NaT, np.nan)
            rows.append({
                "building": name,
                "total_kwh": blk.total(),
                "peak_time": ts,
                "peak_kwh": peakv
            })
        return pd.DataFrame(rows)


# -----------------------------
# DASHBOARD
# -----------------------------
def make_charts(df_all, daydf, wkdf):
    fig, axs = plt.subplots(3, 1, figsize=(12, 14), constrained_layout=True)

    # daily line chart
    ax = axs[0]
    for name, g in daydf.groupby("building"):
        ax.plot(g["timestamp"], g["kwh"], label=name)
    ax.set_title("Daily Energy Use")
    ax.legend()

    # weekly bar chart
    ax = axs[1]
    wk_avg = wkdf.groupby("building")["kwh"].mean()
    wk_avg.plot(kind="bar", ax=ax)
    ax.set_title("Avg Weekly Use")

    # peak scatter
    ax = axs[2]
    pk = df_all.groupby("building")["kwh"].max().reset_index()
    xvals = np.arange(len(pk))
    ax.scatter(xvals, pk["kwh"])
    ax.set_xticks(xvals)
    ax.set_xticklabels(pk["building"], rotation=40)
    ax.set_title("Peak Hour Usage")

    fig.suptitle("Campus Energy Dashboard – Navya Kumar")
    fig.savefig(OUT_DIR / "dashboard.png")
    plt.close(fig)
    print("Dashboard saved.")


# -----------------------------
# WRITE OUTPUT FILES
# -----------------------------
def save_all(df_clean, bsum):
    df_clean.to_csv(OUT_DIR / "cleaned_energy_data.csv", index=False)
    bsum.to_csv(OUT_DIR / "building_summary.csv", index=False)

    # executive summary
    tot = df_clean["kwh"].sum()
    top = bsum.sort_values("total_kwh", ascending=False).iloc[0]
    global_peak_idx = df_clean["kwh"].idxmax()
    global_peak_time = df_clean.loc[global_peak_idx, "timestamp"]
    global_peak_val = df_clean.loc[global_peak_idx, "kwh"]

    with open(OUT_DIR / "summary.txt", "w") as f:
        f.write("Campus Energy Summary Report\n")
        f.write("Author: Navya Kumar (2501410054)\n\n")
        f.write(f"Total Campus Consumption: {tot:.2f} kWh\n")
        f.write(f"Highest Usage Building: {top['building']} ({top['total_kwh']:.2f} kWh)\n")
        f.write(f"Peak Reading: {global_peak_val:.2f} kWh at {global_peak_time}\n")

    print("Outputs saved.")


# -----------------------------
# MAIN ENTRY
# -----------------------------
def run():
    print("Loading files...")
    data = load_everything()
    if data.empty:
        print("No valid data found. Stopping.")
        return

    print("Making stats...")
    day = daily_stats(data)
    week = weekly_stats(data)
    sum1 = bld_summary(data)

    mgr = BlockManager()
    mgr.feed(data)
    mgr_sum = mgr.make_summary()

    print("Creating dashboard...")
    make_charts(data, day, week)

    print("Writing files...")
    save_all(data, mgr_sum)

    print("All done.")


if __name__ == "__main__":
    run()

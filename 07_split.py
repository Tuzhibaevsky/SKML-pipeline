import h5py as h5
import numpy as np
import os

infile = './out/final/merged.h5'
outdir = './out/split'
outname = outdir + '/merged.npz'
os.makedirs(outdir, exist_ok=True)

train_ratio = 0.70
val_ratio = 0.15
test_ratio = 1 - train_ratio - val_ratio

f = h5.File(infile, 'r')
pid_flg = f['labels'][:]
# Cut background events
good_idx = np.argwhere(pid_flg != 0).flatten()

good_idx = np.random.permutation(good_idx)

n_good = good_idx.shape[0]
train_num = int(n_good * train_ratio)
val_num = int(n_good * (val_ratio+train_ratio))

train_idxs = good_idx[:train_num]
val_idxs = good_idx[train_num:val_num]
test_idxs = good_idx[val_num:]

split_idxs = {'train_idxs': train_idxs, 'val_idxs': val_idxs, 'test_idxs': test_idxs}

np.savez(outname, **split_idxs)
# SKML-pipeline

v0.1.0 by Yikai Xu, 28 Nov. 2024

This directory is mainly the whole pipeline to produce h5 datasets for WatChMaL Machine Learning. The pipeline can do production from generating random vertices to merging final hdf5 files and split files. (Simply copy them to any gpu node and you can do the training) 

Though sadly the ML training itself cannot be done on `sukap` since no gpu is on this node, it would still be of much use to prepare the whole dataset ready for training since there's usually a long queue on CC nodes.

**PS:** the best place to run the ML code in all CC nodes is `Narval` afaik, as it has 40 GB Display Mem per GPU, which is the largest among all CC nodes, and thus allowing a largest batch size, hence efficiently reducing the training time (though the queues might be slightly longer)

You can submit a job to start queueing before the h5 files are transferred to the nodes if you are running WatChMaL on CC, as the queueing time of a job is always longer than the file transfer time.

# Steps of Pipeline

For python env, you can source your own, or `env.sh` in this directory.

It is recommended that you run python scripts and shell scripts on different terminals, and source env **only** on the python one.

## Overview

1. `gen_vec` > Random Vecs (Text File)
2. `skdetsim` > zbs Files
3. 
    - A: `zbs2root/read_zbs` or `QT_job` > ROOT for QT
    - B: `convert_root/` > ROOT (conventional)
4. 
    - A: `qt2h5` > original h5 file
    - B: `read_root` > npy for extra truths
5. `subst_h5` > to put extra truths into h5 files
6. `merge_h5` > merge h5 files
7. `gen_split` > generate split files
------


## 1. Generation of Random Vectors

**From nothing to text vector files**

(If you want to generate vectors according to neutrino flux or something not mathematically simple, go to `neut` experts)

**Command:** `python gen_vec.py`

**Input/Dependency:** *nothing*

**Args:** written explicitly in the script, no argparse
- modify `ln 12` for output dir
- modify `ln 3-4` for number of events and files

**Output:** text files for vertices, by default we have:
- directory: `genvec/` (ln 12)
- filenames: `genvec_{i:03d}.dat` (ln 116)

### To Check generated Vecs:

You can go to `/disk03/usr8/yikai/gen_vec.ipynb` to check if vecs are generated properly.

## 2. skdetsim of Vectors

*Modified from Nahid's script*

**From text vec files to zbs**

### 2.1 Make seed files

Makes seed files for `skdetsim`, as the card file has `NEUT-RAND 0`

**Command:** `perl mk_seed.pl`

**Input/Dependency:** *nothing*

**Args:** written explicitly in the script, no argparse
- modify `ln 3` for number of files

**Output:** text files for random seeds, by default we have:
- directory: `seeds/` (ln 2)
- filenames: `random.tbl.{i:03d}` (ln 15)

### 2.2 Make subdirectories of config

Makes subdirectories for jobs.

**Command:** `perl mk_massprod.pl`

**Dependency:** (ln 6-8)
- `skdetsim_high.sh` (skdetsim shell script)
- `sk5_official.card` (card file)
- `skdetsim_high` (skdetsim main executable)

**Args:** written explicitly in the script, no argparse
- modify `ln 2` for index of files
- check `ln 6-8` for dep directories

**Output:** text files for random seeds, by default we have:
- directory: `massprod/` (ln 4)
- filenames: `{i:03d}/` (ln 3-5)
    - with symlinks of all 3 input files

### 2.3 Run skdetsim

Submit jobs for `skdetsim`.

**Command:** `detsim_dosubmit.sh` (`nohup detsim_dosubmit.sh > _detsim.log 2>&1 &` might be better if you are generating a huge amount of events)

**Input:** (ln 7, ln 76)
- Generated vectors by **#1**
    - by default in `genvec/`

**Dependencies:**
- Output of **#2.2**
    - by default in `massprod/{i:03d}/`
- Random seed files by **#2.1**
    - by default in `seeds/`

**Args:** written explicitly in the script, no argparse, so tweak...
- modify `ln 5-6` for index of files
- modify `ln 7-9` for i/o/dep directories
- check `ln 69` for job time limit (longer time for less timeout rate, but consumes more time)
- check `ln 73` for env

**Output:** zbs files for results, by default we have:
- directory: `gendet/` (ln 8)
    - `gendet/err` for error files
    - `gendet/log` for log files
    - `gendet/out` for output zbs files
- filenames: `out/skdetsim_{i:03d}.zbs` (ln 76)

### 2.4 Check zbs output and delete bad ones

**REWORKING IN PROGRESS**
*Not Available For Now*

- `gendet/check_log.sh` to read all log files and print out the ones erred
- `gendet/check_err.sh` to read all err files (cannot cover all errors, thus not recommended)
- `gendet/auto_del.sh` to generate a file `err_files.log` which documents all problematic files and deletes corresponding zbs files in `gendet/out`

For pipeline:
- Just run `auto_del.sh` is enough.

### 2.5 Pre-cat zbs output for manageability (Recommended, but optional)

`cat` zbs files by their last 2 digits, resulting in 100 output files.

**Command:** `gendet/concatenate.sh`

**Input:**
- Generated good zbs files by **#2.3 & 2.4**
    - by default in `gendet/out`

**Args:** written explicitly in the script, no argparse, so tweak...
- modify `ln 9` for output directories/filenames

**Output:** some concatenated zbs files, by default we have:
- directory: `gendet/cat/` (ln 9)
- filenames: `gen_id_{i:02d}.zbs` (ln 9)

**Be careful! Check if the output files already exist, as the script is gonna append them, not overwrite them**

## 3A. Convert zbs to QT-ROOT

*copied from Cedar*

**From zbs files to QT-root**

The main executable is in `zbs2root/`, namely `zbs2root/read_zbs`. You can recompile it (but don't have to) as the source code is included in the same directory.

**Command:** `./QT_control.sh` 
- For one single file, you can just go to `zbs2root/read_zbs` and do a `pjsub` of it.

**Input:**
- Generated good zbs files by **#2**
    - by default in `gendet/cat`

**Args:** written explicitly in the script, no argparse, so tweak...
- modify `ln 4-5` in `./QT_control.sh` for index of files
- modify `ln 1-11` in `./QT_job.sh` for i/o/exec/etc. directories 

**Output:** QT-ROOT, by default we have:
- directory: `genqt/` (ln 2 in `./QT_job.sh`)
- filenames: `{i:02d}.root`

Error files and log files appear in `.errs` and `.logs` respectively, you can use `clean_err.sh` to filter non-empty ones, and remove them after checking.

## 4A. Dump QT-ROOT to hdf5

*copied and modified from Cedar WatChMaL script*

**QT-root to hdf5**

**Command:** `./qt2h5_control.sh` 
- For one single file, you can just go to `python qt2h5.py` and do a `pjsub` of it.

**Input:**
- QT-ROOT files by **#3A**
    - by default in `genqt/`

**Args:** written explicitly in the script, and argparse for python applies (c.f.`qt2h5.py` for parsed args)
- modify `ln 5` in `./qt2h5_control.sh` for input directory
- modify `ln 4` in `./qt2h5.sh` for output directory

**Output:** QT-ROOT by default we have:
- directory: `genh5/` (ln 4 in `./qt2h5.sh`)
- filenames: `{i:02d}_digi.h5`

Error files and log files appear in `.errs` and `.logs` respectively, you can use `clean_err.sh` to filter non-empty ones, and remove them after checking.

## 3B. Convert zbs to conventional ROOT

*Provided by Nahid*

**From zbs files to root (conventional)**

**First**, one should run `convert_root/cleanup.sh` to remove all flags before running the command below.

**Command:** `convert_root/convert_job.sh` 
- `pjsub` it (recommended for like 100 files), or use `convert_root/start-convert.sh`

**Input:**
- Generated good zbs files by **#2**
    - by default in `gendet/cat`

**Args:** written explicitly in the script, no argparse, so tweak...
- modify `ln 11-12` for i/o directories
- check `ln 5` for env

**Output:** hbk and ROOT (conventional) files, by default we have:
- directory: `genroot/` (ln 11)
    - `genroot/hbk/` and `genroot/tree/`
- filenames: input file name + `.hbk` or `.root`

## 4B. Extract info from conventional ROOT

**From root (conventional) to npy**

Read `ent_pos, ent_dir` and `Pid_flg` from root file and store them in numpy format.

**Command:** `python read_root.py`

**Input:**
- Generated root files by **#3B**
    - by default in `genroot/tree`

**Args:** written explicitly in the script, no argparse, so tweak...
- modify `ln 5-7` for input
- modify `ln 53` for output

**Output:** npy files, by default we have:
- directory: `gennpy/` (ln 53)
- filenames: `all_1M.npy` (ln 53)
    - you definitely want to change it

## 5. Substitute some h5 keys with npy info

*copied and modified from Cedar WatChMaL script*

Merge npy info into h5 files, and discard some irrelevant keys

**Command:** `subst_h5_control.sh`

**Input:**
- Generated h5 files by **#4A**
    - by default in `genh5/`
- Extracted npy files by **#4B**
    - by default in `gennpy/`

**Args:** written explicitly in the script, and argparse for python applies (c.f.`subst_h5.py` for parsed args)
- modify `ln 5` in `subst_h5_control.sh` for input h5 directory
- modify `ln 4` in `./subst_h5.sh` for output directory
- modify `ln 16` in `./subst_h5.py` for input numpy file (or pass in `./subst_h5.sh` file by `-n`)

**Output:** h5 files, by default we have:
- directory: `genfinal/` (ln 4 in `./subst_h5.sh`)
- filenames: `f_{i:02d}_digi.h5`

Error files and log files appear in `.errs` and `.logs` respectively, you can use `clean_err.sh` to filter non-empty ones, and remove them after checking.

## 6. Merge all h5 files into one

*copied and modified from Cedar WatChMaL script*

Merge all h5 files, so that file transfer can be easier.

**Command:** `./merge_h5.sh` (`pjsub` it)
- If you want to merge h5 by small batches, figure it out in `merge_h5_control.sh`

**Input:**
- Generated h5 files by **#5**
    - by default in `genfinal/`

**Args:** written explicitly in the script, and argparse for python applies (c.f.`merge_h5.py` for parsed args)
- modify `./merge_h5.sh`, by passing `-i, -o, -p` for i/o dir and input prefix
    - `-p` can be useful if you only want to merge h5 starting with certain pattern

**Output:** h5 files, by default we have: (`-o` in `./merge_h5.sh`)
- directory: `./`
- filenames: `gen_all.h5`

## 7. Generate split file

Generate a split file for the final h5

**Command:** `python gen_split.py`
- Very light, so no need to `pjsub` it

**Input:**
- Merged h5 files by **#6**
    - by default in `./`

**Args:** written explicitly in the script, no argparse
- modify `ln 4` in `gen_split.py`

**Output:** npz split file, by default we have:
- directory: `./`
- filenames: `gen_all.npz`
    - Same directory and name asthe input h5 file, but all ext name changed into npz

## Then...

**Copy the merged h5 and split npz file to wherever you like to do the training!**

You can directly use `./gen_all.h5` and `./gen_dll.npz` for training

### Some other stuff:

- In `umred2prod/` there are some file related to `umred2` UPMU dataset
- In `test/` there are some example intermediate datasets

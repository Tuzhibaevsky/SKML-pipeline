# SKML-pipeline

by Yikai Xu, Last updated 09 Feb 2025

This repo is for the whole pipeline to produce h5 datasets (and split files) for WatChMaL Machine Learning. The pipeline can do production of datasets from generating random vertices to final hdf5 files and split files, which can be simply copied to any gpu node and you can do the training with WatChMaL code.

Though sadly the ML training itself cannot be done on `sukap` since no gpu is on this node, it would still be of much use to prepare the whole dataset ready for training since there's usually a long queue on CC nodes.

**PS:** the best place to run the ML code among all CC nodes is `Narval` afaik, as it has 40 GB Display Mem per GPU, which is the largest among all CC nodes, and thus allowing a largest batch size, hence efficiently reducing the training time (though the queues might be slightly longer)

You can submit a job to start queueing before the h5 files are transferred to the nodes if you are running WatChMaL on CC, as the queueing time of a job is always longer than the file transfer time.

# Steps of Pipeline

For python env, you can source your own, or `env.sh` in this directory.

## Overview

1. Generation of Random Vectors
2. `skdetsim` of Vectors, Getting `zbs` Files
3. Converting `zbs` Files into `root` Format
    - A: For *Q* and *T* by *PMT index* > "QT ROOT" file
    - B: Common Data Fields > "Conventional ROOT" file
4. From ROOT to More Python-Readable Files
    - A: "QT ROOT" > `h5`
    - B: Required Fields in "Conventional ROOT" > `npy`
5. Writing `npy` Data into `h5`, Substitution of some Fields
6. Merger of All Sub-`h5` Files
7. Generation of Split Files
------


## 1. Generation of Random Vectors

**From nothing to text vector files**

(If you want to generate vectors according to neutrino flux or something not mathematically simple, go to `neut` experts)


## 2. skdetsim of Vectors

*Modified from Nahid's script*

**From text vec files to zbs**

### 2.1 Make seed files

Makes seed files for `skdetsim`, as the card file has `NEUT-RAND 0`

### 2.2 Make subdirectories for job submission

Makes subdirectories for jobs.

### 2.3 Run skdetsim

Submit jobs for `skdetsim`.

### 2.4 Check zbs output and delete bad ones

Automatically deletes bad zbs files.

### 2.5 Pre-cat zbs output for manageability (Recommended, but optional)

`cat` zbs files by their numbers.

## 3A. Convert zbs to QT-ROOT

*copied from Cedar*

**From zbs files to QT-root**

The main executable is in `zbs2root/`, namely `zbs2root/read_zbs`. You can recompile it (but don't have to) as the source code is included in the same directory.

Will use the github repo for `zbs2root` and fork it as a sub-module in the future.

## 4A. Dump QT-ROOT to hdf5

*copied and modified from Cedar WatChMaL script*

**QT-root to hdf5**

## 3B. Convert zbs to conventional ROOT

*Provided by Nahid*

**From zbs files to root (conventional)**

## 4B. Extract info from conventional ROOT

**From root (conventional) to npy**

Read `ent_pos, ent_dir` and `Pid_flg` from root file and store them in numpy format.

## 5. Substitute some h5 keys with npy info

*copied and modified from Cedar WatChMaL script*

Merge npy info into h5 files, and discard some irrelevant keys

## 6. Merge all h5 files into one

*copied and modified from Cedar WatChMaL script*

Merge all h5 files, so that file transfer can be done easier.

## 7. Generate split file

Generate a split file for the final h5

## Then...

**Copy the merged h5 and split npz file to wherever you like to do the training!**

(In the `out/final` and `out/split` directories)


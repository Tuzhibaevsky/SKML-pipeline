'''
Originally by Nick Prouse (Watchmal)
'''

import argparse
import h5py
import numpy as np
import glob

def combine_files(input_path, output_path, string):

    input_files = glob.glob(input_path+'/*'+string+'.*')
    output_file = output_path+'/'+string+'_combine.hy'

    print("output file:", output_file)
    out_file = h5py.File(output_file, 'w')
    #infiles = [h5py.File(f, 'r') for f in input_files]
    infiles = []
    for f in input_files:
        print(f)
        infiles.append(h5py.File(f,'r'))
    print(f"opened input file {infiles[0].filename}")
    keys = infiles[0].keys()
    attr_keys = infiles[0].attrs.keys()
    for f in infiles[1:]:
        print(f"opened and checking input file {f.filename}")
        if f.keys() != keys:
            raise KeyError(f"HDF5 file {f.filename} keys {f.keys()} do not match first file's keys {keys}.")
        if f.attrs.keys() != attr_keys:
            raise KeyError(f"HDF5 file {f.filename} attributes {f.attrs.keys()} do not match first file's attributes {attr_keys}.")
    for k in attr_keys:
        out_file.attrs[k]  = np.hstack([f.attrs[k] for f in infiles]).tolist()
    for k in keys:
        dtype = infiles[0][k].dtype
        shape = list(infiles[0][k].shape)
        for f in infiles[1:]:
            shape[0] += f[k].shape[0]
            if shape[1:] != list(f[k].shape[1:]):
                raise ValueError(f"Array {k} in {f.filename} has shape {f[k].shape} which is incompatible with extending previous files shape {shape}.")
        print(f"writing {k}, shape {shape}, dtype {dtype}")
        dset = out_file.create_dataset(k, shape=shape, dtype=dtype)
        isIndex = False
        if k == "event_hits_index":
            isIndex = True
            offset = 0
            print("  is an index array, so adding length of hit_pmt array in each file to the index values of the following file")
        start = 0
        for f in infiles:
            stop = start+f[k].shape[0]
            print(f"  entries {start}:{stop} from file {f.filename}")
            if isIndex:
                dset[start:stop] = np.array(f[k]) + offset
                offset += f['hit_pmt'].shape[0]
            else:
                dset[start:stop] = f[k]
            start = stop
    print(f"Written output file {out_file.filename}.")
    out_file.close()

def get_args():
    parser = argparse.ArgumentParser(description='dump sim data into other datasets')
    parser.add_argument('-i', '--input_dir', type=str, default=None)
    parser.add_argument('-o', '--output_file', type=str, default=None)
    parser.add_argument('-p', '--prefix', type=str, default='')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    config = get_args()
    print("output file:", config.output_file)
    out_file = h5py.File(config.output_file, 'w')
    config.input_files = glob.glob(config.input_dir+'/'+config.prefix+'*')
    config.input_files = sorted(config.input_files)
    infiles = [h5py.File(f, 'r') for f in config.input_files]
    print(f"opened input file {infiles[0].filename}")
    keys = infiles[0].keys()
    attr_keys = infiles[0].attrs.keys()
    for f in infiles[1:]:
        print(f"opened and checking input file {f.filename}")
        if f.keys() != keys:
            raise KeyError(f"HDF5 file {f.filename} keys {f.keys()} do not match first file's keys {keys}.")
        if f.attrs.keys() != attr_keys:
            raise KeyError(f"HDF5 file {f.filename} attributes {f.attrs.keys()} do not match first file's attributes {attr_keys}.")
    for k in attr_keys:
        out_file.attrs[k]  = np.hstack([f.attrs[k] for f in infiles]).tolist()
    for k in keys:
        dtype = infiles[0][k].dtype
        shape = list(infiles[0][k].shape)
        for f in infiles[1:]:
            shape[0] += f[k].shape[0]
            if shape[1:] != list(f[k].shape[1:]):
                raise ValueError(f"Array {k} in {f.filename} has shape {f[k].shape} which is incompatible with extending previous files shape {shape}.")
        print(f"writing {k}, shape {shape}, dtype {dtype}")
        dset = out_file.create_dataset(k, shape=shape, dtype=dtype)
        isIndex = False
        if k == "event_hits_index":
            isIndex = True
            offset = 0
            print("  is an index array, so adding length of hit_pmt array in each file to the index values of the following file")
        start = 0
        for f in infiles:
            stop = start+f[k].shape[0]
            print(f"  entries {start}:{stop} from file {f.filename}")
            if isIndex:
                dset[start:stop] = np.array(f[k]) + offset
                offset += f['hit_pmt'].shape[0]
            else:
                dset[start:stop] = f[k]
            start = stop
    print(f"Written output file {out_file.filename}.")
    out_file.close()

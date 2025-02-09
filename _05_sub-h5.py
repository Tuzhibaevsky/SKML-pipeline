
"""
Merge entry position/direction and pid flag fields into h5 files

"""

import h5py as h5
import numpy as np
import os

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-i', type=str, help='Directory of input h5 files')
parser.add_argument('-f', type=str, help='Single input h5 file')
parser.add_argument('-n', type=str, help='Path to the npy file')
parser.add_argument('-o', type=str, help='Directory of output h5 files')

args = parser.parse_args()

if args.i:
    print('Input directory (ignores single file):', args.i)
    h5dir = args.i
    h5files = os.listdir(h5dir)
    h5files.sort()
elif args.f:
    print('Single input file:', args.f)
    h5dir = os.path.dirname(args.f)
    h5files = [os.path.basename(args.f),]
else:
    print('No input file or directory specified, exits')
    exit(1)

npyfn = args.n
npyfile = np.load(npyfn, allow_pickle=True).item()

outdir = args.o

copy_keys = ['directions', 'energies', 'event_hits_index', 'event_ids',
             'hit_charge', 'hit_pmt', 'hit_time', 'positions', 'root_files',]

print('Keys to be copied:')
print(', '.join(copy_keys))

cut_ambient = False

total_files = len(h5files)
processed = 0

for h5file in h5files:
    processed += 1
    if 'h5' not in h5file:
        print(f'NOT AN H5 FILE: {h5file}, SKIPS')
        continue
    print(f'Dealing: {h5file}', processed, '/', total_files)
    npykey = h5file.split('/')[-1].split('_')[0]
    npykey = '' + npykey + ''
    if npykey not in npyfile:
        print(f'*** NOT FOUND: {npykey} ***')
        continue
    # else:
    #     print(f'Match: {npykey}')
    npas = npyfile[npykey]
    h5F = h5.File(f'{h5dir}/{h5file}', 'r')
    nev_h5 = h5F["labels"].shape[0]
    nev_npy = len(npas[-1])
    print(nev_h5, 'events in h5')
    print(nev_npy, 'events in npy')
    if nev_h5 != nev_npy:
        print(f'*** MISMATCH ***')
        break
    npy_ent_dir = np.array(npas[0])
    npy_ent_pos = np.array(npas[1])
    npy_pid_flg = np.array(npas[2])
    
    outF = h5.File(f'{outdir}/f_{h5file}.hy', 'w')
    
    for key in copy_keys:
        outF.create_dataset(key, data=h5F[key], dtype=h5F[key].dtype)
    outF.move('directions', 'gen_directions')
    outF.move('positions', 'gen_positions')
    
    outF.create_dataset('directions', data=npy_ent_dir.reshape(-1, 1, 3), dtype=h5F['directions'].dtype)
    outF.create_dataset('positions', data=npy_ent_pos.reshape(-1, 1, 3), dtype=h5F['positions'].dtype)
    outF.create_dataset('labels', data=npy_pid_flg, dtype='int32')
    # originally generated labels are dummy, replace them
    # however, the key of labels should always exist in the final h5 file, or it will cause a problem
    
    polars = np.arccos(npy_ent_dir[..., 2]).reshape(-1)
    azimuths = np.arctan2(npy_ent_dir[..., 1], npy_ent_dir[..., 0]).reshape(-1)
    angles = np.stack([polars, azimuths], axis=-1)
    outF.create_dataset('angles', data=angles, dtype='float32')
    
    h5F.close()
    print('cut', cut_ambient)
    if cut_ambient:
        # Only store events with non-0 labels
        # Would be really slow, hence commented out
        '''
        mask = npy_pid_flg != 0
        out_keys = outF.keys()
        
        start_indices = outF['event_hits_index']
        end_indices = np.roll(start_indices, -1)
        end_indices[-1] = outF['hit_pmt'].shape[0]
        sel_start_indices = start_indices[mask]
        sel_end_indices = end_indices[mask]
        
        for key in out_keys:
            if 'hit_' not in key:
                cache_key = outF[key][:][mask]
                cache_dtype = outF[key].dtype
                del outF[key]
                outF.create_dataset(key, data=cache_key, dtype=cache_dtype)
            else:
                hit_var = np.array([])
                for i, (start, end) in enumerate(zip(sel_start_indices, sel_end_indices)):
                    print(i, '/', sel_start_indices.shape[0], ':', start, '-', end, end='\r', flush=True)
                    hit_var = np.append(hit_var, outF[key][:][start:end])
                cache_key = hit_var
                cache_dtype = outF[key].dtype
                del outF[key]
                outF.create_dataset(key, data=cache_key, dtype=cache_dtype)
            
            print(f'{key} written: {outF[key].shape}')
        '''
    outF.close()
    print(f'Finished: {h5file}')
print('All done')
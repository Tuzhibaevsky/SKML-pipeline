
"""
Python 3 script for processing a list of ROOT files into .npz files

To keep references to the original ROOT files, the file path is stored in the output.
An index is saved for every event in the output npz file corresponding to the event index within that ROOT file (ev).

Authors: Nick Prouse, modifications by Felix Cormier

(Copied from Cedar and Adapted for Sukap by Yikai Xu)

"""

import h5py
import matplotlib.pyplot as plt
import math
import numpy as np
import ROOT
import os
import argparse

ROOT.gROOT.SetBatch(True)

class SKDETSIM:
    def __init__(self,infile) -> None:
        inFile = ROOT.TFile.Open(infile ,"READ")
        #print(dir(inFile))
        self.file = inFile
        tree = inFile.T
        self.tree = tree
        self.nevent = tree.GetEntries()
        #self.tree.GetEvent(0)
        #print(f'num trigs?: {len(self.tree.T)}')
        #print(f'nvc: {self.tree.nvc}, 0: {self.tree.ID[0]}, 1: {self.tree.ID[1]}, 3: {self.tree.ID[2]}')

    def get_event(self, ev):
        # Delete previous triggers to prevent memory leak (only if file does not change)
        #print(ev)
        self.tree.GetEvent(ev)
        self.nhits = len(self.tree.ID)
        self.current_event = ev

    def get_event_info(self):
        i0 = 0
        self.tree.GetEvent(self.current_event)
        mass_correction = 0
        if self.tree.ipvc[i0] == 11:
            mass_correction = 0.51099895
        elif self.tree.ipvc[i0] == 13:
            mass_correction = 105.6583755
        elif self.tree.ipvc[i0] == 211:
            mass_correction = 139.57039
        total_p = math.sqrt(math.pow(self.tree.pvc[3*i0],2)+math.pow(self.tree.pvc[3*i0+1],2)+math.pow(self.tree.pvc[3*i0+2],2))
        #if self.current_event == 0 or self.current_event == 1 or self.current_event == 2:
            #print(f'nevent: {self.current_event}, x mom : {self.tree.pvc[0]}, y mom: {self.tree.pvc[1]}, z mom: {self.tree.pvc[2]}, total p: {total_p} ')
        return {
            "pid": self.tree.ipvc[i0],
            #End for photon decay vertex, position for photon production vertex
            "position": [self.tree.posivc[3*i0], self.tree.posivc[3*i0+1], self.tree.posivc[3*i0+2]],# e+ / e- should have same position
            "gamma_start_vtx": [-999,-999,-999], # e+ / e- should have same position
            "isConversion": False,
            "energy_electron": -999,
            "energy_positron": -999,
            "direction_electron": [-999,-999,-999],
            "direction_positron": [-999,-999,-999],
            "direction": [self.tree.pvc[3*i0]/total_p, self.tree.pvc[3*i0+1]/total_p, self.tree.pvc[3*i0+2]/total_p],
            "energy": math.sqrt( math.pow(total_p,2) + math.pow(mass_correction,2))
        }
    
    def get_digitized_hits(self):
        position = []
        charge = []
        time = []
        pmt = []
        trigger = []
        for hit in range(self.nhits):
            pmt_id = self.tree.ID[hit]-1
            position.append([self.tree.X[hit], self.tree.Y[hit], self.tree.Z[hit]])
            charge.append(self.tree.Q[hit])
            time.append(self.tree.T[hit])
            pmt.append(pmt_id)
            trigger.append(0)
        hits = {
            "position": np.asarray(position, dtype=np.float32),
            "charge": np.asarray(charge, dtype=np.float32),
            "time": np.asarray(time, dtype=np.float32),
            "pmt": np.asarray(pmt, dtype=np.int32),
            "trigger": np.asarray(trigger, dtype=np.int32),
        }
        return hits

def dump_file_skdetsim(infile, outfile, radius = 1690, half_height = 1810):

    # All data arrays are initialized here
    skdetsim = SKDETSIM(infile)
    nevents = skdetsim.nevent

    event_id = np.empty(nevents, dtype=np.int32)
    root_file = np.empty(nevents, dtype=object)

    pid = np.empty(nevents, dtype=np.int32)
    position = np.empty((nevents, 3), dtype=np.float64)
    gamma_start_vtx = np.empty((nevents, 3), dtype=np.float64)
    isConversion = np.empty(nevents, dtype=np.float64)
    direction = np.empty((nevents, 3), dtype=np.float64)
    energy = np.empty(nevents,dtype=np.float64)
    electron_direction = np.empty((nevents, 3), dtype=np.float64)
    electron_energy = np.empty(nevents,dtype=np.float64)
    positron_direction = np.empty((nevents, 3), dtype=np.float64)
    positron_energy = np.empty(nevents,dtype=np.float64)

    primary_charged_range = np.empty(nevents, dtype=np.float64)

    digi_hit_pmt = np.empty(nevents, dtype=object)
    digi_hit_pmt_pos = np.empty(nevents, dtype=object)
    digi_hit_pmt_or = np.empty(nevents, dtype=object)
    digi_hit_charge = np.empty(nevents, dtype=object)
    digi_hit_time = np.empty(nevents, dtype=object)
    digi_hit_trigger = np.empty(nevents, dtype=object)

    track_id = np.empty(nevents, dtype=object)
    track_pid = np.empty(nevents, dtype=object)
    track_start_time = np.empty(nevents, dtype=object)
    track_energy = np.empty(nevents, dtype=object)
    track_start_position = np.empty(nevents, dtype=object)
    track_stop_position = np.empty(nevents, dtype=object)
    track_parent = np.empty(nevents, dtype=object)
    track_flag = np.empty(nevents, dtype=object)

    trigger_time = np.empty(nevents, dtype=object)
    trigger_type = np.empty(nevents, dtype=object)

    for ev in range(skdetsim.nevent):
        skdetsim.get_event(ev)
        if np.mod(ev, 100)==0:
            print(f'Got event {ev}', flush=True)
        event_info = skdetsim.get_event_info()
        pid[ev] = event_info["pid"]
        if event_info["isConversion"]:
            gamma_start_vtx[ev] = event_info["gamma_start_vtx"]
            electron_direction[ev] = event_info["direction_electron"]
            electron_energy[ev] = event_info["energy_electron"]
            positron_direction[ev] = event_info["direction_positron"]
            positron_energy[ev] = event_info["energy_positron"]
        else:
            gamma_start_vtx[ev]= np.array([-99999,-99999,-99999])
            electron_direction[ev] = np.array([-99999,-99999,-99999])
            electron_energy[ev] = -999
            positron_direction[ev] = np.array([-99999,-99999,-99999])
            positron_energy[ev] = -999
        isConversion[ev] = event_info["isConversion"]
        position[ev] = event_info["position"]
        direction[ev] = event_info["direction"]
        energy[ev] = event_info["energy"]
        primary_charged_range[ev] = -999

        track_pid[ev] = event_info["pid"]
        track_energy[ev] = event_info["energy"]
        track_start_position[ev] = event_info["position"]
        track_stop_position[ev] = event_info["position"]


        digi_hits = skdetsim.get_digitized_hits()
        digi_hit_pmt[ev] = digi_hits["pmt"]
        '''
        for i,pmt_no in enumerate(digi_hit_pmt[ev]):
            if i==0:
                print(f"position: {skgeofile['position'][pmt_no]}, orientation: {skgeofile['orientation'][pmt_no]}")
                digi_hit_pmt_pos[ev] = [(skgeofile['position'][pmt_no])]
                digi_hit_pmt_or[ev] = [(skgeofile['orientation'][pmt_no])]
            else:
                digi_hit_pmt_pos[ev].append((skgeofile['position'][pmt_no]))
                digi_hit_pmt_or[ev].append((skgeofile['orientation'][pmt_no]))
        '''
        digi_hit_charge[ev] = digi_hits["charge"]
        digi_hit_time[ev] = digi_hits["time"]
        digi_hit_trigger[ev] = digi_hits["trigger"]

        #Add fake triggers since we don't get that info in SKDETSIM (yet?)
        trigger_time[ev] = np.asarray([0],dtype=np.float32)
        trigger_type[ev] = np.asarray([0],dtype=np.int32)

        event_id[ev] = ev
        root_file[ev] = infile

    dump_digi_hits(outfile, root_file, radius, half_height, event_id, pid, position, primary_charged_range, isConversion, gamma_start_vtx, direction, energy, electron_energy, electron_direction, positron_energy, positron_direction, digi_hit_pmt, digi_hit_pmt_pos, digi_hit_pmt_or, digi_hit_charge, digi_hit_time, digi_hit_trigger, track_pid, track_energy, track_start_position, track_stop_position, trigger_time, trigger_type, save_tracks=False)

    del skdetsim
    

def dump_digi_hits(outfile, infile, radius, half_height, event_id, pid, position, primary_charged_range, isConversion, gamma_start_vtx, direction, energy, electron_energy, electron_direction, positron_energy, positron_direction, digi_hit_pmt, digi_hit_pmt_pos, digi_hit_pmt_or, digi_hit_charge, digi_hit_time, digi_hit_trigger, track_pid, track_energy, track_start_position, track_stop_position, trigger_time, trigger_type, save_tracks=True):
    """Save the digi hits, event variables

    Args:
        Inputs
    """
    f = h5py.File(outfile+'_digi.h5', 'w')
    print("IN DUMP DIGI HITS", flush=True)

    hit_triggers = digi_hit_trigger
    total_rows = hit_triggers.shape[0]
    event_triggers = np.full(hit_triggers.shape[0], np.nan)
    min_hits=1
    offset = 0
    offset_next = 0
    hit_offset = 0
    hit_offset_next = 0
    total_hits=0
    good_hits=0
    good_rows=0

    for i, (times, types, hit_trigs) in enumerate(zip(trigger_time, trigger_type, hit_triggers)):
        #print(f"i: {i}, times: {times}, types: {types}, hit_trigs: {hit_trigs}")
        good_triggers = np.where(types == 0)[0]
        #print(good_triggers)
        if len(good_triggers) == 0:
            continue
        first_trigger = good_triggers[np.argmin(times[good_triggers])]
        nhits = np.count_nonzero(hit_trigs == first_trigger)
        total_hits += nhits
        #print(f"first trig: {first_trigger}, good_trigger: {good_triggers}, nhits: {nhits}")
        if nhits >= min_hits:
            event_triggers[i] = first_trigger
            good_hits += nhits
            good_rows += 1
    file_event_triggers = event_triggers
    
    dset_labels = f.create_dataset("labels",
                                   shape=(total_rows,),
                                   dtype=np.int32)
    dset_IDX = f.create_dataset("event_ids",
                                shape=(total_rows,),
                                dtype=np.int32)
    dset_PATHS=f.create_dataset("root_files",
                                shape=(total_rows,),
                                dtype=h5py.special_dtype(vlen=str))
    dset_hit_time = f.create_dataset("hit_time",
                                     shape=(good_hits, ),
                                     dtype=np.float32)
    dset_hit_charge = f.create_dataset("hit_charge",
                                       shape=(good_hits, ),
                                       dtype=np.float32)
    dset_hit_pmt = f.create_dataset("hit_pmt",
                                    shape=(good_hits, ),
                                    dtype=np.int32)
    '''
    dset_hit_pmt_pos = f.create_dataset("hit_pmt_pos",
                                    shape=(good_hits, 3),
                                    dtype=np.float32)
    dset_hit_pmt_or = f.create_dataset("hit_pmt_or",
                                    shape=(good_hits, 3),
                                    dtype=np.float32)
    '''
    dset_event_hit_index = f.create_dataset("event_hits_index",
                                            shape=(total_rows,),
                                            dtype=np.int64)  # int32 is too small to fit large indices
    dset_energies = f.create_dataset("energies",
                                     shape=(total_rows, 1),
                                     dtype=np.float32)
    dset_electron_energies = f.create_dataset("energies_electron",
                                     shape=(total_rows, 1),
                                     dtype=np.float32)
    dset_positron_energies = f.create_dataset("energies_positron",
                                     shape=(total_rows, 1),
                                     dtype=np.float32)
    dset_primary_charged_range = f.create_dataset("primary_charged_range",
                                      shape=(total_rows, 1),
                                      dtype=np.float32)
    dset_positions = f.create_dataset("positions",
                                      shape=(total_rows, 1, 3),
                                      dtype=np.float32)
    dset_directions=f.create_dataset("directions",
                                    shape=(total_rows, 1, 3),
                                    dtype=np.float32)
    dset_electron_directions=f.create_dataset("directions_electron",
                                    shape=(total_rows, 1, 3),
                                    dtype=np.float32)
    dset_positron_directions=f.create_dataset("directions_positron",
                                    shape=(total_rows, 1, 3),
                                    dtype=np.float32)
    dset_angles = f.create_dataset("angles",
                                   shape=(total_rows, 2),
                                   dtype=np.float32)
    dset_veto = f.create_dataset("veto",
                                 shape=(total_rows,),
                                 dtype=np.bool_)
    dset_veto2 = f.create_dataset("veto2",
                                  shape=(total_rows,),
                                  dtype=np.bool_)
    dset_gamma_start_vtx = f.create_dataset("gamma_start_vtx",
                                    shape=(total_rows, 1, 3),
                                    dtype=np.float32)
                        

    good_events = ~np.isnan(file_event_triggers)

    offset_next = event_id.shape[0]

    dset_IDX[offset:offset_next] = event_id
    dset_PATHS[offset:offset_next] = infile
    dset_energies[offset:offset_next, :] = energy.reshape(-1, 1)
    dset_electron_energies[offset:offset_next, :] = electron_energy.reshape(-1, 1) 
    dset_positron_energies[offset:offset_next, :] = positron_energy.reshape(-1, 1)
    dset_positions[offset:offset_next, :, :] = position.reshape(-1, 1, 3)
    dset_primary_charged_range[offset:offset_next, :] = primary_charged_range.reshape(-1, 1)
    dset_directions[offset:offset_next, :, :] = direction.reshape(-1, 1, 3)
    dset_electron_directions[offset:offset_next, :, :] = electron_direction.reshape(-1, 1, 3)
    dset_positron_directions[offset:offset_next, :, :] = positron_direction.reshape(-1, 1, 3)

    labels = np.full(pid.shape[0], -1)
    label_map = {13: 0, 11: 1, 22: 2}
    for k, v in label_map.items():
        labels[pid == k] = v
    dset_labels[offset:offset_next] = labels
    dset_gamma_start_vtx[offset:offset_next, :, :] = gamma_start_vtx.reshape(-1, 1, 3)


    polars = np.arccos(direction[:, 2])
    azimuths = np.arctan2(direction[:, 1], direction[:, 0])
    dset_angles[offset:offset_next, :] = np.hstack((polars.reshape(-1, 1), azimuths.reshape(-1, 1)))

    if save_tracks:
        for i, (pids, energies, starts, stops) in enumerate(zip(track_pid, track_energy, track_start_position, track_stop_position)):
            muons_above_threshold = (np.abs(pids) == 13) & (energies > 166)
            electrons_above_threshold = (np.abs(pids) == 11) & (energies > 2)
            gammas_above_threshold = (np.abs(pids) == 22) & (energies > 2)
            above_threshold = muons_above_threshold | electrons_above_threshold | gammas_above_threshold
            outside_tank = (np.linalg.norm(stops[:, (0, 1)], axis=1) > radius) | (np.abs(stops[:, 2]) > half_height)
            dset_veto[offset+i] = np.any(above_threshold & outside_tank)
            end_energies_estimate = energies - np.linalg.norm(stops - starts, axis=1)*2
            muons_above_threshold = (np.abs(pids) == 13) & (end_energies_estimate > 166)
            electrons_above_threshold = (np.abs(pids) == 11) & (end_energies_estimate > 2)
            gammas_above_threshold = (np.abs(pids) == 22) & (end_energies_estimate > 2)
            above_threshold = muons_above_threshold | electrons_above_threshold | gammas_above_threshold
            dset_veto2[offset+i] = np.any(above_threshold & outside_tank)

    for i, (trigs, times, charges, pmts, pmt_pos, pmt_or) in enumerate(zip(hit_triggers, digi_hit_time, digi_hit_charge, digi_hit_pmt, digi_hit_pmt_pos, digi_hit_pmt_or)):
        if np.mod(i, 100)==0:
            print(i, flush=True)
        dset_event_hit_index[offset+i] = hit_offset
        hit_indices = np.where(trigs == event_triggers[i])[0]
        hit_offset_next += len(hit_indices)
        dset_hit_time[hit_offset:hit_offset_next] = times[hit_indices]
        dset_hit_charge[hit_offset:hit_offset_next] = charges[hit_indices]
        dset_hit_pmt[hit_offset:hit_offset_next] = pmts[hit_indices]
        pmt_pos = np.array(pmt_pos)
        pmt_or = np.array(pmt_or)
        #This somehow breaks if there's no PMTs, so skip if that happens
        if hit_offset == hit_offset_next:
            pass
        hit_offset = hit_offset_next

    offset = offset_next
    f.close()

def get_args():
    parser = argparse.ArgumentParser(description='dump sim data into other datasets')
    parser.add_argument('-i', '--input_dir', type=str, default=None)
    parser.add_argument('-f', '--input_file', type=str, default=None)
    parser.add_argument('-o', '--output_dir', type=str, default=None)
    args = parser.parse_args()
    return args

if __name__ == '__main__':

    config = get_args()
    if config.output_dir is not None:
        print("output directory: " + str(config.output_dir))
        if not os.path.exists(config.output_dir):
            print("                  (does not exist... creating new directory)")
            os.mkdir(config.output_dir)
        if not os.path.isdir(config.output_dir):
            raise argparse.ArgumentTypeError("Cannot access or create output directory" + config.output_dir)
    else:
        print("output directory not provided... output files will be in same locations as input files")
        
    if config.input_file is not None:
        print("input file: " + str(config.input_file))
        if not os.path.exists(config.input_file):
            raise argparse.ArgumentTypeError("Cannot access input file" + config.input_file)
        if not os.path.isfile(config.input_file):
            raise argparse.ArgumentTypeError("Cannot access input file" + config.input_file)
        config.input_files = [config.input_file]
    
    if config.input_dir is not None:
        print("input directory: " + str(config.input_dir))
        print("ignore input file as input directory is provided")
        if not os.path.exists(config.input_dir):
            raise argparse.ArgumentTypeError("Cannot access input directory" + config.input_dir)
        if not os.path.isdir(config.input_dir):
            raise argparse.ArgumentTypeError("Cannot access input directory" + config.input_dir)
        config.input_files = [os.path.join(config.input_dir, f) for f in os.listdir(config.input_dir) if os.path.isfile(os.path.join(config.input_dir, f))]

    file_count = len(config.input_files)
    current_file = 0
    

    for input_file in config.input_files:
        if os.path.splitext(input_file)[1].lower() != '.root':
            print("File " + input_file + " is not a .root file, skipping")
            continue
        input_file = os.path.abspath(input_file)

        if config.output_dir is None:
            output_file = os.path.splitext(input_file)[0] # + '.npz'
        else:
            output_file = os.path.join(config.output_dir, os.path.splitext(os.path.basename(input_file))[0]) # + '.npz'

        print("\nNow processing " + input_file)
        print("Outputting to " + output_file)

        dump_file_skdetsim(input_file, output_file)

        current_file += 1
        print("Finished converting file " + output_file + " (" + str(current_file) + "/" + str(file_count) + ")")

    print("\n=========== ALL FILES CONVERTED ===========\n")
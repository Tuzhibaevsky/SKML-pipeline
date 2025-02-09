import ROOT
import os
import numpy as np

directory = "./out/root/tree"
outdir = './out/npy'
outfile = outdir + '/data'
filelist = os.listdir(directory)
os.makedirs(outdir, exist_ok=True)

#filelist = ['gen_id_0k.zbs.root',]

grandData = {}
for infile in filelist:
    all_ent_dir = []
    all_ent_pos = []
    all_Pid_flg = []
    #all_fit_dir = []
    #all_fit_len = []
    
    print(infile)
    inFile = ROOT.TFile.Open(directory+'/'+infile ,"READ")
    chain = inFile.Get('h1')
    for e in chain:
        ent_dir = e.ent_dir
        ent_pos = e.ent_pos
        Pid_flg = e.Pid_flg
        #fit_dir = e.Fit_dir
        #fit_len = e.Fit_len
        
        all_ent_dir.append([d for d in ent_dir])
        all_ent_pos.append([d for d in ent_pos])
        all_Pid_flg.append(Pid_flg)
        #all_fit_dir.append([d for d in fit_dir])
        #all_fit_len.append(fit_len)
    array_ent_dir = np.array(all_ent_dir)
    array_ent_pos = np.array(all_ent_pos)
    # array_ent_dir_len2 = (array_ent_dir**2).sum(axis=1)
    # print(array_ent_dir_len2)
    # problematic = np.argwhere(np.abs(array_ent_dir_len2 - 1) > 0.01).flatten()
    array_Pid_flg = np.array(all_Pid_flg)
    #print(array_Pid_flg)
    #array_fit_dir = np.array(all_fit_dir)
    #array_fit_len = np.array(all_fit_len)


    # if len(problematic) > 0:
    #     print(infile)
    #     print(problematic)
    #     print([array_Pid_flg[each] for each in problematic])
    filenum = infile.split('.')[0].split('_')[-1]
    grandData[filenum] = (all_ent_dir, all_ent_pos, all_Pid_flg)
#print('entry directions\n', array_ent_dir)
#print('entry positions\n', array_ent_pos)
#print('pid flags\n', array_Pid_flg)
# print('fitted directions\n', array_fit_dir)
# print('fitted lengths\n', array_fit_len)
np.save(outfile, grandData)


# print(array_ent_pos.shape)
# rs = np.sqrt(array_ent_pos[:, 0]**2 + array_ent_pos[:, 1]**2)
# zs = array_ent_pos[:, 2]
# print(rs.max(), rs.min(), zs.max(), zs.min())
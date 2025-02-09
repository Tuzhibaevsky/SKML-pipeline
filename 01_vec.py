import numpy as np
import os

n_batch = 2 # Events per file
n_files = 1000 # Number of files
n_offset = 0 # Offset for file numbering

radius = 1684.7 # Other refs: ent_pos 1684.7 OD 1965 #cm
halfz = 1804.7  # Other refs: ent_pos 1804.7 OD 2070 #cm
back_dist = 4000 # Move vertices backwards to avoid 'in-PMT' vertices

MUMASS = 105.6583755 # MeV
LOWLIM = 1600 # MeV
UPLIM = 90_000_000 # MeV

test = False

writedir = './out/vec'
os.makedirs(writedir, exist_ok=True)
rng = np.random.default_rng(seed=514)

def get_nums(n, side_ratio):
    face_val = rng.uniform(0, 1, n)
    face_flg = 1*(face_val < (1-side_ratio)) - 1*(face_val > side_ratio)
    n_top = (face_flg == 1).sum()
    n_barrel = (face_flg == 0).sum()
    n_bottom = (face_flg == -1).sum()
    return n_top, n_barrel, n_bottom

def gen_vecs(n, side=0):
    # positions
    pos_azi = rng.uniform(0, 2*np.pi, n)
    if side == 0:
        pos_zs = rng.uniform(-halfz, halfz, n)
        pos_xs = radius * np.cos(pos_azi)
        pos_ys = radius * np.sin(pos_azi)
    else:
        pos_rsq = rng.uniform(0, radius**2, n)
        pos_rs = np.sqrt(pos_rsq)
        pos_xs = pos_rs * np.cos(pos_azi)
        pos_ys = pos_rs * np.sin(pos_azi)
        if side == 1:
            pos_zs = halfz * np.ones(n)
        else:
            pos_zs = -halfz * np.ones(n)
    poss = np.column_stack((pos_xs, pos_ys, pos_zs))
    
    # directions
    dir_azi = rng.uniform(0, 2*np.pi, n)
    dir_zs = rng.uniform(-1, 1, n)
    dir_xs = np.sqrt(1 - dir_zs**2) * np.cos(dir_azi)
    dir_ys = np.sqrt(1 - dir_zs**2) * np.sin(dir_azi)
    if side == 0:
        out_flg = 2*(np.cos(dir_azi - pos_azi) < 0)-1
        dir_xs = dir_xs * out_flg
        dir_ys = dir_ys * out_flg
    else:
        if side == 1:
            dir_zs = -np.abs(dir_zs)
        else:
            dir_zs = np.abs(dir_zs)

    dirs = np.column_stack((dir_xs, dir_ys, dir_zs))
    
    poss = poss - dirs * back_dist # move back 1mm to avoid self-intersecting
    vecs = np.stack((poss, dirs))
    return vecs.transpose(1, 0, 2)

def gen_energy(n, low=LOWLIM, high=UPLIM): #MeVs
    logs = rng.uniform(np.log(low), np.log(high), n)
    return np.exp(logs)

def gen_particles(n):
    particles = rng.choice([-13, 13], n)
    return particles

def write_one(filename, vecs, energies, particles):
    '''A sample of the output: (Refer to https://webhome.phy.duke.edu/~schol/sk_intro/sk_mc1.html)
    $ begin
    $ vertex -20.2448 -1509.1 -1830.16 0
    $ track 11 0.864735 0.224434 0.660167 -0.0213236 0
    $ end
    '''
    str_b = ' $ begin'
    str_v = ' $ vertex '
    str_t = ' $ track '
    str_e = ' $ end'
    with open(filename, 'w') as f:
        for it in range(n_batch):
            f.write(str_b + '\n')
            f.write(str_v + f'{vecs[it][0][0]} {vecs[it][0][1]} {vecs[it][0][2]} 0\n')
            f.write(str_t + f'{particles[it]} {energies[it]} {vecs[it][1][0]} {vecs[it][1][1]} {vecs[it][1][2]} 0\n')
            f.write(str_e + '\n')
        f.close()

def read_one(filename):
    
    str_b = ' $ begin'
    str_v = ' $ vertex '
    str_t = ' $ track '
    str_e = ' $ end'
    
    # Only supports single particle events as for now,
    #  so time difference can be ignored
    event_count = 0
    positions = []
    directions = []
    particles = []
    energies = []
    in_event = 0
    with open(filename, 'r') as f:
        for line in f:
            assert in_event in [0,1]
            if line == str_b + '\n':
                in_event += 1
                event_count += 1
            elif line == str_e + '\n':
                in_event -= 1
            elif in_event == 1:
                if line.startswith(str_v):
                    positions.append([float(i) for i in line[9:].split()][:3])
                elif line.startswith(str_t):
                    words = line[8:].split()
                    particles.append(int(words[0]))
                    energies.append(float(words[1]))
                    directions.append([float(i) for i in words[2:5]])
        f.close()
    return {
        "count": event_count,
        "positions": positions,
        "directions": directions,
        "particles": particles,
        "energies": energies,
    }

if __name__ == '__main__':

    n = n_batch * n_files
    #a_side = np.pi*radius**2
    #a_barrel = 2*np.pi*radius*2*halfz
    a_ratio = 4*halfz/radius
    side_ratio = 1/(2+a_ratio)
    n_top, n_barrel, n_bottom = get_nums(n, side_ratio)

    vec_top = gen_vecs(n_top, 1)
    vec_barrel = gen_vecs(n_barrel, 0)
    vec_bottom = gen_vecs(n_bottom, -1)
    all_vecs = np.concatenate((vec_top, vec_barrel, vec_bottom))
    rng.shuffle(all_vecs)

    energies = gen_energy(n)
    particles = gen_particles(n)

    if not test: 
        for i in range(n_files):
            print(f'Writing file {i+1}/{n_files}', end='\r')
            i_s = i * n_batch
            i_e = (i+1) * n_batch
            batch_vecs = all_vecs[i_s:i_e]
            batch_energies = energies[i_s:i_e]
            batch_particles = particles[i_s:i_e]
            #subdir = f'{writedir}/{i:03d}'
            #os.makedirs(subdir, exist_ok=True)
            numbering = f'{(i+n_offset):03d}'
            write_one(writedir+f'/vec_{numbering}.dat', batch_vecs, batch_energies, batch_particles)

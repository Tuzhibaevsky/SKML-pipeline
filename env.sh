export CXX=g++
export CPP="gcc -E"
export CC=gcc
export F77=gfortran

export SKOFL_ROOT=/usr/local/sklib_gcc8/skofl_23c
export ATMPD_ROOT=/usr/local/sklib_gcc8/atmpd_23c

export CERN=/usr/local/sklib_gcc8/cern
export CERN_LEVEL=2005
export CERN_ROOT=${CERN}/${CERN_LEVEL}
export NEUT_ROOT=/usr/local/sklib_gcc8/neut_5.4.0.1.rev634.t2ksk

export PATH=${CERN_ROOT}/bin:$PATH

export LD_LIBRARY_PATH=${SKOFL_ROOT}/lib:${ATMPD_ROOT}/bin

export PATH=${SKOFL_ROOT}/bin:${ATMPD_ROOT}/bin:$PATH

export ICONV_DIR=/home/skastro/softwares/libiconv-1.16/build/

source "/home/skastro/softwares/anaconda3/etc/profile.d/conda.sh"
source /home/skastro/softwares/root-6.18.00-build/bin/thisroot.sh
conda activate astro

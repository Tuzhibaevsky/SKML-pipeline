#!/bin/csh -f
uname -a

# Source environment scripts
source /usr/local/sklib_gcc8/cshenv_gcc8_skofl_23c+atmpd_23c+neut_5.6.4

# Set script environment
setenv FLAGDIR $PWD/.cache/conv-root/flag

#set BASEDIR = '/disk03/upmu4/SK6_MC_oct24/water/precisefit'
set BASEDIR = $PWD'/out/root'
set INPUTDIR = $PWD'/out/det/cat'
set HBOOKDIR = $BASEDIR/hbk
set ROOTDIR = $BASEDIR/tree

#set INPUTDIR = /disk01/upmu2/jan2018_mc_17a/SK4/rock/vector
#set HBOOKDIR = /disk03/upmu4/test/hbk
#set ROOTDIR = /disk03/upmu4/test/root

mkdir -p $HBOOKDIR $ROOTDIR

setenv CURDIR `pwd`

foreach file ( `ls $INPUTDIR` )
  # Check lock file
  if ( -e ${FLAGDIR}/$file ) then  
    echo $file 'is locked by other process!'
    continue 
  endif
  if ( -e ${HBOOKDIR}/$file.hbk ) then  
    echo $file 'is already processed!'
    continue 
  endif

  echo 'Starting hbook conversion!' $file

  # Make lock file
  touch  ${FLAGDIR}/$file
  
  $ATMPD_ROOT/src/analysis/official_ntuple/fillnt_simple.sh -o ${HBOOKDIR}/$file.hbk ${INPUTDIR}/$file
  h2root ${HBOOKDIR}/$file.hbk ${ROOTDIR}/$file.root 1 1 0 8000 0

end



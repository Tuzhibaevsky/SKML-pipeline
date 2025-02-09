#!/bin/csh -f

# General setting
set GROUP = all
set FILE = 0
set FILEEND = 2999
set BASEDIR = `pwd`
set INPUTDIR = $BASEDIR/out/vec
set OUTPUTDIR = $BASEDIR/out/det
set RANFILE_PATH = $BASEDIR/out/seeds
set NEUT_ROOT = '/usr/local/sklib_gcc8/neut_5.4.0.1.rev634.t2ksk'
set SKDETSIM_PATH = '/home/upmu/tools/skdetsim-v15p3'


set SLEEPTIME = 10

mkdir -p $OUTPUTDIR/log
mkdir -p $OUTPUTDIR/err
mkdir -p $OUTPUTDIR/zbs

while ( $FILE <= $FILEEND )
    set CURRENT_JOBS = `pjstat | wc -l`
    #echo "Current jobs: $CURRENT_JOBS"

    set LOOPS = 0
    while ( $CURRENT_JOBS >= 300 )
        if ( $LOOPS == 0 ) then
            echo "Current jobs ($CURRENT_JOBS) exceed limit. Waiting..."
        endif
        set LOOPS = `expr $LOOPS + 1`
        set MINS = `expr $LOOPS \* $SLEEPTIME / 60`
        set SECS = `expr $LOOPS \* $SLEEPTIME % 60`
        sleep $SLEEPTIME
        echo "$MINS min $SECS sec..."
        set CURRENT_JOBS = `pjstat | wc -l`
        echo "Current jobs: $CURRENT_JOBS"
    end

    # cd ./masssim/$FILE
    # if( $FILE < 1000 ) then
    #     set sub = `printf "%03d" $FILE`
    # else
    #     set sub = `printf "%04d" $FILE`
    # endif

    set sub = `printf "%03d" $FILE`
    cd $BASEDIR/out/sim/$sub
    echo 'SUB' $sub

    set HERE = `pwd`
    set OUT  = $OUTPUTDIR
    set IN = $INPUTDIR

    set SUBRUN_NUM=`expr $FILE % 13 + 1`
    #echo 'MCSUBRUN=' $SUBRUN_NUM
    set RANFILE = $RANFILE_PATH/random.tbl.$sub #FILE
    set ctr = `printf "%02d" $SUBRUN_NUM`
    #echo `pwd`
    echo '#\!/bin/csh -f' >! ./skdetsim_high_${sub}.${ctr}.sh
    echo "setenv RANFILE " $RANFILE >> ./skdetsim_high_${sub}.${ctr}.sh
    echo "setenv MC_SUBNUM " $SUBRUN_NUM >> ./skdetsim_high_${sub}.${ctr}.sh
    echo "setenv NEUT_ROOT " $NEUT_ROOT >> ./skdetsim_high_${sub}.${ctr}.sh
    cat $SKDETSIM_PATH/skdetsim_high.sh >> ./skdetsim_high_${sub}.${ctr}.sh

    cat > det.$sub.$ctr.sh<<EOF
#!/bin/csh

#PJMScript

#PJM -L "rscgrp=all"
#PJM -L "elapse=2:00:00"
#PJM -e $OUT/err/det_${sub}.err
#PJM -o $OUT/log/det_${sub}.log

source /usr/local/sklib_gcc8/cshenv_gcc8_skofl_23c+atmpd_23c+neut_5.4.0.1

cd $HERE
./skdetsim_high_${sub}.${ctr}.sh sk5_official.card $OUT/zbs/skdetsim_${sub}.zbs $IN/vec_${sub}.dat
EOF

    chmod +x det.$sub.$ctr.sh
    chmod +x skdetsim_high_$sub.$ctr.sh
    pjsub -L rscgrp=$GROUP det.$sub.$ctr.sh
    cd $BASEDIR
    set FILE=`expr $FILE + 1`
end

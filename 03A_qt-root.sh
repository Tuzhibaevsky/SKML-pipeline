#!/bin/csh -f

set SLEEPTIME = 5
set FILESTART = 0
set FILEEND = 9

set MODE = ''

# set MODE = $1
# if (-z $MODE) then
#     set MODE = QE
# endif

set i = $FILESTART
mkdir -p .cache
mkdir -p .errs
mkdir -p .logs

set WD = `pwd`
set INDIR = $WD'/out/det/cat/'
set OUTDIR = $WD'/out/qt/'
set INPREFIX = 'cat_'

mkdir -p $OUTDIR

while ( $i <= $FILEEND )
    set istr = `printf "%03d" $i`
    #"%03d"
    set CURRENT_JOBS = `pjstat | wc -l`
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
    set COPYSH = .cache/QT_job_$MODE.$istr.sh
    echo $istr
    echo '#\!/bin/bash' >! $COPYSH
    echo '#PJM -L "rscgrp=all"' >> $COPYSH
    echo '#PJM -e ./.errs/QTjob.'$MODE$istr >> $COPYSH
    echo '#PJM -o ./.logs/QTjob.'$MODE$istr >> $COPYSH
    echo 'ISTR='$istr >> $COPYSH
    echo 'MODE='$MODE >> $COPYSH
    echo 'INDIR='$INDIR >> $COPYSH
    echo 'OUTDIR='$OUTDIR >> $COPYSH
    echo 'INPREFIX='$INPREFIX >> $COPYSH
    echo 'INSUFFIX=.zbs' >> $COPYSH #_$MODE.rock.zbs.detsim.umred2
    echo 'OUTSUFFIX=.root' >> $COPYSH #_$MODE.root
    echo 'EXECDIR='$WD'/zbs2root/' >> $COPYSH
    cat ./_03A_qt-root_job.sh >> $COPYSH
    pjsub $COPYSH
    set i = `expr $i + 1`
end

#clean up
set UNFINISHED = `pjstat | grep "QT_job_$MODE" | wc -l`
while ( $UNFINISHED > 0 )
    echo "Waiting for $UNFINISHED jobs to finish..."
    sleep 3
    set UNFINISHED = `pjstat | grep "QT_job_$MODE" | wc -l`
end
echo "All jobs finished, cleaning up..."
rm .cache/QT_job_$MODE.*.sh
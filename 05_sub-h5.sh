#!/bin/bash

SLEEPTIME=5

INDIR=$PWD/out/qth5/
OUTDIR=$PWD/out/subh5/
NPYFILE=$PWD/out/npy/data.npy

mkdir -p $OUTDIR

for FILE in $INDIR/*
do
    FILENAME=$(basename -s .h5 $FILE)
    echo $FILENAME
    CURRENT_JOBS=`pjstat | wc -l`
    LOOPS=0
    while [ $CURRENT_JOBS -ge 500 ]
    do
        if [ $LOOPS -eq 0 ]; then
            echo "Current jobs ($CURRENT_JOBS) exceed limit. Waiting..."
        fi
        LOOPS=`expr $LOOPS + 1`
        MINS=`expr $LOOPS \* $SLEEPTIME / 60`
        SECS=`expr $LOOPS \* $SLEEPTIME % 60`
        sleep $SLEEPTIME
        echo "$MINS min $SECS sec..."
        CURRENT_JOBS=`pjstat | wc -l`
        echo "Current jobs: $CURRENT_JOBS"
    done    

    COPYSH=.cache/sub-h5.$FILENAME.sh
    echo '#!/bin/bash' > $COPYSH
    echo '#PJM -L "rscgrp=all"' >> $COPYSH
    echo '#PJM -e ./.errs/sub-h5.'$FILENAME >> $COPYSH
    echo '#PJM -o ./.logs/sub-h5.'$FILENAME >> $COPYSH
    echo 'FILE='$FILE >> $COPYSH
    #echo 'INDIR='$INDIR >> $COPYSH
    echo 'OUTDIR='$OUTDIR >> $COPYSH
    echo 'NPYFILE='$NPYFILE >> $COPYSH
    cat ./_05_sub-h5_job.sh >> $COPYSH
    pjsub $COPYSH
done

#clean up
UNFINISHED=`pjstat | grep "sub-h5" | wc -l` 
while [ $UNFINISHED -gt 0 ]
do
    echo "Waiting for $UNFINISHED jobs to finish..."
    sleep 10
    UNFINISHED=`pjstat | grep "sub-h5" | wc -l`
done
echo "All jobs finished, cleaning up..."
rm .cache/sub-h5.*.sh
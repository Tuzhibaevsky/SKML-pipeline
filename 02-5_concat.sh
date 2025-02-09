#!/bin/bash

outfolder=./out/det/cat/
infolder=./out/det/zbs/
ni=0
nf=999
perfile=100

for num in $(seq $ni $nf)
do
    fnum=$(printf "%03d" $num)
    infile=$infolder'/skdetsim_'$fnum'.zbs'
    onum=$(printf "%03d" $((num/perfile)))
    outfile=$outfolder'/cat_'$onum'.zbs'

    if [ ! -d $outfolder ]
    then
        mkdir $outfolder
    fi

    if [ ! -e $infile ]
    then
        echo $infile missing, making dummy empty input
        touch $infile
    fi

    if [ $((num%perfile)) -eq 0 ]
    then
        echo Writing to out file $onum
        printf '%03d ' $num
        cat $infile > $outfile
    else
        printf '%03d ' $num
        cat $infile >> $outfile
    fi
done
#!/bin/bash

jobs=`pjstat | grep det | wc -l`
if [ $jobs -ne 0 ]
then
    echo "There are still $jobs detsim jobs running. Please check again later, as unfinished ones will be regarded as bad outputs."
    read -p "Or do you want to continue now? (y/n) " -n 1 -r
    case $REPLY in
        Y | y)
            echo
            ;;
        N | n)
            echo
            exit 1
            ;;
        *)
            echo
            echo "Invalid input. Exiting."
            exit 2
            ;;
    esac
fi

#First read all error files:
OUTPUTDIR=./out/det
ni=0
nf=999

echo "***ERROR FILES***"
# Check error files, only print
for num in $(seq $ni $nf)
do
    fnum=$(printf '%03d' $num)
    file=$OUTPUTDIR"/err/det_$fnum.err"
    printf $file
    if [ -s $file ]
    then
        printf ' Error\n'
    else
        if [ -e $file ]
        then
            printf ' Empty\n'
            rm $file
        else
            printf ' NotExist\n'
        fi
    fi
done

# Check log files, print + record
echo "***LOG FILES***"

echo "# BAD OUTPUTS" > $OUTPUTDIR/bad_outputs
for num in $(seq $ni $nf)
do
    fnum=$(printf '%03d' $num)
    file=$OUTPUTDIR"/log/det_$fnum.log"
    if [ -s $file ]
    then
        printf $file
        kwd=$(tail -n 1 $file | cut -d' ' -f5)
        if [ "$kwd" = "SYSTEM" ]
        then
            rm $file
            printf ' Good\n'
        else
            printf ' Bad\n'
            echo $fnum >> $OUTPUTDIR/bad_outputs
        fi
    else
        printf $file
        printf ' NoLog\n'
        if [ -e $file ]
        then
            rm $file
        fi
    fi
done

# Read from Record file and delete
lines=$(cat $OUTPUTDIR/bad_outputs)
for line in $lines
do
    if [ ${line:0} == "#" ]
    then
        continue
    fi

    if [ -z $line ]
    then
        continue
    fi

    if [ -e $OUTPUTDIR"/zbs/skdetsim_"$line".zbs" ]
    then
        rm $OUTPUTDIR"/zbs/skdetsim_"$line".zbs"
        echo "Deleted: skdetsim_"$line".zbs"
    fi

done


#source ~/env.sh
cd $EXECDIR

#filenum=`basename -s $INSUFFIX $infile | sed "s/$INPREFIX//"`
filenum=$ISTR
infile=$INDIR$INPREFIX$filenum$INSUFFIX
echo $filenum
if [ ! -f $infile ]; then
    echo "File $infile does not exist."
    exit 1
fi
read_zbs $infile $OUTDIR$filenum$OUTSUFFIX

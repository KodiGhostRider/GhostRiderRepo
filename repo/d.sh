for i in `echo *` ; do
cd $i 
echo *.zip|tr " "  "\n" |sort -n |head -n -1|xargs rm -rf 
cd -
pwd
done

#!/bin/bash -x
#alias python=python3
cd /opt/GhostRider
#git pull origin master
git pull
python3.4  new_xml_gen.py
sleep 7
git add *
git commit -a -m "update push in : `date`"
git push 

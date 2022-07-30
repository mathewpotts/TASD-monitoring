#!/bin/bash

DS=$1

if [ -z "$DS" ]
then
	read -p "SD data set you want to transfer : " DS
fi

yr=${DS:4:2}

while true; do
	echo
        read -p "Transfer $DS to tadserv at the UofU? (y/n) " yn
        case $yn in
        	[Yy]* ) break;;
                [Nn]* ) echo;read -p "SD data set you want to transfer : " DS;;
                * ) echo;echo "Please answer y or n.";;
        esac
done

/usr/bin/rsync -Pau /home/sdsys/outerdisk/$DS tamember@tadserv.physics.utah.edu:/pool02/tadserv5/tasd/TASD$yr/

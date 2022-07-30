#!/bin/bash

#Script for sending SD maintenance files to blm. Mathew Potts 20200816

# usage: ./import_to_blm.sh {pass}

# Requirments: need photos and files in directory.
# sshpass is also required

# Steps :
# 0) transfer files from gps 
# 1) rename all photos
# 2) open a feild check list for all sds
# 3) scp them to blm

# Open photo and name it
# .... repeat
# using xdg-open <file>

read -p "Date of maintinance (i.g. YYYYMMDD): " date 
maintinance_dir=~/sd_maintinance/$date

echo "Uploading files from : $maintinance_dir"
echo
for file in $maintinance_dir/*; do
    echo
    echo "Opening $file..."
    # If files have GV
    if [[ ${file: -4} == ".jpg" ]] ; then
	xdg-open $file
	echo
	read -p "SD NUMBER (e.g. SD1413) : " sd_num
	wait
	new_filename="$maintinance_dir/${sd_num}_${date}_GV.jpg"
	echo
	
	while true; do
	    echo
	    read -p "Rename $file -> $new_filename? (y/n) " yn
	    case $yn in
		[Yy]* ) break;;
		[Nn]* ) echo;read -p "SD NUMBER (e.g. SD1413) : " sd_num;new_filename="$maintinance_dir/${sd_num}_${date}_GV.jpg";;
		* ) echo;echo "Please answer y or n.";;
	    esac
	done
	
	echo
	mv $file $new_filename
	pic="sshpass -p 'tinctoria' scp $new_filename blm@www.telescopearray.org:SDs/${sd_num}/."
	echo $pic
	$pic
	echo

	wget "http://telescopearray.org/tawiki/images/4/4d/Field_Checklist.doc" -P $maintinance_dir &>/dev/null
	FC="$maintinance_dir/Field_Checklist.doc"
	xdg-open $FC
	echo "Please fill out check list and save it."
	wait
	new_filename="$maintinance_dir/${sd_num}_${date}_FC.doc";
	echo

	while true; do
	    read -p "Rename $FC -> $new_filename? (y/n) " yn
	    case $yn in
		[Yy]* ) break;;
		[Nn]* ) xdg-open $FC;;
		* ) echo "Please answer y or n.";;
	    esac
	done

	mv $FC $new_filename
	echo
	lowriter --convert-to pdf $maintinance_dir/*.doc --outdir $maintinance_dir/
	checklist="sshpass -p 'tinctoria' scp $maintinance_dir/${sd_num}_${date}_FC.pdf blm@www.telescopearray.org:SDs/${sd_num}/."
	echo $checklist
	$checklist
	echo
	
	wait
    fi
    
    # If files have gps
    if [ ${file: -4} == ".gpx" ] ; then
	mkdir $maintinance_dir/$date
	new_filename="$maintinance_dir/TRK_${date}.gpx"
	mv $file $new_filename
	mv $new_file $maintinance_dir/$date
	gpx_dir=$maintinance_dir/$date
	gps="sshpass -p '$1' scp -r $gpx_dir blm@www.telescopearray.org:GPS_Track_Files/."
	echo $gps
	$gps
    fi
    
done

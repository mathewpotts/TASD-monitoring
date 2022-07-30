#!/usr/bin/env python3

######################################################################################################
##                                                                                                  ##
## Purpose: Extract, Transform, and Load (ETL) SD access list to crcpc00 then ssh into crcpc00      ##
## Author:  Mathew Potts                                                                            ##
## Updated: 2021-11-2                                                                               ##
## Version: 2.6                                                                                     ##
## Requirments: sshpass (sudo apt-get install sshpass)                                              ##
##              FOR PYTHON3-                                                                        ##
##              python3-bs4 (sudo apt-get install python3-bs4)                                      ##
##              python3-requests (sudo apt-get install python3-requests)                            ##
##              FOR PYTHON2-                                                                        ##
##              sudo python -m pip install BeautifulSoup                                            ##
##              sudo python -m pip install requests                                                 ##
##                                                                                                  ##
######################################################################################################
## IMPORT LIBS

import sys
import os
import argparse
import datetime as dt
import re
try:
    import requests
    from bs4 import BeautifulSoup as bs
except:
    sys.exit("ERROR: Datascrapper requires BeautifulSoup4 & Requests. Please install...")
    
######################################################################################################
## CLASSES

## GET_ACCESSLIST
class GET_ACCESSLIST:
    '''
    This function is executed when the GET_ACCESSLIST class is called. It checks the date to get the right URL and uses the python requests library to 'scrape' the access list off the wiki. Once the request is made the status of the request is check and if is bad (ex. the server is unavailble) it exit the program with error.
    '''
    def __init__(self,month,year,pw):
        mn_str = str(month)
        yr_str = str(year)
        if month < 10:
            self.url = "http://www.cosmicray-ocu.jp/tafdwiki/index.php?SDmaintenance%20"+yr_str+"%2F0"+mn_str
        elif month >= 10:
            self.url = "http://www.cosmicray-ocu.jp/tafdwiki/index.php?SDmaintenance%20"+yr_str+"%2F"+mn_str
        page = requests.get(self.url,auth=('tamember',pw[1]))
        try:
            page.raise_for_status()
        except requests.exceptions.HTTPError as e:
            sys.exit("ERROR: {}".format(e))
            
        self.soup = bs(page.text,'html.parser')

    '''
    This function checks the part of the list for anything that doesn't match the 'pattern' of the access list (i.e. SK 1234 - 20191217 - Explaination...) then prints it to a text file that is sent to the crcpc00. This checking helps when people add DAQ towers to the access list which are not need to cross check when doing SD monitoring. It will also help when someone puts an \n before information containted in the access lsit by removing it.
    '''
    def bs4_to_file(self,idx,filename,file_option):
        cut_tmp_list = []
        tmp_list = re.split('\n+(?=\w+\s\d+)',self.soup.find_all('pre')[idx].get_text())
        for entry in tmp_list:
            match = re.match('\w+\s\d+',entry)
            if match:
                cut_tmp_list.append(entry)
        outfile = open(filename,file_option)
        outfile.writelines('\n'.join(cut_tmp_list)+'\n')
        outfile.close()

                            
######################################################################################################
## FUNCTIONS

'''
This is the main function that is called when the user wants the access list 'scraped' from the wiki. It calls the GET_ACCESSLIST class and assigns a index to each list currently present on the wiki. These indexs represent the html pre tag index. These lists are then combined to larger lists (combined_list, nomon_list, nocheckerror_list) depending on which SD section need to cross checked and which can be ignored during SD monitoring. This cross checking is handled on crcpc00. Then the bs4_to_file function is called from the GET_ACCESSLIST class to write the text file.
'''
def get_accesslist_main(pw):
    get_al = GET_ACCESSLIST(dt.datetime.now().month,dt.datetime.now().year,pw)
    accesslist = 0
    futurelist = 1
    oktoleave = 2
    sunsaver_HV = 3
    badlocation = 4
    nomonit = 5
    combined_list = [accesslist,futurelist,oktoleave,sunsaver_HV,badlocation,nomonit]
    nomon_list = [oktoleave,nomonit]
    nocheckerror_list = [sunsaver_HV,badlocation,oktoleave,nomonit]
    all_lists = [combined_list,nomon_list,nocheckerror_list]
    for list in all_lists:
        for x in list:
            if x == accesslist:
                get_al.bs4_to_file(x,'accesslist_raw_str.txt','w')
            else:
                get_al.bs4_to_file(x,'accesslist_raw_str.txt','a')
        if list != nocheckerror_list:
            os.system('printf "\n---\n" >> accesslist_raw_str.txt')

'''
Small function that is used to ask the user for a yes or no input. On a invalid entry the question will be asked again. 
'''
def ask_user(question):
    # Checking version of python for which version fo input to use
    ver = sys.version[:1]
    if ver == '2':
        check = raw_input(question + " (y/n): ")
    else:
        check = input(question + " (y/n): ")
    # Ask question
    if check[:1] == 'y' or check[:1] == 'Y':
        return True
    elif check[:1] == 'n' or check[:1] == 'N':
        return False
    else:
        print('Invalid Input')
        return ask_user(question)

'''

'''
def read_in_args():
    parser = argparse.ArgumentParser(description = 'TA SD Monitoring Log-in Script. ETL the access list on the wiki to the crcpc00 for SD error cross-checking.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-pw',metavar='password',nargs=3,action='store',help='Passwords for Charon and CRC repectively. (Example -pw CharonPass OCUwikiPass CRCloginPass)')
    group.add_argument('-i',metavar='infile',action='store',help='ASCII file with one password per line. In the same order as the -pw flag.')
    args   = parser.parse_args()
    pw     = args.pw
    infile = args.i
    if infile != None and os.path.exists(infile):
        #read text file
        f=open(infile,"r")
        lines=f.readlines()
        pw1 = lines[0][:-1]
        pw2 = lines[1][:-1]
        pw3 = lines[2][:-1]
        pw  = [pw1,pw2,pw3]
        #print(pw)
        return pw
    else:
        #print(pw)
        return pw 


def main():
    pw = read_in_args()
    # Calls the ask_user function on true scrap access list and scp it to crcpc00
    check = ask_user("Do you want to transfer access list to crcpc00?")
    if check == True:
        print('\nRunning Datascrap of Access List...')
        get_accesslist_main(pw)
        print('\nSending Access list to crcpc00...')
        os.system('sshpass -p "{0}" scp -o StrictHostKeyChecking=no accesslist_raw_str.txt sdsys@205.197.210.166:~/'.format(pw[2]))
        os.system('rm accesslist_raw_str.txt')
        
    # If ask_user is false just connect to crcpc00
    print('\nConnecting to crcpc00...\n')
    os.system('''sshpass -p "{0}" ssh -Y -o StrictHostKeyChecking=no hires@155.101.14.10 -t "ssh -Y -l sdsys 205.197.210.166 -t 'ssh -Y crcpc00'"'''.format(pw[0]))
    print('\nGood Bye... Come again soon...\n')

#######################################################################################################
## PROGRAM

if __name__ == "__main__":
    main()
    
        


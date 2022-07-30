#!/usr/bin/env python
#coding: utf-8

from __future__ import absolute_import, division, with_statement
import datetime
import os
import re


def highlight(a_str, font_weight='01;95m', csi="\x1B["):
    return csi + font_weight + a_str + csi + '0m'


# CheckNow
class CheckNow(object):
    def __init__(self, checknow_path, tower_name_abbrs):
        self.checknow_path = checknow_path
        self.tower_name_abbrs = tower_name_abbrs
        print ('''\
_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/
Display the detector numbers with warning in "sdshift" output.
Please cut&paste the detector numnbers to fill out the sdshift check log.
---------------------------------------------------------------------------''')

    def display_info(self, tname, needed, switch=0):
        checknow_file = self.checknow_path + 'checknow_' + tname + '.txt'

        try:
            tower_abbr = self.tower_name_abbrs[tname]
        except KeyError:
            print 'Unknown tower!!!'

        tower_name_uppercase = tname[0:2].upper()

	try:
            with open(checknow_file) as checknow:
                if needed == 'time':
                    print tower_name_uppercase, 'time: ',
                    for line in checknow:
	                if (len(line.split()) == 8 and re.search(tower_abbr + r'.*', line)):
	                    print line,
            	elif needed == 'commErrors':
                    for line in checknow:
                    	fields = line.split()
                    	if len(fields) == 4 and fields[3] == '5':
                            print highlight(tower_name_uppercase+fields[0]),
                       	    comm.append(tower_name_uppercase+fields[0]) # Fill comm error list
                       	    switch = 1
            	elif needed == 'secnumErrors':
                    for line in checknow:
                    	fields = line.split()
                    	if len(fields) == 4 and int(fields[1]) > 1:
                            print highlight(tower_name_uppercase+fields[0]),
                            secnum.append(tower_name_uppercase+fields[0]) # Fill secnum error list
                            switch = 1
            	elif needed == 'trigErrors':
                    for line in checknow:
                    	fields = line.split()
                    	if len(fields) == 4 and int(fields[2]) > 1:
	                    print highlight(tower_name_uppercase+fields[0]),
        	            trig.append(tower_name_uppercase+fields[0]) # Fill trig error list
                	    switch = 1
            	else:
                    print 'Unknown Info!!!'
                if switch:
                    print
        except Exception:
            print(checknow_file + " not FOUND!! Tower is down.")

def display_wrapper(a_fun, needs_title_str, p_str=''):
    fields = re.split(r'(\s|\()', needs_title_str)
    arg = needs_title_str if len(fields) == 1 else fields[4]
    if arg != needs_title_str:
        print highlight(needs_title_str, '01;31;40m')
        for name in TOWER_NAME_ABBRS.keys():
            a_fun(name, arg)
    else:
        for name in TOWER_NAME_ABBRS.keys():
            a_fun(name, arg)
    print p_str


# SIMPLEWARNINGS
class Simplewarning(object):
    def __init__(self, yesterday):
        self.yesterday = yesterday

    def getwarning(self):
        for tname in ['SK', 'BR', 'LR']:
            os.system(' '.join(['/home/sdsys/sdshift/getwarning', self.yesterday, tname, '>',tname+'_warning.tmp']))

    def display(self):
        # Replace with class internal method!!!
        def extract(warning_file, warning_type, pattern_str, field2print):
            err_dets = {'SK': [], 'BR': [], 'LR': [], 'MD': []}
            err_dets_keys = err_dets.keys()

            pattern = re.compile(pattern_str)
            print highlight(warning_type, '01;31;40m')
            DET_pattern = re.compile(r'DET(\d{4})')

            for prefix in err_dets_keys:
                with open(prefix+'_'+warning_file) as f_obj:
                    for line in f_obj:
                        if pattern.search(line):
                            err_dets[prefix].append(DET_pattern.sub(prefix+r'\g<1>', line))

            for ls_name in err_dets_keys:
                if err_dets[ls_name]:
                    for line in err_dets[ls_name]:
                        print highlight(line.split()[field2print]),
                        if warning_type == ' * GPS Number : ': # append detectors to appropriate error arrays 
                            gpsnum.append(line.split()[field2print])
                        if warning_type == ' * GPS Operation Mode Error: ':
                            gpsmode.append(line.split()[field2print])
                        if warning_type == ' * Battery Voltage (High Voltage): ':
                            batthigh.append(line.split()[field2print])
                        if warning_type == ' * Battery Voltage (Low Voltage) : ':
                            battlow.append(line.split()[field2print])
                        if warning_type == ' * Solar Voltage (High Voltage) : ':
                            solhigh.append(line.split()[field2print])
                        if warning_type == ' * Solar Voltage (Low Voltage) : ':
                            sollow.append(line.split()[field2print])
                        if warning_type == ' * Pedestal Level : ':
                            ped.append(line.split()[field2print])

                    print

            for ls_name in err_dets_keys:
                if err_dets[ls_name]:
                    print ''.join(err_dets[ls_name]).strip()
            print


        print '_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/'
        print 'Display all warnings of SK, BR, LR, and MD occured YESTERDAY.'
        print 'Please cut and paste the detector numnbers to fill out the sdshift check log.'
        print '---------------------------------------------------------------------------'
        print '" Date '+self.yesterday+'", All warnings'
        print '---------------------------------------------------------------------------'


        extract('warning.tmp', ' * GPS Number : ', 'dgps', 1)
        extract('warning.tmp', ' * GPS Operation Mode Error: ', 'GPS operation mode error', 1)
        extract('warning.tmp', ' * Battery Voltage (High Voltage): ', 'High battery voltage', 1)
        extract('warning.tmp', ' * Battery Voltage (Low Voltage) : ', 'Low battery voltage', 1)
        extract('warning.tmp', ' * Solar Voltage (High Voltage) : ', 'High solar voltage', 1)
        extract('warning.tmp', ' * Solar Voltage (Low Voltage) : ', 'Low solar voltage', 1)
        extract('warning.tmp', ' * Pedestal Level : ', 'Low Pedestal', 1)

        print '---------------------------------------------------------------------------'

# CrossCheck added with work from Isaac Buckland and Mathew Potts
class CrossCheck(object):
    def __init__(self,accesslist_path):
	self.date = os.popen("date +'%b %-d'").read()
	self.check_accesslist_file()
        self.al_list = open(accesslist_path,"r").read()
        self.al_last_transfer_date = os.popen("ls -l %s | awk '{print $6\" \"$7}'" % accesslist_path).read()
        self.list_types = {
	    'al':[],
	    'ok':[],
	    'no':[]
        }
        self.list_types_order=['al','ok','no'] 
        self.list_types_cut = {
	    'al_cut':[],
	    'ok_cut':[],
	    'no_cut':[]
        }
        self.error_keys=['comm','gps','batt']
        
        ################# ADD KEY WORDS IF NEEDED #################
        self.error_dict={        
	    'comm':['antenna','LAN cable','signal','communicating','communication','communicate','offline','onsite reboot','reboot onsite','high comerr','trigger','pedestal'],
            'gps':['gps'],
            'batt':['battery','solar','CC']
        }
        ###########################################################
        
        self.reference_dict={
            'comm':[],
            'gps':[],
            'batt':[]
        }
        self.comm_errtypes = ['comm','trig','ped']
        self.gps_errtypes = ['secnum','gpsnum','gpsmode']
        self.batt_errtypes = ['batthigh','battlow','solhigh','sollow']

    def parse_al(self):
        al_list = self.al_list.split('\n---\n')
        idx=0
        for type in self.list_types_order:
	    self.list_types[type] = re.compile("\n+(?=[SK|BR|LR])").split(al_list[idx]) 
	    idx+=1
        for type in self.list_types_order:
	    for entries in range(len(self.list_types[type])):
		#print(entries)
		self.list_types_cut[type + '_cut'].append(re.match(r"^\w+\s\d+",self.list_types[type][entries]).group().replace(' ',''))
        for key in self.error_keys:
    	    for key_words in self.error_dict[key]:
    		for entries in range(len(self.list_types['al'])):
    		    if re.search(key_words,self.list_types['al'][entries],re.IGNORECASE):
    			result = re.match(r"(^\w+)\s\d+",self.list_types['al'][entries]).group()
    			self.reference_dict[key].append(result.replace(' ',''))
        for key in self.error_keys:
            for x in vars(self)[key+'_errtypes']:
                vars(self)['new_' + x] = [det for det in globals()[x] if det not in self.reference_dict[key] and det not in self.list_types_cut['no_cut']]

    def display_CrossCheck(self):
        for x in errtypes:
	    print
    	    print '---------------------------------------------------------------------------'
   	    if x != 'battlow' and x != 'batthigh' and x != 'solhigh':
    	        print(highlight('new ' + x + ' error:','01;31;40m'))
		if vars(self)['new_' + x] != []:
		    for y in vars(self)['new_' + x]:
		        print highlight(y),
		else:
		    print highlight('No errors today','01;32;40m'),
	    elif x=='battlow' or x=='batthigh' or x=='solhigh':
 		print highlight('all ' + x + ' errors: *may already be on access list','01;31;40m')
		if globals()[x] != []:
		    for y in globals()[x]:
			if y != 'SK2423': # not a detector
			    sdnum = y[:2] + ' ' + y[2:]
			    log_entry = [entry for entry in self.list_types['al'] if sdnum in entry]
			    if len(log_entry) > 0: # the list will only have entries if they are on the access list already
		            	print highlight('\n*' + log_entry[0],'01;33;40m')
			    else:
				print highlight(y),
		else:
		    print highlight('No errors today','01;32;40m'),
        print highlight('\n\nPress enter to continue.','01;31m')
        os.system('read gonext')

    def may_have_recovered(self):
        all_errors = list(set(comm+secnum+trig+gpsnum+gpsmode+batthigh+battlow+solhigh+sollow+ped))
        no_error = [det for det in self.reference_dict['comm'] + self.reference_dict['gps'] + self.reference_dict['batt'] if det not in all_errors]
        no_error = list(dict.fromkeys(no_error))    
        print '\n---------------------------------------------------------------------------'
        print "Detectors on access list with no error today, may have recovered. Please check plots:\n"
        for det in no_error:
	    if det not in self.list_types_cut['no_cut']:
		sdnum = det[:2] + ' ' + det[2:]
		for entries in range(len(self.list_types['al'])):
		    if re.search("%s(?!.*replace)"%sdnum,self.list_types['al'][entries],re.IGNORECASE): #add another condition for replace
        		print highlight(self.list_types['al'][entries],'01;32;40m') + highlight('\n ^ http://www.icrr.u-tokyo.ac.jp/~tamember/towermonitor/DET'+ sdnum[3:] 
+'/thissd.jpg \n','01;34m')
			os.system('read gonext')

    def check_accesslist_file(self):
	print '\n---------------------------------------------------------------------------\n'
	print 'Grabbing accesslist lastest from crclogin...'
        os.system('rsync -Pauv sdsys@crclogin:~/accesslist_raw_str.txt ~/sdshift/')
	self.al_last_transfer_date = os.popen("ls -l %s | awk '{print $6\" \"$7}'" % accesslist_path).read()
        print 'ACCESS LIST TRANSFER DATE: %s' % self.al_last_transfer_date
        if self.al_last_transfer_date != self.date:
	    print highlight('ACCESS LIST IS OUT OF DATE!! CROSS CHECK MAY NOT BE ACCURATE!!\n','01;31m')
	    print highlight('Please transfer updated list. End program.','01;31m')
	    #print highlight('\n\nPress enter to continue.','01;31m')
	    #os.system('read gonext')
	    exit(1)
        print '---------------------------------------------------------------------------'


if __name__ == '__main__':

    # Initiate arrays of error lists that are filled in the CheckNow and SimpleWarning classes
    errtypes = ['comm','secnum','trig','gpsnum','gpsmode','batthigh','battlow','solhigh','sollow','ped']
    for errname in errtypes:
        vars()[errname] = []
        
    # CheckNow
    CHECKNOW_PATH = '/home/sdsys/datatrans/log/'
    TOWER_NAME_ABBRS = {'sk': 'sk', 'brm': 'br', 'lr': 'lr'}
    txt_sep = '-' * 75
    checknow_warnings = CheckNow(CHECKNOW_PATH, TOWER_NAME_ABBRS)

    title = '- All(SK/BR/LR) errors are summarized as follows:'
    display_wrapper(checknow_warnings.display_info, 'time', txt_sep+'\n'+title)
    display_wrapper(checknow_warnings.display_info, ' * commErrors(5) : ')
    display_wrapper(checknow_warnings.display_info, ' * secnumErrors(>=1) : ')
    display_wrapper(checknow_warnings.display_info, ' * trigErrors(>=1) : ','\n'+txt_sep)

    print(highlight('Press enter to continue.','01;31;40m'))
    os.system('read gonext')

    # SimpleWarning
    YESTERDAY = (datetime.date.today() - datetime.timedelta(1)).__str__()

    today_simplewarning = Simplewarning(YESTERDAY)
    today_simplewarning.getwarning()
    today_simplewarning.display()

    print('\n'+highlight('Press enter to continue.','01;31m'))
    os.system('read gonext')

    # CrossCheck
    accesslist_path ='/home/sdsys/sdshift/accesslist_raw_str.txt'
    
    CrossCheck=CrossCheck(accesslist_path)
    CrossCheck.parse_al()
    CrossCheck.display_CrossCheck()
    CrossCheck.may_have_recovered()

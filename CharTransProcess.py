#!/usr/local/python/bin/python
#-*- coding: iso-8859-15 -*-


##############################################################################
### NZBGET POST-PROCESSING SCRIPT                                          ###

# Fixed filenames encoding issue for Synology NAS.
#
# If a file has been archieved under an ISO-8859 environment and unarchived
# under an UTF8 environment, then you will get an encoding format
# problem. The file will not be readable through SAMBA.
#
# Renaming script for NZBGet runnning under Synology NAS. By default 
# the NZB software is running under UTF-8 encoding format
# in order to correctly handle the french accents (éèàç...) a NZBGet
# post-script must be run in order to convert the file encoding.
#
# To fix this problem, you must convert the encoding format
# to the UTF8 (default Synology encoding). The script is trying to detect
# if the original file/directory are coming from a RAR archive. In this
# case the unrar command on your Syno system will unpack in CP850 format (DOS).
#
# NB: in all cases, files will be readable through samba, even if the detection
# failed. But converted characters will not be good, ex: Î? instead é.
#
# Author: LapinFou
# Forum discussion: http://nzbget.sourceforge.net/forum/viewtopic.php?f=3&t=829&hilit=characters&sid=e7bb0da02a6d387073917e79140246e1#p4935
# Version: 1.0 (release date: 2013-11-03).
#
# Special Thanks to: Andrey Prygunkov (nzbget@gmail.com).
#
# NOTE: This script requires SynoCommunity Python to be installed on your system.
#
# NOTE: The script doesn't have any configuration options.

### NZBGET POST-PROCESSING SCRIPT                                          ###
##############################################################################


# get library modules
import sys
import os
import subprocess
import shutil

#######################################################################
# NZBGET - BEGIN

# Exit codes used by NZBGet
POSTPROCESS_SUCCESS=93
POSTPROCESS_NONE=95
POSTPROCESS_ERROR=94

# Check if the script is called from nzbget 11.0 or later
if not 'NZBOP_SCRIPTDIR' in os.environ:
	print('*** NZBGet post-processing script ***')
	print('This script is supposed to be called from nzbget (11.0 or later).')
	sys.exit(POSTPROCESS_ERROR)

if not os.path.exists(os.environ['NZBPP_DIRECTORY']):
	print('Destination directory doesn\'t exist, exiting')
	sys.exit(POSTPROCESS_NONE)

# Check par and unpack status for errors
#if os.environ['NZBPP_PARSTATUS'] == '1' or os.environ['NZBPP_PARSTATUS'] == '4' or os.environ['NZBPP_UNPACKSTATUS'] == '1':
#	print('[WARNING] Download of "%s" has failed, exiting' % (os.environ['NZBPP_NZBNAME']))
#	sys.exit(POSTPROCESS_NONE)

# NZBGET - END
#######################################################################


########################
# ----- Functions ---- #
########################

# Special character hex range:
# CP850: 0x80-0xA5 (fortunately not used in ISO-8859-15)
# UTF-8: 1st hex code 0xC2-0xC3 followed by a 2nd hex code 0xA1-0xFF
# ISO-8859-15: 0xA6-0xFF
# The function will detect if fileDirName contains a special character
# If there is special character, detects if it is a UTF-8, CP850 or ISO-8859-15 encoding
def renameFunc(fullPath, fileDirName):
	encodingDetected = False
	# parsing all files/directories in odrer to detect if CP850 is used
	for Idx in range(len(fileDirName)):
		# /!\ detection is done 2char by 2char for UTF-8 special character
		if (len(fileDirName) != 1) & (Idx < (len(fileDirName) - 1)):
			# Detect UTF-8
			if ((fileDirName[Idx] == '\xC2') | (fileDirName[Idx] == '\xC3')) & ((fileDirName[Idx+1] >= '\xA0') & (fileDirName[Idx+1] <= '\xFF')):
				print os.path.join(fullPath, fileDirName) + " -> UTF-8 detected: Nothing to be done"
				encodingDetected = True
				break;
			# Detect CP850
			elif ((fileDirName[Idx] >= '\x80') & (fileDirName[Idx] <= '\xA5')):
				utf8Name = fileDirName.decode('cp850')
				utf8Name = utf8Name.encode('utf-8')
				os.rename(os.path.join(fullPath, fileDirName), os.path.join(fullPath, utf8Name))
				print os.path.join(fullPath, utf8Name) + " -> CP850 detected: Renamed"
				encodingDetected = True
				break;
			# Detect ISO-8859-15
			elif (fileDirName[Idx] >= '\xA6') & (fileDirName[Idx] <= '\xFF'):
				utf8Name = fileDirName.decode('iso-8859-15')
				utf8Name = utf8Name.encode('utf-8')
				os.rename(os.path.join(fullPath, fileDirName), os.path.join(fullPath, utf8Name))
				print os.path.join(fullPath, utf8Name) + " -> ISO-8859-15 detected: Renamed"
				encodingDetected = True
				break;
		else:
			# Detect CP850
			if ((fileDirName[Idx] >= '\x80') & (fileDirName[Idx] <= '\xA5')):
				utf8Name = fileDirName.decode('cp850')
				utf8Name = utf8Name.encode('utf-8')
				os.rename(os.path.join(fullPath, fileDirName), os.path.join(fullPath, utf8Name))
				print os.path.join(fullPath, utf8Name) + " -> CP850 detected: Renamed"
				encodingDetected = True
				break;
			# Detect ISO-8859-15
			elif (fileDirName[Idx] >= '\xA6') & (fileDirName[Idx] <= '\xFF'):
				utf8Name = fileDirName.decode('iso-8859-15')
				utf8Name = utf8Name.encode('utf-8')
				os.rename(os.path.join(fullPath, fileDirName), os.path.join(fullPath, utf8Name))
				print os.path.join(fullPath, utf8Name) + " -> ISO-8859-15 detected: Renamed"
				encodingDetected = True
				break;
	if (encodingDetected == False):
		print os.path.join(fullPath, fileDirName) + " -> No special characters detected: Nothing to be done"
	return

########################
# --- Main Program --- #
########################
print "Launching CharTranslator Python script v1.0 ..."
print ""

# Change current directory to destination
os.chdir(os.environ['NZBPP_DIRECTORY'])

# display directory of the SABnzbd job
currentFolder = os.getcwd()
print "Current folder is " + currentFolder

# process each sub-folders starting from the deepest level
print 100*'-'
print "Renaming folders to UTF-8 format..."
for dirname, dirnames, filenames in os.walk('.', topdown=False):
	for subdirname in dirnames:
		renameFunc(dirname, subdirname)
print "Folder renaming Done !"
print 100*'-'
print ""

# process each file recursively
print 100*'-'
print "Renaming files to UTF-8 format..."
for dirname, dirnames, filenames in os.walk('.'):
	for filename in filenames:
		renameFunc(dirname, filename)
print "Files renaming Done !"
print 100*'-'
print ""

print ""
print "Character encoding translation done!"


# NZBGET
# All OK, returning exit status 'POSTPROCESS_SUCCESS' (int <93>) to let NZBGet know
# that our script has successfully completed.
sys.exit(POSTPROCESS_SUCCESS)

#!/usr/bin/env python
import imaplib, time
import sys, re

class mapsync():

	f_server = ''
	f_username = ''
	f_password = ''

	#copy to
	t_server = ''
	t_username = ''
	t_password = ''


	def __init__(self, from_server, to_server):
		# Setup the server setup
		self.f_server = from_server
		self.t_server = to_server
		

	def connectToServers(self):
		# This connects to the two servers
		self.From = imaplib.IMAP4(self.f_server) 
		self.From.login(self.f_username, self.f_password)

		self.To = imaplib.IMAP4(self.t_server) 
		self.To.login(self.t_username, self.t_password)

	def getFolderList(self,M):
		typ,data = M.list()

		incoming_folder = []
		for x in data:
			folder = x.split('"."')
			incoming_folder.append(folder[-1].strip())

		return incoming_folder



	def SyncFolder(self, from_user,from_password,to_user,to_password):

		print("Starting Run for " + from_user)
		self.f_username = from_user
		self.f_password = from_password

		self.t_username = to_user
		self.t_password = to_password

		self.connectToServers();
		# Takes the from and to and compare the two arrays
		from_array = self.getFolderList(self.From)
		to_array = self.getFolderList(self.To)
		

		for folder_name in from_array:
			if folder_name in to_array:
				print(">> This folder exists " + folder_name )
				self.moveMsg(folder_name)
				# let's start moving files from the old server to the new
			else:
				self.createFolder(self.To, folder_name)
				time.sleep(0.5)
				self.moveMsg(folder_name)
		
		self.From.logout()
		self.To.logout()

	def createFolder(self,destination, name):
		destination.create(name)
		destination.subscribe(name)
		print("Create folder " + name + " in destination")
		#end- createfolder()
	
	def moveMsg(self,boxname):
		# Move messages from defined boxname

		selectedbox = self.From.select(boxname)
		print("Fetching emails from %s"%boxname)
		
		# Clear up the flag emails (incase it has stalled and you've started again)
		self.expunge()

		typ, data = self.From.search(None, 'ALL')
		print(">>>>" + typ)
		
		print("Found %d Messages"%len(data[0].split()))
		regex = r"Message-ID:[\s|\S]?<(.*?)>\s"
		for muid in data[0].split():
			# start messageUID process
			status, msg = self.From.fetch(muid,"(FLAGS INTERNALDATE BODY.PEEK[])") #Get email
			Email = msg[0][1]
			flags = imaplib.ParseFlags(msg[0][0]) # get Flags
			if "\\Recent" in flags:
				flag_str = "\\Seen"
			else:
				flag_str = " ".join(flags)
			print(">>>>>" + flag_str)
			date = imaplib.Time2Internaldate(imaplib.Internaldate2tuple(msg[0][0])) #get date
			copy_result = self.To.append(boxname, flag_str, date, Email) # Copy to Archive
			if copy_result[0] == 'OK':
				del_msg = self.From.store(muid, '+FLAGS', '\\Deleted') # Mark for deletion (this is deleted via expunge)
		self.expunge()
		#end- moveMsg()

    def expunge(self):
		ex = self.From.expunge()
		time.sleep(0.5)
		print 'expunge status: %s' % ex[0]
		if not ex[1][0]: # result can be ['OK', [None]] if no messages need to be deleted
			print 'expunge count: 0'
		else:
			print 'expunge count: %s' % len(ex[1])
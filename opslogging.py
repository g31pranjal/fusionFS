from enum import Enum
import paramiko
import pwd
import os
import time
import random, string

def getRandomAlphaNum() :
	return ''.join(random.choice(string.ascii_uppercase + \
		string.ascii_lowercase + string.digits) for _ in range(16))


class actions(Enum) :
	MKDIR = 1<<0
	RMDIR = 1<<1
	RENAME = 1<<2
	UPDATE = 1<<3
	DEL = 1<<4
	CREATE = 1<<5
	WRITE = 1<<6


class logUnit :
	def __init__(self, action, preds) :
		self.action = action
		self.predicates = preds

	def addLogStamp(self, seq, tm) :
		self.seq = seq
		self.time = tm

	def addPredicate(self, key, value) :
		if key not in self.predicates.keys() :
			self.predicates[key] = value
		else :
			print("[sftphandle] error in creating log unit, repeated predicate")

	def toString(self) :
		a = (self.seq, self.time, self.action, self.predicates)
		return str(a)


class logg :

	def __init__(self, sftp, drct) :
		self.__log = list()
		self.__logseq = 1
		self.__connect = sftp
		self.__dir = drct

		try :
			self.__connect.listdir(self.__dir)
		except :
			self.__connect.mkdir(self.__dir)

		self.__log_file_path = os.path.join(self.__dir, "log.seq")
		try :
			self.__connect.open(self.__log_file_path, "r" )
		except :
			self.__connect.open(self.__log_file_path, "w")
		
		self.__log_dir_path = os.path.join(self.__dir, "log")
		try :
			self.__connect.listdir(self.__log_dir_path)
		except :
			self.__connect.mkdir(self.__log_dir_path)
	

	def __getLogStamp(self) :
		a = self.__logseq	
		self.__logseq += 1
		b = time.time()
		return a, b

	def addAction(self, logunit) :
		a, b = self.__getLogStamp()
		logunit.addLogStamp(a, b)

		self.__log.append(logunit)
		self.prnt()
		self.flushLogs()

		# if len(self.__log) > 5 :
		# 	self.flushLogs()

	def prnt(self) :
		col = ""
		for entry in self.__log :
			col = entry.toString() + "\n"
		# print col
		return col

	def flushLogs(self) :
		try :
			f = self.__connect.open(self.__log_file_path, "a")
			f.write(self.prnt())
			f.close()
		except Exception as e:
			# print(e)
			print("[sftphandle/version] cannot flush logs")

	def logFile(self, abspath) :
		newFile = os.path.join(self.__log_dir_path, getRandomAlphaNum())
		try :
			self.__connect.rename(abspath, newFile)
			return newFile
		except :
			print("[sftphandle/version] cannot log file from %s -> %s" % (abspath, newFile))
			return None

	def storeDiff(self, data) :

		newFile = os.path.join(self.__log_dir_path, getRandomAlphaNum())
		try :
			f = self.__connect.open(newFile, 'w')
			f.write(data)
			f.flush()
			f.close()
			return newFile
		except :
			print("[sftphandle/version] cannot write diff at " % (newFile))
			return None
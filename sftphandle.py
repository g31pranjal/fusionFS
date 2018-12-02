import paramiko
import pwd
import os
import time
from enum import Enum
import random, string


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


class logger :

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
		print col
		return col

	def flushLogs(self) :
		try :
			f = self.__connect.open(self.__log_file_path, "a")
			f.write(self.prnt())
			f.close()
		except Exception as e:
			print(e)
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


def getRandomAlphaNum() :
	return ''.join(random.choice(string.ascii_uppercase + \
		string.ascii_lowercase + string.digits) for _ in range(16))


class SftpHandle :

	def __init__(self, config) :
		self.native = config
		try :
			self.__client = paramiko.SSHClient()
			self.__client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			self.__client.load_system_host_keys()
			self.__client.connect(self.native[u'host'], port=22, username=self.native[u'user'], \
				password=self.native[u'pass'])
			self.__connect = sftp = self.__client.open_sftp()
			print("[sftphandle @ %s] sftp:%s connected." % (self.native[u'name'], self.native[u'name']))
		except Exception :
			print("[sftphandle @ %s] error initializing the sftp handle." % (self.native[u'name']))
			raise Exception

		self.__connect.chdir(".")

		marker_search = filter( lambda x : x == 'fusion.marker', self.__connect.listdir() )
		if len(marker_search) == 0 :
			print("[sftphandle @ %s] marker not found." % (self.native[u'name']))
			raise Exception

		self.__localUser = pwd.getpwnam('in-arena')
		self.__log = logger(self.__connect, self.__abspath(self.native['version_dir']))
		


	def __abspath(self, path) :
		user_seg = self.__connect.getcwd()
		cont_seg = self.native[u'base']
		while(len(cont_seg) > 0 and cont_seg[0] == '/') :
			cont_seg = cont_seg[1:]
		while(len(path) > 0 and path[0] == '/') : 
			path = path[1:]

		a = os.path.join(cont_seg, path)
		return a


	def chmod(self, path, mode) :
		abspath = self.__abspath(path)
		return self.__connect.chmod(self.__abspath(path), mode)
		

	def readdir(self, path) :
		abspath = self.__abspath(path)
		lst = self.__connect.listdir(self.__abspath(path))
		lst = ['.', '..'] + lst
		return lst


	def getattr(self, path) :
		# print("sftp getatr")
		abspath = self.__abspath(path)
		# print abspath
		stats = self.__connect.lstat(abspath)
		stats = dict((key, getattr(stats, key)) for key in \
			( 'st_atime', 'st_mode', 'st_uid', 'st_gid', 'st_mtime', 'st_size'))
		stats['st_uid'] = self.__localUser.pw_uid
		stats['st_gid'] = self.__localUser.pw_gid
		return stats
		# try :
		# except :
		# 	print("[sftphandle @ %s] file not found" % (self.native[u'name']))
		# 	return None


	def unlink(self, path) :
		abspath = self.__abspath(path)
		newFile = self.__log.logFile(abspath)
		lu = logUnit(actions.DEL, { 'path' : abspath, 'logged' : newFile })
		self.__log.addAction(lu)


	def rename(self, old, new) :
		abspathold = self.__abspath(old)
		abspathnew = self.__abspath(new)

		try :
			f = self.__connect.open(abspathnew)
			f.close()
			print("trying to update the file") 
			newFile = self.__log.logFile(abspathnew)
			print("newfile %s" % (newFile))
			try :
				self.__connect.rename(abspathold, abspathnew)		
				lu = logUnit(actions.UPDATE, { 'path' : abspathnew, 'logged' : newFile })
				self.__log.addAction(lu)
			except Exception as e :
				raise Exception
		
		except :
			try :
				self.__connect.rename(abspathold, abspathnew)		
			except Exception as e :
				print e
				raise Exception
			lu = logUnit(actions.RENAME, { 'old' : old, 'new' : new })
			self.__log.addAction(lu)
	
	

	def mkdir(self, path, mode) :
		abspath = self.__abspath(path)
		self.__connect.mkdir(abspath)
		lu = logUnit(actions.MKDIR, { 'path' : path })
		self.__log.addAction(lu)


	def rmdir(self, path) :
		abspath = self.__abspath(path)
		self.__connect.rmdir(abspath)
		lu = logUnit(actions.RMDIR, { 'path' : path })
		self.__log.addAction(lu)


	def utimens(self, path, times) :
		abspath = self.__abspath(path)
		self.__connect.utime(abspath, times)


	def open(self, path, flags) :
		# mimicks system call open for only read flag
		abspath = self.__abspath(path)
		a = self.__connect.open(abspath, "r")
		a.close()
		return True


	def create(self, path, mode) :
		abspath = self.__abspath(path)
		a = self.__connect.open(abspath, "w")
		a.close()
		lu = logUnit(actions.CREATE, { 'path' : abspath })
		self.__log.addAction(lu)


	def read(self, path, length, offset) :
		abspath = self.__abspath(path)
		f = self.__connect.open(abspath)
		f.seek(offset, 0)
		buf = f.read(length)
		f.close()
		print "reading..."
		return buf

	def write(self, path, data, offset) :
		abspath = self.__abspath(path)
		f = self.__connect.open(abspath, 'r+')
		f.seek(offset, 0)
		f.write(data)
		f.flush()
		f.close()
		newFile = self.__log.storeDiff(data)
		lu = logUnit(actions.WRITE, { 'path' : abspath, 'logged' : newFile, 'offset' : offset })
		self.__log.addAction(lu)
		return len(data)



	def destroy(self) :
		self.__connect.close()
		self.__client.close()

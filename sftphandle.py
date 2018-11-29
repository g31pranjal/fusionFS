import paramiko
import pwd
import os
import time
from enum import Enum


class actions(Enum) :
	MKDIR = 1<<0
	RMDIR = 1<<1
	RENAME = 1<<2


class logUnit :
	def __init__(self, action, preds) :
		self.action = action
		self.predicates = preds

	def addLogStamp(self, seq, tm) :
		self.seq = seq
		self.time = time

	def addPredicate(self, key, value) :
		if key not in self.predicates.keys() :
			self.predicates[key] = value
		else :
			print("[sftphandle] error in creating log unit, repeated predicate")


class versionControl :

	def __init__(self, sftp, drct) :
		self.__log = list()
		self.__logseq = 1
		self.__connect = sftp
		self.__dir = drct

		try :
			self.__connect.listdir(self.__dir)
		except :
			self.__connect.mkdir(self.__dir)

		log_file_path = os.path.join(self.__dir, "log.seq")
		try :
			self.__connect.open(log_file_path, "r" )
		except :
			self.__connect.open(log_file_path, "w")
		
		log_dir_path = os.path.join(self.__dir, "log")
		try :
			self.__connect.listdir(log_dir_path)
		except :
			self.__connect.mkdir(log_dir_path)
	

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

		# if len(self.__log) > 5 :
		# 	self.flushLogs()

	def prnt(self) :
		for entry in self.__log :
			print(entry.seq)
			print(entry.time)
			print(entry.action)
			print(entry.predicates)
			print("===")

	def flushLogs(self) :
		# write mechanism 
		pass




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
		self.__log = versionControl(self.__connect, self.__abspath(self.native['version_dir']))
		




	def __abspath(self, path) :
		user_seg = self.__connect.getcwd()
		cont_seg = self.native[u'base']
		while(len(cont_seg) > 0 and cont_seg[0] == '/') :
			cont_seg = cont_seg[1:]
		while(len(path) > 0 and path[0] == '/') : 
			path = path[1:]

		a = os.path.join(cont_seg, path)
		return a



	def readdir(self, path) :
		abspath = self.__abspath(path)
		lst = self.__connect.listdir(self.__abspath(path))
		lst = ['.', '..'] + lst
		return lst


	def getattr(self, path) :
		print("sftp getatr")
		abspath = self.__abspath(path)
		print abspath
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
		self.__connect.unlink(abspath)


	def rename(self, old, new) :
		abspathold = self.__abspath(old)
		abspathnew = self.__abspath(new)
		self.__connect.rename(abspathold, abspathnew)		
		try :
			lu = logUnit(actions.RENAME, { 'old' : old, 'new' : new })
			self.__log.addAction(lu)
		except Exception as e :
			print e
			raise Exception

	

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


	def open(self, path) :
		# mimicks system call open for only read flag
		abspath = self.__abspath(path)
		a = self.__connect.open(abspath, "r")
		a.close()
		return True
		# try :
		# except :
		# 	print("[sftphandle @ %s] cannot open file at %s" % (self.native[u'name'], path))
		# 	return None	


	def create(self, path, mode) :
		abspath = self.__abspath(path)
		a = self.__connect.open(abspath, "w")
		a.close()


	def read(self, path, length, offset) :
		abspath = self.__abspath(path)
		f = self.__connect.open(abspath)
		f.seek(offset, 0)
		buf = f.read(length)
		f.close()
		print buf
		return buf

	def write(self, path, data, offset) :
		abspath = self.__abspath(path)
		f = self.__connect.open(abspath, 'r+')
		f.seek(offset, 0)
		f.write(data)
		f.close()
		print "written...."
		return len(data)




	def destroy(self) :
		self.__connect.close()
		self.__client.close()

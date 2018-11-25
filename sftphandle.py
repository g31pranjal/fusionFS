import paramiko
import pwd
import os

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
		try :
			lst = self.__connect.listdir(self.__abspath(path))
			lst = ['.', '..'] + lst
			return lst
		except :
			print("[sftphandle @ %s] cannot list directory not found" % (self.native[u'name']))
			return None


	def getattr(self, path) :
		try :
			abspath = self.__abspath(path)
			stats = self.__connect.lstat(abspath)
			stats = dict((key, getattr(stats, key)) for key in \
				( 'st_atime', 'st_mode', 'st_uid', 'st_gid', 'st_mtime', 'st_size'))
			stats['st_uid'] = self.__localUser.pw_uid
			stats['st_gid'] = self.__localUser.pw_gid
			return stats
		except :
			print("[sftphandle @ %s] file not found" % (self.native[u'name']))
			return None


	def rename(self, old, new) :
		try :
			abspathold = self.__abspath(old)
			abspathnew = self.__abspath(new)
			self.__connect.rename(abspathold, abspathnew)
			return True
		except :
			print("[sftphandle @ %s] cannot rename" % (self.native[u'name']))
			return None


	def mkdirrec(self, path, mode) :
		abspath = self.__abspath(path)
		print("[sftphandle @ %s] mkdirrec %s" % (self.native[u'name'], abspath))
		try :
			self.__connect.mkdir(abspath)
			return True
		except IOError :
			self.mkdirrec(os.path.dirname(path), mode)
			self.__connect.mkdir(path)


	def rmdir(self, path) :
		try :
			abspath = self.__abspath(path)
			self.__connect.rmdir(abspath)
			return True
		except :
			print("[sftphandle @ %s] cannot remove directory" % (self.native[u'name']))
			return None		


	def destroy(self) :
		self.__connect.close()
		self.__client.close()

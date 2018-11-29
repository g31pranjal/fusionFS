import gdrivehandle
import sftphandle
import dbxhandle
import errno
import json
import os
import random

class FusionFS :


	def __init__(self) :

		if not os.path.exists('./config.json') :
			print("[fusion] cannot find config.json")
			raise Exception("cannot start FUSE")

		config = json.load(open('config.json'))

		self.__handleLists = list()
		for cont in config[u'containers'] :
			if cont[u'use'] == 1 :
				if cont[u'type'] == 'dbx' :
					try :
						self.__handleLists.append(dbxhandle.DbxHandle(cont))
					except :
						pass
				elif cont[u'type'] == 'sftp' :
					try :
						self.__handleLists.append(sftphandle.SftpHandle(cont))
					except :
						pass

		if config[u'properties'][u'mirroring'] != 1 :
			self.__mirrors = -1
		else :
			self.__mirrors = config[u'properties'][u'mirrors']
		self.__logging = bool(config[u'properties'][u'logging'])
		self.__explorer = dict()

		print("[fusion] total containers online : %d" % (len(self.__handleLists)))



	def __getSites(self, num = -1, excpt = list() ) :
		if num == -1 :
			num = self.__mirrors
		assert(len(self.__handleLists)-len(excpt) >= num)
		sites = list()
		while(len(sites) != num) :
			r = int(random.random()*(len(self.__handleLists)))
			if r not in (excpt + sites) :
				sites.append(r)
		return sites



	def getContainers(self) :
		return map( lambda x : x.native[u'name'],self.__handleLists )


	def getProperties(self) :
		atr = dict()
		atr['mirroring'] = True if self.__mirrors > 0 else False
		atr['mirrors'] = self.__mirrors 
		atr['logging'] = self.__logging
		return atr


	def readdir(self, path) :

		lst = set()
		if path in self.__explorer.keys() :
			for i in self.__explorer[path] :
				handle = self.__handleLists[i]
				try :
					a = handle.readdir(path)
					lst = lst.union( map(lambda x : str(x) , a))
				except :
					print("[fusion] readdir failed at handle %d" % (i))
		else :
			sites = list()
			for i, handle in enumerate(self.__handleLists) :
				try :
					a = handle.readdir(path)
					lst = lst.union( map(lambda x : str(x) , a))
					sites.append(i)
				except :
					print("[fusion] readdir failed at handle %d" % (i))
			self.__explorer[path] = sites

		return list(lst)



	def getattr(self, path) :

		lst = list()
		if path in self.__explorer.keys() :
			# print("getting here")
			# print(self.__explorer[path])
			for i in self.__explorer[path] :
				handle = self.__handleLists[i] 
				try :
					a = handle.getattr(path)
					lst.append(a)
				except :
					print("[fusion] getattr failed at handle %d" % (i))
		else :
			sites = list()
			for i, handle in enumerate(self.__handleLists) :
				try :
					a = handle.getattr(path)
					sites.append(i)
					lst.append(a)
				except :
					print("[fusion] getattr failed at handle %d" % (i))
			self.__explorer[path] = sites
			# print self.__explorer

		if len(lst) != 0 :
			return lst[0]
		else :
			print("[fusion] raising error.") 
			raise OSError(errno.ENOENT, "No such file or directory", path)


	def unlink(self, path) :
		if path in self.__explorer.keys() :
			for i in self.__explorer[path] :
				handle = self.__handleLists[i] 
				try :
					handle.unlink(path)
				except :
					print("[fusion] rename failed at handle %i" % (i))
			del self.__explorer[path]
		else :	
			sites = list()
			for i, handle in enumerate(self.__handleLists) :
				try :
					handle.unlink(path)
					sites.append(i)
				except :
					print("[fusion] rename failed at handle %i" % (i))
			

	def rename(self, old, new) :
		if old in self.__explorer.keys() :
			for i in self.__explorer[old] :
				handle = self.__handleLists[i] 
				try :
					a = handle.rename(old, new)
				except :
					print("[fusion] rename failed at handle %i" % (i))
			tmp = self.__explorer[old]
			del self.__explorer[old]
			self.__explorer[new] = tmp
		else :	
			sites = list()
			for i, handle in enumerate(self.__handleLists) :
				try :
					a = handle.rename(old, new)
					sites.append(i)
				except :
					print("[fusion] rename failed at handle %i" % (i))
			self.__explorer[new] = sites



	def mkdir(self, path, mode, sites=None) :
		print path 
		if path in self.__explorer.keys() and self.__mirrors > 0 and \
			len(self.__explorer[path]) >= self.__mirrors :
			pass
		else :
			newsites = list()
			if not sites :
				if path in self.__explorer.keys() :
					sites = self.__getSites(num=self.__mirrors-len(self.__explorer[path]), \
						excpt=list())
				else :
					sites = self.__getSites(num=self.__mirrors, excpt=list())
			
			for i in sites :
				handle = self.__handleLists[i]
				try :
					a = handle.mkdir(path, mode)
					newsites.append(i)
				except :
					self.mkdir(os.path.dirname(path), mode, [i,])
					a = handle.mkdir(path, mode)
					newsites.append(i)
			
			if path in self.__explorer.keys() :
				self.__explorer[path] = self.__explorer[path] + newsites
			else :
				self.__explorer[path] = newsites

	

	def rmdir(self, path) :
		if path in self.__explorer.keys() :
			for i in self.__explorer[path] :
				handle = self.__handleLists[i] 
				try :
					a = handle.rmdir(path)
				except : 
					print("[fusion] cannot remove directory at handle %d" % (self.native[u'name'], i))

			del self.__explorer[path]
		else :
			for i, handle in enumerate(self.__handleLists) :
				try :
					a = handle.rmdir(path)
				except : 
					print("[fusion] cannot remove directory at handle %d" % (self.native[u'name'], i))



	def open(self, path, flags) :
		flags = flags^(1<<15)
		# print flags
		if path in self.__explorer.keys() :
			for i in self.__explorer[path] :
				handle = self.__handleLists[i]
				try :
					if flags == 0 :
						a = handle.open(path, flags)
						return a
					else : 
						print("[fusion] open in other than read flag not handled")
				except :
					pass
		else :
			for i, handle in enumerate(self.__handleLists) :
				try :	
					if flags == 0 :
						a = handle.open(path, flags)
						return a
					else :
						print("[fusion] open in other than read flag not handled")
				except :
					pass



	def create(self, path, mode) :
		if path in self.__explorer.keys() and self.__mirrors > 0 and \
			len(self.__explorer[path]) >= self.__mirrors :
			pass
		else :

			newsites = list()
			if path in self.__explorer.keys() :
				sites = self.__getSites(num=self.__mirrors-len(self.__explorer[path]), \
					excpt=list())
			else :
				sites = self.__getSites(num=self.__mirrors, excpt=list())
			
			for i in sites :
				handle = self.__handleLists[i]
				try :
					a = handle.create(path, mode)
					newsites.append(i)
				except IOError :
					try :
						self.mkdir(os.path.split(path)[0], 777, [i,])
						a = handle.create(path, mode)
						newsites.append(i)
					except :
						print("[fusion] create failed internal at handle %d" % (i))
				except :
					print("[fusion] create failed external at handle %d" % (i))
			
			if path in self.__explorer.keys() :
				self.__explorer[path] = self.__explorer[path] + newsites
			else :
				self.__explorer[path] = newsites



	def read(self, path, length, offset) :
		if path in self.__explorer.keys() :
			for i in self.__explorer[path] :
				handle = self.__handleLists[i]
				try :
					a = handle.read(path, length, offset)
					return a
				except :
					pass
		else :
			for i, handle in enumerate(self.__handleLists) :
				try :	
					a = handle.read(path, length, offset)
					return a
				except :
					pass


	def write(self, path, buf, offset) :
		if path in self.__explorer.keys() :
			for i in self.__explorer[path] :
				handle = self.__handleLists[i]
				try :
					a = handle.write(path, buf, offset)
					return a
				except :
					pass
		else :
			for i, handle in enumerate(self.__handleLists) :
				try :	
					a = handle.write(path, buf, offset)
					return a
				except :
					pass

		


	def isDir(self, path) :
		return True


# fs = FusionFS()

import json
import dbxhandle
import gdrivehandle
import sftphandle
import os
import errno

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

		self.__explorer = dict()
		print("[fusion] total containers online : %d" % (len(self.__handleLists)))


	def readdir(self, path) :

		lst = set()
		if path in self.__explorer.keys() :
			for i in self.__explorer[path] :
				handle = self.__handleLists[i]
				a = handle.readdir(path)
				if(a != None) :
					lst = lst.union( map(lambda x : str(x) , a))
		else :
			sites = list()
			for i, handle in enumerate(self.__handleLists) :
				a = handle.readdir(path)
				if(a != None) :
					lst = lst.union( map(lambda x : str(x) , a))
					sites.append(i)
			self.__explorer[path] = sites
			# print self.__explorer

		return list(lst)



	def getattr(self, path) :

		lst = list()
		if path in self.__explorer.keys() :
			for i in self.__explorer[path] :
				handle = self.__handleLists[i] 
				a = handle.getattr(path)
				if a != None :
					lst.append(a)
		else :
			sites = list()
			for i, handle in enumerate(self.__handleLists) :
				a = handle.getattr(path)
				if a != None :
					sites.append(i)
					lst.append(a)
			self.__explorer[path] = sites
			# print self.__explorer

		if len(lst) != 0 :
			return lst[0]
		else :
			print("[fusion] raising error.") 
			raise OSError(errno.ENOENT, "No such file or directory", path)



	def rename(self, old, new) :
		if old in self.__explorer.keys() :
			for i in self.__explorer[old] :
				handle = self.__handleLists[i] 
				a = handle.rename(old, new)
			tmp = self.__explorer[old]
			del self.__explorer[old]
			self.__explorer[new] = tmp
		else :	
			sites = list()
			for i, handle in enumerate(self.__handleLists) :
				a = handle.rename(old, new)
				if a != None :
					res = a
					sites.append(i)
			self.__explorer[new] = sites

		print self.__explorer[new]


	def isDir(self, path) :
		return True




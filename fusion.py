import json
import dbxhandle
import gdrivehandle
import sftphandle
import os


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

		print("[fusion] total containers online : %d" % (len(self.__handleLists)))


	def readdir(self, path) :
		lst = set()
		for handle in self.__handleLists :
			a = handle.readdir(path)
			if(a != None) :
				lst = lst.union( map(lambda x : str(x) , a))
		return list(lst)



	def getattr(self, path) :
		lst = list()
		for handle in self.__handleLists :
			a = handle.getattr(path)
			if a != None :
				lst.append(a)

		return lst[0]


	def isDir(self, path) :
		return True




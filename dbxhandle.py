import dropbox

class DbxHandle :

	def __init__(self, config) :
		self.__native = config
		try :
			self.__connect = dropbox.Dropbox(config[u'auth'])
			self.__user = self.__connect.users_get_current_account()
			print("dbx:%s connected." % self.__native[u'name'])
		except dropbox.exceptions.AuthError :
			print("failed to establish connection.")
			raise dropbox.exceptions.AuthError
		except Exception :
			print("error initializing the dbx handle.")
			raise Exception

		self.__housekeeping()


	def __housekeeping(self) :
		print self.__connect.files_search("", "fusion.marker", mode=dropbox.files.SearchMode('filename', None))

	def getUserInfo(self) :
		return self.__user
		
	def retrieveHeirarchy(self) :

		lst = list()

		more = True;
		init = True;

		while(more) :
			if(init) :
				req = self.__connect.files_list_folder(self.native[u'base'], recursive=True)
				cursor = req.cursor;
				init = False;
			else :
				req = self.__connect.files_list_folder_continue(cursor)
			more = req.has_more
			for entry in req.entries :
				print entry.path_display

		return lst
		


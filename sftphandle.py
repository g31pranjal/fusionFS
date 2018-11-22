import pysftp

class SftpHandle :

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
		
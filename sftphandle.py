import pysftp

class SftpHandle :

	def __init__(self, config) :
		self.__native = config
		try :
			cnopts = pysftp.CnOpts()
			cnopts.hostkeys = None   
			self.__connect = pysftp.Connection(host=self.__native[u'host'], \
			username=self.__native[u'user'], password=self.__native[u'pass']\
			, cnopts = cnopts )
			print("[sftphandler] sftp:%s connected." % self.__native[u'name'])
		except Exception :
			print("[sftphandler] error initializing the sftp handle.")
			raise Exception

		# self.__housekeeping()

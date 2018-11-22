import json
import dbxhandle
import gdrivehandle
import sftphandle


if __name__ == '__main__' :

	# check if the config.json exists

	config = json.load(open('config.json'))

	handleLists = list()

	for cont in config[u'containers'] :
		if cont[u'type'] == 'dbx' :
			try :
				handleLists.append(dbxhandle.DbxHandle(cont))
			except :
				pass
		elif cont[u'type'] == 'sftp' :
			try :
				handleLists.append(sftphandle.SftpHandle(cont))
			except :
				pass


	print handleLists

	# for handle in handleLists :
	# 	handle.retrieveHeirarchy()






import json
import dbxhandle
import gdrivehandle
import sftphandle


if __name__ == '__main__' :

	config = json.load(open('config.json'))

	handleLists = list()

	for cont in config[u'containers'] :
		if cont[u'type'] == 'dbx' :
			handleLists.append(dbxhandle.DbxHandle(cont))
		elif cont[u'type'] == 'sftp' :
			handleLists.append(sftphandle.SftpHandle(cont))



	for handle in handleLists :
		handle.retrieveHeirarchy()






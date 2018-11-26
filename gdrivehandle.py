from __future__ import print_function
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from httplib2 import Http
from oauth2client import file, client, tools
import json

# If modifying these scopes, delete the file token.json.
SCOPES_READONLY = 'https://www.googleapis.com/auth/drive.metadata.readonly'
SCOPES_FULL	= 'https://www.googleapis.com/auth/drive'
FOLDER          = 'application/vnd.google-apps.folder'
FILE 		= 'application/vnd.google-apps.file'

class GoogleDriveHandle:

	def __init__(self, config):
		self.__object       = {}
		self.__native       = config
		store               = file.Storage('token.json') 
		self.__credentials  = store.get()
		self.__rootid       = None	
                try:
			if not self.__credentials or self.__credentials.invalid:
				flow               = client.flow_from_clientsecrets('credentials.json', SCOPES_FULL)
    		        	self.__credentials = tools.run_flow(flow, store)
                                self.__refresh_token = self.__credentials.refresh_token
				self.__connect = build('drive', 'v3', http=self.__credentials.authorize(Http()))			
			else:
				self.__refresh_token = self.__credentials.refresh_token
				client_id 	     = self.__credentials.client_id
				client_secret        = self.__credentials.client_secret		
				token_url            = self.__credentials.token_uri	
		                
				self.__credentials = Credentials(
							None,
							refresh_token = self.__refresh_token,
							token_uri     = token_url,
							client_id     = client_id,
							client_secret = client_secret)
			        self.__connect = build('drive', 'v3', credentials = self.__credentials)	
			print("token established")
             	except Exception as ex:
			print("Error initializing the google drive handle!!")
			template = "Exception type {0} occurred. Arguments:\n{1!r}"
			message  = template.format(type(ex).__name__, ex.args)
			#print (message)
			raise ex;	

	def getCredentials(self, config):
		try:
	        	store               = file.Storage('token.json')
        	        self.__credentials  = store.get()
                
                        if not self.__credentials or self.__credentials.invalid:
                                flow               = client.flow_from_clientsecrets('credentials.json', SCOPES_FULL)
                                self.__credentials = tools.run_flow(flow, store)
                                self.__refresh_token = self.__credentials.refresh_token
                                self.__connect = build('drive', 'v3', http=self.__credentials.authorize(Http()))
                        else:
                                self.__refresh_token = self.__credentials.refresh_token
                                client_id            = self.__credentials.client_id
                                client_secret        = self.__credentials.client_secret
                                token_url            = self.__credentials.token_uri

                                self.__credentials = Credentials(
                                                        None,
                                                        refresh_token = self.__refresh_token,
                                                        token_uri     = token_url,
                                                        client_id     = client_id,
                                                        client_secret = client_secret)
                                self.__connect = build('drive', 'v3', credentials = self.__credentials)
                        print("token established")
                except Exception as ex:
                        print("Error initializing the google drive handle!!")
                        template = "Exception type {0} occurred. Arguments:\n{1!r}"
                        message  = template.format(type(ex).__name__, ex.args)
                        #print (message)
                        raise ex;

	def HandleException(self, ex):
		template = "Exception type {0} occurred. Arguments:\n{1!r}"
                message  = template.format(type(ex).__name__, ex.args)
                print (message)
                raise ex
                
		
      	def authorize(self, flag):
		self.__credentials.refresh_token = self.__refresh_token 
	
        def scanfiles(self, name=None, is_folder=None, parent=None, query='folder,name,createdTime'):
                q = []
                if name is not None:
                        q.append("name = '%s'" % name.replace("'", "\\'"))
                if is_folder is not None:
                        q.append("mimeType %s '%s'" % ('=' if is_folder else '!=', FOLDER))
                if parent is not None:
                        q.append("'%s' in parents" % parent.replace("'", "\\'"))
                params = {'pageToken': None, 'orderBy': query, 'fields':"files(name, id, parents, mimeType, kind)"}
                if q:
                        params['q'] = ' and '.join(q)
			#print(params)
                while True:
                        response = self.__connect.files().list(**params).execute()
			#print (response)
                        for f in response['files']:
	                        yield f
                        try:
                            params['pageToken'] = response['nextPageToken']
                        except KeyError:
                            return

        def scan(self, top):
                top, = self.scanfiles(name=top, is_folder=True)
                stack = [((top['name'],), top)]
                while stack:
                        path, top = stack.pop()
                        dirs, files = is_file = [], []
                        for f in self.scanfiles(parent=top['id']):
                            is_file[f['mimeType'] != FOLDER].append(f)
                        yield path, top, dirs, files
                        if dirs:
                            stack.extend((path + (d['name'],), d) for d in dirs)

	def getFileListbyQuery(self, query, folder_list, file_list):
                try:
                        token = ''
                        more  = True
                        lst   = list()
                        while (more):
                                if token == '':
                                        list_result = self.__connect.files().list(pageSize=10, fields="nextPageToken, files(name, mimeType, kind, id, parents)", q=query).execute()
                                else:
                                        list_result = self.__connect.files().list(pageSize=1000, pageToken=token, fields="nextPageToken, files(name, mimeType, kind, id, parents)", q=query).execute()
                                for filename in list_result['files']:
                                        if FOLDER  == filename[u'mimeType']:
                                                folder_list.append(filename)
						print(filename)
                                        else:
                                                file_list.append(filename)
                                token = list_result.get('nextPageToken', None)
                                if token is None:
                                        more = False
                        return ;
                except HttpError as err:
                        if err.resp.get('content-type', '').startswith('application/json'):
                            reason = json.loads(err.content).get('error').get('errors')[0].get('reason')
                            print("REASON:%s" % reason)
			raise Exception
                except Exception as ex:
                        #print ("GoogleDrive: File list not processed!!!")
                        ##print("Error initializing the google drive handle!!")
                        template = "Exception type {0} occurred. Arguments:\n{1!r}"
                        message  = template.format(type(ex).__name__, ex.args)
                        #print (message)
                        raise ex;
	

        def retrieveHierarchy(self):
		folder_list = []
		file_list   = []
		try:
			self.getFileListbyQuery("'root' in parents", folder_list, file_list);
			'''
			self.getFileListbyQuery("sharedWithMe and mimeType='application/vnd.google-apps.folder'",
				   folder_list, file_list);
                        '''
			for file in file_list:
				temp = file[u'name']
				self.__object[temp] = file
				if 'parents' in file and self.__rootid is None:
					self.__rootid = file[u'parents'][0]
								
			for folder in folder_list:
				print ("folder--->%s" % folder[u'name'])
				for path, root, dirs, files in self.scan(folder[u'name']):
				        temp_path = '/'.join(path)
					for dir in dirs:
					       self.__object[temp_path + '/' + dir[u'name']] = dir	
			        	for temp_files in files:
					       self.__object[temp_path+'/'+temp_files[u'name']] = temp_files	
        				       #print(temp_path + '/' + temp_files[u'name'])
			for folder in folder_list:
				temp = folder[u'name']
				self.__object[temp] = folder
                                if 'parents' in folder and self.__rootid is None:
                                        self.__rootid = folder[u'parents'][0]

		except Exception as ex:
			print("Exception")
                        template = "Exception type {0} occurred. Arguments:\n{1!r}"
                        message  = template.format(type(ex).__name__, ex.args)
                        print (message)
                        raise ex;
			HandleException(ex)


	def getmetadata(self, file_id):
       		try:
			print("In get metadata %s" %file_id)
                	file = self.__connect.files().get(fileId=file_id).execute()
			print(file)
                	print ('MIME type: %s' % file['mimeType'])
                	return file;
		except Exception as ex:
			self.HandleException(ex)
         	except errors.HttpError, error:
                	print ('An error occurred: %s' % error)

	def getfilecontent(self, file_id):
        	try:
                	result = self.__connect.files().get_media(fileId=file_id).execute()
              		print (result)
                	return result
		except Exception as ex:
			self.HandleException(ex)
        	except errors.HttpError, error:
                	print ('An error occurred: %s' % error)

	def getfile(self, file_id, local_fd):
        	request = self.__connect.files().get_media(fileId=file_id)
        	media_request = http.MediaIoBaseDownload(local_fd, request)

        	while True:
                	try:
                        	download_progress, done = media_request.next_chunk()
                	except errors.HttpError, error:
                        	#print ('An error occurred: %s' % error)
                        	return
                	if download_progress:
                        	print ('Download Progress: %d%%' % int(download_progress.progress() * 100))
                	if done:
                        	#print ('Download Complete')
                        	return

	def movefile(self, filename, new_path):
		try:
			if filename not in self.__object:
				print("source %s not present to be moved." % filename)
				return
			if new_path in self.__object:
				print("destination %s is already present. unable to move" % new_path)
				return
			actual_name = self.getactualfilename(filename)
			parent      = self.getparent(new_path)
			if parent is None and '/' in new_path:
				print("Invalid path %s unable to move." % parent)
				return
			if parent is None:
				new_parent = self.__rootid
			else:			  
				new_parent = self.__object[parent][u'id']
			file = self.__connect.files().get(fileId=self.__object[filename][u'id'],
       	        		                 fields='parents').execute()
			previous_parents = ",".join(file.get('parents'))
			file = self.__connect.files().update(fileId=self.__object[filename][u'id'],
                		                    addParents=new_parent,
                        		            removeParents=previous_parents,
                                		    fields='name, kind, mimeType, id, parents').execute()
			del self.__object[filename]		
			self.__object[new_path] = file
			print("File moved to new location %s" % new_path)
		except Exception as ex:
			self.HandleException(ex)
	'''
	def copyfile(self, filename, new_path):
		try:
                        if filename not in self.__object:
                                print("source %s not present to be copied." % filename)
				return
                        if new_path in self.__object:
                                print("destination %s is already present. unable to copy" % new_path)
				return
                        actual_name = self.getactualfilename(filename)
                        parent      = self.getparent(new_path)
                        if parent is None and '/' in new_path:
                                print("Invalid path %s unable to copy" % parent)
				return
			if parent is not None:
				parent_id   = self.__object[parent][u'id']
				copied_file = { 'title': self.__object[parent][u'name'], 'parents': [parent]}
				#copied_file['parents'] =  [parent_id]
			else:
				copied_file = { 'title': self.__object[parent][u'name'], 'parents':['root']} 
				#copied_file['parents'] = ['root']

			file =  self.__connect.files().copy(
			        fileId=self.__object[filename][u'id'], body = copied_file,
							fields='name, kind, mimeType, id, parents').execute()
                        self.__object[new_path] = file
			print("file copied %s" % new_path)
                except Exception as ex:
                        self.HandleException(ex)
	'''
	
	def mkdir(self, gfilename, parent_id = None, mime_type = None):
		try:
			item = self.__object[gfilename]
			if item:
				print("Folder:%s already present, unable to create" % gfilename)
				return;	
		except KeyError: 
			1;

		file_metadata = {
		    'name': self.getactualfilename(gfilename),
		    'mimeType': 'application/vnd.google-apps.folder'
		}

		if parent_id:
			file_metadata['parents'] = [{'id': parent_id}]
		elif '/' in gfilename:
		        parent_path = self.getparent(gfilename)
			try :
				item = self.__object[parent_path]
			except KeyError:
				print("Path invalid:%s. Unable to create folder" % item)
				return
			file_metadata['parents'] = [item[u'id']] # [{'id': item[u'id']}]
	
		file = self.__connect.files().create(body=file_metadata,
               	                     fields='id, name, parents, kind, mimeType').execute()
		print ('Folder created: %s' % file.get('name'))
		self.__object[gfilename] = file

	def listdir(self, path):
		try:
			item = self.__object[path]
			lspaths = []
			print("In list dir")	
			for item in self.__object.keys():
				if path in item:
					lspaths.append(item)
			return lspaths
		except KeyError:
			print("The given path:%s does not exists" % path)
			return []

	def rmdir(self, gfilename, parent_id = None, mime_type = None):
                try:
                        item = self.__object[gfilename]
			if item[u'mimeType'] != FOLDER:
				print("Given path is not a folder, unable to delete")
				return;
                except KeyError: 
                        print("Path:%s does not exists. Unable to delete folder" % gfilename)
                        return;

		paths = self.listdir(gfilename)	
		if len(paths) > 1:		
                	print("Unable to delete. Multiple files in the path")
			return;
		paths = self.__object[gfilename]
		print("rm directory---> %s" % gfilename)	
                self.__connect.files().delete(fileId=paths[u'id']).execute()
                print ('Folder deleted:%s' % paths[u'name'])
                del self.__object[gfilename] 

	def recrrmdir(self, gfilename):
		try:
			item = self.__object[gfilename]
		except KeyError:
			print("Given path : %s is not present. unable to delete" % gfilename)
			return;

		paths = self.listdir(gfilename)
		sorted(paths, reverse=True)
		for item in paths:
			if self.__object[item][u'mimeType']  == FOLDER:
				self.rmdir(item)
			else:
				self.deleteFileByPath(item)
		
	def deleteFileByPath(self, path):
		try:
			item = self.__object[path]
			if item[u'mimeType'] == FOLDER:
				print("Given path is of a folder, unable to delete.")
				return;
		except KeyError:
			print("File to be deleted is not present.")
			return;

                paths = self.__object[path]
                self.__connect.files().delete(fileId=paths[u'id']).execute()
                print ('File deleted %s' % paths[u'name'])
                del self.__object[path]
			

	def readFile(self):
		1;
	def writeFile(self):
		1;
	
	def printPaths(self):
		for item in sorted(self.__object.iterkeys()):
			print (item, self.__object[item][u'id'])	

	def printIDs(self):
		for item in sorted(self.__object.iterkeys()):
			
			print(item, self.__object[item][u'id'], self.__object[item][u'parents'])
	def getmetas(self):
		try:
			print("in getmetas")
			for item in self.__object.keys():
				value = self.__object[item]
				#print (value)	
				if  'cpp' in value[u'name']:
					print("CPPP found")
					self.getmetadata(value[u'id'])
					print("objects")
					print(value[u'mimeType'])				
					#self.getfilecontent(value[u'id']) 
				elif 'txt' in value[u'name'] or 'Manoj.txt' in value[u'name']:
					print("TXT found")
					self.getmetadata(value[u'id'])
					print("run time->%s"% self.__object[item])
					self.getfilecontent(value[u'id'])
					
					print("Deleted file!!!")
					self.deleteFile(value[u'id']);
					print("   Returned from delete. comnitnuing loop")
			print("Meta loop complete");	
			self.createFile('Manoj.txt', 'manoj-title', 'Its about shar', 'manoj.txt')
                        self.createFile('Manoj1.txt', 'manoj-title', 'Its about shar', 'manoj.txt')
                        self.createFile('Manoj2.txt', 'manoj-title', 'Its about shar', 'manoj.txt')
                        self.createFile('Manoj.txt', 'manoj-title', 'Its about shar', 'manoj.txt')
			self.deleteFileByPath('Manoj.txt')
			self.rmdir('satti')
			self.rmdir('satti/sonu1')
			self.rmdir('satti/sonu1/sharma')
			self.rmdir('satti/sonu1')
			self.rmdir('satti')
			#'''
			self.mkdir('satti')
			self.mkdir('satti/sonu1')
			self.mkdir('satti/sonu1/sharma')

			self.listdir('satti')
			self.createFile('satti/sonu1/sharma/Manoj.txt', 'manoj','ds','manoj.txt')
			self.createFile('satti/sonu1/Manoj.txt', 'manoj', 'ds', 'manoj.txt')
			
			self.movefile('satti/sonu1/sharma/Manoj.txt', 'satti/sonu1/Manoj.txt')
	
			self.rmdir('satti')
			self.recrrmdir('satti/sonu');
			self.recrrmdir('satti/sonu1');
                        self.mkdir('satti/sonu1/sharma2');
                        self.createFile('satti/sonu1/sharma2/Manoj.txt', 'manoj', 'ds', 'manoj.txt')
                        self.movefile('satti/sonu1/sharma2/Manoj.txt', 'satti/Manoj11.txt')
			self.movefile('satti/sonu1/Manoj.txt', 'Manoj10.txt')
			self.movefile('satti/sonu1/sharma2/Manoj.txt', 'Manoj10.txt')
			self.movefile('satti/Manoj11.txt', 'Manoj11.txt')	
			self.movefile('Manoj11.txt','satti/Manoj12.txt')
			'''
			self.copyfile('satti/sonu1/sharma2/Manoj.txt' , 'satti/sonu1/Manoj.txt')
			self.copyfile('satti/sonu1/Manoj.txt', 'satti/sonu1/sharma/Manoj.txt')		
			self.copyfile('satti/sonu1/sharma2/Manoj.txt','satti/Manoj.txt')
			self.copyfile('satti/sonu1/sharma2/Manoj.txt', 'Manoj10.txt')
			self.copyfile('satti/sonu1/sharma/Manoj.txt', 'satti/satti.txt')	
			'''
			print("end metas")
			print("!!!!!!!!!!!root_id%s" % self.__rootid)	
	        except Exception as ex:
	                #print("Error initializing the google drive handle!!")
        	        template = "Exception type {0} occurred. Arguments:\n{1!r}"
                	message  = template.format(type(ex).__name__, ex.args)
               		#print (message)

	def getparent(self, filename):
		try:
			if '/' in filename:
				item = filename.split('/')
				item = item[:-1]
				filename = '/'.join(item)
				item = self.__object[filename]
				return filename
			
		except KeyError:
			return None

	def getactualfilename(self, filename):
		if '/' in filename:
			item = filename.split('/')
			return item[-1]
		else:
			return filename

	def createFile(self, gfilename, title, description, filename, parent_id = None, mime_type = None):
		try:
			try:
				if parent_id != None or '/' in gfilename:
					parent 	   =  self.getparent(gfilename)
                                	
					if parent is None:
						print("Invalid path. Unable to create file")
						return;
						
				        parent_id = self.__object[parent][u'id']		
				item = self.__object[gfilename]
				print ("ITEM %s" % item)	
				if item:
					print("file already present. unable to create.")
					return;
			except KeyError:
				print(" Creating File ")
					
			print("In create file")
			media_body = MediaFileUpload(filename, mimetype=mime_type, resumable = True)
			body = {
		    	'title': title,
			'name': self.getactualfilename(gfilename),
		    	'description': description,
		    	'mimeType': mime_type
				}
			if parent_id:
		    		body['parents'] = [parent_id]
	
		
			file = self.__connect.files().create(
		        	body=body,
		        	media_body=media_body).execute()

		    	print ('File ID: %s' % file['id'])
			'''
			if parent_id:
				#prepare path
				item = self.getparentItemforId(parent_id)
				self.__object[item+'/'+gfilename] = file
			else:
			'''	
			self.__object[gfilename] = file
			
	  	    	return file
		except KeyError:
			print("problem key already present!! create file")
		except Exception as ex:
		    self.HandleException(ex)
		except errors.HttpError, error:
		    print ('An error occurred: %s' % error)
		    return None

        def getparentItemforId(self, parent_id):
                for item in self.__object:
                        value = self.__object[item]
                        if value[u'parents'] == id :
                                return item

	def getItemforId(self, id):
		for item in self.__object:
			value = self.__object[item]
			if value[u'id'] == id :
				return item
		return None;
 		 	
	def deleteFile(self, file_id):
		try:
			item = self.getItemforId(file_id)	
			if item is None:
				print ("No such file present to be deleted");
				return;
			self.__connect.files().delete(fileId=file_id).execute()
			print("deleted file")
			item = self.getItemforId(file_id)
			print("Deleting item from object: %s" % item);
			del self.__object[item]
			print("Deleting finished");		
		except Exception as ex:
			self.HandleException(ex)	


if __name__=='__main__':
	try:
        	config = json.load(open('config.json'))
		container = config[u'containers']
		g = GoogleDriveHandle(container[0]) 
		g.retrieveHierarchy();
		g.printPaths();	
		print("Get file")
		g.getCredentials(config)
		print("Credentials")
		g.getmetas()
		g.printPaths();	
		g.printIDs();	
 	except Exception as ex:
		#print("Error initializing the google drive handle!!")
	        template = "Exception type {0} occurred. Arguments:\n{1!r}"
	        message  = template.format(type(ex).__name__, ex.args)
	        #print (message)

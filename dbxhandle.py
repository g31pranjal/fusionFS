import dropbox
import json
import random
from dropbox import files
import pwd

class DbxHandle :

	def __init__(self, config) :
		self.__native = config
		self.__object = {}
		try :
			self.__connect = dropbox.Dropbox(config[u'auth'])
			self.__user = self.__connect.users_get_current_account()
			print("[self.__connecthandle] dbx:%s connected." % self.__native[u'name'])
		except dropbox.exceptions.AuthError :
			print("[self.__connecthandle] failed to establish connection.")
			raise dropbox.exceptions.AuthError
		except Exception as ex:
			print("[self.__connecthandle] error initializing the dbx handle.")
                        template = "Exception type {0} occurred. Arguments:\n{1!r}"
                        message  = template.format(type(ex).__name__, ex.args)
                        #print (message)
                        raise ex;

                self.__localUser = pwd.getpwnam('mk2sharm')

		#self.__housekeeping()


	def request(self, route, namespace, arg, arg_binary=None):
        	pass

        def HandleException(self, ex):
                template = "Exception type {0} occurred. Arguments:\n{1!r}"
                message  = template.format(type(ex).__name__, ex.args)
                print (message)

        def abspath(self, path) :
		if len(path) == 1 and path == '/':
			return ""  #self.__native['base']
		else:
			return path
		if 1:1
		elif self.__native['base'] not in path:
			return self.__native['base'] + path
		else:
			return path

	def retrieveHeirarchy(self) :

		lst = list()

		more = True;
		init = True;

		while(more) :
			if(init) :
				req = self.__connect.files_list_folder(self.__native[u'base'], recursive=True)
				cursor = req.cursor;
				init = False;
			else :
				req = self.__connect.files_list_folder_continue(cursor)
			more = req.has_more
			for entry in req.entries :
				print(entry.path_display)
				lst.append(entry.path_display)
		return lst


        def getattr(self, path):
                try:
			stats = {}
			path  = self.abspath(path)
			#print("dropbox getattr %s" % path)	
			if path != "":
				meta = self.__connect.files_get_metadata(path)
			if path == "":
                                #print ("this is a folder")      
                                stats['st_mode']   = 16895
                                stats['size']      = 4096
			
			elif (isinstance(meta, dropbox.files.FileMetadata)):
				#print("this is a file")
				stats['st_mode']   = 33277
				stats['size']	   = meta.size
			elif (isinstance(meta, dropbox.files.FolderMetadata)):
				#print ("this is a folder")	
				stats['st_mode']   = 16895
				stats['size']      = 4096
                        stats['st_uid']    = self.__localUser.pw_uid
                        stats['st_gid']    = self.__localUser.pw_gid
                        stats['st_mtime']   = 1543296474 + random.randint(1,101)
                        stats['st_atime']  = 1543296474
			
			return stats
		except Exception as ex:
			print("dropbox invalid path %s" % path)
			self.HandleException(ex)
			return None	
                except KeyError:
                        print("[gdrivehandle @ %s] Directory/file not found" % (self.native[u'name']))
                        return None
		
        def getactualfilename(self, filename):
               item = filename.split('/')
               return item[-1]

        def readdir(self, path):
                try:
			lst = []
			init = True
			more = True
			#if path == '/':
			#	return [self.getactualfilename(self.__native[u'base'])] 
			path = self.abspath(path)
			print("dropbox readdir() path %s" % path)
	                while(more) :
        	                if(init) :
				
         				req = self.__connect.files_list_folder(path, recursive=False)
                               	 	cursor = req.cursor;
                                	init = False;
                        	else :
                                	req = self.__connect.files_list_folder_continue(cursor)
                        	more = req.has_more
                        	for entry in req.entries :
                                	#print(entry.path_display)
					print(self.getactualfilename(entry.path_display))
					lst.append(self.getactualfilename(entry.path_display))
                                	#lst.append(entry.path_display)

			lst = lst + ['.','..']			
			sorted(lst);
			return lst
		except Exception as ex:
			print("drobpox path invalid %s" % path)
			return None;
                except KeyError:
                        print("[gdrivehandle @ %s] cannot list directory not found" % (self.native[u'name']))
                        return None
		
	def mkdirrec(self, path, mode):
		try:
			
			req = self.__connect.files_create_folder(path, False)
			#print ("dropbox mkdir folder %s" % path) 
			print(req)	
			return True	
		except Exception as ex:
			print("Dropbox folder already present");	
			self.HandleException(ex)	
			return None

        def rmdir(self, path):
		try:
			req = self.__connect.files_delete(path)
			#print("dropbox Path %s deleted" % path)
		except Exception as ex:
			print("dropbox Path %s not present" % path)
			self.HandleException(ex)
			return None


	def copy(self, src, dest):
		try:
			#print ("DROPBOX FILE COPY")
			req = self.__connect.files_copy(src, dest, True, True, True)
			#print("dropbox copied src %s to %s" , src, dest)
		except Exception as ex:

			self.HandleException(ex)
			return None
	
	def createFile(self, filename):
		try:
			#req = self.__connect.files_upload(0, filename, WriteMode('add'), False, None, None)
			req = self.__connect.files_upload('', filename)  #, "mode":"add")
			#print("dropbox created file %s" % filename)
		except Exception as ex:
			print("dropbox unable to create file %s" % filename)
			self.HandleException(ex)
			return None

	def rename(self, src, dest):
		try:
                        #print ("DROPBOX FILE MOVE ")

			req = self.__connect.files_move(src, dest, True, True, True) #, False, False, False)
			#print("Files moved from %s to %s" , src,  dest)	
		except Exception as ex:
			print("Dropbox invalid path provided %s to be moved" % src)
			self.HandleException(ex)

	def __housekeeping(self) :
		
		marker_search = self.__connect.files_search("", "fusion.marker", mode=dropbox.files.SearchMode('filename', None))
		if len(marker_search.matches) == 0 :
			print("[self.__connecthandle] marker not found.")
			raise Exception

			

	def getUserInfo(self) :
		return self.__user

		
if __name__ == '__main__':
	config = json.load(open('config.json'))
	container = config[u'containers']
	d = DbxHandle(container[0])
	d.readdir("")
	d.createFile("/manoj.txt")
	d.mkdir("/fusion")
	d.copy("/manoj.txt", "/fusion/")	
	#lst = d.get_file_names_to_move('/manoj1.txt', None)	
	#print (lst)
	d.move("/manoj.txt", "/manoj_drop")
	d.copy("/manoj_drop", "/fusion/manoj_text_copied")
	d.copy("/manoj_drop","/manojcopieed")
	d.copy("/manojcopieed", "/fusion-container/manoj_copy_text")
	d.copy("/manoj_drop", "/manoj_copy.txt")
	#d.retrieveHeirarchy()
	''''
	d.getattr('/fusion-container/costaa/js/liner.js')
	d.getattr('/fusion-container/costaa/js')
	d.getattr('/waterloo')
	d.getattr('/')
	d.readdir('/fusion-container')
	d.getattr('/fusion-container')	
	d.readdir('/fusion-container/costaa/js')
	d.copy('/fusion-container/costaa/js/', '/fusion-container/costaa')
	d.rmpath('/fusion-container/zzzzzz')
	d.mkdir('/fusion-container/zzzzzz')
	d.mkdir('/fusion-container/ma')
	d.mkdir('/fusion-container/sa')
	d.createFile('/fusion-container/manoj6.txt')
	d.move('/fusion-container/ma/manoj5.txt', '/home/fusion-container/sa/')	
	d.copy('/fusion-container/yyyyyy/manoj10.txt' , '/home/fusion-container/')
	d.readdir('/fusion-container/ma')
	d.readdir('/fusion-container/sa')
	d.copy('/fusion-container/ma/', '/fusion-container/')
	d.readdir("");	
	d.mkdir('/fusion-container/zzzzzz')
	d.getattr('/fusion-container/zzzzzz')	
	d.rmpath('/fusion-container/zzzzzz')
	d.getattr('/fusion-container/zzzzzz')
        d.mkdir('/fusion-container/zzzzzz')
	d.mkdir('/fusion-container/yyyyyy')
		
        d.createFile('/fusion-container/yyyyyy/manoj10.txt')

	d.copy('/fusion-container/yyyyyy/manoj10.txt' , '/fusion-container/zzzzzz/')
	d.readdir('/fusion-container/zzzzzz/')
	d.readdir('/fusion-container/yyyyyy/')
		
	d.createFile('/fusion-container/zzzzzz/manoj1.txt')
	d.readdir('/fusion-container/zzzzzz/')
	d.readdir('/fusion-container/yyyyyy/')
	d.move('/fusion-container/zzzzzz/manoj1.txt' , '/fusion-container/yyyyyy/')
        d.readdir('/fusion-container/yyyyyy/')
	d.readdir('/fusion-container/zzzzzz/')
	d.copy('/fusion-container/yyyyyy' , '/fusion-container/zzzzzz')
	d.readdir('/fusion-container/yyyyyy/')
        d.readdir('/fusion-container/zzzzzz/')
	'''	

import dropbox as dbx

handle = dbx.Dropbox('uHXPWn28nD4AAAAAAAAAYqp72JILeyO8L6TSDPXYGxLyKQdo3yT1v5otptaE_o-y')

for entry in handle.files_list_folder('').entries:
	print(entry)


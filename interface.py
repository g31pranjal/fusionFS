#!/usr/bin/env python

import os
import fusion
# import sys
# import errno
import fuse
import logging

class fuse_interface(fuse.LoggingMixIn, fuse.Operations) :

	def __init__(self) :
		self.__FD = 1
		self.__finstance = fusion.FusionFS();
		print("[interface] started FUSE instance at %s" % (mountpoint))
		pass


	def access(self, path, mode) :
		print("[interface] access, path -> %s, mode %d" % (path, mode))


	def chmod(self, path, mode):
		print("[interface] chmod, path -> %s, mode %d" % (path, mode))
		return self.__finstance.chmod(path, mode)


	# intercept owner change requests. 
	def chown(self, path, uid, gid):
		print("[interface] chown, path -> %s" % (path))


	def getattr(self, path, fh=None):
		print("[interface] getattr, path -> %s" % (path))
		a = self.__finstance.getattr(path)
		print a
		return a

		
	def readdir(self, path, fh) :
		print("[interface] readdir, path:%s" % (path) )
		dirents = []
		if self.__finstance.isDir(path) :
			lst = self.__finstance.readdir(path)
			dirents.extend(lst)
			# print dirents
		for r in dirents:
			yield r


# 	def readlink(self, path):
# 		print("method,readlink")
# 		pathname = os.readlink(self._full_path(path))
# 		if pathname.startswith("/"):
# 			# Path name is absolute, sanitize it.
# 			return os.path.relpath(pathname, self.root)
# 		else:
# 			return pathname

# 	def mknod(self, path, mode, dev):
# 		print("method,mknod")
# 		return os.mknod(self._full_path(path), mode, dev)

	def rmdir(self, path):
		print("[interface] rmdir, path:%s" % (path) )
		return self.__finstance.rmdir(path)

	def mkdir(self, path, mode):
		print("[interface] mkdir, path:%s" % (path) )
		return self.__finstance.mkdir(path, mode)

# 	def statfs(self, path):
# 		print("method,statfs")
# 		full_path = self._full_path(path)
# 		stv = os.statvfs(full_path)
# 		return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
# 			'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag',
# 			'f_frsize', 'f_namemax'))

	def unlink(self, path):
		print("[interface] unlink, path:%s" %(path))
		return self.__finstance.unlink(path)

# 	def symlink(self, name, target):
# 		print("method,symlink")
# 		return os.symlink(name, self._full_path(target))

	def rename(self, old, new):
		print("[interface] rename, path:%s to path:%s" % (old, new) )
		return self.__finstance.rename(old, new)


# 	def link(self, target, name):
# 		print("method,link")
# 		return os.link(self._full_path(target), self._full_path(name))

	def utimens(self, path, times=None):
		print("[interface] utimens, path:%s" % (path))
		return self.__finstance.utimens(path, times)

	def open(self, path, flags):
		print("[interface] open, path:%s" % (path) )
		self.__finstance.open(path, flags)
		self.__FD += 1
		return self.__FD
		# return os.open(full_path, flags)

	def create(self, path, mode, fi=None):
		print("[interface] create, path:%s" % (path) )
		self.__finstance.create(path, mode)
		self.__FD += 1
		return self.__FD
		# return os.open(full_path, os.O_WRONLY | os.O_CREAT, mode)

	def read(self, path, length, offset, fh):
		print("[interface] read, path:%s" % (path) )
		return self.__finstance.read(path, length, offset)

	def write(self, path, buf, offset, fh):
		print("[interface] write, path:%s" % (path) )
		return self.__finstance.write(path, buf, offset)

	# def truncate(self, path, length, fh=None):
	# 	print("[interface] truncate, path:%s" % (path))
	# 	self.__finstance.truncate(path, length)

	# no need for flushing, since every action on cotainer is discrete
	def flush(self, path, fh):
		pass

	# no need of handle release
	def release(self, path, fh):
		pass

	# no need for flushing, since every action on cotainer is discrete
	def fsync(self, path, fdatasync, fh):
		pass

def main(mountpoint):
	
	logging.basicConfig(level=logging.WARNING)

	try :
		fuse.FUSE(fuse_interface(), mountpoint, nothreads=True, foreground=True)
	except Exception as e:
		print("[interface] faulted : %s" % str(e))
		print("exiting.")
		exit()


if __name__ == '__main__':


	mountpoint = "~/fused"

	if not os.path.exists(mountpoint) :
		os.makedirs(mountpoint)

	main(mountpoint)


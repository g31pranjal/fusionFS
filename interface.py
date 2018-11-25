#!/usr/bin/env python

import os
import fusion
# import sys
# import errno
import fuse

class fuse_interface(fuse.LoggingMixIn, fuse.Operations) :

	def __init__(self) :
		self.__finstance = fusion.FusionFS();
		print("[interface] started FUSE instance at %s" % (mountpoint))
		pass

# 	# Helpers
# 	# =======

# 	def _full_path(self, partial):
# 		if partial.startswith("/"):
# 			partial = partial[1:]
# 		path = os.path.join(self.root, partial)
# 		return path

# 	# Filesystem methods
# 	# ==================

	def access(self, path, mode) :
		print("method,access")
		# full_path = self._full_path(path)
		# if not os.access(full_path, mode):
		# 	raise FuseOSError(errno.EACCES)
		# else :
		# 	print(os.access(full_path, mode))


# 	def chmod(self, path, mode):
# 		print("method,chmod")
# 		full_path = self._full_path(path)
# 		return os.chmod(full_path, mode)

# 	def chown(self, path, uid, gid):
# 		print("method,chown")
# 		full_path = self._full_path(path)
# 		return os.chown(full_path, uid, gid)


	def getattr(self, path, fh=None):
		print("[interface] getattr, path -> %s" % (path))
		return self.__finstance.getattr(path)

		
	def readdir(self, path, fh) :
		print("[interface] readdir, path:%s" % (path) )
		dirents = []
		if self.__finstance.isDir(path) :
			lst = self.__finstance.readdir(path)
			dirents.extend(lst)
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

# 	def rmdir(self, path):
# 		print("method,rmdir")
# 		full_path = self._full_path(path)
# 		return os.rmdir(full_path)

# 	def mkdir(self, path, mode):
# 		print("method,mkdir")
# 		return os.mkdir(self._full_path(path), mode)

# 	def statfs(self, path):
# 		print("method,statfs")
# 		full_path = self._full_path(path)
# 		stv = os.statvfs(full_path)
# 		return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
# 			'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag',
# 			'f_frsize', 'f_namemax'))

# 	def unlink(self, path):
# 		print("method,unlink")
# 		return os.unlink(self._full_path(path))

# 	def symlink(self, name, target):
# 		print("method,symlink")
# 		return os.symlink(name, self._full_path(target))

	def rename(self, old, new):
		print("[interface] rename, path:%s to path:%s" % (old, new) )
		return self.__finstance.rename(old, new)


# 	def link(self, target, name):
# 		print("method,link")
# 		return os.link(self._full_path(target), self._full_path(name))

# 	def utimens(self, path, times=None):
# 		print("method,utimens")
# 		return os.utime(self._full_path(path), times)

	# File methods
	# ============

	# def open(self, path, flags):
	# 	print("method,open")
	# 	full_path = self._full_path(path)
	# 	return os.open(full_path, flags)

	# def create(self, path, mode, fi=None):
	# 	print("method,create")
	# 	full_path = self._full_path(path)
	# 	return os.open(full_path, os.O_WRONLY | os.O_CREAT, mode)

	# def read(self, path, length, offset, fh):
	# 	print("method,read")
	# 	os.lseek(fh, offset, os.SEEK_SET)
	# 	return os.read(fh, length)

	# def write(self, path, buf, offset, fh):
	# 	print("method,write")
	# 	os.lseek(fh, offset, os.SEEK_SET)
	# 	return os.write(fh, buf)

	# def truncate(self, path, length, fh=None):
	# 	print("method,truncate")
	# 	full_path = self._full_path(path)
	# 	with open(full_path, 'r+') as f:
	# 		f.truncate(length)

	# def flush(self, path, fh):
	# 	print("method,flush")
	# 	return os.fsync(fh)

	# def release(self, path, fh):
	# 	print("method,release")
	# 	return os.close(fh)

	# def fsync(self, path, fdatasync, fh):
	# 	print("method,fsync")
	# 	return self.flush(path, fh)


def main(mountpoint):
	try :
		fuse.FUSE(fuse_interface(), mountpoint, nothreads=True, foreground=True)
	except Exception as e:
		print("[interface] faulted : %s" % str(e))
		print("exiting.")
		exit()


if __name__ == '__main__':


	mountpoint = "~/fuse"

	if not os.path.exists(mountpoint) :
		os.makedirs(mountpoint)

	main(mountpoint)
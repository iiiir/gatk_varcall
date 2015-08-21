import os, re

class File:
	'''
    ext: file extention
	path: full path + filename
	prefix: file name without .xxx
	absprefix: filename without .xxx plus path
	'''
	def __init__(self, path, name=None, iszipfile=False):
		fullpath  = str(path) if name is None else os.path.join(str(path), str(name))
		self.path = os.path.abspath(fullpath)
		self.dir  = os.path.dirname(self.path)
		self.name = os.path.basename(self.path)
		if iszipfile:
			nmatch  = re.match(r"(.+)\.([^.]+\.[^.]+)$", self.name)
		else:
			nmatch  = re.match(r"(.+)\.([^.]+)$", self.name)
		self.prefix = self.name if nmatch is None else nmatch.group(1)
		self.ext    = '' if nmatch is None else nmatch.group(2)
		self.absprefix = os.path.join(self.dir, self.prefix)

	def __str__(self):
		return self.path

	def chdir(self, dir):
		'''
		Change path of a file
		Return a NEW object
		'''
		return File(dir, self.name)

	def chext(self, ext):
		'''
		Change exptension name (e.g. fastq -> bam)
		Return a NEW object
		'''
		return File(self.absprefix+"."+ext)

	def exists(self):
		'''
		Cehck if file exists
		'''
		return os.path.exists(self.path)

	def desc():
		s=""
		members = [attr for attr in dir(self) if not callable(attr) and not attr.startswith("__")]
		for member in members:
			s += "%s:\t%s\n"%(member,getattr(self, member))
		return s

class Dir(File):

	def __init__(self, path, name=None):
		File.__init__(self, path, name)

	def mkdirs(self):
		if self.exists():
			return False
		else:
			os.makedirs(self.path)

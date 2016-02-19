#!/usr/bin/python
#
# Squid cache extractor v1.2
# Peter Pilarski

import sys
import os
from re import sub as re_sub
from mimetypes import guess_extension

class Squidce:
	def main(self):
		if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
			self.scExtract(os.path.realpath(sys.argv[1]))
		else:
			self.usage()
			sys.exit(1)

	def usage(self):
		print """Squid Content Extractor

Usage:
squidce.py <cache file>
	The only argument that this tool accepts is the filename of a squid
	cache file.
\nExamples:
	squidce.py ./squid/00/00/000000FF
	find ./squid/00 -type f -exec ./squidce.py '{}' \;
	for i in `grep -lir "example\.com" ./squid`; do ./squidce.py $i; done\n"""

	def scExtract(self, inFile):
		# Get name of this cache file
		sCName = inFile.split('/')[-1]
		# Don't process swap.state file, bad things happen
		# To do: write a test for valid spools instead.
		if sCName=="swap.state": return 0
		sCache=open(inFile,"rb").read()
		# URL is at offset 0x3C = 60 and is a null-terminated string
		cURL=sCache[60:sCache.find('\x00', 60)]
		print "Extracting: ", cURL
		# Content/header delimiter is 0d0a0d0a (CRLFx2)
		cOffset=sCache.find('\x0d\x0a\x0d\x0a')
		# Get MIME type/subtype
		typeOffset = sCache.find("Content-Type:")
		if typeOffset>0: cType = sCache[typeOffset+14:cOffset].split('\x0d\x0a')[0].split(';')[0]
		else: cType="application/octet-stream"
		# Get timestamp
		dateOffset=sCache.find("Date:")
		if dateOffset>0:cTime=sCache[dateOffset+6:sCache.find('\x0d\x0a', dateOffset)]
		else: cTime="NULL"
		# Get filename from URL
		cFName = cURL.split('#')[0].split('?')[0].split('&')[0].split('/')[-1]
		# Or use input filename, with extension from mimetype if found
		if not cFName or len(cFName)>255: 
			ext = guess_extension(cType, strict=True)
			if ext: cFName=sCName+ext
			else: cFName=sCName
		# Create output DIR
		if not os.path.exists('./extracted/'+sCName): os.makedirs('./extracted/'+sCName,0744)
		# Write header contents
		open('./extracted/'+sCName+'/header','wb').write(sCache[60:cOffset])
		# Write file contents
		open('./extracted/'+sCName+'/'+cFName,"wb").write(sCache[(cOffset+4):])
		# Write info to log file
		logFile = open('./extracted/squidce.log','a')
		logFile.write("%s: \n\t-Cache URL:\t%s\n\t-Saved as:\t%s(%s)\n\t-Timestamp:\t%s\n" % (sCName, cURL, cFName, cType, cTime))
		logFile.close()
		
Squidce().main()

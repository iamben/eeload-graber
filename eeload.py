#!/usr/local/bin/python
# -*- coding: utf8 -*-
import urllib, urllib2
import cookielib
import sys, time
import re

def chunk_report( bytes_so_far, chunk_size, total_size ):
	percent = float(bytes_so_far) / total_size
	percent = round(percent*100, 2)

	sys.stdout.write( "Downloaded %d of %d bytes (%0.2f%%)\r" %
		(bytes_so_far, total_size, percent) )

	if bytes_so_far >= total_size:
		sys.stdout.write('\n')

def chunk_read( response, fileName, chunk_size=8192, report_hook=None ):
	downloadDir = "./OP/"
	total_size = int( response.info().getheader('Content-Length').strip() )
	bytes_so_far = 0
	fp = open( downloadDir + fileName, "wb" )

	while True:
		chunk = response.read(chunk_size)
		bytes_so_far += len(chunk)

		if not chunk:
			break
		else:
			#write back
			fp.write( chunk )

		if report_hook:
			report_hook(bytes_so_far, chunk_size, total_size)

	fp.close()
	return bytes_so_far

def main():
	#main
	if len( sys.argv ) is not 2:
		sys.stderr.write( '[Usage] eeload.py DownloadURL\n' )
		exit(1)

	urlPrefix = "http://www.eeload.com"
	downloadPrefix = "http://www.eeload.com/Click/"
	cj = cookielib.CookieJar()
	downloadRegex = re.compile( "\"/down\.php\?[a-zA-Z0-9]+\"" )
	fileNameRegex = re.compile( "(?<=\<title\>)[^\s]+(avi|mkv|rar)", re.IGNORECASE )

	#url opener setup
	opener = urllib2.build_opener( urllib2.HTTPCookieProcessor( cj ) )
	opener.addheaders = [( 'User-agent', 'Mozilla/5.0' )]
	urllib2.install_opener( opener )

	#get download link and make cookie
	downloadRequest = urllib2.Request( sys.argv[1] )
	downloadResponse = urllib2.urlopen( downloadRequest ).read()
	downloadPage = downloadRegex.search( downloadResponse ).group()[1:-1]
	fileName = fileNameRegex.search( downloadResponse ).group()

	#fake cookie
	cj.set_cookie( cookielib.Cookie(version=0, name='ee_downtime', value=str(int(time.time())), port=None, port_specified=False, domain='.eeload.com', domain_specified=True, domain_initial_dot=True, path='/', path_specified=True, secure=False, expires=None, discard=False, comment=None, comment_url=None, rest={'HttpOnly': None}, rfc2109=False) )

	cookieReq = urllib2.Request(urlPrefix+downloadPage)
	cookieReq.add_header( 'Refer', sys.argv[1] )
	cj.add_cookie_header( cookieReq )
	urllib2.urlopen( cookieReq )		#get cookie from down.php

	fileReq = urllib2.Request(downloadPrefix+downloadPage.split("?")[1])
	fileReq.add_header( 'Refer', urlPrefix+downloadPage )
	cj.add_cookie_header( fileReq )
	fileStream = urllib2.urlopen( fileReq )

	print "Getting file %s..." % fileName
	chunk_read( fileStream, fileName, report_hook=chunk_report )



if __name__ == '__main__':
	main()


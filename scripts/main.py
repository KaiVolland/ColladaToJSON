################################################################################
#!c:\python27\python.exe
#
# Server side python execution using WSGI
# Author: Martin Christen, martin.christen@fhnw.ch
#
# Run this script then open your webbrowser and enter:
#   localhost:8000/?a=5
#   localhost:8000/?a=1&b=20
#   localhost:8000/?c=123
#
# or install apache with mod_wsgi and run it directly on your website!
#
# (c) 2012 by FHNW University of Applied Sciences and Arts Northwestern Switzerland
################################################################################

import os.path
import os
import sys
import cgi

sys.path.append("/var/www/converter/scripts/")

from daeConverter import *
import string
import zipfile
from cStringIO import StringIO
import time
import kmzConverter
import shutil


################################################################################
message_text = "empty!"
################################################################################

def application(environ, start_response):
    # emit status / headers


    form = cgi.FieldStorage(fp=environ['wsgi.input'],environ=environ)

    ##----------------------------------------------------------------------------------------------------------------------

    fileitem = form['datafile']

    # Test if the file was uploaded
    if fileitem.filename:
        # strip leading path from file name to avoid directory traversal attacks
        fn = os.path.basename(fileitem.filename)
        open(fn, 'wb').write(fileitem.file.read())
        message = 'The file "' + fn + '" was uploaded successfully'
    else:
        message = 'No file was uploaded'

    #---------------------------------------------------------------------------
    #check if input is correct!
    lng = float(form.getvalue("lng"))
    lat = float(form.getvalue("lat"))
    elv = float(form.getvalue("elv"))
    filename = form.getvalue("filename")
    prettyprint = form.getvalue("pretty")

    dir = 'tmpfolder'+str(time.time())
    dir = dir[:-3]
    diroriginal = dir+'/temp'
    dirnew = dir+'/out'
    os.mkdir(dir, 0777)
    os.mkdir(diroriginal, 0777)
    os.mkdir(dirnew, 0777)

    #check if it's a zip file...
    print fileitem.filename[-3:]
    if fileitem.filename[-3:]=='dae':
        convertedfilepath = convertCollada(fn,[lng,lat,elv],dirnew)


    elif fileitem.filename[-3:]=='kmz' or fileitem.filename[-3:]=='zip':
        kmzconv = kmzConverter.kmzConverter();
        convertedfilepath = kmzconv.convertKmz(fn,diroriginal,dirnew,fileitem.filename)
    else:
        print "filetype not suported"




    status = "200 OK"
    #headers = [ ('Content-Type', 'application/octet-stream'),
    #            ('Access-Control-Allow-Origin','*'),
    #            ('Content-Length',str(os.path.getsize(convertedfile)))]

    filename = convertedfilepath.split('/')
    filename = filename[-1]
    fin = open(convertedfilepath, "rb")
    size = os.path.getsize(convertedfilepath)
    headers = [   ('Content-Type', 'application/octet-stream'),
        ('Content-length', str(size)), ('Content-Disposition', 'attachment; filename='+filename)
    ]



    #headers = [('content-type', 'text/plain')]
    #todo: insert no-cache info into the header
    start_response(status, headers)
    return fin

    #delete the two folders
    shutil.rmtree(diroriginal)
    shutil.rmtree(dirnew)

#-------------------------------------------------------------------------------
# FOR STAND ALONE EXECUTION / DEBUGGING:
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    # this runs when script is started directly from commandline
    try:
        # create a simple WSGI server and run the application
        from wsgiref import simple_server
        print "Running test application - point your browser at http://localhost:8000/ ..."
        httpd = simple_server.WSGIServer(('', 8000), simple_server.WSGIRequestHandler)
        httpd.set_app(application)
        httpd.serve_forever()
    except ImportError:
        # wsgiref not installed, just output html to stdout
        for content in application({}, lambda status, headers: None):
            print content
#-------------------------------------------------------------------------------
			


__author__ = 'benjamin.loesch'
from daeConverter import *
import glob, os
import unzip
try:
    import xml.etree.cElementTree as ElementTree
except ImportError:
    import xml.etree.ElementTree as ElementTree
import re
import sys
from zipfile import BadZipfile, ZipFile
import daeConverter
import zipfile
import shutil

class kmzConverter:
    def __init__(self, verbose = False, percent = 10):
        self.verbose = verbose
        self.percent = percent


    def convertKmz(self, file, dir, dirout,fname):

        #extract the zip file to a folder
        un = unzip.unzip()
        un.extract(file,dir)


        #extract the lng,lat,elv form kml file
        for filename in glob.glob(dir+"/*.kml"):
            kmlfile = open(filename,'r')
            pos_ori = self.extractLocation(kmlfile)
            kmlfile.close()
            #kmlfile.delete()

        #search the colladafile
        for colladafilepath in glob.glob(dir+"/*/*.dae"):
            (path,name) = os.path.split(colladafilepath)
            convertCollada(colladafilepath,[float(pos_ori[0]),float(pos_ori[1]),float(pos_ori[2])],dirout) #writes the jsonfile into the extracted folder structure

        #copy all images in the output folder
        self.copyimages(dir,dirout,'jpg', 'png','gif','json') #add supporting filetypes here...

        dirred = dir.split("/")
        #store the jsonfile in a new zip file
        return self.zipper(dirout,dirred[0]+'/jsonzip.zip')


    def copyimages(self, dirsrc,dirdest,*args):
        for file in os.listdir(dirsrc):
            dirfile = os.path.join(dirsrc, file)
            if os.path.isfile(dirfile):
                if len(args) == 0:
                    fileList.append(dirfile)
                else:
                    if os.path.splitext(dirfile)[1][1:] in args:
                        shutil.copyfile(dirfile, os.path.join(dirdest, file))
            elif os.path.isdir(dirfile):
                print "Accessing directory:", dirfile
                self.copyimages(dirfile,dirdest, *args)
            else:
                pass



    # Function written by TomPayne camp2camp from
    # https://github.com/OpenWebGlobe/WebViewer/blob/minimal-example/scripts/kmz-extract-location.py
    def extractLocation(self, kmlfile):

        et = ElementTree.parse(kmlfile)
        namespace = re.match(r'\{(.*)\}', et.getroot().tag).group(1)
       # print 'Location:'
       # for location in et.findall('//{%s}Location' % namespace):
       #     print '\tLatitude: %s' % location.find('{%s}latitude' % namespace).text
       # print '\tLongitude: %s' % location.find('{%s}longitude' % namespace).text
       # print '\tAltitude: %s' % location.find('{%s}altitude' % namespace).text
       # print 'Orientation:'
       # for orientation in et.findall('//{%s}Orientation' % namespace):
       #     print '\tRoll: %s' % orientation.find('{%s}roll' % namespace).text
       # print '\tTilt: %s' % orientation.find('{%s}tilt' % namespace).text
       # print '\tHeading: %s' % orientation.find('{%s}heading' % namespace).text
        for location in et.findall('//{%s}Location' % namespace):
            lng = location.find('{%s}longitude' % namespace).text
            lat = location.find('{%s}latitude' % namespace).text
            elv = location.find('{%s}altitude' % namespace).text
        for orientation in et.findall('//{%s}Orientation' % namespace):
            yaw = orientation.find('{%s}heading' % namespace).text
            pitch = orientation.find('{%s}tilt' % namespace).text
            roll = orientation.find('{%s}roll' % namespace).text

        return [lng,lat,elv,yaw,pitch,roll]


    def zipper(self, dir, zip_file):
        zip = zipfile.ZipFile(zip_file, 'w', compression=zipfile.ZIP_DEFLATED)
        root_len = len(os.path.abspath(dir))
        for root, dirs, files in os.walk(dir):
            archive_root = os.path.abspath(root)[root_len:]
            for f in files:
                fullpath = os.path.join(root, f)
                archive_name = os.path.join(archive_root, f)
                print f
                zip.write(fullpath, archive_name, zipfile.ZIP_DEFLATED)
        zip.close()
        return zip_file




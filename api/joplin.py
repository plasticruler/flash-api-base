from flask_restful import Resource, reqparse
from run import app
import webdav.client as wc
import tempfile
import base64
import re
from os import listdir
from os.path import isfile, join

parser = reqparse.RequestParser()
parser.add_argument(
    'op', help="This field cannot be blank", required=True,location='args')
parser.add_argument('path',help='Remote path',required=False, location='args')
class DAVResource():
    @staticmethod
    def getWC():
        options = {
            'webdav_hostname':app.config['WEBDAV_HOST'],
            'webdav_login':app.config['WEBDAV_USERNAME'],
            'webdav_password':app.config['WEBDAV_PASSWORD'],
            'webdav_root':app.config['WEBDAV_ROOT'],
            'verbose': False
        }
        return wc.Client(options)

    @staticmethod
    def listcontents(remote_path):
        return DAVResource.getWC().list(remote_path)

    @staticmethod
    def downloadFile(remote_path,local_path):
        return DAVResource.getWC().download_sync(remote_path, local_path)
    @staticmethod
    def getFileContents(local_path):
        with open(local_path,'rb') as f:
            return f.read()
class JoplinMetaData(object):
    def __init__(self,contents):
        self.lines = contents.split('\n')
        self._title = self.lines[0]
        self._id = self.getProperty("id")
        self._is_todo = self.getProperty("is_todo")=="0"
        self._source = self.getProperty("source")
        self._parent_id = self.getProperty("parent_id")
        self._type = self.getProperty("type_")
        self._source_application = self.getProperty("source_application")
        self._source = self.getProperty("source")
        self._is_conflict = self.getProperty("is_conflict")
        self._user_updated_time = self.getProperty("user_updated_time")
    @property
    def user_updated_time(self):
        return self._user_updated_time
    @property
    def id(self):
        return self._id
    @property
    def is_conflict(self):
        return self._is_conflict==1
    @property
    def type_(self):
        return self._type
    @property
    def parent_id(self):
        return self._parent_id
    @property
    def source(self):
        return self._source
    @property
    def is_todo(self):
        return self._is_todo==1
    @property
    def title(self):
        return self._title

    def getProperty(self,propertyName):
        for l in self.lines[::-1]:
            if l.startswith("{}:".format(propertyName)):
                return l[l.find(":")+1:len(l)].strip()
        return None
  
class JoplinFile(Resource):
    def getFileContentsAsBase64(self,path):
        t = tempfile.NamedTemporaryFile(delete=True)
        DAVResource.downloadFile(path,t.name)
        try:
            with open(t.name, "rb") as i:
                s = base64.b64encode(i.read())
        finally:
            t.close()
        return s
    def get(self):  
        data = parser.parse_args()
        if data["op"] == "list":
            return {
            "message": "Ok",
            "data": DAVResource.listcontents(data['path'])
        }
        if data["op"] == "get-files":
            td = tempfile.mkdtemp("jpx13f")
            filesData = []
            DAVResource.getWC().pull(remote_directory=data['path'], local_directory=td)
            files = [f for f in listdir(td) if isfile(join(td,f))]
            for fileName in files:
                fileContents = DAVResource.getFileContents(join(td,fileName))
                jmd = JoplinMetaData(fileContents)
                filesData.append({"type":jmd.type_,"parent_id":jmd.parent_id, "user_updated_time":jmd.user_updated_time,"title":jmd.title,"id":jmd.id,"source":jmd.source,"source_application":jmd._source_application})
            return {
                "message":"Ok",
                "data": filesData
            }        
        if data["op"] == "downloadfile":
            return {
                "message": "Ok",
                "data" : self.getFileContentsAsBase64(data['path'])
            }
        if data["op"] == "jview":
            fileContents = self.getFileContentsAsBase64(data['path'])
            fileContents = base64.b64decode(fileContents)
            jmd = JoplinMetaData(fileContents)
            title = jmd.title
            return {
                "title":title,
                "doctype" : jmd.type_,
                "message" : "Ok"
            }
        if data["op"] == "viewfile":
            t = tempfile.NamedTemporaryFile(delete=True)
            DAVResource.downloadFile(data['path'], t.name)
            try:
                with open(t.name,"rb") as i:
                    s = i.read()
            finally:
                t.close()
            print s
            return {
                "message": "Ok",
                "data" : s
            }
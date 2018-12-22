from flask_restful import Resource, reqparse
from run import app
import webdav.client as wc
import tempfile
import base64

parser = reqparse.RequestParser()
parser.add_argument(
    'op', help="This field cannot be blank", required=True,location='args')
parser.add_argument('path',help='Remote folder',required=False, location='args')
class DAVResource():
    @staticmethod
    def getWC():
        options = {
            'webdav_hostname':app.config['WEBDAV_HOST'],
            'webdav_login':app.config['WEBDAV_USERNAME'],
            'webdav_password':app.config['WEBDAV_PASSWORD'],
            'webdav_root':app.config['WEBDAV_ROOT'],
            'verbose': True
        }
        return wc.Client(options)

    @staticmethod
    def listcontents(remote_path):
        return DAVResource.getWC().list(remote_path)

    @staticmethod
    def downloadFile(remote_path,local_path):
        print "Trying download of {}".format(remote_path)
        return DAVResource.getWC().download_sync(remote_path, local_path)

class WebDavFile(Resource):
    def get(self):  
        data = parser.parse_args()
        if data["op"] == "list":
            return {
            "message": "Ok",
            "data": DAVResource.listcontents(data['path'])
        } 
        if data["op"] == "downloadfile":
            t = tempfile.NamedTemporaryFile(delete=True)
            DAVResource.downloadFile(data['path'], t.name)
            try:
                with open(t.name, "rb") as i:
                    s = base64.b64encode(i.read())
            finally:
                t.close()
            return {
                "message": "Ok",
                "data" : s
            }
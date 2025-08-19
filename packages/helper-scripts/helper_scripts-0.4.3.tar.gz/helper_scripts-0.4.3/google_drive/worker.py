import mimetypes
from googleapiclient.errors import HttpError
from google_drive import get_service
from googleapiclient.http import MediaFileUpload
import io
from datetime import datetime as dt

from os import path,getcwd

_mimetypes_ = {
    'xlsx':'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'csv':'text/csv',
    'xls':'application/vnd.ms-excel',
    'pdf':'application/pdf'
}

class worker():
    scope_readonly = 'https://www.googleapis.com/auth/drive.metadata.readonly'
    scope_write = 'https://www.googleapis.com/auth/drive'
    initial_download_path = getcwd()

    def __init__(self,api_name='drive',api_version='v3',key_file_location='') -> None:
        self.api_name = api_name
        self.api_version = api_version
        self.key_file_location = key_file_location

    def construct_service(self,scope:str =None):
        service = get_service(
            api_name=self.api_name,
            api_version=self.api_version,
            scopes=[scope],
            key_file_location=self.key_file_location)
        return service
        
    def read_drive_files(self,scope=scope_readonly,file_id:str = None,filename:str = None, ignore_trashed=True):
        apply_query = False
        is_id_search = False

        try:
            service = self.construct_service(scope=scope)

            query_name_filter = f"name contains '{filename}'"

            query_trash_filter = "trashed=false"

            if filename is not None and ignore_trashed == True:
                query_filter = f"{query_name_filter} and {query_trash_filter}"
                apply_query=True

            if filename is not None and ignore_trashed == False:
                query_filter = f"{query_name_filter}"
                apply_query = True

            fetched_items = False

            if file_id is not None:
                file_id = str(file_id)
                file_by_id = service.files().get(fileId=file_id).execute()
                files = {"files": [file_by_id]}
                is_id_search = True

            if is_id_search != True:
                if apply_query:
                    files = service.files().list(q=query_filter).execute()
                else:
                    files = service.files().list().execute()

            json_files_array = files.get('files')
            if json_files_array:
                fetched_items = True

            if not fetched_items:
                return {'code':200,'items':[]}
            
            return {'code':200,'items':json_files_array}


        except HttpError as error:
            # TODO
            return {'code':-999,'error':error}

    def download_drive_file(self,file_id = None,download_path=initial_download_path,filename=None,scope=scope_write,export=False,filetype=None,mimetype=None,export_name=None):
        if file_id is None and filename is None:
            return {'code':-999,'error':'file_id or filename must be provided'}
        
        if file_id is not None and filename is not None:
            return {'code':-999,'error':'both file_id and filename can\'t be used'}
        
        res_file_ids = []
        res_filenames = []
        try:
            service = self.construct_service(scope=scope)

            if filename is not None:
                response = self.read_drive_files(filename=filename)
                code = response['code']
                if code != 200:
                    return response
                
                files = response['items']
                for file in files:
                    res_file_ids.append(file['id'])
                    res_filenames.append(file['name'])

            if file_id is not None:
                response = self.read_drive_files(file_id=file_id)
                code = response['code']
                if code != 200:
                    return response
                
                files = response['items']
                for file in files:
                    res_file_ids.append(file['id'])
                    res_filenames.append(file['name'])

            for res_file_id in res_file_ids:
                idx = res_file_ids.index(res_file_id)
                res_filename = res_filenames[idx]

                if export:
                    config_filetype = filetype
                    config_mimetype = mimetype
                    if config_filetype == None and config_mimetype == None:
                        return {'code':-999,'error': "Both mimetype and filetype can't be none"}

                    if config_mimetype is None:
                        _mimetype_ = _mimetypes_[config_filetype]
                    else:
                        _mimetype_ = config_mimetype

                    if config_filetype is None:
                        if _mimetype_ is not None:
                            for key,value in _mimetypes_.items:
                                if value == _mimetype_.lower():
                                    config_filetype = key
                                    break
                        else:
                            return {'code':-999,'error':"Unble to detect file type. Please specify it"}


                    request = service.files().export_media(fileId=file_id, mimeType=_mimetype_).execute()
                    if str(config_filetype).startswith('.'):
                        config_filetype = config_filetype[1]

                    if export_name is not None:
                        res_filename = f'{export_name}.{str(config_filetype)}'
                    else:
                        res_filename = f'{config_filetype}.{str(config_filetype)}'
                else:
                    request = service.files().get_media(fileId=res_file_id).execute()

                file_bytes = io.BytesIO(request)

                full_download_path = path.join(download_path, res_filename)
            
                if path.exists(full_download_path):
                    current_datetime = dt.now()
                    current_datetime_str = current_datetime.strftime('%Y%m%d%H%M%S')
                    full_download_path = path.join(download_path,current_datetime_str+"_"+res_filename)

                    
                with open(full_download_path, 'wb') as f:
                    f.write(file_bytes.getbuffer())

            return {'code':200,'message':'download complete'}

        except HttpError as error:
            return {'code':-999,'error':error}
        

    def upload_file_to_drive(self,scope=scope_write,filename=None,file_path=None,parent_folder_id=None,mimetype=None,coerce=True):
        
        try:
            service = self.construct_service(scope=scope)
            # TODO check if the file exists in the service in a given parent folder
            # current_datetime = dt.now()
            # current_datetime_str = current_datetime.strftime('%Y%m%d%H%M%S')

            file_metadata = {
                'name': filename
            }
            if parent_folder_id:
                file_metadata['parents'] = [parent_folder_id]

            if mimetype is None:
                mimetype = mimetypes.guess_type(file_path)[0]

            media = MediaFileUpload(file_path,resumable=True,mimetype=mimetype)
            file = service.files().create(body=file_metadata,
                media_body=media,fields='id').execute()
            
            return {'code':200,'message':'upload complete'}
            
        except HttpError as error:
            return {'code':-999,'error':error}
        
    def get_file_permissions(self,file_id=None):
        try:
            service = self.construct_service(scope=self.scope_write)
            request = service.permissions().list(fileId=file_id).execute()
            return {'code':200,'item':request}

        except HttpError as error:
            return {'code':-999,'error':error}
        
    def delete_drive_files(self,file_ids:list=[],reset=False):
        drive_files = []

        if len(file_ids)==0 and reset == False:
            return {'code':-999,'message':'file_ids is empty'}

        try:
            service = self.construct_service(scope=self.scope_write)

            if (file_ids is None or len(file_ids) == 0) and reset == True:
                response = self.read_drive_files(ignore_trashed=False)
                code = response['code']
                if code != 200:
                    return response
                
                files = response['items']
                for file in files:
                    drive_files.append(file['id'])

            else:
                drive_files = file_ids
            
            n=0
            errors = []
            for file_id in drive_files:
                try:
                    service.files().delete(fileId=file_id).execute()
                    n+=1
                except HttpError as error:
                    errors.append(error)
                    

            return {'code':200,'message':f'{n} files deleted','errors':errors}

        except HttpError as error:
            return {'code':-999,'error':error}
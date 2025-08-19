import os
import json
from office365.sharepoint.client_context import ClientContext
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.files.file_creation_information import FileCreationInformation

class Sharepoint:
    def __init__(self, url, client, secret):
        self.url = url
        context_auth = AuthenticationContext(authority_url=url)
        context_auth.acquire_token_for_app(client_id=client, client_secret=secret)
        self.ctx = ClientContext(self.url, context_auth)

    def _open_binary(self, rel_url, file_name):
        """
        Abrimos el archivo binario
        :param rel_url:
        :param file_name:
        :return:
        """
        url = fr"{self.url}/_api/web/GetFolderByServerRelativeUrl('{rel_url}')/Files('{file_name}')/$value"
        request = RequestOptions(url)
        request.method = HttpMethod.Get
        response = self.ctx.execute_request_direct(request)
        return response

    def upload_file(self, file_name, directory):
        """
        Subimos un Arhcivo a SharePoint
        :param file_name: Nombre del Archivo a subir
        :param directory: Directorio Donde queremos subir el Archivo Ej. {instance}.upload_file(local_path, '/sites/site_name/Folcer/SubFolcer/...')
        :return:
        """
        cargado = False
        try:
            if os.path.isfile(file_name):
                file_content = open(file_name, 'rb')
                file_info = FileCreationInformation()
                file_info.content = file_content
                file_info.overwrite = True
                file_info.url = os.path.basename(file_name)
                self.ctx.web.get_folder_by_server_relative_url(directory).files.add(file_info)
                self.ctx.execute_query()
                cargado = True
            else:
                print(f"El Archivo {file_name} NO existe")
        except Exception as e:
            print(e)

        return cargado

    def download_file(self, file_name, directory, localdir=os.path.join(os.getcwd(), 'download')):
        """
        Descargamos el Archivo desde SharePoint
        El archivo se descarga en la carpeta donde se esta ejecutando el Script
        :param directory: Directorio de donde descargar el Archivo
        :param file_name: Nombre del archivo a descargar
        :param localdir: Directorio local para almacenar
        :return:
        """
        descargado = False
        try:
            # Abrimos de forma binaria el Archivo que queremos descargar
            url = f"{self.url}/_api/web/GetFolderByServerRelativeUrl('{directory}')/Files('{file_name}')/$value"
            request = RequestOptions(url)
            request.method = HttpMethod.Get
            response = self.ctx.execute_request_direct(request)

            # Verificamos que la descarga se haya hecho de forma correcta
            if str(response) != "<Response [404]>":
                file_path = os.path.join(localdir, file_name)
                with open(file_path, 'wb') as local_file:
                    local_file.write(response.content)
                    local_file.close()
                descargado = True
            else:
                print(f"No se encontro el Archivo con el Nombre: {file_name} dentro de la Carpeta: {directory}")
        except Exception as e:
            print(e)

        return descargado

    def download_folder(self, directory, localdir=os.path.join(os.getcwd(), 'assets', 'download')):
        """
        Descargamos el Folder desde SharePoint
        El archivo se descarga en la carpeta donde se esta ejecutando el Script
        :param directory: Directorio de donde descargar el Archivo
        :param file_name: Nombre del archivo a descargar
        :param localdir: Directorio local para almacenar
        :return:

        /Web/GetFolderByServerRelativeUrl('/" + path + "')/Files
        """
        descargado = False
        try:
            url = f"{self.url}/_api/web/GetFolderByServerRelativeUrl('{directory}')/Files"
            print(url)
            request = RequestOptions(url)
            request.method = HttpMethod.Get
            directory_root = self.ctx.execute_request_direct(request)

            res = json.loads(directory_root.content)
            files = res['d']["results"]
            for file in files:
                self.download_file(directory, file["Name"], localdir)
                #self.delete_file(os.path.join("/".join(directory.split('/')[-3:]), file["Name"]))
            descargado = True

        except Exception as e:
            print(e)

        return descargado

    def make_folder(self, directory, new_directory):
        """
        Creamos una carpeta nueva en SharePoint
        :param directory: Directorio sobre el cual vamos a hacer el nuevo Directorio
        :param new_directory: Nombre del nuevo Directorio
        :return:
        """
        creado = False
        try:
            self.ctx.web.folders.add(f"{directory}/{new_directory}")
            self.ctx.execute_query()
            creado = True
        except Exception as e:
            print(e)

        return creado

    def list_folders(self, directory):
        """
        Colocamos en una lista, todos los folders de un Directorio
        :param directory: Ruta del Directorio a examinar
        :return:
        """
        folders = []
        try:
            directory_root = self.ctx.web.get_folder_by_server_relative_url(directory)
            self.ctx.load(directory_root)
            self.ctx.execute_query()

            folders_temp = directory_root.folders
            self.ctx.load(folders_temp)
            self.ctx.execute_query()

            for myfolder in folders_temp:
                print(f"Nombre del Folder: {myfolder.properties['ServerRelativeUrl']}")
                folders.append(myfolder.properties['ServerRelativeUrl'])
        except Exception as e:
            print(e)

        return folders

    def list_files(self, directory):
        """
        Colocamos en una lista, todos los archivos de un Directorio
        :param directory: Ruta del Directorio a examinar
        :return:
        """
        files = []
        try:
            directory_root = self.ctx.web.get_folder_by_server_relative_url(directory)
            self.ctx.load(directory_root)
            self.ctx.execute_query()

            files_temp = directory_root.files
            self.ctx.load(files_temp)
            self.ctx.execute_query()

            for myfile in files_temp:
                print(f"Nombre del Archivo: {myfile.properties['ServerRelativeUrl']}")
                files.append(myfile.properties["ServerRelativeUrl"])
        except Exception as e:
            print(e)

        return files

    def is_directory(self, directory):
        """
        Verificamos si un Directorio ya existe
        :param directory: Directorio a comprobar si ya existe
        :return:
        """
        existe = False
        try:
            folder = self.ctx.web.get_folder_by_server_relative_url(directory)
            self.ctx.load(folder)
            self.ctx.execute_query()
            existe = True
        except Exception as e:
            print("Directory not Found: {}".format(directory))
            print(e)

        return existe

    def is_file(self, file_name, site_name):
        """
        Verificamos si un archivo ya existe en una determinada carpeta
        :param file_name: Archivo a verificar si ya existe
        :return:
        """
        existe = False
        try:
            new_file_name = file_name if file_name.find(f"/sites/{site_name}/") != -1 else f"/sites/{site_name}/{file_name}"
            file = self.ctx.web.get_file_by_server_relative_url(new_file_name)
            self.ctx.load(file)
            self.ctx.execute_query()
            existe = True
        except Exception as e:
            print(e)

        return existe

    def move_file(self, source_file, destination_file, site_name):
        """
        Movemosun archivo o un lugar diferente
        :param source_file: Ruta del Archivo que se va a Mover
        :param destination_file: Ruta del Archivo donde va a quedar
        :return:
        """
        try:
            new_sfile_name = source_file if source_file.find(f"/sites/{site_name}/") != -1 else f"/sites/{site_name}/{source_file}"
            new_dfile_name = destination_file if destination_file.find(f"/sites/{site_name}/") != -1 \
                else f"/sites/{site_name}/{destination_file}"

            obj_sf = self.ctx.web.get_file_by_server_relative_url(new_sfile_name)
            obj_sf.moveto(new_dfile_name, 1)
            self.ctx.execute_query()
        except Exception as e:
            print(e)

    def delete_file(self, file_name, site_name):
        """
        Eliminamos un archivo de una Ruta
        :param file_name: Ruta del Archivo a eliminar
        :return:
        """
        try:
            new_sfile_name = file_name if file_name.find(f"/sites/{site_name}/") != -1 else f"/sites/{site_name}/{file_name}"
            file_to_delete = self.ctx.web.get_file_by_server_relative_url(new_sfile_name)
            file_to_delete.delete_object()
            self.ctx.execute_query()
        except Exception as e:
            print(e)

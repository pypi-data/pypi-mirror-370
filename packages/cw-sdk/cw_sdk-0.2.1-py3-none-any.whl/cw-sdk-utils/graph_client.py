import http.client
import json
import msal
import os
import urllib.parse
import logging
from urllib.parse import quote

SHAREPOINT_SITE = os.getenv('sharepoint_site_name')
SHAREPOINT_SITE_LEGALES = os.getenv('sharepoint_site_name_legales')

class SharePointGraph:
    def __init__(self):
        self.SECRETID = None
        self.APPID = None
        self.TENANTID = None
        self.token = None
        self.site_id = None
        self.drive_id = None
        self.item_id = None
    
    def _az_auth(self, secret_id, app_id, tenant_id):
        self.SECRETID = secret_id
        self.APPID = app_id
        self.TENANTID = tenant_id

    def get_token(self):
        try:
            authority = f'https://login.microsoftonline.com/{self.TENANTID}'
            app = msal.ConfidentialClientApplication(
                self.APPID, authority=authority, client_credential=self.SECRETID)
            access_token = app.acquire_token_for_client(scopes=['https://graph.microsoft.com/.default'])
            self.token = access_token['access_token']
            logging.info(f"🔐 Access Token: {self.token}")
        except Exception as e:
            logging.error(f"❌ Error al obetener Token: {e}")
            raise ValueError(f"❌ Error al obetener Token: {e}")

    def get_site_id(self, context="cw"):
        try:
            site = SHAREPOINT_SITE if context == 'cw' else SHAREPOINT_SITE_LEGALES
            conn = http.client.HTTPSConnection("graph.microsoft.com")
            headers = {'Authorization': f'Bearer {self.token}'}
            conn.request("GET", f"/v1.0/sites/customswatch.sharepoint.com:/sites/{site}", '', headers)
            data = json.loads(conn.getresponse().read().decode("utf-8"))
            self.site_id = data["id"].split(',')[1]
            logging.info(f"🔐 Site ID ({site}): {self.site_id}")
        except Exception as e:
            logging.error(f"❌ Error al obetener Site ID: {e}")
            raise ValueError(f"❌ Error al obetener Site ID: {e}")
    
    def get_drive_id(self, context="cw"):
        try:
            site = SHAREPOINT_SITE if context == 'cw' else SHAREPOINT_SITE_LEGALES
            conn = http.client.HTTPSConnection("graph.microsoft.com")
            headers = {'Authorization': f'Bearer {self.token}'}
            conn.request("GET", f"/v1.0/sites/{self.site_id}/drives", '', headers)
            data = json.loads(conn.getresponse().read().decode("utf-8"))
            self.drive_id = data["value"][2]['id']
            logging.info(f"🔐 Drive ID ({site}): {self.drive_id}")
        except Exception as e:
            logging.error(f"❌ Error al obetener Drive ID: {e}")
            raise ValueError(f"❌ Error al obetener Drive ID: {e}")
    
    def get_item_id(self, base_path, context="cw"):
        try:
            site = SHAREPOINT_SITE if context == 'cw' else SHAREPOINT_SITE_LEGALES
            conn = http.client.HTTPSConnection("graph.microsoft.com")
            headers = {'Authorization': f'Bearer {self.token}'} 
            encoded_path = quote(base_path.split(',')[:-1])
            conn.request("GET", f"/v1.0/drives/{self.drive_id}/root:/{encoded_path}:/children", '', headers)
            data = json.loads(conn.getresponse().read().decode("utf-8"))
            self.item_id = [item for item in data['value'] if item['name'].strip().lower() == base_path.split("/")[-1].strip().lower()][0]['id']
            logging.info(f"Item ID ({site}/{base_path}): {self.item_id}")
        except Exception as e:
            logging.error(f"❌ Error al obetener Item ID: {e}")
            raise ValueError(f"❌ Error al obetener Item ID: {e}")


    def _auth(self, base_path, context="cw"):
        try:
            self.get_token()
            self.get_site_id(context)
            self.get_drive_id(context)
            self.get_item_id(base_path, context)
        except Exception as e:
            logging.error(f"❌ Error en autenticación Graph: {e}")
            raise ValueError(f"❌ Error en autenticación Graph: {e}")
    
    def check_dir(self, folder_name, base_path, context="cw"):
        try:
            if not all([self.token, self.drive_id]):
                self._auth(base_path, context)
        
            conn = http.client.HTTPSConnection("graph.microsoft.com")
            headers = {'Authorization': f'Bearer {self.token}'}
        
            url = f"/v1.0/drives/{self.drive_id}/root:/{quote(base_path)}:/children"
        
            while url:
                conn.request("GET", url, '', headers)
                resp = conn.getresponse()
                data = json.loads(resp.read().decode("utf-8"))
        
                for item in data.get('value', []):
                    if item['name'].strip().lower() == folder_name.strip().lower():
                        logging.info(f"✅ La carpeta '{folder_name}' ya existe.")
                        return True
        
                # Si hay más páginas, seguir
                url = None
                if '@odata.nextLink' in data:
                    next_url = data['@odata.nextLink']
                    # Remover dominio para reutilizar conn
                    url = next_url.replace("https://graph.microsoft.com", "")
        
            logging.info(f"⚠️ La carpeta '{folder_name}' NO existe.")
            return False
        except Exception as e:
            logging.error(f"❌ Error en en la corroboracion de carpeta con Graph: {e}")
            raise ValueError(f"❌ Error en en la corroboracion de carpeta con Graph: {e}")

    def mk_dir(self, folder_name, base_path, context="cw"):
        try:
            if not all([self.token, self.drive_id, self.item_id]):
                self._auth(base_path, context)

            conn = http.client.HTTPSConnection("graph.microsoft.com")
            payload = json.dumps({
                "name": folder_name,
                "folder": {},
                "@microsoft.graph.conflictBehavior": "rename"
            })
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
            conn.request("POST", f"/v1.0/drives/{self.drive_id}/items/{self.item_id}/children", payload, headers)
            data = json.loads(conn.getresponse().read().decode("utf-8"))
            logging.info(f"📁 Carpeta creada: {data['name']}")
            return data["name"]
        except Exception as e:
            logging.error(f"❌ Error creando carpeta: {e}")
            return None
    
    def download_file(self, base_path, file_name, context="cw"):
        try:
            if not all([self.token, self.drive_id]):
                self._auth(base_path, context)
    
            conn = http.client.HTTPSConnection("graph.microsoft.com")
            headers = {
                "Authorization": f"Bearer {self.token}"
            }
    
            # Ruta al archivo
            route = f"/v1.0/drives/{self.drive_id}/root:/{base_path}/{file_name}:/content"
            conn.request("GET", route, headers=headers)
            response = conn.getresponse()
    
            if 200 <= response.status < 300:
                logging.info(f"📄 Archivo '{file_name}' descargado correctamente.")
                return response.read()  # Retorna los bytes del archivo
            else:
                raise Exception(f"❌ Error al descargar archivo '{file_name}': {response.status} {response.read().decode()}")
        except Exception as e:
            logging.error(f"❌ Error en download_file: {e}")
            return None
    
    def upload_file(self, base_path, file_name, content_bytes, context='cw'):
        try:
            if not all([self.token, self.drive_id]):
                self._auth(base_path, context)
    
            conn = http.client.HTTPSConnection("graph.microsoft.com")
            endpoint = f"/v1.0/drives/{self.drive_id}/root:/{urllib.parse.quote(base_path + '/' + file_name)}:/content"
            conn.request("PUT", endpoint, body=content_bytes, headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/octet-stream"
            })
    
            response = conn.getresponse()
            if response.status >= 200 and response.status < 300:
                logging.info(f"✅ Archivo '{file_name}' subido correctamente.")
            else:
                raise ValueError(f"❌ Error subiendo archivo '{file_name}': {response.status} {response.read().decode()}")
        except Exception as e:
            logging.error(f"❌ Error en upload_file: {e}")
            raise ValueError(f"❌ Error subiendo archivo '{file_name}': {response.status} {response.read().decode()}")
    
    def del_file(self, filename, base_path, context="cw"):
        try:
            if not all([self.token, self.drive_id]):
                self._auth(base_path, context)

            deleted = 0
            deleted_files = []
            self._auth(base_path, context)

            conn = http.client.HTTPSConnection("graph.microsoft.com")
            headers = {'Authorization': f'Bearer {self.token}'}

            route_api = f"/v1.0/drives/{self.drive_id}/root:/Datos/ADUANAS/Robot:/children"

            while route_api:
                conn.request("GET", route_api, '', headers)
                resp = conn.getresponse()
                data_api = json.loads(resp.read().decode("utf-8"))

                for api in data_api.get('value', []):

                    dir = api['name']
                    dir_encoded = urllib.parse.quote(dir)

                    route = f"/v1.0/drives/{self.drive_id}/root:/Datos/ADUANAS/Robot/{dir_encoded}:/children"

                    while route:
                        conn.request("GET", route, '', headers)
                        resp = conn.getresponse()
                        data = json.loads(resp.read().decode("utf-8"))
                        for file in data.get('value', []):
                            if filename in file['name']:
                                conn.request("DELETE", f"/v1.0/drives/{self.drive_id}/items/{file['id']}", '', headers)
                                conn.getresponse()
                                logging.info(f"🗑️ Archivo eliminado: {file['name']}")
                                deleted_files.append(file['name'])
                                deleted += 1
                        # Si hay más páginas, seguir
                        route = None
                        if '@odata.nextLink' in data:
                            next_url = data['@odata.nextLink']
                            # Remover dominio para reutilizar conn
                            route = next_url.replace("https://graph.microsoft.com", "")

                # Si hay más páginas, seguir
                route_api = None
                if '@odata.nextLink' in data_api:
                    next_url = data_api['@odata.nextLink']
                    # Remover dominio para reutilizar conn
                    route_api = next_url.replace("https://graph.microsoft.com", "")

            return deleted_files
        except Exception as e:
                    logging.error(f"❌ Error al eliminar archivos en {api.get('name')}: {e}")
    
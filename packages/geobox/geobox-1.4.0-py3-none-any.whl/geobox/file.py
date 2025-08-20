from urllib.parse import urljoin
from typing import Optional, Dict, List, Union, TYPE_CHECKING
import os
import mimetypes
from geobox.exception import ValidationError
import requests
import sys
from pathlib import Path

from .base import Base
from .enums import FileFormat, PublishFileType, InputGeomType, FileType
from .utils import clean_data
from .task import Task
from .feature import Feature

if TYPE_CHECKING:
    from . import GeoboxClient 
    from .user import User

class File(Base):
    """
    A class to interact with files in Geobox.

    This class provides functionality to interact with files in Geobox.
    It supports various operations including CRUD operations on files, as well as advanced operations like publishing, and sharing files.
    It also provides properties to access the file data, and a method to download the file.
    """
    BASE_ENDPOINT: str = 'files/'

    def __init__(self, 
                api: 'GeoboxClient', 
                uuid: str, 
                data: Optional[Dict] = {}):
        """
        Constructs all the necessary attributes for the File object.

        Args:
            api (Api): The API instance.
            uuid (str): The UUID of the file.
            data (Dict, optional): The data of the file.
        """
        super().__init__(api, uuid=uuid, data=data)


    def __repr__(self) -> str:
        """
        Return a string representation of the File object.

        Returns:
            str: A string representation of the File object.
        """
        return f"File(uuid={self.uuid}, file_name={self.name}, file_type={self.file_type.value})"


    @property
    def layers(self) -> List[Dict]:
        """
        Get the layers of the file.

        Returns:
            List[Dict]: The layers of the file.
        
        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> file = File.get_file(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> file.layers
        """
        return self.data.get('layers', {}).get('layers', [])


    @property
    def file_type(self) -> 'FileType':
        """
        Get the file type

        Returns:
            FileType: the file type enumeration

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> file = File.get_file(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> file.file_type
        """
        return FileType(self.data.get('file_type'))


    @classmethod
    def upload_file(cls, api: 'GeoboxClient', path: str, user_id: int = None, scan_archive: bool = True) -> 'File':
        """
        Upload a file to the GeoBox API.

        Args:
            api (GeoboxClient): The API instance.
            path (str): The path to the file to upload.
            user_id (int, optional): specific user. privileges required.
            scan_archive (bool, optional): Whether to scan the archive for layers. default: True

        Returns:
            File: The uploaded file instance.

        Raises:
            ValueError: If the file type is invalid.
            FileNotFoundError: If the file does not exist.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.file import File
            >>> client = GeoboxClient()
            >>> file = File.upload_file(client, path='path/to/file.shp')
            or
            >>> file = client.upload_file(path='path/to/file.shp')
        """
        # Check if the file exists
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")

        # Check if the file type is valid
        FileFormat(os.path.splitext(path)[1])

        data = clean_data({
            "user_id": user_id,
            "scan_archive": scan_archive
        })
        
        endpoint = cls.BASE_ENDPOINT
        with open(path, 'rb') as f:
            files = {'file': f}
            file_data = api.post(endpoint, data, is_json=False, files=files)
        return cls(api, file_data['uuid'], file_data)


    @classmethod
    def get_files(cls, api:'GeoboxClient', **kwargs) -> Union[List['File'], int]:
        """
        Retrieves a list of files.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.

        Keyword Args:
            q (str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'"
            search (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): comma separated list of fields for searching
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D.NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): if true, the total number of results will be returned. default is False.
            skip (int): number of results to skip. default is 0.
            limit (int): number of results to return. default is 10.
            user_id (int): filter by user id.
            shared (bool): Whether to return shared files. default is False.
            
        Returns:
            List[File] | int: A list of File objects or the total number of results.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.file import File 
            >>> client = GeoboxClient()
            >>> files = File.get_files(client, search_fields='name', search='GIS', order_by='name', skip=10, limit=10)
            or
            >>> files = client.get_files(search_fields='name', search='GIS', order_by='name', skip=10, limit=10)
        """
        params = {
            'f': 'json',
            'q': kwargs.get('q', None),
            'search': kwargs.get('search', None),
            'search_fields': kwargs.get('search_fields', None),
            'order_by': kwargs.get('order_by', None),
            'return_count': kwargs.get('return_count', False),
            'skip': kwargs.get('skip', 0),
            'limit': kwargs.get('limit', 10),
            'user_id': kwargs.get('user_id', None),
            'shared': kwargs.get('shared', False)
        }
        return super()._get_list(api, cls.BASE_ENDPOINT, params, factory_func=lambda api, item: cls(api, item['uuid'], item))


    @classmethod
    def get_file(cls, api: 'GeoboxClient', uuid: str, user_id: int = None) -> 'File':
        """
        Retrieves a file by its UUID.

        Args:
            api (Api): The API instance.
            uuid (str): The UUID of the file.
            user_id (int, optional): specific user. privileges required.

        Returns:
            File: The retrieved file instance.

        Raises:
            NotFoundError: If the file with the specified UUID is not found.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.file import File
            >>> client = GeoboxClient()
            >>> file = File.get_file(client, uuid="12345678-1234-5678-1234-567812345678")
            or
            >>> file = client.get_file(uuid="12345678-1234-5678-1234-567812345678")
        """
        params = {
            'f': 'json',
            'user_id': user_id
        }
        return super()._get_detail(api, cls.BASE_ENDPOINT, f'{uuid}/info', params, factory_func=lambda api, item: File(api, item['uuid'], item))


    @classmethod
    def get_files_by_name(cls, api: 'GeoboxClient', name: str, user_id: int = None) -> List['File']:
        """
        Get files by name

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            name (str): the name of the file to get
            user_id (int, optional): specific user. privileges required.

        Returns:
            List[File]: returns files that matches the given name

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.file import File
            >>> client = GeoboxClient()
            >>> files = File.get_files_by_name(client, name='test')
            or
            >>> files = client.get_files_by_name(name='test')
        """
        return cls.get_files(api, q=f"name = '{name}'", user_id=user_id)
    

    def _get_save_path(self, save_path: str = None) -> str:
        """
        Get the path where the file should be saved.

        Args:
            save_path (str, optional): The path to save the file.

        Returns:
            str: The path where the file is saved.
        
        Raises:
            ValueError: If save_path does not end with a '/'.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.file import File
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> file_path = File.get_file(client, uuid="12345678-1234-5678-1234-567812345678")
        """
        # If save_path is provided, check if it ends with a '/'
        if save_path and save_path.endswith('/'):
            return f'{save_path}'
        
        if save_path and not save_path.endswith('/'):
            raise ValueError("save_path must end with a '/'")
        
        return os.getcwd()
    

    def _get_file_name(self, response: requests.Response) -> str:
        """
        Get the file name from the response.

        Args:
            response (requests.Response): The response of the request.

        Returns:
            str: The file name 
        """
        if 'Content-Disposition' in response.headers and 'filename=' in response.headers['Content-Disposition']:
            file_name = response.headers['Content-Disposition'].split('filename=')[-1].strip().strip('"')

        else:
            content_type = response.headers.get("Content-Type", "")
            file_name = f'{self.name}.{mimetypes.guess_extension(content_type.split(";")[0])}'

        return file_name


    def _create_progress_bar(self) -> 'tqdm':
        """Creates a progress bar for the task."""
        try:
            from tqdm.auto import tqdm
        except ImportError:
            from .api import logger
            logger.warning("[tqdm] extra is required to show the progress bar. install with: pip insatll geobox[tqdm]")
            return None

        return tqdm(unit="B", 
                        total=int(self.size), 
                        file=sys.stdout,
                        dynamic_ncols=True,
                        desc="Downloading",
                        unit_scale=True,
                        unit_divisor=1024, 
                        ascii=True
                )


    def download(self, save_path: str = None, progress_bar: bool = True) -> str:
        """
        Download a file and save it to the specified path.
        
        Args:
            save_path (str, optional): Path where the file should be saved. 
                                    If not provided, it saves to the current working directory
                                    using the original filename and appropriate extension.
            progress_bar (bool, optional): Whether to show a progress bar. default: True
        
        Returns:
            str: Path where the file was saved
            
        Raises:
            ValueError: If uuid is not set
            OSError: If there are issues with file operations

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.file import File
            >>> client = GeoboxClient()
            >>> file = File.get_file(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> file.download(save_path='path/to/save/')
        """
        if not self.uuid:
            raise ValueError("File UUID is required to download the file")
        
        save_path = self._get_save_path(save_path)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with self.api.get(f"{self.endpoint}download/", stream=True) as response:
            file_name = self._get_file_name(response)
            full_path = f"{save_path}/{file_name}"
            with open(full_path, 'wb') as f:
                pbar = self._create_progress_bar() if progress_bar else None
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    if pbar:
                        pbar.update(len(chunk))
                        pbar.refresh()
                if pbar:
                    pbar.close()

        return os.path.abspath(full_path)


    def delete(self) -> None:
        """
        Deletes the file.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.file import File
            >>> client = GeoboxClient()
            >>> file = File.get_file(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> file.delete()
        """
        return super().delete(self.endpoint)


    def publish(self, 
                    name: str, 
                    publish_as: 'PublishFileType' = None, 
                    input_geom_type: 'InputGeomType' = None, 
                    input_layer: str = None, 
                    input_dataset: str = None, 
                    user_id: int = None, 
                    input_srid: int = Feature.BASE_SRID, 
                    file_encoding: str = "UTF-8", 
                    replace_domain_codes_by_values: bool = False, 
                    report_errors: bool = True, 
                    as_terrain: bool = False) -> 'Task':
        """
        Publishes a file as a layer.

        Args:
            name (str): The name of the layer.
            publish_as (PublishFileType): The type of layer to publish as.
            input_geom_type (InputGeomType, optional): The geometry type of the layer.
            input_layer (str, optional): The name of the input layer.
            input_dataset (str, optional): The name of the input dataset.
            user_id (int, optional): Specific user. privileges required.
            input_srid (int, optional): The SRID of the layer. default is: 3857
            file_encoding (str, optional): The encoding of the file. default is "utf-8".
            replace_domain_codes_by_values (bool, optional): Whether to replace domain codes by values. default is False.
            report_errors (bool, optional): Whether to report errors. default is True.
            as_terrain (bool, optional): Whether to publish as terrain. default is False.

        Returns:
            Task: The task object.

        Raises:
            ValueError: If the publish_as is not a valid PublishFileType.
            ValidationError: if the zipped file doesn't have any layers to publish.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.file import File
            >>> client = GeoboxClient()
            >>> file = File.get_file(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> file.publish(publish_as=PublishFileType.VECTOR, 
            ...                     layer_name='my_layer', 
            ...                     input_geom_type=InputGeomType.POINT, 
            ...                     input_layer='layer1', 
            ...                     input_dataset='dataset1', 
            ...                     input_srid=4326, 
            ...                     file_encoding='UTF-8')
        """
        if not publish_as:
            # checks the file format or file first layer format to dynamically set the publish_as
            if self.file_type.value in ['GeoJSON', 'GPKG', 'DXF', 'GPX', 'Shapefile', 'KML', 'CSV', 'FileGDB'] or \
                (self.file_type.value in ['Complex'] and self.layers and \
                    FileType(self.layers[0]['format']).value in ['GeoJSON', 'GPKG', 'DXF', 'GPX', 'Shapefile', 'KML', 'CSV', 'FileGDB']):
                publish_as = PublishFileType.VECTOR

            elif self.file_type.value in ['GeoTIFF'] or \
                    (self.file_type.value in ['Complex'] and self.layers and \
                        FileType(self.layers[0]['format']).value in ['GeoTIFF']):
                publish_as = PublishFileType.RASTER

            elif self.file_type.value in ['GLB'] or \
                    (self.file_type.value in ['Complex'] and self.layers and \
                        FileType(self.layers[0]['format']).value in ['GLB']):
                publish_as = PublishFileType.MODEL3D

            elif self.file_type.value in ['ThreedTiles']:
                publish_as = PublishFileType.Tiles3D

            else:
                raise ValidationError('Unknown format')

        data = clean_data({
            "publish_as": publish_as.value if isinstance(publish_as, PublishFileType) else publish_as,
            "layer_name": name,
            "input_layer": self.layers[0]['layer'] if not input_layer and self.layers else input_layer,
            "input_geom_type": input_geom_type.value if isinstance(input_geom_type, InputGeomType) else input_geom_type,
            "replace_domain_codes_by_values": replace_domain_codes_by_values,
            "input_dataset": self.layers[0]['dataset'] if not input_layer and self.layers else input_dataset,
            "user_id": user_id,
            "input_srid": input_srid,
            "file_encoding": file_encoding,
            "report_errors": report_errors,
            "as_terrain": as_terrain
        })
        endpoint = urljoin(self.endpoint, 'publish/')
        response = self.api.post(endpoint, data, is_json=False)
        task = Task.get_task(self.api, response.get('task_id'))
        return task


    def share(self, users: List['User']) -> None:
        """
        Shares the file with specified users.

        Args:
            users (List[User]): The list of users objects to share the file with.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.file import File
            >>> client = GeoboxClient()
            >>> file = File.get_file(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> users = client.search_users(search='John')
            >>> file.share(users=users)
        """
        super()._share(self.endpoint, users)
    

    def unshare(self, users: List['User']) -> None:
        """
        Unshares the file with specified users.

        Args:
            users (List[User]): The list of users objects to unshare the file with.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.file import File
            >>> client = GeoboxClient()
            >>> file = File.get_file(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> users = client.search_users(search='John')
            >>> file.unshare(users=users)
        """
        super()._unshare(self.endpoint, users)


    def get_shared_users(self, search: str = None, skip: int = 0, limit: int = 10) -> List['User']:
        """
        Retrieves the list of users the file is shared with.

        Args:
            search (str, optional): The search query.
            skip (int, optional): The number of users to skip.
            limit (int, optional): The maximum number of users to retrieve.

        Returns:
            List[User]: The list of shared users.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.file import File
            >>> client = GeoboxClient()
            >>> file = File.get_file(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> file.get_shared_users(search='John', skip=0, limit=10)
        """
        params = {
            'search': search,
            'skip': skip,
            'limit': limit
        }
        return super()._get_shared_users(self.endpoint, params)

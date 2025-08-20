from urllib.parse import urljoin, urlencode
from typing import Optional, Dict, List, Optional, Union, TYPE_CHECKING
import time

from .base import Base
from .enums import TaskStatus

if TYPE_CHECKING:
    from . import GeoboxClient
    from .vectorlayer import VectorLayer
    from .raster import Raster
    from .model3d import Model
    from .file import File
    from .tile3d import Tile3d

class Task(Base):
    """
    A class to represent a task in Geobox.

    This class provides functionality to interact with tasks in Geobox.
    It supports various operations including getting tasks, as well as advanced operations like waiting for a task to finish.
    It also provides properties to access the task data, and a method to abort the task.
    """
    BASE_ENDPOINT: str = 'tasks/'

    def __init__(self, 
                 api: 'GeoboxClient', 
                 uuid: str, 
                 data: Optional[Dict] = {}):
        """
        Constructs all the necessary attributes for the Task object.

        Args:
            api (GeoboxClient): The API instance.
            uuid (str): The UUID of the task.
            data (Dict, optional): The task data.
        """
        super().__init__(api, uuid=uuid, data=data)
        self._data = data if isinstance(data, dict) else {}


    def refresh_data(self) -> None:
        """
        Updates the task data.
        """
        self._data = self.get_task(self.api, self.uuid).data


    @property
    def output_asset(self) -> Union['VectorLayer', 'Raster', 'Model', 'File', 'Tile3d', None]:
        """
        output asset property

        Returns:
            VectorLayer | Raster | Model | Tile3d | None: if task type is publish, it returns the published layer

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.task import Task
            >>> client = GeoboxClient()
            >>> task = Task.get_task(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> task.output_asset
        """
        if self.data.get('result', {}).get('layer_uuid'):
            return self.api.get_vector(uuid=self.data['result']['layer_uuid'])

        elif self.data.get('result', {}).get('raster_uuid'):
            return self.api.get_raster(uuid=self.data['result']['raster_uuid'])

        elif self.data.get('result', {}).get('model_uuid'):
            return self.api.get_model(uuid=self.data['result']['model_uuid'])

        elif self.data.get('result', {}).get('file_uuid'):
            return self.api.get_file(uuid=self.data['result']['file_uuid'])
        
        elif self.data.get('result', {}).get('3dtiles_uuid'):
            return self.api.get_3dtile(uuid=self.data['result']['3dtiles_uuid'])

        else:
            return None


    @property
    def data(self) -> Dict:
        """
        Returns the task data.

        Returns:
            Dict: the task data as a dictionary
            
        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.task import Task
            >>> client = GeoboxClient()
            >>> task = Task.get_task(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> task.data
        """
        return self._data
    

    @data.setter
    def data(self, value: Dict) -> None:
        """
        Sets the task data.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.task import Task
            >>> client = GeoboxClient()
            >>> task = Task.get_task(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> task.data = {'name': 'test'}
        """
        self._data = value if isinstance(value, dict) else {}
    

    @property
    def status(self) -> 'TaskStatus':
        """
        Returns the status of the task. (auto refresh)

        Returns:
            TaskStatus: the status of the task(SUCCESS, FAILURE, ABORTED, PENDING, PROGRESS)
        
        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.task import Task
            >>> client = GeoboxClient()
            >>> task = Task.get_task(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> task.status
        """
        self.refresh_data()
        return TaskStatus(self._data.get('state'))


    @property
    def errors(self) -> Union[Dict, None]:
        """
        Get the task errors.

        Returns:
            Dict | None: if there are any errors

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.task import Task
            >>> client = GeoboxClient()
            >>> task = Task.get_task(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> task.errors    
        """
        result = self.data.get('result', {})
        if result.get('errors') or result.get('detail', {}).get('msg'):
            return result
        else: 
            return None


    @property
    def progress(self) -> Union[int, None]:
        """
        Returns the progress of the task.

        Returns:
            int | None: the progress of the task in percentage or None if the task is not running

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.task import Task
            >>> client = GeoboxClient()
            >>> task = Task.get_task(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> task.progress
        """
        endpoint = urljoin(self.endpoint, 'status/')
        response = self.api.get(endpoint)
        
        current = response.get('current')
        total = response.get('total')
        if not total or not current:
            return None
        
        return int((current / total) * 100)

    
    def _wait(self, timeout: Union[int, None] = None, interval: int = 1, progress_bar: bool = True) -> 'TaskStatus':
        start_time = time.time()
        last_progress = 0
        pbar = self._create_progress_bar() if progress_bar else None
        
        try:
            while True:
                self._check_timeout(start_time, timeout)
                status = self.status
                
                if self._is_final_state(status):
                    self._update_progress_bar(pbar, last_progress, status)
                    return TaskStatus(status)
                
                if pbar:
                    last_progress = self._update_progress_bar(pbar, last_progress)
                
                time.sleep(interval)
        finally:
            if pbar:
                pbar.close()


    def wait(self, timeout: Union[int, None] = None, interval: int = 1, progress_bar: bool = True, retry: int = 3) -> 'TaskStatus':
        """
        Wait for the task to finish.
        
        Args:
            timeout (int, optional): Maximum time to wait in seconds.
            interval (int, optional): Time between status checks in seconds.
            progress_bar (bool, optional): Whether to show a progress bar. default: True
            retry (int, optional): Number of times to retry if waiting for the task fails. default is 3
            
        Returns:
            TaskStatus: the status of the task(SUCCESS, FAILURE, ABORTED, PENDING, PROGRESS)
            
        Raises:
            TimeoutError: If the task doesn't complete within timeout seconds.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.task import Task
            >>> client = GeoboxClient()
            >>> task = Task.get_task(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> task.wait() # return the status of the task
        """
        last_exception = None

        for attempt in range(1, retry + 1):
            try:
                return self._wait(timeout, interval, progress_bar)
            except Exception as e:
                last_exception = e
                print(f"[Retry {attempt}/{retry}] Task wait failed: {e}")
                time.sleep(interval)
        raise last_exception


    def _create_progress_bar(self) -> 'tqdm':
        """Creates a progress bar for the task."""
        try:
            from tqdm.auto import tqdm
        except ImportError:
            from .api import logger
            logger.warning("[tqdm] extra is required to show the progress bar. install with: pip insatll geobox[tqdm]")
            return None

        return tqdm(total=100, colour='green', desc=f"Task: {self.name}", unit="%", leave=True)


    def _check_timeout(self, start_time: float, timeout: Union[int, None]) -> None:
        """Checks if the task has exceeded the timeout period."""
        if timeout and time.time() - start_time > timeout:
            raise TimeoutError(f"Task {self.name} timed out after {timeout} seconds")


    def _is_final_state(self, status: 'TaskStatus') -> bool:
        """Checks if the task has reached a final state."""
        return status in [TaskStatus.FAILURE, TaskStatus.SUCCESS, TaskStatus.ABORTED]


    def _update_progress_bar(self, pbar: Union['tqdm', None], last_progress: int, status: 'TaskStatus' = None) -> int:
        """
        Updates the progress bar with current progress and returns the new last_progress.
        
        Args:
            pbar (tqdm | None): The progress bar to update
            last_progress (int): The last progress value
            status (TaskStatus, optional): The task status. If provided and SUCCESS, updates to 100%
            
        Returns:
            int: The new last_progress value
        """
        if not pbar:
            return last_progress
        
        if status == TaskStatus.SUCCESS:
            pbar.update(100 - last_progress)
            return 100
        
        current_progress = self.progress
        if current_progress is not None:
            progress_diff = current_progress - last_progress
            if progress_diff > 0:
                pbar.update(progress_diff)
                return current_progress
        return last_progress


    def abort(self) -> None:
        """
        Aborts the task.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.task import Task
            >>> client = GeoboxClient()
            >>> task = Task.get_task(client, uuid="12345678-1234-5678-1234-567812345678")
            >>> task.abort()
        """
        endpoint = urljoin(self.endpoint, 'abort/')
        self.api.post(endpoint)


    @classmethod
    def get_tasks(cls, api: 'GeoboxClient', **kwargs) -> Union[List['Task'], int]:
        """
        Get a list of tasks

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            
        Keyword Args:
            state (TaskStatus): Available values : TaskStatus.PENDING, TaskStatus.PROGRESS, TaskStatus.SUCCESS, TaskStatus.FAILURE, TaskStatus.ABORTED
            q (str): query filter based on OGC CQL standard. e.g. "field1 LIKE '%GIS%' AND created_at > '2021-01-01'"
            search (str): search term for keyword-based searching among search_fields or all textual fields if search_fields does not have value. NOTE: if q param is defined this param will be ignored.
            search_fields (str): comma separated list of fields for searching.
            order_by (str): comma separated list of fields for sorting results [field1 A|D, field2 A|D, …]. e.g. name A, type D. NOTE: "A" denotes ascending order and "D" denotes descending order.
            return_count (bool): The count of the tasks. default is False.
            skip (int): The skip of the task. default is 0.
            limit (int): The limit of the task. default is 10.
            user_id (int): Specific user. privileges required.
            shared (bool): Whether to return shared tasks. default is False.

        Returns:
            List[Task] | int: The list of task objects or the count of the tasks if return_count is True.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.task import Task
            >>> client = GeoboxClient()
            >>> tasks = Task.get_tasks(client)
            or
            >>> tasks = client.get_tasks()
        """
        params = {
            'f': 'json',
            'state': kwargs.get('state').value if kwargs.get('state') else None,
            'q': kwargs.get('q'),
            'search': kwargs.get('search'),
            'search_fields': kwargs.get('search_fields'),
            'order_by': kwargs.get('order_by'),
            'return_count': kwargs.get('return_count', False),
            'skip': kwargs.get('skip'),
            'limit': kwargs.get('limit'),
            'user_id': kwargs.get('user_id'),
            'shared': kwargs.get('shared', False)
        }
        return super()._get_list(api, cls.BASE_ENDPOINT, params, factory_func=lambda api, item: Task(api, item['uuid'], item))
        


    @classmethod
    def get_task(cls, api: 'GeoboxClient', uuid: str) -> 'Task':
        """
        Gets a task.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            uuid (str): The UUID of the task.

        Returns:
            Task: The task object.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.task import Task
            >>> client = GeoboxClient()
            >>> task = Task.get_task(client, uuid="12345678-1234-5678-1234-567812345678")
            or
            >>> task = client.get_task(uuid="12345678-1234-5678-1234-567812345678")
        """
        return super()._get_detail(api, cls.BASE_ENDPOINT, uuid, factory_func=lambda api, item: Task(api, item['uuid'], item))


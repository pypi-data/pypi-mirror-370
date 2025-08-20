from typing import Dict, TYPE_CHECKING
from urllib.parse import urljoin, urlencode

from .enums import RoutingGeometryType, RoutingOverviewLevel
from .utils import clean_data

if TYPE_CHECKING:
    from . import GeoboxClient

class Routing:

    BASE_ENDPOINT = 'routing/'

    @classmethod
    def route(cls, api: 'GeoboxClient', stops: str, **kwargs) -> Dict:
        """
        Find best driving routes between coordinates and return results.

        Args:
            api (GeoboxClient): The GeoboxClient instance for making requests.
            stops (str): Comma-separated list of stop coordinates in the format lon,lat;lon,lat.

        Keyword Args:
            alternatives (bool): Whether to return alternative routes. Default value : False.
            steps (bool): Whether to include step-by-step navigation instructions. Default value : False.
            geometries (RoutingGeometryType): Format of the returned geometry.
            overview (RoutingOverviewLevel): Level of detail in the returned geometry.
            annotations (bool): Whether to include additional metadata like speed, weight, etc.

        Returns:
            Dict: the routing output

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.route import Routing
            >>> client = GeoboxClient()
            >>> route = routing.route(client,
            ...                         stops="53,33;56,36",
            ...                         alternatives=True,
            ...                         steps=True,
            ...                         geometries=RoutingGeometryType.geojson,
            ...                         overview=RoutingOverviewLevel.full,
            ...                         annotations=True)
            or
            >>> route = client.route(stops="53,33;56,36",
            ...                         alternatives=True,
            ...                         steps=True,
            ...                         geometries=RoutingGeometryType.geojson,
            ...                         overview=RoutingOverviewLevel.full,
            ...                         annotations=True)
        """
        params = clean_data({
            'stops': stops,
            'alternatives': kwargs.get('alternatives'),
            'steps': kwargs.get('steps'),
            'geometries': kwargs.get('geometries').value if kwargs.get('geometries') else None,
            'overview': kwargs.get('overview').value if kwargs.get('geometries') else None,
            'annotaions': kwargs.get('annotations')
        })
        query_string = urlencode(params)
        endpoint = f"{cls.BASE_ENDPOINT}route?{query_string}"
        return api.get(endpoint)
    

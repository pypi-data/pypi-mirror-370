from urllib.parse import urljoin
from typing import Optional, List, Dict, Any, TYPE_CHECKING

from .base import Base
from .enums import FeatureType

if TYPE_CHECKING:
    from .vectorlayer import VectorLayer

class Feature(Base):
    """
    A class representing a feature in a vector layer in Geobox.

    This class provides functionality to create, manage, and manipulate features in a vector layer.
    It supports various operations including CRUD operations on features, as well as advanced operations like transforming geometries.
    It also provides properties to access the feature geometry and properties, and a method to transform the feature geometry.
    """
    BASE_SRID = 3857

    def __init__(self, 
                 layer: 'VectorLayer', 
                 srid: Optional[int] = 3857,
                 data: Optional[Dict] = {}):
        """
        Constructs all the necessary attributes for the Feature object.

        Args:
            layer (VectorLayer): The vector layer this feature belongs to
            srid (int, optional): The Spatial Reference System Identifier (default is 3857)
            data (Dict, optional): The feature data contains the feature geometry and properties

        Example:
            >>> from geobox import GeoboxClient, Feature
            >>> client = GeoboxClient()
            >>> layer = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>> feature = Feature(layer=layer, srid=4326) # example srid set to 4326
            >>> feature.save()
        """
        super().__init__(api=layer.api)
        self.layer = layer
        self._srid = srid
        self.data = data or {}
        self.original_geometry = self.data.get('geometry')
        self.endpoint = urljoin(layer.endpoint, f'features/{self.data.get("id")}/') if self.data.get('id') else None


    def __dir__(self) -> List[str]:
        """
        Return a list of available attributes for the Feature object.
        
        This method extends the default dir() behavior to include:
        - All keys from the feature data dictionary
        - All keys from the geometry dictionary
        - All keys from the properties dictionary
        
        This allows for better IDE autocompletion and introspection of feature attributes.
        
        Returns:
            list: A list of attribute names available on this Feature object.
        """
        return super().__dir__() + list(self.data.keys()) + list(self.data.get('geometry').keys()) + list(self.data.get('properties').keys())


    def __repr__(self) -> str:
        """
        Return a string representation of the Feature object.

        Returns:
            str: A string representation of the Feature object.
        """
        return f"Feature(id={self.id}, type={self.feature_type})"
    

    def __getattr__(self, name: str) -> Any:
        """
        Get an attribute from the resource.

        Args:
            name (str): The name of the attribute
        """
        if name in self.data:
            return self.data.get(name)
        # elif name in self.data['geometry']:
        #     return self.data['geometry'].get(name)
        elif name in self.data['properties']:
            return self.data['properties'].get(name)
        
        raise AttributeError(f"Feature has no attribute {name}")


    @property
    def srid(self) -> int:
        """
        Get the Spatial Reference System Identifier (SRID) of the feature.

        Returns:
            int: The SRID of the feature.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> layer = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>> feature = layer.get_feature(id=1)
            >>> feature.srid  # 3857
        """
        return self._srid
    

    @property
    def feature_type(self) -> 'FeatureType':
        """
        Get the type of the feature.

        Returns:
            FeatureType: The type of the feature.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> layer = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>> feature = layer.get_feature(id=1)
            >>> feature.feature_type
        """
        return FeatureType(self.data.get('geometry').get('type')) if self.data.get('geometry') else None
    

    @property
    def coordinates(self) -> List[float]:
        """
        Get the coordinates of the ferepoature.

        Returns:
            list: The coordinates of the feature.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> layer = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>> feature = layer.get_feature(id=1)
            >>> feature.coordinates
        """
        return self.data.get('geometry').get('coordinates') if self.data.get('geometry') else None
    

    @coordinates.setter
    def coordinates(self, value: List[float]) -> None:
        """
        Set the coordinates of the feature.

        Args:
            value (list): The coordinates to set.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> layer = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>> feature = layer.get_feature(id=1)
            >>> feature.coordinates = [10, 20]
        """
        self.data['geometry']['coordinates'] = value
    

    @property
    def length(self) -> float:
        """
        Returns the length of thefeature geometry (geometry package extra is required!)

        Returns:
            float: the length of thefeature geometry

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> layer = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>> feature = layer.get_feature(id=1)
            >>> feature.length
        """
        try:
            return self.geom_length
        except AttributeError:
            endpoint = f'{self.endpoint}length'
            return self.api.get(endpoint)


    @property
    def area(self) -> float:
        """
        Returns the area of thefeature geometry (geometry package extra is required!)

        Returns:
            float: the area of thefeature geometry

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> layer = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>> feature = layer.get_feature(id=1)
            >>> feature.area
        """
        try:
            return self.geom_area
        except AttributeError:
            endpoint = f'{self.endpoint}area'
            return self.api.get(endpoint)
    
    
    def save(self) -> None:
        """
        Save the feature. Creates a new feature if feature_id is None, updates existing feature otherwise.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> layer = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>> feature = layer.get_feature(id=1)
            >>> feature.properties['name'] = 'New Name'
            >>> feature.save()
        """
        data = self.data.copy()
        try:
            if self.id:
                if self.srid != self.BASE_SRID:
                    self.data['geometry'] = self.original_geometry
                self.update(self.data)
                self.coordinates = data['geometry']['coordinates']
        except AttributeError:
            endpoint = urljoin(self.layer.endpoint, 'features/')
            response = self.layer.api.post(endpoint, data)
            self.endpoint = urljoin(self.layer.endpoint, f'features/{response["id"]}/')        
            self.data.update(response)


    def delete(self) -> None:
        """
        Delete the feature.

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> layer = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>> feature = layer.get_feature(id=1)
            >>> feature.delete()
        """
        super().delete(self.endpoint)


    def update(self, geojson: Dict) -> Dict:
        """
        Update the feature data property.

        Args:
            geojson (Dict): The GeoJSON data for the feature

        Returns:
            Dict: The response from the API.

        Example:
            >>> from geobox import GeoboxClient
            >>> client = GeoboxClient()
            >>> layer = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>> feature = layer.get_feature(id=1)
            >>> geojson = {
                "geometry": {
                    "type": "Point",
                    "coordinates": [10, 20]
                }
            }
            >>> feature.update(geojson)
        """
        return super()._update(self.endpoint, geojson, clean=False)
    

    @classmethod
    def create_feature(cls, layer: 'VectorLayer', geojson: Dict) -> 'Feature':
        """
        Create a new feature in the vector layer.

        Args:
            layer (VectorLayer): The vector layer to create the feature in
            geojson (Dict): The GeoJSON data for the feature

        Returns:
            Feature: The created feature instance

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.feature import Feature
            >>> client = GeoboxClient()
            >>> layer = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>> geojson = {
            ...    "type": "Feature",
            ...    "geometry": {"type": "Point", "coordinates": [10, 20]},
            ...    "properties": {"name": "My Point"}
            ... }
            >>> feature = Feature.create_feature(layer, geojson)
        """
        endpoint = urljoin(layer.endpoint, 'features/')
        return cls._create(layer.api, endpoint, geojson, factory_func=lambda api, item: Feature(layer, data=item))


    @classmethod
    def get_feature(cls, layer: 'VectorLayer', feature_id: int, user_id: int = None) -> 'Feature':
        """
        Get a feature by its ID.

        Args:
            layer (VectorLayer): The vector layer the feature belongs to
            feature_id (int): The ID of the feature
            user_id (int): specific user. privileges required.

        Returns:
            Feature: The retrieved feature instance

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.feature import Feature
            >>> client = GeoboxClient()
            >>> layer = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>> feature = Feature.get_feature(layer, feature_id=1)
        """
        param = {
            'f': 'json',
            'user_id': user_id
        }
        endpoint = urljoin(layer.endpoint, f'features/')
        return cls._get_detail(layer.api, endpoint, uuid=feature_id, params=param, factory_func=lambda api, item: Feature(layer, data=item))


    @property
    def geometry(self) -> 'BaseGeometry':
        """
        Get the feature geometry as a Shapely geometry object.

        Returns:
            shapely.geometry.BaseGeometry: The Shapely geometry object representing the feature's geometry

        Raises:
            ValueError: If the geometry is not a dictionary
            ValueError: If the geometry type is not present in the feature data
            ValueError: If the geometry coordinates are not present in the feature data
            ImportError: If shapely is not installed

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.feature import Feature
            >>> client = GeoboxClient()
            >>> layer = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>> feature = layer.get_feature(id=1)
            >>> feature.geometry
        """
        try:
            from shapely.geometry import shape
        except ImportError:
            raise ImportError(
                "The 'geometry' extra is required for this function. "
                "Install it with: pip install geobox[geometry]"
            )
        
        if not self.data:
            return None
        
        elif not self.data.get('geometry'):
            raise ValueError("Geometry is not present in the feature data")
        
        elif not isinstance(self.data['geometry'], dict):
            raise ValueError("Geometry is not a dictionary")
        
        elif not self.data['geometry'].get('type'):
            raise ValueError("Geometry type is not present in the feature data")
        
        elif not self.data['geometry'].get('coordinates'):
            raise ValueError("Geometry coordinates are not present in the feature data")
        
        else:
            return shape(self.data['geometry'])
    

    @geometry.setter
    def geometry(self, value: object) -> None:
        """
        Set the feature geometry.

        Args:
            value (object): The geometry to set.

        Raises:
            ValueError: If geometry type is not supported
            ValueError: If the geometry has a different type than the layer type
            ImportError: If shapely is not installed

        Returns:
            None

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.feature import Feature
            >>> from shapely.affinity import translate
            >>> client = GeoboxClient()
            >>> layer = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>> feature = layer.get_feature(id=1)
            >>> geom = feature.geometry
            >>> geom = translate(geom, 3.0, 0.5) # example change applied to the feature's geometry
            >>> feature.geometry = geom
            >>> feature.save()
        """
        try:
            from shapely.geometry import mapping, Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon
        except ImportError:
            raise ImportError(
                "The 'geometry' extra is required for this function. "
                "Install it with: pip install geobox[geometry]"
            )
        
        if not isinstance(value, (Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon)):
            raise ValueError("Geometry must be a Shapely geometry object")
        
        elif self.feature_type and value.geom_type != self.feature_type.value:
            raise ValueError("Geometry must have the same type as the layer type")
        
        else:
            self.data['geometry'] = mapping(value)

        
    def transform(self, out_srid: int) -> 'Feature':
        """
        Transform the feature geometry to a new SRID.

        Args:
            out_srid (int): The target SRID to transform the geometry to (e.g., 4326 for WGS84, 3857 for Web Mercator)

        Returns:
            Feature: A new Feature instance with transformed geometry.

        Raises:
            ValueError: If the feature has no geometry or if the transformation fails.
            ImportError: If pyproj is not installed.

        Example:
            >>> from geobox import GeoboxClient
            >>> from geobox.feature import Feature
            >>> client = GeoboxClient()
            >>> layer = client.get_vector(uuid="12345678-1234-5678-1234-567812345678")
            >>> feature = layer.get_feature(id=1, srid=3857)
            >>> # Transform from Web Mercator (3857) to WGS84 (4326)
            >>> transformed = feature.transform(out_srid=4326)
            >>> transformed.srid  # 4326
        """
        try:
            from pyproj import Transformer
            from shapely.geometry import Point, LineString, Polygon, MultiPoint, MultiLineString, MultiPolygon, mapping
        except ImportError:
            raise ImportError(
                "The 'geometry' extra is required for this function. "
                "Install it with: pip install geobox[geometry]"
            )

        if not self.data or not self.data.get('geometry'):
            raise ValueError("Feature geometry is required for transformation")

        # Get the current SRID from the feature or default to 3857 (Web Mercator)
        current_srid = self.srid or 3857

        # Create transformer
        transformer = Transformer.from_crs(current_srid, out_srid, always_xy=True)

        # Get the geometry
        geom = self.geometry

        # Transform coordinates based on geometry type
        if geom.geom_type == 'Point':
            x, y = geom.x, geom.y
            new_x, new_y = transformer.transform(x, y)
            new_geom = Point(new_x, new_y)
        elif geom.geom_type == 'LineString':
            coords = list(geom.coords)
            new_coords = [transformer.transform(x, y) for x, y in coords]
            new_geom = LineString(new_coords)
        elif geom.geom_type == 'Polygon':
            exterior = [transformer.transform(x, y) for x, y in geom.exterior.coords]
            interiors = [[transformer.transform(x, y) for x, y in interior.coords] for interior in geom.interiors]
            new_geom = Polygon(exterior, holes=interiors)
        elif geom.geom_type == 'MultiPoint':
            new_geoms = [Point(transformer.transform(point.x, point.y)) for point in geom.geoms]
            new_geom = MultiPoint(new_geoms)
        elif geom.geom_type == 'MultiLineString':
            new_geoms = [LineString([transformer.transform(x, y) for x, y in line.coords]) for line in geom.geoms]
            new_geom = MultiLineString(new_geoms)
        elif geom.geom_type == 'MultiPolygon':
            new_geoms = []
            for poly in geom.geoms:
                exterior = [transformer.transform(x, y) for x, y in poly.exterior.coords]
                interiors = [[transformer.transform(x, y) for x, y in interior.coords] for interior in poly.interiors]
                new_geoms.append(Polygon(exterior, holes=interiors))
            new_geom = MultiPolygon(new_geoms)

        # update the feature data
        self.data['geometry'] = mapping(new_geom)
        self._srid = out_srid

        return self



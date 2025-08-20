import pytest
from shapely.geometry import shape, Point
from shapely.affinity import translate
import math
from pyproj import Transformer
from unittest.mock import patch

from geobox.feature import Feature, FeatureType
from geobox.vectorlayer import VectorLayer, LayerType


@pytest.mark.parametrize("feature_type", [type.value for type in FeatureType])
def test_init(api, mock_vector_data, mock_feature_data, feature_type):
    """Test initialization of Feature object for different geometry types"""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType.MultiPoint, data=mock_vector_data)
    feature_data = mock_feature_data[feature_type]
    feature = Feature(layer, srid=3857, data=mock_feature_data[feature_type])
    assert feature.layer == layer
    assert feature.id == feature_data['id']
    assert feature.data == feature_data
    assert feature.srid == 3857
    assert feature.endpoint == f'{layer.endpoint}features/{feature_data["id"]}/'


@pytest.mark.parametrize("feature_type", [type.value for type in FeatureType])
def test_repr(api, mock_vector_data, mock_feature_data, feature_type):
    """Test the repr method of Feature object for different geometry types"""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType.MultiPoint, data=mock_vector_data)
    feature_data = mock_feature_data[feature_type]
    feature = Feature(layer, srid=3857, data=mock_feature_data[feature_type])
    assert repr(feature) == f"Feature(id={mock_feature_data[feature_type]['id']}, type={FeatureType(feature_type)})"


@pytest.mark.parametrize("feature_type", [type.value for type in FeatureType])
def test_dir(api, mock_vector_data, mock_feature_data, feature_type):
    """Test the dir method of Feature object for different geometry types"""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType.MultiPoint, data=mock_vector_data)
    feature_data = mock_feature_data[feature_type]
    feature = Feature(layer, srid=3857, data=mock_feature_data[feature_type])
    expected_attrs = list(feature_data.keys()) + list(feature_data['geometry'].keys()) + list(feature_data['properties'].keys())
    actual_attrs = dir(feature)
    # Check that all expected attributes are in the actual dir() result
    for attr in expected_attrs:
        assert attr in actual_attrs, f"Expected attribute '{attr}' not found in dir(feature)"


@pytest.mark.parametrize("feature_type", [type.value for type in FeatureType])
def test_getattr(api, mock_vector_data, mock_feature_data, feature_type):
    """Test the getattr method of Feature object for different geometry types"""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType.MultiPoint, data=mock_vector_data)
    feature_data = mock_feature_data[feature_type]
    feature = Feature(layer, srid=3857, data=mock_feature_data[feature_type])
    assert feature.id == feature_data['id']
    assert feature.name == feature_data['properties']['name']
    assert feature.coordinates == feature_data['geometry']['coordinates']
    assert feature.srid == 3857
    assert feature.feature_type == FeatureType(feature_type)
    assert feature.geometry == shape(feature_data['geometry'])
    with pytest.raises(AttributeError):
        feature.invalid_property


@pytest.mark.parametrize("feature_type", [type.value for type in FeatureType])
def test_save(api, mock_vector_data, mock_feature_data, feature_type):
    """Test saving a feature for different geometry types"""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType.MultiPoint, data=mock_vector_data)
    feature_data = mock_feature_data[feature_type]
    
    request_data = feature_data.copy()
    
    feature = Feature(layer, srid=3857, data=request_data.copy())
    api.post.return_value = feature_data

    feature.save()
    api.put.assert_called_once_with(f'{layer.endpoint}features/{feature_data["id"]}/', request_data)
    assert feature.id == feature_data['id']
    assert feature.data == feature_data

    # save new feature
    request_data = feature_data.copy()
    del request_data['id']
    
    feature = Feature(layer, srid=3857, data=request_data.copy())
    api.post.return_value = feature_data

    feature.save()
    api.post.assert_called_once_with(f'{layer.endpoint}features/', request_data)
    assert feature.id == feature_data['id']
    assert feature.data == feature_data


@pytest.mark.parametrize("feature_type", [type.value for type in FeatureType])
def test_save_srid(api, mock_vector_data, mock_feature_data, feature_type):
    """Test saving a feature with a different srid"""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType.MultiPoint, data=mock_vector_data)
    feature_data = mock_feature_data[feature_type]
    feature = Feature(layer, srid=3857, data=feature_data)
    feature.transform(4326)
    coords = feature.coordinates
    feature.save()
    assert feature.srid == 4326
    assert feature.coordinates == coords

    feature = Feature(layer, srid=3857, data=feature_data)
    coords = feature.coordinates
    feature.save()
    assert feature.srid == 3857
    assert feature.coordinates == coords


@pytest.mark.parametrize("feature_type", [type.value for type in FeatureType])
def test_delete(api, mock_vector_data, mock_feature_data, feature_type):
    """Test deleting a feature for different geometry types"""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType.MultiPoint, data=mock_vector_data)
    feature_data = mock_feature_data[feature_type]
    feature = Feature(layer, srid=3857, data=feature_data)
    feature.delete()
    api.delete.assert_called_once_with(f'{layer.endpoint}features/{feature_data["id"]}/')


@pytest.mark.parametrize("feature_type", [type.value for type in FeatureType])
def test_update(api, mock_vector_data, mock_feature_data, feature_type):
    """Test updating a feature for different geometry types"""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType.MultiPoint, data=mock_vector_data)
    feature_data = mock_feature_data[feature_type]
    feature = Feature(layer, srid=3857, data=feature_data)
    new_feature_data = feature.data
    new_feature_data['name'] = 'test_update'
    feature.update(new_feature_data)
    api.put.assert_called_once_with(f'{layer.endpoint}features/{feature_data["id"]}/', new_feature_data)
    
    feature.transform(4326)
    coords = feature.coordinates
    feature.update(new_feature_data)
    assert feature.srid == 4326
    assert feature.coordinates == coords


@pytest.mark.parametrize("feature_type", [type.value for type in FeatureType])
def test_create_feature(api, mock_vector_data, mock_feature_data, feature_type):
    """Test creating a feature for different geometry types"""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType.MultiPoint, data=mock_vector_data)
    feature_data = mock_feature_data[feature_type]
    
    expected_request = {
        'type': 'Feature',
        'geometry': feature_data['geometry'],
        'properties': {'name': f'test_{feature_type.lower()}'}
    }
    
    api_response = {
        'type': 'Feature',
        'geometry': feature_data['geometry'],
        'properties': {'name': f'test_{feature_type.lower()}'},
        'id': feature_data['id'],
        'bbox': feature_data['bbox']
    }
    api.post.return_value = api_response
    
    feature = Feature.create_feature(
        layer=layer, 
        geojson=expected_request
    )
    api.post.assert_called_once_with(f'{layer.endpoint}features/', expected_request)
    assert isinstance(feature, Feature)
    assert feature.layer == layer
    assert feature.srid == 3857
    assert feature.data == api_response


@pytest.mark.parametrize("feature_type", [type.value for type in FeatureType])
def test_get_feature(api, mock_vector_data, mock_feature_data, feature_type):
    """Test getting a feature for different geometry types"""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType.MultiPoint, data=mock_vector_data)
    feature_data = mock_feature_data[feature_type]

    api.get.return_value = feature_data
    
    feature = Feature.get_feature(layer, feature_data['id'])
    api.get.assert_called_once_with(f'vectorLayers/{mock_vector_data["uuid"]}/features/{feature_data["id"]}/?f=json')
    assert isinstance(feature, Feature)
    assert feature.layer == layer
    assert feature.id == feature_data['id']
    assert feature.data == feature_data


@pytest.mark.parametrize("feature_type", [type.value for type in FeatureType])
def test_geometry(api, mock_vector_data, mock_feature_data, feature_type):
    """Test getting a feature geometry for different geometry types"""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType.MultiPoint, data=mock_vector_data)
    feature_data = mock_feature_data[feature_type]
    feature = Feature(layer, srid=3857, data=feature_data)
    assert isinstance(feature.geometry, type(shape(feature_data['geometry'])))
    assert feature.geometry.area == feature_data['properties']['geom_area']
    assert feature.geometry.length == feature_data['properties']['geom_length']


def test_geometry_no_data(api, mock_vector_data):
    """Test geometry property when feature has no data"""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType('Point'), data=mock_vector_data)
    feature = Feature(layer, srid=3857, data=None)  # No data
    
    result = feature.geometry
    assert result is None


def test_geometry_no_geometry_field(api, mock_vector_data):
    """Test geometry property when feature data has no geometry field"""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType('Point'), data=mock_vector_data)
    feature = Feature(layer, srid=3857, data={'properties': {'name': 'test'}})  # No geometry field
    
    with pytest.raises(ValueError, match="Geometry is not present in the feature data"):
        feature.geometry


def test_geometry_not_dict(api, mock_vector_data):
    """Test geometry property when geometry is not a dictionary"""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType('Point'), data=mock_vector_data)
    feature = Feature(layer, srid=3857, data={'geometry': 'not_a_dict'})
    
    with pytest.raises(ValueError, match="Geometry is not a dictionary"):
        feature.geometry


def test_geometry_no_type(api, mock_vector_data):
    """Test geometry property when geometry has no type field"""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType('Point'), data=mock_vector_data)
    feature = Feature(layer, srid=3857, data={'geometry': {'coordinates': [1, 2]}})  # No type
    
    with pytest.raises(ValueError, match="Geometry type is not present in the feature data"):
        feature.geometry


def test_geometry_no_coordinates(api, mock_vector_data):
    """Test geometry property when geometry has no coordinates field"""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType('Point'), data=mock_vector_data)
    feature = Feature(layer, srid=3857, data={'geometry': {'type': 'Point'}})  # No coordinates
    
    with pytest.raises(ValueError, match="Geometry coordinates are not present in the feature data"):
        feature.geometry


def test_geometry_import_error(api, mock_vector_data, mock_feature_data):
    """Test geometry property when shapely is not available"""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType('Point'), data=mock_vector_data)
    feature = Feature(layer, srid=3857, data=mock_feature_data['Point'])
    
    with patch('builtins.__import__', side_effect=ImportError):
        with pytest.raises(ImportError, match="The 'geometry' extra is required for this function"):
            feature.geometry


@pytest.mark.parametrize("feature_type", [type.value for type in FeatureType])
def test_set_geometry_with_error_cases(api, mock_vector_data, mock_feature_data, feature_type):
    """Test setting a feature geometry with error conditions"""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType.MultiPoint, data=mock_vector_data)
    feature_data = mock_feature_data[feature_type]
    feature = Feature(layer, srid=3857, data=feature_data)
    
    # Test 1: Setting invalid geometry type (not a Shapely object)
    with pytest.raises(ValueError, match="Geometry must be a Shapely geometry object"):
        feature.geometry = "not_a_geometry"
    
    # Test 2: Setting geometry with different type than layer type
    if feature_type != "Point":  # Only test if current type is not Point
        point_geom = Point(1, 2)
        with pytest.raises(ValueError, match="Geometry must have the same type as the layer type"):
            feature.geometry = point_geom
    
    # Test 3: ImportError when shapely is not available
    with patch('builtins.__import__', side_effect=ImportError):
        with pytest.raises(ImportError, match="The 'geometry' extra is required for this function"):
            feature.geometry = Point(1, 2)


@pytest.mark.parametrize("feature_type", [type.value for type in FeatureType])
def test_set_geometry_success(api, mock_vector_data, mock_feature_data, feature_type):
    """Test setting a feature geometry for different geometry types"""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType.MultiPoint, data=mock_vector_data)
    feature_data = mock_feature_data[feature_type]
    feature = Feature(layer, srid=3857, data=feature_data)
    
    new_geometry = shape(feature_data['geometry'])
    new_geometry = translate(new_geometry, 100, 100)
    
    feature.geometry = new_geometry
    feature.save()
    
    api.put.assert_called_once_with(f'vectorLayers/{mock_vector_data["uuid"]}/features/{feature_data["id"]}/', feature.data)


@pytest.mark.parametrize("feature_type", [type.value for type in FeatureType])
def test_srid(api, mock_vector_data, mock_feature_data, feature_type):
    """Test getting a feature srid for different geometry types"""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType.MultiPoint, data=mock_vector_data)
    feature_data = mock_feature_data[feature_type]
    feature = Feature(layer, srid=3857, data=feature_data)
    assert feature.srid == 3857
    with pytest.raises(AttributeError):
        feature.srid = 4326

    feature = Feature(layer, srid=4326, data=feature_data)
    assert feature.srid == 4326
    

@pytest.mark.parametrize("feature_type", [type.value for type in FeatureType])
def test_properties(api, mock_vector_data, mock_feature_data, feature_type):
    """Test getting a feature properties for different geometry types"""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType.MultiPoint, data=mock_vector_data)
    feature_data = mock_feature_data[feature_type]
    feature = Feature(layer, srid=3857, data=feature_data)
    assert feature.properties == feature_data['properties']


@pytest.mark.parametrize("feature_type", [type.value for type in FeatureType])
def test_feature_type(api, mock_vector_data, mock_feature_data, feature_type):
    """Test getting a feature type for different geometry types"""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType.MultiPoint, data=mock_vector_data)
    feature_data = mock_feature_data[feature_type]
    feature = Feature(layer, srid=3857, data=feature_data)
    assert feature.feature_type == FeatureType(feature_type)


@pytest.mark.parametrize("feature_type", [type.value for type in FeatureType])
def test_coordinates(api, mock_vector_data, mock_feature_data, feature_type):
    """Test getting a feature coordinates for different geometry types"""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType.MultiPoint, data=mock_vector_data)
    feature_data = mock_feature_data[feature_type]
    feature = Feature(layer, srid=3857, data=feature_data)
    assert feature.coordinates == feature_data['geometry']['coordinates']


@pytest.mark.parametrize("feature_type", [type.value for type in FeatureType])
def test_length(api, mock_vector_data, mock_feature_data, feature_type):
    """Test getting a feature length for different geometry types"""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType.MultiPoint, data=mock_vector_data)
    feature_data = mock_feature_data[feature_type]
    feature = Feature(layer, srid=3857, data=feature_data)
    assert feature.length == feature_data['properties']['geom_length']
    # api call
    del feature_data['properties']['geom_length']
    feature = Feature(layer, srid=3857, data=feature_data)
    api.get.return_value = 20
    assert feature.length == 20
    api.get.assert_called_once_with(f'{feature.endpoint}length')


@pytest.mark.parametrize("feature_type", [type.value for type in FeatureType])
def test_area(api, mock_vector_data, mock_feature_data, feature_type):
    """Test getting a feature area for different geometry types"""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType.MultiPoint, data=mock_vector_data)
    feature_data = mock_feature_data[feature_type]
    feature = Feature(layer, srid=3857, data=feature_data)
    assert feature.area == feature_data['properties']['geom_area']
    # api call
    del feature_data['properties']['geom_area']
    feature = Feature(layer, srid=3857, data=feature_data)
    api.get.return_value = 20
    assert feature.area == 20
    api.get.assert_called_once_with(f'{feature.endpoint}area')

    
@pytest.mark.parametrize("feature_type", [type.value for type in FeatureType])
def test_transform_all_types(api, mock_vector_data, mock_feature_data, feature_type):
    """Test the local transform method of Feature for all geometry types."""
    
    # Create a layer and feature for the given geometry type
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType.MultiPoint, data=mock_vector_data)
    feature_data = mock_feature_data[feature_type]
    feature = Feature(layer, srid=3857, data=feature_data.copy())

    # Save original geometry for comparison
    original_geom = shape(feature_data['geometry'])

    # Manually transform the geometry using pyproj
    transformer = Transformer.from_crs(3857, 4326, always_xy=True)
    if feature_type == "Point":
        x, y = original_geom.x, original_geom.y
        manual_transformed_coords = transformer.transform(x, y)

    elif feature_type == "LineString":
        manual_transformed_coords = [transformer.transform(x, y) for x, y in original_geom.coords]

    elif feature_type == "Polygon":
        exterior = [transformer.transform(x, y) for x, y in original_geom.exterior.coords]
        interiors = [[transformer.transform(x, y) for x, y in interior.coords] for interior in original_geom.interiors]
        manual_transformed_coords = [exterior] + interiors

    elif feature_type == "MultiPoint":
        manual_transformed_coords = [transformer.transform(point.x, point.y) for point in original_geom.geoms]

    elif feature_type == "MultiLineString":
        manual_transformed_coords = [[transformer.transform(x, y) for x, y in line.coords] for line in original_geom.geoms]

    elif feature_type == "MultiPolygon":
        manual_transformed_coords = []
        for poly in original_geom.geoms:
            exterior = [transformer.transform(x, y) for x, y in poly.exterior.coords]
            interiors = [[transformer.transform(x, y) for x, y in interior.coords] for interior in poly.interiors]
            manual_transformed_coords.append([exterior] + interiors)

    # Transform to WGS84 (4326) using the feature's transform method
    feature.transform(out_srid=4326)

    assert feature.srid == 4326

    transformed_geom = feature.geometry
    # Compare the manually transformed coordinates with the feature's transformed coordinates
    if feature_type == "Point":
        trans_x, trans_y = transformed_geom.x, transformed_geom.y
        assert math.isclose(trans_x, manual_transformed_coords[0], abs_tol=1e-7)
        assert math.isclose(trans_y, manual_transformed_coords[1], abs_tol=1e-7)
    else:
        # For other types, compare the coordinates
        assert transformed_geom.equals_exact(shape({'type': feature_type, 'coordinates': manual_transformed_coords}), 1e-7)


@pytest.mark.parametrize("feature_type", [type.value for type in FeatureType])
def test_transform_missing_data(api, mock_vector_data, mock_feature_data, feature_type):
    """Test ValueError when feature has no data."""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType("Point"), data=mock_vector_data)
    feature_data = mock_feature_data[feature_type]
    del feature_data['geometry']
    feature = Feature(layer, data=feature_data)  # No geometry data
    
    with pytest.raises(ValueError, match="Feature geometry is required for transformation"):
        feature.transform(out_srid=4326)


def test_transform_import_error(api, mock_vector_data, mock_feature_data):
    """Test geometry property when shapely is not available"""
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType('Point'), data=mock_vector_data)
    feature = Feature(layer, srid=3857, data=mock_feature_data['Point'])
    
    with patch('builtins.__import__', side_effect=ImportError):
        with pytest.raises(ImportError, match="The 'geometry' extra is required for this function"):
            feature.transform(4326)


def test_get_count_error(api, mock_vector_data, mock_feature_data):
    layer = VectorLayer(api, uuid=mock_vector_data['uuid'], layer_type=LayerType('Point'), data=mock_vector_data)
    api.get.return_value = {'count_number': 123}
    with pytest.raises(ValueError, match='Invalid response format'):
        count = layer.get_features(return_count=True)
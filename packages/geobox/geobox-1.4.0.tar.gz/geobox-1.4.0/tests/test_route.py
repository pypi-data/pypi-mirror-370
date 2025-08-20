import pytest
from unittest.mock import patch

from geobox.route import Routing, RoutingGeometryType, RoutingOverviewLevel
from geobox.user import User

def test_route(api):
    api.get.return_value = {'route': 'value'}
    route = Routing.route(api, 
                            stops='53,33;56,36', 
                            alternatives=True, 
                            steps=True,
                            geometries=RoutingGeometryType.geojson,
                            overview=RoutingOverviewLevel.Full,
                            annotations=True)
    assert route == {'route': 'value'}
    api.get.assert_called_once_with('routing/route?stops=53%2C33%3B56%2C36&alternatives=True&steps=True&geometries=geojson&overview=full&annotaions=True')
    
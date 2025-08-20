[<img width="200" alt="Geobox logo" src="https://www.geobox.ir/wp-content/uploads/2022/05/geologo-slider.png">](https://www.geobox.ir/)


Geobox® is a cloud-based GIS platform that enables users (local governments, companies and individuals) to easily upload their geo-spatial data, publish them as geo-services, visualize and analyze their geo-content (geo-data or -services) and share them with others. Geobox is a modern, world-class and cloud-ready geo-spatial platform that provides standard, safe, efficient and easy to use GI-Services.

Geobox python SDK provides seamless integration with the Geobox API, enabling developers to work with geospatial data and services programmatically. This comprehensive toolkit empowers applications to leverage advanced geospatial capabilities including data management and analysis.

[Here](https://geobox.readthedocs.io) you can find the official documentation for Geobox Python SDK.

Installation
============

Enable Virtualenv and Install Dependencies:

```
pip install geobox
```

Install with Geometry Dependencies

```
pip install geobox[geometry]
```
```
from geobox import GeoboxClient

client = GeoboxClient()

layer = client.get_vectors(search='tehran')[0]
feature = layer.get_feature(feature_id=1)
geom = feature.geometry
```

Install with Progress Bar Support

```
pip install geobox[tqdm]
```
```
from geobox import GeoboxClient

client = GeoboxClient()

task = client.get_tasks()[0]
task.wait() # shows progress bar by default. use progress_bar=False to disable it.
```

Install with All Available Dependencies

```
pip install geobox[all]
```


Example
=======

```
from geobox import GeoboxClient

client = GeoboxClient()

layer = client.get_vectors(search='tehran')[0]
features = layer.get_features(out_srid=4326, bbox_srid=4326)
fields = layer.get_fields()
```
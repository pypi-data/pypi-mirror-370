import pytest

from geobox.attachment import Attachment, AttachmentResourceType
from geobox.file import File
from geobox.vectorlayer import VectorLayer, LayerType
from geobox.feature import Feature
from geobox.view import VectorLayerView
from geobox.map import Map


def test_init(api, mock_attachment_data):
    attachment = Attachment(api, mock_attachment_data['id'], mock_attachment_data)
    assert attachment.name == mock_attachment_data['name']
    assert attachment.attachment_id == mock_attachment_data['id']
    assert attachment.data == mock_attachment_data
    assert attachment.endpoint == f'{Attachment.BASE_ENDPOINT}{attachment.attachment_id}/'


def test_repr(api, mock_attachment_data):
    attachment = Attachment(api, mock_attachment_data['id'], mock_attachment_data)
    assert repr(attachment) == f"Attachment(id={attachment.attachment_id}, name={attachment.name})"


def test_file(api, mock_attachment_data):
    attachment = Attachment(api, mock_attachment_data['id'], mock_attachment_data)
    file = attachment.file
    assert type(file) == File
    assert file.data == mock_attachment_data['file']


def test_get_attachments(api, mock_attachment_data, mock_vector_data):
    api.get.return_value = [mock_attachment_data, mock_attachment_data]
    layer = VectorLayer(api, mock_vector_data['uuid'], LayerType.Polygon, mock_vector_data)
    attachments = Attachment.get_attachments(api, resource_type=AttachmentResourceType.Vector, resource_uuid=layer.uuid)
    api.get.assert_called_once_with(f'{Attachment.BASE_ENDPOINT}?resource_type=vector&resource_uuid=297fa7ca-877a-400c-8003-d65de9e791c2&skip=0&limit=10')
    assert len(attachments) == 2
    assert type(attachments[0]) == Attachment
    assert attachments[0].data == mock_attachment_data


def test_create_attachment(api, mock_attachment_data, mock_vector_data, mock_feature_data, mock_view_data, mock_map_data):
    api.post.return_value = mock_attachment_data
    layer = VectorLayer(api, mock_attachment_data['key'].split(':')[1], LayerType.Polygon, mock_vector_data)
    mock_feature_data['Polygon']['id'] = 1
    feature = Feature(layer, data=mock_feature_data['Polygon'])
    file = File(api, mock_attachment_data['file']['uuid'], mock_attachment_data['file'])
    attachment = Attachment.create_attachment(api,
                                        name=mock_attachment_data['name'],
                                        loc_x=mock_attachment_data['loc_x'],
                                        loc_y=mock_attachment_data['loc_y'],
                                        resource=layer,
                                        file=file,
                                        feature=feature,
                                        display_name=mock_attachment_data['display_name'],
                                        description=mock_attachment_data['description'])
    api.post.assert_called_once_with(Attachment.BASE_ENDPOINT, {'name': 'scene_(1).png', 'loc_x': 51.190273, 'loc_y': 35.71116, 'resource_type': 'vector', 'resource_uuid': '0da64b20-90bd-4e56-88f3-903a2dc97d49', 'element_id': 1, 'file_id': 6764})
    assert type(attachment) == Attachment
    assert attachment.attachment_id == mock_attachment_data['id']
    assert attachment.data == mock_attachment_data
    # view resource
    view = VectorLayerView(api, mock_view_data['uuid'], LayerType.Polygon, mock_view_data)
    attachment = Attachment.create_attachment(api,
                                        name=mock_attachment_data['name'],
                                        loc_x=mock_attachment_data['loc_x'],
                                        loc_y=mock_attachment_data['loc_y'],
                                        resource=view,
                                        file=file,
                                        feature=feature,
                                        display_name=mock_attachment_data['display_name'],
                                        description=mock_attachment_data['description'])
    assert type(attachment) == Attachment
    # map resource
    map = Map(api, mock_map_data['uuid'], mock_map_data)
    attachment = Attachment.create_attachment(api,
                                        name=mock_attachment_data['name'],
                                        loc_x=mock_attachment_data['loc_x'],
                                        loc_y=mock_attachment_data['loc_y'],
                                        resource=map,
                                        file=file,
                                        feature=feature,
                                        display_name=mock_attachment_data['display_name'],
                                        description=mock_attachment_data['description'])
    assert type(attachment) == Attachment



def test_update_attachment(api, mock_attachment_data):
    expected_data = {'name': 'updated_name', 
                'display_name': 'updated display name', 
                'description': 'updated description', 
                'loc_x': 10, 
                'loc_y': 20}
    api.put.return_value = {**mock_attachment_data, **expected_data}
    updated_data = Attachment.update_attachment(api, attachment_id=mock_attachment_data['id'],
                                                    name=expected_data['name'],
                                                    display_name=expected_data['display_name'],
                                                    description=expected_data['description'],
                                                    loc_x=expected_data['loc_x'],
                                                    loc_y=expected_data['loc_y'])
    api.put.assert_called_once_with(f"{Attachment.BASE_ENDPOINT}{mock_attachment_data['id']}", expected_data)
    assert updated_data == {**mock_attachment_data, **expected_data}


def test_update(api, mock_attachment_data, mock_vector_data):
    api.get.return_value = [mock_attachment_data, mock_attachment_data]
    layer = VectorLayer(api, mock_attachment_data['key'].split(':')[1], LayerType.Polygon, mock_vector_data)
    attachment = Attachment.get_attachments(api, resource_type=AttachmentResourceType.Vector, resource_uuid=layer.uuid)[0]
    expected_data = {'name': 'updated_name', 
            'display_name': 'updated display name', 
            'description': 'updated description', 
            'loc_x': 10, 
            'loc_y': 20}
    updated_data = {**mock_attachment_data, **expected_data}

    api.put.return_value = updated_data
    attachment.update(name=expected_data['name'],
                        display_name=expected_data['display_name'],
                        description=expected_data['description'],
                        loc_x=expected_data['loc_x'],
                        loc_y=expected_data['loc_y'])
    api.put.assert_called_once_with(attachment.endpoint, expected_data)
    assert attachment.data == updated_data


def test_delete(api, mock_attachment_data, mock_vector_data):
    api.get.return_value = [mock_attachment_data, mock_attachment_data]
    layer = VectorLayer(api, mock_attachment_data['key'].split(':')[1], LayerType.Polygon, mock_vector_data)
    attachment = Attachment.get_attachments(api, resource_type=AttachmentResourceType.Vector, resource_uuid=layer.uuid)[0]
    endpoint = attachment.endpoint
    attachment.delete()
    api.delete.assert_called_once_with(endpoint)
    assert attachment.attachment_id is None
    assert attachment.endpoint is None


def test_thumbnail(api, mock_attachment_data, mock_vector_data):
    api.get.return_value = [mock_attachment_data, mock_attachment_data]
    layer = VectorLayer(api, mock_attachment_data['key'].split(':')[1], LayerType.Polygon, mock_vector_data)
    attachment = Attachment.get_attachments(api, resource_type=AttachmentResourceType.Vector, resource_uuid=layer.uuid)[0]
    thumbnail_url = attachment.thumbnail
    assert thumbnail_url == f"{api.base_url}{attachment.endpoint}thumbnail"


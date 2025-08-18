
"""
Serialization utilities for variable values using the local mimetypes module.

Provides serialize_value and deserialize_value for converting Python objects to and from
MIME bundles and metadata, using the extensible mimetypes registry.
"""


from . import mimetypes

def serialize_value(value):
    """
    Serialize a Python object to a MIME bundle and metadata using the local mimetypes registry.
    Returns:
        dict: {"data": {mimetype: value}, "metadata": {mimetype: {type: (module, class)}}}
    """
    data, metadata = mimetypes.serialize_object(value)
    return {"data": data, "metadata": metadata}


def deserialize_value(data, metadata):
    """
    Deserialize a Python object from a MIME bundle and metadata using the local mimetypes registry.
    Args:
        data (dict): MIME bundle
        metadata (dict): Metadata for the MIME bundle
    Returns:
        The deserialized Python object.
    """
    return mimetypes.deserialize_object(data, metadata)

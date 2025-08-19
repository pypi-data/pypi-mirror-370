import pytest

from dism_core.properties.base import BaseProperties, Tag


@pytest.fixture
def valid_props_no_tags() -> dict:
    return {
        "Description": "Example description",
        "Name": "autoencoder",
    }


@pytest.fixture
def valid_props_with_tags() -> dict:
    return {
        "Description": "Example description",
        "Name": "autoencoder",
        "Tags": [
            {"Name": "tag1", "Value": "value1"},
            {"Name": "tag2", "Value": "value2"},
        ],
    }


def test_valid_props_no_tags(valid_props_no_tags):
    props = BaseProperties(**valid_props_no_tags)
    assert props.Description == "Example description"
    assert props.Name == "autoencoder"
    assert props.Tags is None
    assert isinstance(props, BaseProperties)


def test_valid_props_with_tags(valid_props_with_tags):
    props = BaseProperties(**valid_props_with_tags)
    assert props.Description == "Example description"
    assert props.Name == "autoencoder"
    assert props.Tags is not None
    assert isinstance(props.Tags, list)
    assert all(isinstance(tag, Tag) for tag in props.Tags)
    assert isinstance(props, BaseProperties)


def test_invalid_tag():
    with pytest.raises(
        ValueError, match="String must contain only lowercase alphanumeric characters, hyphens, or underscores"
    ):
        Tag(Name="Invalid Tag", Value="value1")


def test_invalid_name():
    with pytest.raises(ValueError, match="String violates RFC 1123 *"):
        BaseProperties(Description="Example description", Name="Invalid Name")
    with pytest.raises(ValueError, match="String violates RFC 1123 *"):
        BaseProperties(Description="Example description", Name="Autoencoder")

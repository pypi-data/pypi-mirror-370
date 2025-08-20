from contentgrid_application_client import ContentGridApplicationClient, Profile, EntityProfile, AttributeProfile
import pytest
from contentgrid_hal_client.exceptions import NotFound
from fixtures import auth_manager, cg_client # noqa: F401

def test_get_profile_attributes(cg_client: ContentGridApplicationClient):
    profile = cg_client.get_profile()
    entity_links = profile.get_entity_links()
    assert len(entity_links) > 0
    assert all(link.name for link in entity_links)
    assert all(link.uri for link in entity_links)

def test_entity_profile_details(cg_client: ContentGridApplicationClient):
    profile = cg_client.get_profile()
    entity_profile = cg_client.get_entity_profile(profile.get_entity_links()[0].name)

    # Test basic entity profile properties
    assert isinstance(entity_profile, EntityProfile)
    assert entity_profile.name is not None
    assert entity_profile.title is not None
    assert entity_profile.description is not None

def test_attribute_profiles(cg_client: ContentGridApplicationClient):
    profile = cg_client.get_profile()
    entity_profile = cg_client.get_entity_profile(profile.get_entity_links()[0].name)

    attribute_profiles = entity_profile.get_attribute_profiles()
    if not attribute_profiles:
        pytest.skip(f"Entity {entity_profile.name} has no attribute profiles to test.")

    # Test first attribute profile properties
    first_attribute = attribute_profiles[0]
    assert isinstance(first_attribute, AttributeProfile)
    assert first_attribute.name is not None
    assert first_attribute.type is not None
    assert isinstance(first_attribute.required, bool)
    assert isinstance(first_attribute.read_only, bool)

def test_invalid_entity_profile(cg_client: ContentGridApplicationClient):
    with pytest.raises(NotFound):
        cg_client.get_entity_profile("non_existent_entity")

def test_nested_attributes(cg_client: ContentGridApplicationClient):
    profile = cg_client.get_profile()
    # Use a known entity type if available, otherwise the first one
    entity_name = "anonymous-candidates" if "anonymous-candidates" in [link.name for link in profile.get_entity_links()] else profile.get_entity_links()[0].name
    entity_profile = cg_client.get_entity_profile(entity_name)

    found_nested = False
    for attribute in entity_profile.get_attribute_profiles():
        nested_attributes = attribute.get_nested_attributes()
        if nested_attributes:
            found_nested = True
            assert all(isinstance(nested, AttributeProfile) for nested in nested_attributes)
            assert all(hasattr(nested, 'name') for nested in nested_attributes)
    if not found_nested:
        print(f"INFO: No nested attributes found for entity {entity_name} to test.")

def test_content_attribute_detection(cg_client: ContentGridApplicationClient):
    profile = cg_client.get_profile()
    entity_profile = cg_client.get_entity_profile(profile.get_entity_links()[0].name)

    for attribute in entity_profile.get_attribute_profiles():
        if attribute.is_content_attribute():
            nested_attrs = attribute.get_nested_attributes()
            assert any(attr.name in ["length", "mimetype", "filename"] for attr in nested_attrs)

def test_relation_profiles(cg_client: ContentGridApplicationClient):
    profile = cg_client.get_profile()
    entity_profile = cg_client.get_entity_profile("anonymous-candidates")

    relation_profiles = entity_profile.get_relation_profiles()
    assert len(relation_profiles) >= 0

    if relation_profiles:
        first_relation = relation_profiles[0]
        assert first_relation.name is not None
        assert first_relation.title is not None
        assert isinstance(first_relation.required, bool)
        assert isinstance(first_relation.many_source_per_target, bool)
        assert isinstance(first_relation.many_target_per_source, bool)

def test_get_specific_relation_profile(cg_client: ContentGridApplicationClient):
    profile = cg_client.get_profile()
    entity_profile = cg_client.get_entity_profile("anonymous-candidates")

    if entity_profile.get_relation_profiles():
        relation_name = entity_profile.get_relation_profiles()[0].name
        relation_profile = entity_profile.get_relation_profile(relation_name)
        assert relation_profile.name == relation_name

        # Test related entity profile retrieval
        related_entity_profile = relation_profile.get_related_entity_profile()
        assert isinstance(related_entity_profile, EntityProfile)
        assert related_entity_profile.name is not None

def test_invalid_relation_profile(cg_client: ContentGridApplicationClient):
    profile = cg_client.get_profile()
    entity_profile = cg_client.get_entity_profile(profile.get_entity_links()[0].name)

    with pytest.raises(ValueError):
        entity_profile.get_relation_profile("non_existent_relation")



def test_singular_plural_conversion(cg_client: ContentGridApplicationClient):
    plural_name = "candidates"
    singular_name = "candidate"

    assert cg_client.get_profile().singular_to_plural_entity_name(singular_name) == plural_name
    assert cg_client.get_profile().plural_to_singular_entity_name(plural_name) == singular_name
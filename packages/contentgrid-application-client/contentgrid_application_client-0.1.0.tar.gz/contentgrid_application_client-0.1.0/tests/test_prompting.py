
import pytest
from contentgrid_application_client import (
    ContentGridApplicationClient,
    EntityCollection,
    EntityObject,
    Profile,
    EntityProfile,
    AttributeProfile
)
from fixtures import cg_client, auth_manager  # noqa: F401

def test_profile_prompt(cg_client: ContentGridApplicationClient):
    profile = cg_client.get_profile()
    prompt_str = profile.prompt()
    assert isinstance(prompt_str, str)
    assert "Entity:" in prompt_str or "Title:" in prompt_str

def test_entity_profile_prompt(cg_client: ContentGridApplicationClient):
    profile = cg_client.get_profile()
    entity_name = profile.get_entity_links()[0].name
    entity_profile = cg_client.get_entity_profile(entity_name)
    prompt_str = entity_profile.prompt()
    assert isinstance(prompt_str, str)
    assert entity_profile.name in prompt_str
    assert entity_profile.title in prompt_str

def test_attribute_profile_prompt(cg_client: ContentGridApplicationClient):
    profile = cg_client.get_profile()
    entity_name = profile.get_entity_links()[0].name
    entity_profile = cg_client.get_entity_profile(entity_name)
    attribute_profiles = entity_profile.get_attribute_profiles()
    if not attribute_profiles:
        pytest.skip(f"Entity {entity_profile.name} has no attribute profiles to test.")
    attr_prompt = attribute_profiles[0].prompt()
    assert isinstance(attr_prompt, str)
    assert attribute_profiles[0].name in attr_prompt

def test_entity_collection_prompt(cg_client: ContentGridApplicationClient):
    profile = cg_client.get_profile()
    entity_name = profile.get_entity_links()[0].name
    collection = cg_client.get_entity_collection(entity_name)
    prompt_str = collection.prompt()
    assert isinstance(prompt_str, str)
    assert "GET request on" in prompt_str

def test_entity_object_prompt(cg_client: ContentGridApplicationClient):
    profile = cg_client.get_profile()
    entity_name = profile.get_entity_links()[0].name
    collection = cg_client.get_entity_collection(entity_name)
    entities = collection.get_entities()
    if not entities:
        pytest.skip(f"No entities found for {entity_name} to test EntityObject.prompt.")
    entity = entities[0]
    prompt_str = entity.prompt()
    assert isinstance(prompt_str, str)
    assert "Entity Instance:" in prompt_str

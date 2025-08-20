from contentgrid_application_client import (
    ContentGridApplicationClient
)
from contentgrid_hal_client.exceptions import IncorrectAttributeType, MissingRequiredAttribute
from fixtures import auth_manager, cg_client # noqa: F401
import logging

default_values = {
    "text": "Management",
    "datetime": "2024-03-18T15:25:54.838Z",
    "checkbox": False,
    "number": 10,
}

def test_create_update_entity(cg_client: ContentGridApplicationClient):
    entity_name = "candidates"
    text_attribute = "name"

    candidates_profile = cg_client.get_entity_profile(entity_name)

    attributes = {}

    for property in candidates_profile.get_template("create-form").properties:
        if property.type.value in default_values.keys():
            attributes[property.name] = default_values[property.type.value]

    logging.info("Creating entity...")
    entity = cg_client.create_entity(entity_name, attributes=attributes)
    logging.info("Entity created.")

    assert entity.metadata is not None
    assert entity.id is not None
    assert entity.get_self_link() is not None
    assert entity.get_profile() is not None

    attributes[text_attribute] = "test-2"
    logging.info("Updating attributes with PUT")
    updated_entity = cg_client.put_entity_attributes(
        entity_link=entity.get_self_link(), attributes=attributes
    )
    logging.info("Updating attributes with PATCH")
    patched_entity = cg_client.patch_entity_attributes(
        entity_link=updated_entity.get_self_link(),
        attributes={text_attribute: "test-3"},
    )
    logging.info("done.")
    assert entity.metadata[text_attribute] == "Management"
    assert updated_entity.metadata[text_attribute] == "test-2"
    assert patched_entity.metadata[text_attribute] == "test-3"

    logging.info("Deleting entity...")
    entity.delete()

    entity_deleted = False
    try:
        cg_client.get_entity_instance(entity_link=entity.get_self_link())
    except Exception as e:
        logging.error(str(e))
        entity_deleted = True

    logging.info("Checking if entity is deleted")
    assert entity_deleted


def test_create_entity_required_relationship(cg_client: ContentGridApplicationClient):
    entity_name = "anonymous-candidates"

    test_candidate = cg_client.create_entity(
        pluralized_entity_name="candidates", attributes={}
    )

    attributes = {
        "anonymized_name": "test-candidate",
        "original": test_candidate.get_self_link(),
    }

    test_anon_candidate = cg_client.create_entity(entity_name, attributes=attributes)
    
    test_anon_candidate.delete()
    test_candidate.delete()


def test_create_entity_incorrect_params(cg_client: ContentGridApplicationClient):
    entity_name = "anonymous-candidates"

    threw_error = False
    try:
        cg_client.create_entity(entity_name, {"anonymized_name": 123})
    except IncorrectAttributeType:
        threw_error = True
    except MissingRequiredAttribute:
        threw_error = True

    assert threw_error

    test_candidate = cg_client.create_entity(
        pluralized_entity_name="candidates", attributes={}
    )

    threw_error = False
    try:
        entity = cg_client.create_entity(
            entity_name,
            {
                "anonymized_name": 123,
                "original": test_candidate.get_self_link(),
            },
        )
    except IncorrectAttributeType:
        threw_error = True
    except MissingRequiredAttribute:
        threw_error = True

    assert threw_error

    threw_error = False
    try:
        entity = cg_client.create_entity(
            entity_name,
            {
                "anonymized_name": "test-candidate",
                "original": test_candidate.get_self_link(),
            },
        )
    except IncorrectAttributeType:
        threw_error = True
    except MissingRequiredAttribute:
        threw_error = True

    assert not threw_error

    entity.delete()

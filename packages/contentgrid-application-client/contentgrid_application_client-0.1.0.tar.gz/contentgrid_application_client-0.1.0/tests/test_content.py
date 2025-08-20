from contentgrid_application_client import ContentGridApplicationClient
from contentgrid_hal_client.exceptions import BadRequest, NotFound
from fixtures import auth_manager, cg_client, pdf_file_path, img_file_path # noqa: F401
import logging
import os


def test_add_content(
    cg_client: ContentGridApplicationClient, pdf_file_path: str, img_file_path: str
):
    os.makedirs("output", exist_ok=True)
    entity_name = "candidates"
    logging.info("Creating test entity...")
    entity = cg_client.create_entity(entity_name, attributes={"name": "test"})

    has_failed = False
    try:
        cg_client.put_content_attribute(
            entity_link=entity.get_self_link(),
            content_attribute_name="test",
            filepath=pdf_file_path,
        )
    except NotFound:
        has_failed = True
    assert has_failed

    has_failed = False
    try:
        cg_client.put_content_attribute(
            entity_link=entity.get_self_link(),
            content_attribute_name="content",
            filepath="test.pdf",
        )
    except BadRequest:
        has_failed = True
    assert has_failed

    logging.info("Adding pdf content...")
    contentlink = cg_client.put_content_attribute(
        entity_link=entity.get_self_link(),
        content_attribute_name="content",
        filepath=pdf_file_path,
    )
    logging.info(contentlink.uri)
    logging.info("validating that content exists")
    filename, file = cg_client.fetch_content_attribute(
        content_link=contentlink
    )

    filepath = os.path.join("output", filename)
    with open(filepath, 'wb') as f:
        f.write(file)

    assert os.path.exists(filepath)

    logging.info("Adding img content...")
    contentlink = cg_client.put_on_content_link(
        content_link=contentlink, filepath=img_file_path
    )
    logging.info(contentlink.uri)
    logging.info("validating that content exists")
    filename, file = cg_client.fetch_content_attribute(
        content_link=contentlink
    )

    filepath = os.path.join("output", filename)
    with open(filepath, 'wb') as f:
        f.write(file)

    assert os.path.exists(filepath)


def test_add_multiple_content(
    cg_client: ContentGridApplicationClient, pdf_file_path: str, img_file_path: str
):
    entity_name = "candidates"
    logging.info("creating test entity...")
    entity = cg_client.create_entity(entity_name, attributes={"name": "test"})
    logging.info("Adding pdf content...")
    cg_client.put_content_attribute(
        entity_link=entity.get_self_link(),
        content_attribute_name="content",
        filepath=pdf_file_path,
    )
    cg_client.put_content_attribute(
        entity_link=entity.get_self_link(),
        content_attribute_name="json_annotations",
        filepath=img_file_path,
    )
    content_file_paths = cg_client.fetch_all_content_attributes_from_entity_link(entity_link=entity.get_self_link())
    assert len(content_file_paths) == 2
    cg_client.delete_link(entity.get_self_link())



from typing import List
from contentgrid_application_client import ContentGridApplicationClient
from contentgrid_hal_client import HALLink
from fixtures import auth_manager, cg_client # noqa: F401


def test_curies(cg_client:ContentGridApplicationClient):
    entity_link_relation = "https://contentgrid.cloud/rels/contentgrid/entity"
    profile = cg_client.get_profile()

    entity_links : List[HALLink] = profile.get_entity_links()

    assert len(entity_links) > 0
    for entity_link in entity_links:
        assert entity_link.link_relation == entity_link_relation

    assert "cg:entity" == profile.curie_registry.compact_curie(entity_link_relation)
    assert profile.curie_registry.expand_curie("cg:entity") == entity_link_relation
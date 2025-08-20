from contentgrid_application_client import ContentGridApplicationClient, EntityCollection
from fixtures import auth_manager, cg_client # noqa: F401

def test_relations(cg_client: ContentGridApplicationClient):
    entity_name = "candidates"
    relation_name = "skills"

    entity = cg_client.create_entity(entity_name, {"name": "test"})

    # fetch related skills
    related_skills = cg_client.get_entity_relation_collection(
        entity.get_self_link(), relation_name
    )

    assert isinstance(related_skills, EntityCollection)

    # entity just instantiated so no skills
    assert len(related_skills.get_entities()) == 0

    skills = cg_client.get_entity_collection("skills")

    amt_skills_to_sample = 4
    skills_selection = skills.get_entities()[:amt_skills_to_sample]
    assert len(skills_selection) == amt_skills_to_sample

    skills_selection[1] = skills_selection[1].get_self_link().uri
    skills_selection[2] = skills_selection[2].get_self_link()

    cg_client.put_entity_relation(
        entity.get_self_link(),
        relation_name=relation_name,
        related_entity_links=skills_selection[:-1],
    )

    related_skills = cg_client.get_entity_relation_collection(
        entity_link=entity.get_self_link(), relation_name=relation_name
    )

    assert len(related_skills.get_entities()) == amt_skills_to_sample - 1

    # post last skill
    cg_client.post_entity_relation(
        entity_link=entity.get_self_link(),
        relation_name=relation_name,
        related_entity_links=[skills_selection[-1]],
    )

    related_skills = cg_client.get_entity_relation_collection(
        entity_link=entity.get_self_link(), relation_name=relation_name
    )
    assert len(related_skills.get_entities()) == amt_skills_to_sample

    cg_client.delete_link(entity.get_self_link())

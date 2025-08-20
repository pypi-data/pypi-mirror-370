from datetime import datetime
from contentgrid_application_client import (
    ContentGridApplicationClient,
    EntitySearch,
    AttributeMatchSearch,
    AttributeRangeSearch,
    RelationSearch,
)
from contentgrid_application_client.application import is_valid_date_format
from fixtures import cg_client, auth_manager # noqa: F401
from unittest.mock import MagicMock
import logging
import pytest

def test_search_with_prefix_suffix(cg_client: ContentGridApplicationClient):
    entity_name = "candidates"

    # Create search parameters with prefix and suffix
    match_search = AttributeMatchSearch(attribute_name="name", value="John")
    range_search = AttributeRangeSearch(attribute_name="age", min_value=25, max_value=35)

    relation_search = RelationSearch(relation_name="skills", attribute_searches=[AttributeMatchSearch(attribute_name="name", value="Machine Learning")])

    entity_search = EntitySearch(
        entity_name=entity_name,
        attribute_searches=[match_search, range_search],
        relation_searches=[relation_search]
    )

    logging.info("Performing search with transformed parameters...")
    results = cg_client.execute_entity_search(
        entity_search=entity_search
    )

    assert results is not None
    assert len(results) == 1
    logging.info("Search completed successfully.")

def test_search_with_limit(cg_client: ContentGridApplicationClient):
    entity_name = "candidates"

    # Mock the generator to return a fixed number of results
    mock_generator = MagicMock()
    mock_generator.get_entities_paged_generator.return_value = iter(["entity1", "entity2", "entity3"])
    cg_client.get_search_entity_collection = MagicMock(return_value=mock_generator)

    entity_search = EntitySearch(entity_name=entity_name)
    results = cg_client.execute_entity_search(entity_search=entity_search, nb_results=2)

    assert results is not None
    assert len(results) == 2
    assert results == ["entity1", "entity2"]
    logging.info("Search with limit completed successfully.")

def test_search_with_no_results(cg_client: ContentGridApplicationClient):
    entity_name = "candidates"

    # Mock the generator to return no results
    mock_generator = MagicMock()
    mock_generator.get_entities_paged_generator.return_value = iter([])
    cg_client.get_search_entity_collection = MagicMock(return_value=mock_generator)

    entity_search = EntitySearch(entity_name=entity_name)
    results = cg_client.execute_entity_search(entity_search=entity_search)

    assert results == []
    logging.info("Search with no results completed successfully.")

def test_search_with_only_relation(cg_client: ContentGridApplicationClient):
    entity_name = "projects"

    # Create a relation search
    relation_search = RelationSearch(relation_name="team", attribute_searches=[AttributeMatchSearch(attribute_name="role", value="Manager")])

    entity_search = EntitySearch(
        entity_name=entity_name,
        relation_searches=[relation_search]
    )

    # Mock the generator to return a single result
    mock_generator = MagicMock()
    mock_generator.get_entities_paged_generator.return_value = iter(["entity1"])
    cg_client.get_search_entity_collection = MagicMock(return_value=mock_generator)

    results = cg_client.execute_entity_search(entity_search=entity_search)

    assert results == ["entity1"]
    logging.info("Search with only relation completed successfully.")

def test_search_with_range_only(cg_client: ContentGridApplicationClient):
    entity_name = "products"

    # Create a range search
    range_search = AttributeRangeSearch(attribute_name="price", min_value=100, max_value=500)

    entity_search = EntitySearch(
        entity_name=entity_name,
        attribute_searches=[range_search]
    )

    # Mock the generator to return multiple results
    mock_generator = MagicMock()
    mock_generator.get_entities_paged_generator.return_value = iter(["product1", "product2", "product3"])
    cg_client.get_search_entity_collection = MagicMock(return_value=mock_generator)

    results = cg_client.execute_entity_search(entity_search=entity_search)

    assert results == ["product1", "product2", "product3"]
    logging.info("Search with range only completed successfully.")

def test_search_with_large_limit(cg_client):
    """Test behavior when the limit is larger than the number of available results."""
    entity_name = "candidates"

    # Mock the generator to return fewer results than the limit
    mock_generator = MagicMock()
    mock_generator.get_entities_paged_generator.return_value = iter(["entity1", "entity2"])
    cg_client.get_search_entity_collection = MagicMock(return_value=mock_generator)

    entity_search = EntitySearch(entity_name=entity_name)
    results = cg_client.execute_entity_search(entity_search=entity_search, nb_results=10)

    assert results == ["entity1", "entity2"]

def test_search_with_no_limit(cg_client):
    """Test behavior when no limit is provided."""
    entity_name = "candidates"

    # Mock the generator to return multiple results
    mock_generator = MagicMock()
    mock_generator.get_entities_paged_generator.return_value = iter(["entity1", "entity2", "entity3"])
    cg_client.get_search_entity_collection = MagicMock(return_value=mock_generator)

    entity_search = EntitySearch(entity_name=entity_name)
    results = cg_client.execute_entity_search(entity_search=entity_search)

    assert results == ["entity1", "entity2", "entity3"]

def test_search_with_multiple_attribute_searches(cg_client):
    """Test behavior when multiple attribute searches are provided."""
    entity_name = "products"

    # Create multiple attribute searches
    match_search1 = AttributeMatchSearch(attribute_name="category", value="electronics")
    match_search2 = AttributeMatchSearch(attribute_name="brand", value="brandX")

    entity_search = EntitySearch(
        entity_name=entity_name,
        attribute_searches=[match_search1, match_search2],
    )

    # Mock the generator to return results
    mock_generator = MagicMock()
    mock_generator.get_entities_paged_generator.return_value = iter(["product1", "product2"])
    cg_client.get_search_entity_collection = MagicMock(return_value=mock_generator)

    results = cg_client.execute_entity_search(entity_search=entity_search)

    assert results == ["product1", "product2"]

def test_search_with_combined_range_and_relation(cg_client):
    """Test behavior when both range and relation searches are combined."""
    entity_name = "projects"

    # Create a range search and a relation search
    range_search = AttributeRangeSearch(attribute_name="budget", min_value=1000, max_value=5000)
    relation_search = RelationSearch(
        relation_name="team",
        attribute_searches=[AttributeMatchSearch(attribute_name="role", value="Developer")],
    )

    entity_search = EntitySearch(
        entity_name=entity_name,
        attribute_searches=[range_search],
        relation_searches=[relation_search],
    )

    # Mock the generator to return results
    mock_generator = MagicMock()
    mock_generator.get_entities_paged_generator.return_value = iter(["project1", "project2"])
    cg_client.get_search_entity_collection = MagicMock(return_value=mock_generator)

    results = cg_client.execute_entity_search(entity_search=entity_search)

    assert results == ["project1", "project2"]

def test_search_with_no_attribute_or_relation(cg_client):
    """Test behavior when no attributes or relations are provided."""
    entity_name = "tasks"

    entity_search = EntitySearch(entity_name=entity_name)

    # Mock the generator to return results
    mock_generator = MagicMock()
    mock_generator.get_entities_paged_generator.return_value = iter(["task1", "task2", "task3"])
    cg_client.get_search_entity_collection = MagicMock(return_value=mock_generator)

    results = cg_client.execute_entity_search(entity_search=entity_search)

    assert results == ["task1", "task2", "task3"]

def test_search_with_invalid_entity_name(cg_client):
    """Test behavior when an invalid entity name is provided."""
    entity_name = "invalid_entity"

    entity_search = EntitySearch(entity_name=entity_name)

    # Mock the generator to raise an exception
    cg_client.get_search_entity_collection = MagicMock(side_effect=Exception("Entity not found"))

    with pytest.raises(Exception, match="Entity not found"):
        cg_client.execute_entity_search(entity_search=entity_search)


def test_search_skills_limited(cg_client):
    skills_entity_name = "skills"
    skills = cg_client.execute_entity_search(entity_search=EntitySearch(skills_entity_name, attribute_searches=[], relation_searches=[]), nb_results=10)
    assert len(skills) == 10


def test_all_fetched(cg_client):
    candidate_entity_name = "candidates"
    entity_search = EntitySearch(candidate_entity_name, attribute_searches=[AttributeMatchSearch(attribute_name="name", value="test")])
    collection = cg_client.get_search_entity_collection(entity_search=entity_search)
    items = collection.page_info.total_items_exact if collection.page_info.total_items_exact else collection.page_info.total_items_estimate
    candidates = cg_client.execute_entity_search(entity_search=entity_search) 
    assert items - 20 <= len(candidates)
    assert items + 20 >= len(candidates)


def test_non_existant_attribute(cg_client):
    non_existant_search = AttributeMatchSearch("non-existant", value="no")

    entity_search = EntitySearch("candidates" , attribute_searches=[non_existant_search])
    with pytest.raises(ValueError, match="not found in entity"):
        cg_client.execute_entity_search(entity_search=entity_search)

    non_existant_search.ignore_errors = True
    entity_search = EntitySearch("candidates" , attribute_searches=[non_existant_search])
    candidates = cg_client.execute_entity_search(entity_search=entity_search, nb_results=1)
    assert len(candidates) == 1

def test_search_different_types(cg_client):
    age_range = AttributeRangeSearch("age", min_value=10, max_value=40)
    name_match = AttributeMatchSearch("name", value="test")
    entity_search = EntitySearch("candidates", attribute_searches=[age_range, name_match])
    candidates = cg_client.execute_entity_search(entity_search, nb_results=1)
    assert len(candidates) >= 0


def test_conversion_of_datetime(cg_client):
    date_range = AttributeRangeSearch("date", min_value=datetime(2025,4,24), max_value=datetime(2026, 4, 24))
    assert isinstance(date_range.min_value, str)
    assert isinstance(date_range.max_value, str)
    assert is_valid_date_format(date_range.min_value)
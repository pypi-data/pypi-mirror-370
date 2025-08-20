from enum import Enum
from typing import Any, Generator, List, Optional, Self, Sequence, Union, cast
from contentgrid_hal_client.hal_forms import HALFormsTemplate
import requests
import os
import logging
import mimetypes

from contentgrid_hal_client.exceptions import BadRequest, IncorrectAttributeType, MissingRequiredAttribute, NotFound, MissingHALTemplate
from contentgrid_hal_client.hal import CurieRegistry, HALFormsClient, HALLink, HALResponse, InteractiveHALResponse
from contentgrid_hal_client.security import ApplicationAuthenticationManager
from datetime import datetime
from email.header import decode_header
from itertools import islice

from contentgrid_hal_client.exceptions import Unauthorized

hal_form_type_check = {
    "text": (lambda value: isinstance(value, str)),
    "datetime": (lambda value: is_valid_date_format(value)),
    "checkbox": (lambda value: isinstance(value, bool)),
    "number": (lambda value: isinstance(value, (int, float))),
    "url": (lambda value: value.startswith("http://") or value.startswith("https://")),
}

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


def is_valid_date_format(date_string):
    try:
        datetime.strptime(date_string, DATETIME_FORMAT)
        return True
    except ValueError:
        return False


hal_form_types = {"text": "string", "datetime": "date (e.g.:2024-03-20T16:48:59.904Z)", "checkbox": "boolean", "number": "int/float", "url": "url"}


class InteractiveApplicationResponse(InteractiveHALResponse):
    def __init__(self, data: dict, client: "ContentGridApplicationClient", curie_registry: CurieRegistry = None) -> None:
        assert isinstance(client, ContentGridApplicationClient)
        super().__init__(data, client, curie_registry)
        self.client: ContentGridApplicationClient = client


class SearchType(Enum):
    EXACT_MATCH = "exact-match"
    PREFIX_MATCH = "prefix-match"
    LESS_THAN = "less-than"
    LESS_THAN_OR_EQUAL = "less-than-or-equal"
    GREATER_THAN = "greater-than"
    GREATER_THAN_OR_EQUAL = "greater-than-or-equal"
    CASE_INSENSITIVE_MATCH = "case-insensitive-match"


class SearchOption(InteractiveApplicationResponse):
    def __init__(self, data: dict, client: "ContentGridApplicationClient", curie_registry: CurieRegistry = None):
        super().__init__(data, client, curie_registry)
        self.parameter_name: str = data["name"]
        self.title: str = data.get("title", self.parameter_name)
        self.type: Optional[SearchType]
        try:
            self.type = SearchType(data["type"])
        except ValueError:
            self.type = None

    def __str__(self) -> str:
        return f"SearchOption(param={self.parameter_name}, type={self.type})"

    def __repr__(self) -> str:
        return self.__str__()


class SearchParam:
    def __init__(self, value: Any, option: SearchOption, key_prefix: str = "", key_suffix: str = "") -> None:
        self.value = value
        self.option = option
        self.key_prefix = key_prefix
        self.key_suffix = key_suffix

    def to_dict(self) -> dict:
        return {
            f"{self.key_prefix}{self.option.parameter_name}{self.key_suffix}": self.value,
        }

    def __str__(self) -> str:
        return f"SearchParam(value={self.value}, option={self.option})"


class EntityCollection(InteractiveApplicationResponse):
    def __init__(self, data: dict, client: "ContentGridApplicationClient", curie_registry: CurieRegistry = None) -> None:
        super().__init__(data, client, curie_registry)
        self.page_info: Optional[PageInfo] = None
        if "page" in data.keys():
            self.page_info = PageInfo(
                size=data["page"]["size"],
                number=data["page"]["number"],
                total_elements=data["page"].get("totalElements", None),
                total_pages=data["page"].get("totalPages", None),
                total_items_exact=data["page"].get("total_items_exact", None),
                total_items_estimate=data["page"].get("total_items_estimate", None),
                next_cursor=data["page"].get("next_cursor", None)
            )

    def get_entities(self) -> List["EntityObject"]:
        return self.get_embedded_objects_by_key("item", infer_type=EntityObject)

    def get_entities_paged_generator(self) -> Generator["EntityObject" , None, None]:
        has_next = True
        while has_next:
            for entity in self.get_entities():
                yield entity
            try:
                self.next()
            except NotFound:
                has_next = False
        return

    def get_entity_profile_link(self) -> HALLink:
        return cast(HALLink, self.get_link("profile"))
        
    def get_entity_profile(self) -> "EntityProfile":
        return self.client.follow_link(self.get_entity_profile_link(), infer_type=EntityProfile)

    def create_entity(self, attributes: dict, attribute_validation=True) -> "EntityObject":
        self.client._transform_hal_links_to_uris(attributes=attributes)
        if attribute_validation:
            entity_profile = self.client.follow_link(self.get_entity_profile_link(), infer_type=EntityProfile)
            self.client._validate_form_payload(template=entity_profile.get_template("create-form"), payload=attributes)
        response = self.client.post(self.get_self_link().uri, json=attributes, headers={"Content-Type": "application/json"})
        data = self.client._validate_json_response(response)
        return EntityObject(data=data, client=self.client)

    def search_entities(self, params: List[SearchParam] | dict) -> "EntityCollection":
        if isinstance(params, dict):
            search_params = params
        elif isinstance(params, list):
            search_params = {}
            for param in params:
                search_params.update(param.to_dict())
        else:
            raise BadRequest("params must be a dict or a list of SearchParam objects")

        entity_profile = self.get_entity_profile()
        try:
            search_template = entity_profile.get_template("search")
            assert search_template.target
            self.client._validate_form_payload(template=search_template, payload=search_params)
        except MissingHALTemplate:
            raise MissingHALTemplate(f"Search template was not present on {entity_profile.get_self_link().uri}")
        except AssertionError:
            raise MissingHALTemplate(f"Search target was not present on {entity_profile.get_self_link().uri}")
        response = self.client.get(search_template.target, params=search_params)
        data = self.client._validate_json_response(response)
        return EntityCollection(data=data, client=self.client)

    def first(self):
        if not self.has_link("first"):
            raise NotFound(f"Collection {self.get_self_link()} has no first page")
        self.__init__(data=self.client.follow_link(self.get_link("first"), infer_type=EntityCollection).data, client=self.client, curie_registry=self.curie_registry)

    def last(self):
        raise DeprecationWarning("Last page is deprecated")
        if not self.has_link("last"):
            raise NotFound(f"Collection {self.get_self_link()} has no last page")
        self.__init__(data=self.client.follow_link(self.get_link("last"), infer_type=EntityCollection).data, client=self.client, curie_registry=self.curie_registry)

    def has_next_page(self) -> bool:
        return self.has_link("next")

    def next(self):
        if not self.has_next_page():
            raise NotFound(f"Collection {self.get_self_link()} has no next page")
        self.__init__(data=self.client.follow_link(self.get_link("next"), infer_type=EntityCollection).data, client=self.client, curie_registry=self.curie_registry)

    def prev(self):
        if not self.has_link("prev"):
            raise NotFound(f"Collection {self.get_self_link()} has no prev page")
        self.__init__(data=self.client.follow_link(self.get_link("prev"), infer_type=EntityCollection).data, client=self.client, curie_registry=self.curie_registry)

    def prompt(self, include_entity_profile: bool = True) -> str:
        lines = []
        if include_entity_profile:
            lines.append(self.get_entity_profile().prompt())
        lines.append(f"GET request on {self.get_self_link().uri} Entity Collection Search Request Results ")
        if self.page_info:
            lines.append(f"Page Info: size={self.page_info.size}, total_elements={self.page_info.total_elements}, total_pages={self.page_info.total_pages}")
            if self.page_info.total_items_exact:
                lines.append(f"Total results : {self.page_info.total_items_exact}")
            else:
                lines.append(f"Total results : {self.page_info.total_items_estimate} (estimated)")
            if self.has_next_page():
                lines.append("Shown results are incomplete. To fetch next results use:")
                if self.page_info.next_cursor:
                    lines.append(f"next cursor: {self.page_info.next_cursor}")
                next_link = self.get_link("next")
                if next_link:
                    lines.append(f"URL : {next_link.uri}")
            else:
                lines.append("Shown results are complete. No other results remaining.")
        else:
            lines.append("No page info available.")
        lines.append("Entities:")
        count = 0
        for entity in self.get_entities():
            if self.page_info:
                lines.append(f'Entity [{count + self.page_info.number * self.page_info.size} / {self.page_info.total_items_estimate} ]')
            count += 1 
            lines.append(entity.prompt(include_entity_profile=False, include_relations=False, include_content=False))
        return "\n".join(lines)

class EntityObject(InteractiveApplicationResponse):
    def __init__(self, data: dict, client: "ContentGridApplicationClient", curie_registry: CurieRegistry = None) -> None:
        super().__init__(data, client, curie_registry)
        self.id = data["id"]

    def get_content_links(self) -> List[HALLink]:
        return self.get_links("https://contentgrid.cloud/rels/contentgrid/content")

    def get_relation_links(self) -> List[HALLink]:
        return self.get_links("https://contentgrid.cloud/rels/contentgrid/relation")

    def get_relation_link(self, relation_name: str) -> HALLink:
        relation_links = self.get_relation_links()
        for relation_link in relation_links:
            if relation_link.name == relation_name:
                return relation_link
        # If relation not found, raise exception.
        raise NotFound(f"Relation {relation_name} not found on entity {self.get_self_link().uri}")

    def get_profile(self) -> "EntityProfile":
        self_link_uri = self.get_self_link().uri
        for entity_profile in self.client.get_profile().get_entity_profiles_generator():
            item_describes = entity_profile._get_item_describes()
            if item_describes and item_describes.expand_template(id=self.id) == self_link_uri:
                return entity_profile
        raise NotFound(f"No entity profile describes {self_link_uri}")

    def get_relation_collection(self, relation_name: str, size: int = 20, params: dict = {}):
        params = self.client._add_page_and_size_to_params(size=size, params=params)
        relation_link = self.get_relation_link(relation_name=relation_name)
        return self.client.follow_link(relation_link, infer_type=EntityCollection, params=params)

    def put_relation(self, relation_name: str, related_entity_links: List[str | HALLink | Self]) -> None:
        relation_link = self.get_relation_link(relation_name=relation_name)
        relation_payload = self._create_text_uri_list_payload(links=related_entity_links)
        response = self.client.put(relation_link.uri, headers={"Accept": "*/*", "Content-Type": "text/uri-list"}, data=relation_payload)
        self.client._validate_non_json_response(response)

    def post_relation(self, relation_name: str, related_entity_links: List[str | HALLink | Self]) -> None:
        relation_link = self.get_relation_link(relation_name=relation_name)
        relation_payload = self._create_text_uri_list_payload(links=related_entity_links)
        response = self.client.post(relation_link.uri, headers={"Accept": "*/*", "Content-Type": "text/uri-list"}, data=relation_payload)
        self.client._validate_non_json_response(response)

    def put_data(self, data: dict, attribute_validation=True) -> None:
        self.client._transform_hal_links_to_uris(attributes=data)
        if attribute_validation:
            self.client._validate_form_payload(template=self.get_template("default"), payload=data)
        return super().put_data(data)

    def patch_data(self, data: dict, attribute_validation=True) -> None:
        self.client._transform_hal_links_to_uris(attributes=data)
        if attribute_validation:
            self.client._validate_form_payload(template=self.get_template("default"), payload=data)
        return super().patch_data(data)

    def put_content_attribute(self, content_attribute_name: str, filepath: str) -> HALLink:
        content_links = self.get_content_links()
        if len(content_links) > 0:
            for content_link in content_links:
                if content_link.name == content_attribute_name:
                    return self.client.put_on_content_link(content_link=content_link, filepath=filepath)
        raise NotFound(f"Content Attribute {content_attribute_name} not found on entity {self.get_self_link().uri}")

    def fetch_content_attribute_by_name(self, content_attribute_name: str) -> tuple[str, bytes]:
        content_links = self.get_content_links()
        if len(content_links) > 0:
            for content_link in content_links:
                if content_link.name == content_attribute_name:
                    return self.client.fetch_content_attribute(content_link=content_link)
        raise NotFound(f"Content Attribute {content_attribute_name} not found on entity {self.get_self_link().uri}")

    def fetch_all_content_attributes(self) -> List[tuple[str, bytes]]:
        files = []
        for hal_content_link in self.get_content_links():
            if self.metadata[hal_content_link.name] is not None:
                files.append(self.client.fetch_content_attribute(hal_content_link))
        return files

    def _create_text_uri_list_payload(self, links: Sequence[str | HALLink | HALResponse]) -> str:
        uri_list = []
        for link in links:
            if isinstance(link, HALLink):
                uri_list.append(link.uri)
            elif isinstance(link, HALResponse):
                uri_list.append(link.get_self_link().uri)
            elif isinstance(link, str):
                uri_list.append(link)
            else:
                raise BadRequest(f"Incorrect Link type {type(link)} in uri list payload, allowed types: HALLink, HALResponse or str")
        return "\n".join(uri_list)

    def prompt(self, include_entity_profile: bool = True, include_relations: bool = True, include_content: bool = True) -> str:
        """ Generate a prompt string for an entity instance.
        Args:
            include_entity_profile (bool): Whether to include the entity profile in the prompt.
            include_relations (bool): Whether to include the relations in the prompt (for now only the links are shown).
            include_content (bool): Whether to include the content attributes in the prompt (for now only the links are shown).
        """
        lines = []
        lines.append(f"Entity Instance: {self.get_self_link().uri}")
        if include_entity_profile:
            lines.append(self.get_profile().prompt())
        # self.metadata is a dict with attribute names as keys and their values
        lines.append(f"Attributes: {self.metadata}")
        # RELATIONS
        if include_relations:
            # TODO can be extended to include the related entity objects in the prompt representation.
            # The related entity objects can be unlimited so only the first page or a limited number of relations can be shown.
            # For now, we just show the relation names and URIs.
            relation_links = self.get_relation_links()
            if not relation_links:
                lines.append("Relations: No Relations defined for this entity.")
            else:
                lines.append("Relations:")
                for relation_link in relation_links:
                    lines.append(f"  - {relation_link.name}: resource {relation_link.uri}")
        # CONTENT ATTRIBUTES
        if include_content:
            # TODO can be extended to include the content of the documents in the prompt representation.
            # The content attributes can be unlimited so only the first page or a limited number of content attributes can be shown.
            # For now, we just show the content attribute names and URIs.
            content_links = self.get_content_links()
            if not content_links:
                lines.append("Content: No Content Attributes defined for this entity.")
            else:
                lines.append("Content:")
                for content_link in content_links:
                    lines.append(f"  - {content_link.name} (content attribute name): {content_link.uri}")
        return "\n".join(lines)

class Profile(InteractiveHALResponse):
    def __init__(self, data: dict, client: HALFormsClient, curie_registry: CurieRegistry = None) -> None:
        super().__init__(data, client, curie_registry)

    def get_entity_links(self) -> List[HALLink]:
        return self.get_links("https://contentgrid.cloud/rels/contentgrid/entity")

    def get_entity_profiles_generator(self) -> Generator["EntityProfile", None, None]:
        for entity_profile_link in self.get_entity_links():
            yield self.client.follow_link(entity_profile_link, infer_type=EntityProfile)

    def get_entity_profile_singular(self, singular_entity_name: str) -> "EntityProfile":  # type: ignore
        for entity_profile in self.get_entity_profiles_generator():
            if entity_profile.name == singular_entity_name:
                return entity_profile
        raise NotFound(f"Entity profile {singular_entity_name} does not exist.")

    def get_entity_profile(self, pluralized_entity_name: str) -> "EntityProfile":  # type: ignore
        for entity_profile_link in self.get_entity_links():
            if entity_profile_link.name == pluralized_entity_name:
                return self.client.follow_link(entity_profile_link, infer_type=EntityProfile)
        raise NotFound(f"Entity Profile {pluralized_entity_name} does not exist.")

    def plural_to_singular_entity_name(self, pluralized_entity_name: str) -> str:
        return self.get_entity_profile(pluralized_entity_name=pluralized_entity_name).name

    def singular_to_plural_entity_name(self, singular_entity_name: str) -> str:
        entity_profile = self.get_entity_profile_singular(singular_entity_name=singular_entity_name)
        for entity_profile_link in self.get_entity_links():
            if entity_profile_link.uri == entity_profile.get_self_link().uri:
                assert entity_profile_link.name
                return entity_profile_link.name
        return ""
    
    def prompt(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        lines = []
        for entity_profile in self.get_entity_profiles_generator():
            lines.append(entity_profile.prompt())
            lines.append("")  # Blank line between entities
        return "\n".join(lines)
    
    def __repr__(self) -> str:
        return self.__str__()


class RelationProfile(InteractiveApplicationResponse):
    def __init__(self, data: dict, client: "ContentGridApplicationClient", curie_registry: CurieRegistry = None):
        super().__init__(data, client, curie_registry)
        self.name = data["name"]
        self.title = data.get("title", self.name)
        self.description = data.get("description", "")
        self.required = data["required"]
        self.many_source_per_target = data["many_source_per_target"]
        self.many_target_per_source = data["many_target_per_source"]

    def get_related_entity_profile(self) -> "EntityProfile":
        return self.client.follow_link(self.get_link("https://contentgrid.cloud/rels/blueprint/target-entity"), infer_type=EntityProfile)

    def get_cardinality(self) -> str:
        return f"{'many' if self.many_source_per_target else 'one'}-to-{'many' if self.many_target_per_source else 'one'}"
        
    def prompt(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f"""
            Relation {self.name} [title: {self.title} required: {self.required} cardinality: {self.get_cardinality()}] <related_entity: {self.get_related_entity_profile().name}>
        """

class AttributeConstraint(InteractiveApplicationResponse):
    def __init__(self, data: dict, client: "ContentGridApplicationClient", curie_registry: CurieRegistry = None):
        super().__init__(data, client, curie_registry)
        self.type: str = data["type"]
        self.values: List[str] = data.get("values", [])
        
    def __str__(self) -> str:
        return f"AttributeConstraint(type={self.type}, values={self.values})"
    
    def __repr__(self) -> str:
        return self.__str__()


class AttributeProfile(InteractiveApplicationResponse):
    def __init__(self, data: dict, client: "ContentGridApplicationClient", curie_registry: CurieRegistry = None):
        super().__init__(data, client, curie_registry)
        self.name: str = data["name"]
        self.title: str = data.get("title", self.name)
        self.type: str = data["type"]
        self.description: str = data["description"]
        self.read_only: bool = data["readOnly"]
        self.required: bool = data["required"]

        # Using get_embedded_objects_by_key for all embedded objects
        self.nested_attributes: List[AttributeProfile] = self.get_embedded_objects_by_key("https://contentgrid.cloud/rels/blueprint/attribute", infer_type=AttributeProfile)
        self.search_options: List[SearchOption] = self.get_embedded_objects_by_key("https://contentgrid.cloud/rels/blueprint/search-param", infer_type=SearchOption)
        self.constraints: List[AttributeConstraint] = self.get_embedded_objects_by_key("https://contentgrid.cloud/rels/blueprint/constraint", infer_type=AttributeConstraint)

        # Private attributes for search options
        # Initialize private attributes for search options
        self.__prefix_search_option: Optional[SearchOption] = None
        self.__exact_search_option: Optional[SearchOption] = None
        self.__less_than_search_option: Optional[SearchOption] = None
        self.__less_than_or_equal_search_option: Optional[SearchOption] = None
        self.__greater_than_search_option: Optional[SearchOption] = None
        self.__greater_than_or_equal_search_option: Optional[SearchOption] = None

    def get_nested_attributes(self) -> List["AttributeProfile"]:
        return self.nested_attributes

    def is_content_attribute(self) -> bool:
        return self.type == "object" and any(attr.name in ["length", "mimetype", "filename"] for attr in self.nested_attributes)

    def get_constraints(self) -> List[AttributeConstraint]:
        return self.constraints

    def get_constraint(self, constraint_type: str) -> Optional[AttributeConstraint]:
        for constraint in self.constraints:
            if constraint.type == constraint_type:
                return constraint
        return None

    def has_required_constraint(self) -> bool:
        return self.get_constraint("required") is not None

    def has_constrained_values(self) -> bool:
        return self.get_constraint("allowed-values") is not None

    def get_allowed_values(self) -> Optional[List[str]]:
        if self.has_constrained_values():
            return self.get_constraint("allowed-values").values  # type: ignore
        return None

    def has_search_capability(self) -> bool:
        return len(self.search_options) > 0

    def get_search_option(self, search_type: SearchType) -> Optional[SearchOption]:
        for search_option in self.search_options:
            if search_option.type == search_type:
                return search_option
        return None

    def get_nested_attribute_by_name(self, name: str) -> Optional["AttributeProfile"]:
        for attr in self.nested_attributes:
            if attr.name == name:
                return attr
        return None

    @property
    def _prefix_search_option(self) -> Optional[SearchOption]:
        if self.__prefix_search_option is None:
            self.__prefix_search_option = self.get_search_option(search_type=SearchType.PREFIX_MATCH)
        return self.__prefix_search_option

    @property
    def _exact_search_option(self) -> Optional[SearchOption]:
        if self.__exact_search_option is None:
            exact_match = self.get_search_option(search_type=SearchType.EXACT_MATCH)
            case_insensitive_match = self.get_search_option(search_type=SearchType.CASE_INSENSITIVE_MATCH)
            if exact_match:
                self.__exact_search_option = exact_match
            elif case_insensitive_match:
                self.__exact_search_option = case_insensitive_match
        return self.__exact_search_option

    @property
    def _less_than_search_option(self) -> Optional[SearchOption]:
        if self.__less_than_search_option is None:
            self.__less_than_search_option = self.get_search_option(search_type=SearchType.LESS_THAN)
        return self.__less_than_search_option

    @property
    def _less_than_or_equal_search_option(self) -> Optional[SearchOption]:
        if self.__less_than_or_equal_search_option is None:
            self.__less_than_or_equal_search_option = self.get_search_option(search_type=SearchType.LESS_THAN_OR_EQUAL)
        return self.__less_than_or_equal_search_option

    @property
    def _greater_than_search_option(self) -> Optional[SearchOption]:
        if self.__greater_than_search_option is None:
            self.__greater_than_search_option = self.get_search_option(search_type=SearchType.GREATER_THAN)
        return self.__greater_than_search_option

    @property
    def _greater_than_or_equal_search_option(self) -> Optional[SearchOption]:
        if self.__greater_than_or_equal_search_option is None:
            self.__greater_than_or_equal_search_option = self.get_search_option(search_type=SearchType.GREATER_THAN_OR_EQUAL)
        return self.__greater_than_or_equal_search_option
    
    def prompt(self) -> str:
        return self.__str__()
    
    def __str__(self) -> str:
        return f"""
            Attribute {self.name} [type: {self.type} read_only: {self.read_only} required: {self.required}] <searchable: {self.has_search_capability()} options: {self.search_options}>  <constraints: {self.constraints}> <nested: {self.nested_attributes}>
        """
    
    def __repr__(self) -> str:
        return self.__str__()


class EntityProfile(InteractiveApplicationResponse):
    def __init__(self, data: dict, client: "ContentGridApplicationClient", curie_registry: CurieRegistry = None):
        super().__init__(data, client, curie_registry)
        self.name: str = data["name"]  # This is the singular_name
        self.title: str = data.get("title", self.name)
        self.description: str = data.get("description", "")
        assert len(self.get_describes()) > 0 # Used to fail initialization if profile is not valid.

    def get_attribute_profiles(self) -> List[AttributeProfile]:
        return self.get_embedded_objects_by_key("https://contentgrid.cloud/rels/blueprint/attribute", infer_type=AttributeProfile)

    def has_search_capability(self) -> bool:
        attribute_profiles = self.get_attribute_profiles()
        return any(attr.has_search_capability() for attr in attribute_profiles)

    def get_attribute_profile(self, attribute_name: str) -> Optional[AttributeProfile]:
        attribute_profiles = self.get_attribute_profiles()
        for attribute_profile in attribute_profiles:
            if attribute_profile.name == attribute_name:
                return attribute_profile
        raise ValueError(f"Attribute {attribute_name} not found in entity {self.name}")

    def get_relation_profiles(self) -> List[RelationProfile]:
        return self.get_embedded_objects_by_key("https://contentgrid.cloud/rels/blueprint/relation", infer_type=RelationProfile)

    def get_relation_profile(self, relation_name: str) -> RelationProfile:
        relation_profiles = self.get_relation_profiles()
        for relation_profile in relation_profiles:
            if relation_profile.name == relation_name:
                return relation_profile
        raise ValueError(f"Relation {relation_name} not found in entity {self.name}")

    def get_describes(self) -> List[HALLink]:
        describes_links = self.get_links("describes")
        try:
            assert len(describes_links) > 0
        except AssertionError:
            raise Exception("Not a valid entity profile. Did not contain any describes link.")
        return describes_links

    def _get_item_describes(self) -> Optional[HALLink]:
        descriptions = self.get_describes()
        for description in descriptions:
            if description.name == "item":
                return description
        return None

    def _get_collection_describes(self) -> Optional[HALLink]:
        descriptions = self.get_describes()
        for description in descriptions:
            if description.name == "collection":
                return description
        return None
    
    def prompt(self) -> str:
        return self.__str__()
    
    def __str__(self) -> str:
        lines = []
        lines.append(f"Entity: {self.name}")
        lines.append(f"\tTitle: {self.title}")
        lines.append(f"\tDescription: {self.description}")
        # Attributes
        attributes = self.get_attribute_profiles()
        if attributes:
            lines.append("\tAttributes:")
            for attr in attributes:
                lines.append(f"\t\t{attr.prompt()}")
        else:
            lines.append("\tAttributes: None")
        # Relations
        relations = self.get_relation_profiles()
        if relations:
            lines.append("\tRelations:")
            for rel in relations:
                lines.append(f"\t\t{rel.prompt()}")
        else:
            lines.append("\tRelations: None")
        return "\n".join(lines)


class PageInfo:
    def __init__(self, size: int, total_elements: int, total_pages: int, number: int, total_items_exact: Optional[int], total_items_estimate: Optional[int], next_cursor: Optional[str]) -> None:
        # DEPRECATION total_elements and total_pages are deprecated in contentgrid paged implementation.
        # Use total_items_exact, total_items_estimate and next_cursor instead 
        self.size: int = size
        self.number: int = number
        self.total_elements: Optional[int] = total_elements
        self.total_pages: Optional[int] = total_pages
        self.total_items_exact: Optional[int] = total_items_exact
        self.total_items_estimate: Optional[int] = total_items_estimate
        self.next_cursor: Optional[str] = next_cursor


_search_form_relation_delimiter = "."


class AttributeMatchSearch:
    def __init__(self, attribute_name: str, value: Union[float | int | datetime | bool | str], prefer_prefix: bool = True, ignore_errors: bool = False) -> None:
        self.attribute_name: str = attribute_name
        self.value: Union[float | int | datetime | bool | str] = value
        self.prefer_prefix: bool = prefer_prefix
        self.ignore_errors: bool = ignore_errors

    def get_search_params(self, attribute_profile: AttributeProfile) -> List[SearchParam]:
        search_params = []
        if self.value is not None:
            if not self.ignore_errors:
                if not attribute_profile.has_search_capability():
                    raise BadRequest(f"Attribute {self.attribute_name} does not support search. Available options: {attribute_profile.search_options}")
                if not attribute_profile._exact_search_option and not attribute_profile._prefix_search_option:
                    raise BadRequest(f"Attribute {self.attribute_name} does not support exact search. Available options: {attribute_profile.search_options}")

            # Exact or prefix match if possible
            if attribute_profile._prefix_search_option and (self.prefer_prefix or not attribute_profile._exact_search_option):
                search_params.append(SearchParam(value=self.value, option=attribute_profile._prefix_search_option))
            elif attribute_profile._exact_search_option:
                search_params.append(SearchParam(value=self.value, option=attribute_profile._exact_search_option))

        return search_params


class AttributeRangeSearch:
    def __init__(
        self,
        attribute_name: str,
        min_value: Optional[Union[float | int | datetime]] = None,
        max_value: Optional[Union[float | int | datetime]] = None,
        include_boundaries: bool = True,
        ignore_errors: bool = False,
    ) -> None:
        self.attribute_name: str = attribute_name

        self.min_value: Optional[Union[float | int | str]]
        if isinstance(min_value, datetime):
            self.min_value = datetime.strftime(min_value, DATETIME_FORMAT)
        else:
            self.min_value = min_value

        self.max_value: Optional[Union[float | int | str]]
        if isinstance(max_value, datetime):
            self.max_value = datetime.strftime(max_value, DATETIME_FORMAT)
        else:
            self.max_value = max_value

        self.include_boundaries: bool = include_boundaries
        self.ignore_errors: bool = ignore_errors

    def get_search_params(self, attribute_profile: AttributeProfile) -> List[SearchParam]:
        search_params = []
        if self.min_value is not None:
            if not self.ignore_errors:
                if not attribute_profile._greater_than_or_equal_search_option and not attribute_profile._greater_than_search_option:
                    raise BadRequest(f"Attribute {self.attribute_name} does not support range search. Available options: {attribute_profile.search_options}")

            # Range search for minimum value
            if attribute_profile._greater_than_or_equal_search_option and self.include_boundaries:
                search_params.append(SearchParam(value=self.min_value, option=attribute_profile._greater_than_or_equal_search_option))
            elif attribute_profile._greater_than_search_option and not self.include_boundaries:
                search_params.append(SearchParam(value=self.min_value, option=attribute_profile._greater_than_search_option))

        if self.max_value is not None:
            if not self.ignore_errors:
                if not attribute_profile._less_than_or_equal_search_option and not attribute_profile._less_than_search_option:
                    raise BadRequest(f"Attribute {self.attribute_name} does not support range search. Available options: {attribute_profile.search_options}")

            # Range search for maximum value
            if attribute_profile._less_than_or_equal_search_option and self.include_boundaries:
                search_params.append(SearchParam(value=self.max_value, option=attribute_profile._less_than_or_equal_search_option))
            elif attribute_profile._less_than_search_option and not self.include_boundaries:
                search_params.append(SearchParam(value=self.max_value, option=attribute_profile._less_than_search_option))

        return search_params


class RelationSearch:
    def __init__(self, relation_name: str, attribute_searches: List[AttributeMatchSearch | AttributeRangeSearch] = [], ignore_errors: bool = False) -> None:
        self.relation_name: str = relation_name
        self.attribute_searches: List[AttributeMatchSearch | AttributeRangeSearch] = attribute_searches
        self.ignore_errors: bool = ignore_errors


class EntitySearch:
    def __init__(self, entity_name: str, attribute_searches: List[AttributeMatchSearch | AttributeRangeSearch] = [], relation_searches: List[RelationSearch] = []) -> None:
        self.entity_name: str = entity_name
        self.attribute_searches: List[AttributeMatchSearch | AttributeRangeSearch] = attribute_searches
        self.relation_searches: List[RelationSearch] = relation_searches

    def transform_to_params(self, entity_profile: EntityProfile) -> List[SearchParam]:
        params = []
        params.extend(self.__transform_attribute_searches_to_params(entity_profile=entity_profile, attribute_searches=self.attribute_searches))

        for relation_search in self.relation_searches:
            try:
                relation_profile = entity_profile.get_relation_profile(relation_name=relation_search.relation_name)
                related_entity_profile = relation_profile.get_related_entity_profile()
            except ValueError as e:
                if not relation_search.ignore_errors:
                    raise e
                else:
                    relation_profile = None
                    related_entity_profile = None

            if relation_profile is not None and related_entity_profile is not None:
                params.extend(
                    self.__transform_attribute_searches_to_params(
                        entity_profile=related_entity_profile,
                        attribute_searches=relation_search.attribute_searches,
                        key_prefix=relation_search.relation_name + _search_form_relation_delimiter,
                    )
                )

        return params

    def __transform_attribute_searches_to_params(
        self, entity_profile: EntityProfile, attribute_searches: List[AttributeMatchSearch | AttributeRangeSearch], key_prefix: str = "", key_suffix: str = ""
    ) -> List[SearchParam]:
        params = []
        for attribute_search in attribute_searches:
            try:
                attribute_profile = entity_profile.get_attribute_profile(attribute_name=attribute_search.attribute_name)
            except ValueError as e:
                if not attribute_search.ignore_errors:
                    raise e
                else:
                    attribute_profile = None

            if attribute_profile is not None:
                search_params = attribute_search.get_search_params(attribute_profile=attribute_profile)
                if key_prefix or key_suffix:
                    for search_param in search_params:
                        if key_prefix:
                            search_param.key_prefix = key_prefix
                        if key_suffix:
                            search_param.key_suffix = key_suffix
                params.extend(search_params)
        return params


class ContentGridApplicationClient(HALFormsClient):
    def __init__(
        self,
        client_endpoint: str,
        auth_uri: str = None,
        auth_manager: ApplicationAuthenticationManager = None,
        client_id: str = None,
        client_secret: str = None,
        token: str = None,
        attribute_validation: bool = True,
        session_cookie: str = None,
        pool_maxsize: int = 10,
    ) -> None:
        logging.info("Initializing ContentGridApplicationClient...")
        super().__init__(
            client_endpoint=client_endpoint,
            auth_uri=auth_uri,
            auth_manager=auth_manager,
            client_id=client_id,
            client_secret=client_secret,
            token=token,
            session_cookie=session_cookie,
            pool_maxsize=pool_maxsize,
        )
        self.attribute_validation = attribute_validation

    def get_profile(self) -> Profile:
        response = self.get("/profile", headers={"Accept": "application/json"})
        data = self._validate_json_response(response)
        return Profile(data, client=self)

    def get_entity_profile(self, pluralized_entity_name: str) -> EntityProfile:
        return self.get_profile().get_entity_profile(pluralized_entity_name=pluralized_entity_name)

    def get_entity_profile_singular(self, singular_entity_name: str) -> EntityProfile:
        return self.get_profile().get_entity_profile_singular(singular_entity_name=singular_entity_name)

    def get_entity_profiles(self) -> List[EntityProfile]:
        return [entity_profile for entity_profile in self.get_profile().get_entity_profiles_generator()]

    def fetch_openapi_yaml(self) -> tuple[str, bytes]:
        res = self.get("/openapi.yml")
        self._validate_non_json_response(res)
        return ("openapi.yml", res.content)

    def get_entity_collection(self, plural_entity_name: str, size: int = 20, params: dict = {}) -> EntityCollection:
        params = self._add_page_and_size_to_params(size=size, params=params)
        try:
            response = self.get(plural_entity_name, params=params)
        except Unauthorized:
            singular_entity_name = plural_entity_name
            response = self.get(self.get_profile().singular_to_plural_entity_name(singular_entity_name=singular_entity_name), params=params)
        data = self._validate_json_response(response)
        return EntityCollection(data, client=self)

    def create_entity(self, pluralized_entity_name: str, attributes: dict) -> EntityObject:
        return self.get_entity_collection(plural_entity_name=pluralized_entity_name).create_entity(attributes=attributes, attribute_validation=self.attribute_validation)

    def get_entity_instance(self, entity_link: HALLink | EntityObject) -> EntityObject:
        if isinstance(entity_link, EntityObject):
            return self.follow_link(entity_link.get_self_link(), infer_type=EntityObject)
        elif isinstance(entity_link, HALLink):
            return self.follow_link(entity_link, infer_type=EntityObject)
        else:
            raise BadRequest(f"entity_link should be of type EntityObject or HALLink. was type {type(entity_link)}")

    def get_entity_relation_collection(self, entity_link: HALLink, relation_name: str, size: int = 20, params: dict = {}) -> EntityCollection:
        return self.get_entity_instance(entity_link=entity_link).get_relation_collection(relation_name=relation_name, size=size, params=params)

    def put_entity_relation(self, entity_link: HALLink, relation_name: str, related_entity_links: List[str | HALLink | EntityObject]) -> None:
        return self.get_entity_instance(entity_link=entity_link).put_relation(relation_name=relation_name, related_entity_links=related_entity_links)

    def post_entity_relation(self, entity_link: HALLink, relation_name: str, related_entity_links: List[str | HALLink | EntityObject]) -> None:
        return self.get_entity_instance(entity_link=entity_link).post_relation(relation_name=relation_name, related_entity_links=related_entity_links)

    def put_entity_attributes(self, entity_link: HALLink, attributes: dict) -> EntityObject:
        entity = self.get_entity_instance(entity_link=entity_link)
        entity.put_data(data=attributes, attribute_validation=self.attribute_validation)
        return entity

    def patch_entity_attributes(self, entity_link: HALLink, attributes: dict) -> EntityObject:
        entity = self.get_entity_instance(entity_link=entity_link)
        entity.patch_data(data=attributes, attribute_validation=self.attribute_validation)
        return entity

    def put_content_attribute(self, entity_link: HALLink, content_attribute_name: str, filepath: str) -> HALLink:
        return self.get_entity_instance(entity_link=entity_link).put_content_attribute(content_attribute_name=content_attribute_name, filepath=filepath)

    def put_on_content_link(self, content_link: HALLink, filepath: str) -> HALLink:
        if os.path.exists(filepath):
            filename = filepath.split("/")[-1]
            files = {"file": (filename, open(filepath, "rb"), mimetypes.guess_type(filepath)[0])}
        else:
            raise BadRequest(f"Provided content not found {filepath}")
        response = self.put(content_link.uri, files=files)  # type: ignore
        self._validate_non_json_response(response=response)
        return content_link

    def fetch_content_attribute(self, content_link: HALLink) -> tuple[str, bytes]:
        response = self.get(content_link.uri, headers={"Accept": "*/*"})
        self._validate_non_json_response(response=response)
        content_disposition = response.headers.get("content-disposition")

        if content_disposition and content_disposition != "attachment":
            filename = decode_header(content_disposition)[1][0].decode("utf-8")
        else:
            # If content-disposition header is not present, try to extract filename from URL
            filename = os.path.basename(content_link.name)  # type: ignore
        return (filename, response.content)

    def fetch_all_content_attributes_from_entity_link(self, entity_link: HALLink) -> List[tuple[str, bytes]]:
        return self.get_entity_instance(entity_link=entity_link).fetch_all_content_attributes()

    def delete_link(self, link: HALLink) -> requests.Response:
        response = self.delete(link.uri)
        self._validate_non_json_response(response)
        return response

    # SEARCH
    def _search_collection_with_params(self, plural_entity_name: str, params: List[SearchParam] | dict) -> EntityCollection:
        return self.get_entity_collection(plural_entity_name=plural_entity_name).search_entities(params=params)

    def get_search_entity_collection(self, entity_search: EntitySearch) -> EntityCollection:
        singular_or_plural_entity_name = entity_search.entity_name
        try:
            plural_entity_name = self.get_profile().singular_to_plural_entity_name(singular_entity_name=singular_or_plural_entity_name)
            entity_profile = self.get_entity_profile_singular(singular_entity_name=singular_or_plural_entity_name)
        except NotFound:
            # Pluralized instead of singular name might have been provided for the entity_search object
            # If this fails the entity does not exist
            plural_entity_name = singular_or_plural_entity_name
            entity_profile = self.get_entity_profile(pluralized_entity_name=singular_or_plural_entity_name)

        search_params = entity_search.transform_to_params(entity_profile=entity_profile)
        return self._search_collection_with_params(plural_entity_name=plural_entity_name, params=search_params)

    def execute_entity_search(self, entity_search: EntitySearch, nb_results: Optional[int] = None, ignore_warnings : bool = False) -> List["EntityObject"]:
        collection = self.get_search_entity_collection(entity_search=entity_search)
        if nb_results:
            entities = list(islice(collection.get_entities_paged_generator(), nb_results))
            nb_found_entities = len(entities)
            if nb_results and not ignore_warnings and len(entities) < nb_results:
                logging.warning(f"Less (entity: {entity_search.entity_name}) results where found than requested. requested number : {nb_results}, actual : {nb_found_entities}")      
            return entities
        else:
            if not ignore_warnings:
                logging.warning(f"Executing entity search on {entity_search.entity_name} with no limit (nb_results parameter). This can take a very long time... To avoid loading all entities in memory, use the entity_generator on the collection search endpoint.")
            return [entity for entity in collection.get_entities_paged_generator()]

    def _validate_form_payload(self, template: HALFormsTemplate, payload: dict, check_requirements: bool = True, fail_on_not_found : bool = True) -> None:
        # Type checking
        for key, value in payload.items():
            hal_property = None
            for property in template.properties:
                if property.name == key:
                    hal_property = property

            if not hal_property:
                logging.warning(f"{key} does not exist in {template}")
                if fail_on_not_found:
                    raise MissingHALTemplate(f"{key} does not exist in {template}")
            else:
                # Determine if property is multi-valued
                multi_valued = False

                # Property without options is considered non multivalued.
                if hal_property.options:
                    options = hal_property.options
                    # A hal_property is multi-valued if:
                    # - maxItems is greater than 1, or
                    # - maxItems is not specified (unlimited) and minItems is at least 0
                    if options.maxItems is None:  # maxItems not specified means unlimited
                        multi_valued = True
                    elif options.maxItems > 1:
                        multi_valued = True

                # Validate based on whether it's multi-valued or not
                if multi_valued:
                    if not isinstance(value, list):
                        raise IncorrectAttributeType(f"HALProperty {key} has an incorrect type {type(value)}. Should be of type {list}")

                    # Validate each item in the list
                    for item in value:
                        if hal_property.type and not hal_form_type_check[hal_property.type.value](item):
                            raise IncorrectAttributeType(
                                f"hal_property {key} has an incorrect type {type(value)} in its list value. {item} is not of type {hal_form_types[hal_property.type.value]}"
                            )
                else:
                    # Single value validation
                    if hal_property.type and not hal_form_type_check[hal_property.type.value](value):
                        raise IncorrectAttributeType(f"Attribute {key} has an incorrect type {type(value)}. Should be of type {hal_form_types[hal_property.type.value]}")

        if check_requirements:
            # Check for required properties is not needed when patching an entity
            for hal_property in template.properties:
                if hal_property.required:
                    if hal_property.name not in payload.keys():
                        raise MissingRequiredAttribute(f"Required attribute {property.name} not present in payload.")

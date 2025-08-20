

from enum import Enum
from typing import List, cast
from contentgrid_hal_client.exceptions import MissingHALTemplate, NotFound
from contentgrid_hal_client import CurieRegistry, HALFormsClient, HALLink, HALResponse, InteractiveHALResponse

def get_blueprint(blueprint_url: str, hal_client: HALFormsClient) -> "Blueprint":
    return hal_client.follow_link(HALLink(uri=blueprint_url), infer_type=Blueprint)

def get_organizations(hal_client : HALFormsClient) -> List["Organization"]:
    return hal_client.follow_link(HALLink(uri="/orgs"), infer_type=InteractiveHALResponse).get_embedded_objects_by_key("organizations", infer_type=Organization)

class Organization(InteractiveHALResponse):
    def __init__(self, data: dict, client: HALFormsClient, curie_registry: CurieRegistry = None) -> None:
        super().__init__(data, client, curie_registry)
        self.name: str = data["name"]
        self.display_name : str = data["display_name"]

    def get_projects(self) -> List["Project"]:
        return self.client.follow_link(self.get_link("projects"), infer_type=InteractiveHALResponse).get_embedded_objects_by_key("projects", infer_type=Project)

    def get_project_by_name(self, project_name : str) -> "Project":
        projects = self.get_projects()
        for project in projects:
            if project.name == project_name:
                return project
        raise NotFound(f"Project {project_name} not found in organization {self.name}")

class Project(InteractiveHALResponse):
    def __init__(self, data: dict, client: HALFormsClient, curie_registry: CurieRegistry = None) -> None:
        super().__init__(data, client, curie_registry)
        self.slug = data["slug"]
        self.name = data["name"]
    
    def get_organization(self) -> Organization:
        return self.client.follow_link(self.get_link("organization"), infer_type=Organization)
    
    def get_bookmark(self) -> str:
        return cast(HALLink, self.get_link("bookmark")).uri
    
    def get_blueprints(self) -> List["Blueprint"]:
        return self.client.follow_link(self.get_link("blueprints"), infer_type=InteractiveHALResponse).get_embedded_objects_by_key("blueprints", infer_type=Blueprint)
    
    def get_blueprint_by_name(self, blueprint_name : str) -> "Blueprint":
        blueprints = self.get_blueprints()
        for blueprint in blueprints:
            if blueprint.name == blueprint_name:
                return blueprint
        raise NotFound(f"blueprint {blueprint_name} not found in project {self.name}")

class Blueprint(InteractiveHALResponse):
    def __init__(self, data: dict, client: HALFormsClient, curie_registry: CurieRegistry = None) -> None:
        super().__init__(data, client, curie_registry)
        self.name = data["name"]
        self.created = data["created"]
        self.updated = data["updated"]

    def get_project(self) -> Project:
        return self.client.follow_link(self.get_link("project"))

    def get_webhooks(self) -> List[HALResponse]:
        return self.client.follow_link(self.get_link("webhooks"), infer_type=HALResponse).get_embedded_objects_by_key(key="webhooks")
    
    def get_entities_link(self) -> HALLink:
        return cast(HALLink, self.get_link("entities"))
    
    # Entity actions
    def get_entity_definitions(self) -> List["EntityDefinition"]:
        return self.client.follow_link(self.get_entities_link(), infer_type=InteractiveHALResponse).get_embedded_objects_by_key("entities", infer_type=EntityDefinition)
    
    def get_entity_definition_by_name(self, entity_name:str) -> "EntityDefinition":
        for entity_definition in self.get_entity_definitions():
            if entity_definition.name == entity_name:
                return entity_definition
        raise NotFound(f"Entity definition {entity_name} not found.")
    
    def create_entity(self, entity_name : str, entity_description : str=None ) -> "EntityDefinition":
        payload = {
            "name" : entity_name
        }

        if entity_description:
            payload["description"] = entity_description
        
        response = self.client.post(self.get_entities_link().uri, json=payload, headers={"Content-Type" : "application/json"})
        data = self.client._validate_json_response(response)
        return EntityDefinition(data=data, client=self.client, curie_registry=self.curie_registry)
    
    # Automation actions
    def get_automations_link(self) -> HALLink:
        return HALLink(uri=self.get_self_link().uri + "/automations")

    def get_automations(self) -> List["Automation"]:
        return self.client.follow_link(self.get_automations_link(), infer_type=InteractiveHALResponse).get_embedded_objects_by_key("automations", infer_type=Automation)
    
    def create_automation(self, automation_name: str, system_name: str, automation_data: dict) -> "Automation":
        payload = {
            "name" : automation_name,
            "system" : system_name,
            "data" : automation_data
        }
        response = self.client.post(self.get_automations_link().uri, json=payload, headers={"Content-Type" : "application/json"})
        data = self.client._validate_json_response(response)
        return Automation(data=data, client=self.client, curie_registry=self.curie_registry)

#AUTOMATIONS
class Automation(InteractiveHALResponse):
    def __init__(self, data: dict, client: HALFormsClient, curie_registry: CurieRegistry = None) -> None:
        super().__init__(data, client, curie_registry)
        self.id : str = data["id"]
        self.system : str = data["system"]
        self.name : str = data["name"]
        self.automation_data : dict = data["data"]

    def get_annotations(self) -> List["AutomationAnnotation"]:
        return self.client.follow_link(self.get_link("annotations"), infer_type=InteractiveHALResponse).get_embedded_objects_by_key("annotations", infer_type=AutomationAnnotation)

    def get_annotations_link(self) -> HALLink:
        annotations_link = self.get_link("annotations")
        if annotations_link:
            return annotations_link
        else:
            raise Exception("Annotations Link not found on Automation")
    
    def _create_annotation(self, json_payload : dict) -> "AutomationAnnotation":
        response = self.client.post(self.get_annotations_link().uri, json=json_payload, headers={"Content-Type" : "application/json"})
        data = self.client._validate_json_response(response)
        return AutomationAnnotation(data=data, client=self.client, curie_registry=self.curie_registry)
    
    def create_annotation_on_entity(self, entity_name : str, data: dict) -> "AutomationAnnotation":
        payload : dict = {"subject" : { "type" : "entity", "entity" : entity_name}, "data" : data}
        return self._create_annotation(json_payload=payload)
    
    def create_annotation_on_attribute(self, entity_name : str, attribute_name : str, data : dict) -> "AutomationAnnotation":
        payload : dict = {"subject" : { "type" : "attribute", "entity" : entity_name, "attribute" : attribute_name}, "data" : data}
        return self._create_annotation(json_payload=payload)

class AutomationAnnotationSubjectType(Enum):
    ENTITY = 0
    ATTRIBUTE = 1
    RELATION = 2
    WEBHOOK = 3

class AutomationAnnotationSubject:
    def __init__(self, subject: dict) -> None:
        self.type: AutomationAnnotationSubjectType = AutomationAnnotationSubjectType[subject["type"].upper()]
        if self.type == AutomationAnnotationSubjectType.ENTITY:
            self.entity = subject["entity"]
        elif self.type == AutomationAnnotationSubjectType.ATTRIBUTE:
            self.entity = subject["entity"]
            self.attribute = subject["attribute"]
        #TODO relation and webhook

class AutomationAnnotation(InteractiveHALResponse):
    def __init__(self, data: dict, client: HALFormsClient, curie_registry: CurieRegistry = None) -> None:
        super().__init__(data, client, curie_registry)
        self.id: str = data["id"]
        self.subject: AutomationAnnotationSubject = AutomationAnnotationSubject(
            data["subject"]
        )
        self.annotation_data: dict = data["data"]

#ENTITIES
class AttributeType(Enum):
    STRING = 0
    LONG = 1
    DOUBLE = 2
    BOOLEAN = 3
    DATETIME = 4
    CONTENT = 5
    AUDIT_METADATA = 6

class ConstraintType(Enum):
    ALLOWED_VALUES = "allowed-values"
    REQUIRED = "required"
    UNIQUE = "unique"

class SearchType(Enum):
    EXACT = "exact"
    PREFIX = "prefix"

class EntityDefinition(InteractiveHALResponse):
    def __init__(self, data: dict, client: HALFormsClient, curie_registry: CurieRegistry = None) -> None:
        super().__init__(data, client, curie_registry)
        self.name : str = data["name"]
        self.description : str = data["description"]
        self.attribute_definitions : List[AttributeDefinition] = self.get_embedded_objects_by_key("attributes", infer_type=AttributeDefinition)
        self.relation_definitions : List[RelationDefinition] = self.get_embedded_objects_by_key("relations", infer_type=RelationDefinition)

    def get_blueprint(self) -> Blueprint:
        return self.client.follow_link(self.get_link("blueprint"), infer_type=Blueprint)
    
    def get_attribute_definition_by_name(self, attribute_name: str) -> "AttributeDefinition":
        for attribute_definition in self.attribute_definitions:
            if attribute_definition.name == attribute_name:
                return attribute_definition
        raise NotFound(f"Attribute definition {attribute_name} not found.")
    
    def create_attribute(self, attribute_name: str, type:AttributeType, *, attribute_description: str=None, natural_id:bool=False):
        payload = {
            "name" : attribute_name,
            "natural_id" : natural_id,
            "type" : type.name,
        }

        if attribute_description:
            payload["description"] = attribute_description

        add_attribute_template = self.get_template("addAttribute")
        response = self.client.get_method_from_string(add_attribute_template.method.value)(add_attribute_template.target, json=payload, headers={"Content-Type" : "application/json"})
        data = self.client._validate_json_response(response)
        self.refetch()
        return AttributeDefinition(data=data, client=self.client, curie_registry=self.curie_registry)

    def patch(self, new_entity_name: str=None, new_entity_description: str=None):
        payload = {}
        if new_entity_name is not None:
            payload["name"] = new_entity_name
        
        if new_entity_description is not None:
            payload["description"] = new_entity_description
        
        self.patch_data(payload)
    
    def get_relation_definition_by_name(self, relation_name: str) -> "RelationDefinition":
        for relation_definition in self.relation_definitions:
            if relation_definition.name == relation_name:
                return relation_definition
        raise NotFound(f"Relation definition {relation_name} not found.")
    
    def create_relation(self, relation_name: str, target:str, many_source_per_target:bool, many_target_per_source:bool, relation_description: str= None, *, required: bool=False):
        payload = {
            "name" : relation_name,
            "required" : required,
            "target" : target,
            "many_source_per_target" : many_source_per_target,
            "many_target_per_source" : many_target_per_source
        }
        if relation_description:
            payload["description"] = relation_description
        
        add_relation_template = self.get_template("addRelation")
        response = self.client.get_method_from_string(add_relation_template.method.value)(add_relation_template.target, json=payload, headers={"Content-Type" : "application/json"})
        data = self.client._validate_json_response(response)
        self.refetch()
        return RelationDefinition(data=data, client=self.client, curie_registry=self.curie_registry)

    def __repr__(self) -> str:
        return self.__str__()
    
    def __str__(self) -> str:
        entity_str = f"[Entity {self.name}] \n"
        entity_str += "Attributes: \n"
        for attribute_definition in self.attribute_definitions:
            entity_str += "\t" + str(attribute_definition) + "\n"
        entity_str += "Relations: \n"
        for relation_definition in self.relation_definitions:
            entity_str += "\t" + str(relation_definition) + "\n"
        return entity_str

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "attributes": [attribute_definition.to_dict() for attribute_definition in self.attribute_definitions],
            "relations": [relation_definition.to_dict() for relation_definition in self.relation_definitions]
        }

class AttributeDefinition(InteractiveHALResponse):
    def __init__(self, data: dict, client: HALFormsClient, curie_registry: CurieRegistry = None) -> None:
        super().__init__(data, client, curie_registry)
        self.name : str = data["name"]
        self.description : str = data["description"]
        self.type : AttributeType = AttributeType[data["type"]]
        self.natural_id : bool = data["natural_id"]

    def get_entity_definition(self) -> EntityDefinition:
        return self.client.follow_link(self.get_link("entity"), infer_type=EntityDefinition)

    def get_blueprint(self) -> Blueprint:
        return self.client.follow_link(self.get_link("blueprint"), infer_type=Blueprint)

    def patch(self, attribute_name :str=None, attribute_description :str=None, attribute_type :AttributeType=None):
        payload = {}
        if attribute_name is not None:
            payload["name"] = attribute_name
        if attribute_description is not None:
            payload["description"] = attribute_description
        if attribute_type is not None:
            payload["type"] = attribute_type.name
        
        self.patch_data(data=payload)
    
    def add_allowed_values_constraint(self, allowed_values: List[str]) -> "AttributeConstraint":
        if "set-allowed-values" in self.templates.keys():
            set_allowed_values_template = self.get_template("set-allowed-values")
            values_property = next(filter(lambda property : property.required, set_allowed_values_template.properties))
            response = self.client.get_method_from_string(set_allowed_values_template.method.value)(set_allowed_values_template.target, json={values_property.name : allowed_values}, headers={"Content-Type" : "application/json"})
            data = self.client._validate_json_response(response)
            self.refetch()
            return AttributeConstraint(data=data, client=self.client, curie_registry=self.curie_registry)
        else:
            raise MissingHALTemplate("Missing set-allowed-values template. This property does not allow an allowed values constraint.")
    
    def enable_required_constraint(self) -> None:
        template_name = "enable-required"

        if template_name in self.templates.keys():
            template = self.get_template(template_name)
            response = self.client.get_method_from_string(template.method.value)(template.target)
            self.client._validate_non_json_response(response)
            self.refetch()
        else:
            raise MissingHALTemplate(f"Missing {template_name} template. This property does not allow being required.")

    def enable_unique_constraint(self) -> None:
        template_name = "enable-unique"

        if template_name in self.templates.keys():
            template = self.get_template(template_name)
            response = self.client.get_method_from_string(template.method.value)(template.target)
            self.client._validate_non_json_response(response)
            self.refetch()
        else:
            raise MissingHALTemplate(f"Missing {template_name} template. This property does not allow being unique.")

    def get_constraints(self) -> List["AttributeConstraint"]:
        key = "constraints"
        if self.embedded:
            return [
                constraint_map[ConstraintType(v["type"])](data=v, client=self.client, curie_registry=self.curie_registry)
                for v in self.embedded[self.curie_registry.compact_curie(key)]
                if AttributeConstraint.valid(v)
            ]
        else:
            return []
    
    def get_constraints_of_type(self, constraint_type: ConstraintType) -> List["AttributeConstraint"]:
        constraints = self.get_constraints()
        return list(filter(lambda constraint : constraint.type == constraint_type, constraints))

    def enable_exact_search(self) -> None:
        template_name = "enable-exact-search"

        if template_name in self.templates.keys():
            template = self.get_template(template_name)
            response = self.client.get_method_from_string(template.method.value)(template.target)
            self.client._validate_non_json_response(response)
            self.refetch()
        else:
            raise MissingHALTemplate(f"Missing {template_name} template. This property does not allow enabling exact search")

    def enable_prefix_search(self) -> None:
        template_name = "enable-prefix-search"

        if template_name in self.templates.keys():
            template = self.get_template(template_name)
            response = self.client.get_method_from_string(template.method.value)(template.target)
            self.client._validate_non_json_response(response)
            self.refetch()
        else:
            raise MissingHALTemplate(f"Missing {template_name} template. This property does not allow enabling prefix search")

    def get_search_options(self) -> List["AttributeSearchOption"]:
        key = "search-options"
        if self.embedded:
            return [
                search_option_map[SearchType(data["type"])](data=data, client=self.client, curie_registry=self.curie_registry)
                for data in self.embedded[self.curie_registry.compact_curie(key)]
                if AttributeSearchOption.valid(data)
            ]
        else:
            return []

    def get_search_options_of_type(self, search_type: SearchType) -> List["AttributeSearchOption"]:
        search_options = self.get_search_options()
        return list(filter(lambda option : option.type == search_type, search_options))

    def __repr__(self) -> str:
        return self.__str__()
    
    def __str__(self) -> str:
        search_options = self.get_search_options()
        exact = any(isinstance(search_option, ExactAttributeSearchOption) for search_option in search_options)
        prefix = any(isinstance(search_option, PrefixAttributeSearchOption) for search_option in search_options)
        constraints = self.get_constraints()
        required = any(isinstance(constraint, RequiredAttributeConstraint) for constraint in constraints)
        unique = any(isinstance(constraint, UniqueAttributeConstraint) for constraint in constraints)

        return f"[Attribute {self.name}] type={self.type.name} | required={required} | unique={unique} | exact_search={exact} | prefix_search={prefix} | natural_id={self.natural_id}"

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "type": self.type.name,
            "constraints": [constraint.to_dict() for constraint in self.get_constraints()],
            "search-options": [search_option.to_dict() for search_option in self.get_search_options()],
            "natural_id": self.natural_id
        }

class AttributeConstraint(InteractiveHALResponse):
    def __init__(self, data: dict, client: HALFormsClient, curie_registry: CurieRegistry = None) -> None:
        super().__init__(data, client, curie_registry)
        self.type : ConstraintType = ConstraintType(data["type"])

    def get_attribute_definition(self) -> AttributeDefinition:
        return self.client.follow_link(self.get_link("attribute"), infer_type=AttributeDefinition)

    def get_entity_definition(self) -> EntityDefinition:
        return self.client.follow_link(self.get_link("entity"), infer_type=EntityDefinition)
    
    def get_blueprint(self) -> Blueprint:
        return self.client.follow_link(self.get_link("blueprint"), infer_type=Blueprint)

    def __str__(self) -> str:
        return f"[{type(self).__name__} {self.type.name}]"

    def __repr__(self) -> str:
        return self.__str__()

    def to_dict(self) -> dict:
        return { "type": self.type.name }

    @staticmethod
    def valid(data: dict) -> bool:
        if "type" not in data:
            return False
        try:
            return ConstraintType(data["type"]) in constraint_map
        except ValueError:
            return False


class AllowedValuesAttributeConstraint(AttributeConstraint):
    def __init__(self, data: dict, client: HALFormsClient, curie_registry: CurieRegistry = None) -> None:
        super().__init__(data, client, curie_registry)
        self.values : List[str] = data["values"]

    def update_values(self, new_values: List[str]) -> None:
        set_allowed_values_template = self.get_template("default")
        values_property_name = next(filter(lambda prop : prop.required, set_allowed_values_template.properties)).name
        response = self.client.get_method_from_string(set_allowed_values_template.method)(self.get_self_link().uri, json={values_property_name : new_values}, headers={"Content-Type" : "application/json"})
        self.client._validate_json_response(response)
        self.refetch()
    
    def __str__(self) -> str:
        if len(self.values) < 50:
            return f"[AllowedValuesAttributeConstraint {self.type.name}] values={self.values}"
        else:
            return f"[AllowedValuesAttributeConstraint {self.type.name}] values={self.values[:50]}... ({len(self.values)} total)"

    def __repr__(self) -> str:
        return self.__str__()

    def to_dict(self) -> dict:
        return {
            "type": self.type.name,
            "values": self.values
        }

class RequiredAttributeConstraint(AttributeConstraint):
    def __init__(self, data: dict, client: HALFormsClient, curie_registry: CurieRegistry = None) -> None:
        super().__init__(data, client, curie_registry)

class UniqueAttributeConstraint(AttributeConstraint):
    def __init__(self, data: dict, client: HALFormsClient, curie_registry: CurieRegistry = None) -> None:
        super().__init__(data, client, curie_registry)

constraint_map = {
    ConstraintType.ALLOWED_VALUES : AllowedValuesAttributeConstraint,
    ConstraintType.REQUIRED : RequiredAttributeConstraint,
    ConstraintType.UNIQUE : UniqueAttributeConstraint
}


class AttributeSearchOption(InteractiveHALResponse):
    def __init__(self, data: dict, client: HALFormsClient, curie_registry: CurieRegistry = None) -> None:
        super().__init__(data, client, curie_registry)
        self.type : SearchType = SearchType(data["type"])

    def get_attribute_definition(self) -> AttributeDefinition:
        return self.client.follow_link(self.get_link("attribute"), infer_type=AttributeDefinition)

    def get_entity_definition(self) -> EntityDefinition:
        return self.client.follow_link(self.get_link("entity"), infer_type=EntityDefinition)

    def get_blueprint(self) -> Blueprint:
        return self.client.follow_link(self.get_link("blueprint"), infer_type=Blueprint)

    def __str__(self) -> str:
        return f"[{type(self).__name__} {self.type.name}]"

    def __repr__(self) -> str:
        return self.__str__()

    def to_dict(self) -> dict:
        return { "type": self.type.name }

    @staticmethod
    def valid(data: dict) -> bool:
        if "type" not in data:
            return False
        try:
            return SearchType(data["type"]) in search_option_map
        except ValueError:
            return False

class ExactAttributeSearchOption(AttributeSearchOption):
    def __init__(self, data: dict, client: HALFormsClient, curie_registry: CurieRegistry = None) -> None:
        super().__init__(data, client, curie_registry)

class PrefixAttributeSearchOption(AttributeSearchOption):
    def __init__(self, data: dict, client: HALFormsClient, curie_registry: CurieRegistry = None) -> None:
        super().__init__(data, client, curie_registry)

search_option_map = {
    SearchType.EXACT : ExactAttributeSearchOption,
    SearchType.PREFIX : PrefixAttributeSearchOption
}


class RelationDefinition(InteractiveHALResponse):
    def __init__(self, data: dict, client: HALFormsClient, curie_registry: CurieRegistry = None) -> None:
        super().__init__(data, client, curie_registry)
        self.name : str = data["name"]
        self.description : str = data["description"]
        self.source : str = data["source"]
        self.target : str = data["target"]
        self.many_source_per_target : bool = data["many_source_per_target"]
        self.many_target_per_source : bool = data["many_target_per_source"]
        self.required : bool = data["required"]

    def get_blueprint(self) -> Blueprint:
        return self.client.follow_link(self.get_link("blueprint"), infer_type=Blueprint)

    def get_source_entity_definition(self) -> EntityDefinition:
        return self.client.follow_link(self.get_link("source"), infer_type=EntityDefinition)
    
    def get_target_entity_definition(self) -> EntityDefinition:
        return self.client.follow_link(self.get_link("target"), infer_type=EntityDefinition)
    
    def patch(self, new_relation_name: str=None, new_relation_description: str=None):
        payload = {}
        if new_relation_name is not None:
            payload["name"] = new_relation_name
        
        if new_relation_description is not None:
            payload["description"] = new_relation_description
        
        self.patch_data(payload)

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f"[Relation {self.name}] required={self.required} | source={self.source} | target={self.target} | many_source_per_target={self.many_source_per_target} | many_target_per_source={self.many_target_per_source}"

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "source": self.source,
            "target": self.target,
            "many_source_per_target": self.many_source_per_target,
            "many_target_per_source": self.many_target_per_source,
            "required": self.required
        }
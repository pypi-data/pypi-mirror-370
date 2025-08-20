import pytest
import threading
from contentgrid_management_client import AttributeType, get_organizations, EntityDefinition, AttributeDefinition, ConstraintType, SearchType,\
    ExactAttributeSearchOption, PrefixAttributeSearchOption, AllowedValuesAttributeConstraint, RequiredAttributeConstraint, UniqueAttributeConstraint
from contentgrid_hal_client import HALFormsClient
import logging
import os

TEST_CONSOLE = os.environ.get("TEST_CONSOLE", default="f") in ["t", "true", "1"]

logging.info(f"TEST_CONSOLE = {TEST_CONSOLE}")

if TEST_CONSOLE:
    client = HALFormsClient(
        client_endpoint="http://172.17.0.1:8080",
        session_cookie="208c9ae8-8b9e-4933-8fec-8f526ea474cd"
    )

    org = get_organizations(hal_client=client)[0]
    proj = org.get_projects()[0]
    blueprint = proj.get_blueprints()[0]

    def test_console():
        org.get_project_by_name(proj.name)
        proj.get_blueprint_by_name(blueprint_name=blueprint.name)

        entity_definitions = blueprint.get_entity_definitions()

        test_entity_definition = entity_definitions[0]
        test_attribute_definition = test_entity_definition.attribute_definitions[0]
        # test_relation = test_entity_definition.relation_definitions[0]

        test_entity_definition.get_blueprint()
        test_attribute_definition.get_blueprint()
        # test_relation.get_blueprint()
        # test_relation.get_source_entity_definition()
        # test_relation.get_target_entity_definition()

        automation = blueprint.create_automation("test", "ml", {"test": "barz"})

        automations = blueprint.get_automations()

        automation = automations[0]
        logging.info(blueprint.get_entity_definition_by_name(entity_definitions[0].name).attribute_definitions)

        logging.info(blueprint.get_automations())

        # logging.info(automation._create_automation_annotation({"test": "yoo"}))
        annotation = automation.create_annotation_on_entity(entity_definitions[0].name, {"test": "yoyo"})
        logging.info(annotation)

        logging.info(annotation.subject.type)

        logging.info(automation.create_annotation_on_attribute(entity_name=entity_definitions[0].name, attribute_name=entity_definitions[0].attribute_definitions[0].name, data= {"test": "yoyo"}).subject.type)

        automation.put_data(data={"name" :"test", "data" : {"foo" : "bar"}})

    @pytest.fixture
    def entity() -> EntityDefinition:
        entity = blueprint.create_entity("test-entity", entity_description="description")
        yield entity
        entity.delete()

    @pytest.fixture
    def attribute(entity: EntityDefinition) -> AttributeDefinition:
        attribute = entity.create_attribute("test_attribute", AttributeType.STRING, attribute_description="description")
        yield attribute
        attribute.delete()

    def test_create_entity():
        entity = blueprint.create_entity(entity_name="testcreateentitiy", entity_description="description")
        assert entity.description == "description"
        entity.patch(new_entity_description="new description")
        assert entity.description == "new description"
        entity.delete()


    def test_create_relation(entity):
        entity.create_relation("testrelation", "test-entity", many_target_per_source=False, many_source_per_target=False, relation_description="description")
        relation = entity.get_relation_definition_by_name("testrelation")
        assert relation.description == "description"
        relation.patch(new_relation_description="new description")
        assert relation.description == "new description"

    def test_create_attribute(entity):
        entity.create_attribute("testattribute", AttributeType.STRING, attribute_description="test attribute description")
        attribute = entity.get_attribute_definition_by_name("testattribute")
        assert attribute.description == "test attribute description"
        attribute.patch(attribute_description="new description")
        assert attribute.description == "new description"

    def test_concurrent():
        threads = []
        for i in range(100):
            thread = threading.Thread(target=blueprint.get_project)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    def test_get_constraints(attribute):
        assert len(attribute.get_constraints()) == 0

    def test_allowed_values(attribute):
        attribute.add_allowed_values_constraint(["a","b","c"])
        constraints = attribute.get_constraints()
        assert len(constraints) == 1
        constraint : AllowedValuesAttributeConstraint = attribute.get_constraints_of_type(ConstraintType.ALLOWED_VALUES)[0]
        assert constraint.values == ["a", "b", "c"]
        assert constraint.type == ConstraintType.ALLOWED_VALUES
        assert isinstance(constraint, AllowedValuesAttributeConstraint)

        constraint.update_values(["a", "b"])
        assert constraint.values == ["a", "b"]

    def test_required(attribute):
        attribute.enable_required_constraint()
        constraints = attribute.get_constraints()
        assert len(constraints) == 1
        constraint : RequiredAttributeConstraint = attribute.get_constraints_of_type(ConstraintType.REQUIRED)[0]
        assert constraint.type == ConstraintType.REQUIRED
        assert isinstance(constraint, RequiredAttributeConstraint)

    def test_unique(attribute):
        attribute.enable_unique_constraint()
        constraints = attribute.get_constraints()
        assert len(constraints) == 1
        constraint : UniqueAttributeConstraint = attribute.get_constraints_of_type(ConstraintType.UNIQUE)[0]
        assert constraint.type == ConstraintType.UNIQUE
        assert isinstance(constraint, UniqueAttributeConstraint)

    def test_exact_search(attribute):
        # Enable exact search option
        attribute.enable_exact_search()
        search_options = attribute.get_search_options()
        assert len(search_options) == 1
        search_option : ExactAttributeSearchOption = attribute.get_search_options_of_type(SearchType.EXACT)[0]
        assert search_option.type == SearchType.EXACT
        assert isinstance(search_option, ExactAttributeSearchOption)

        # Disable exact search option
        search_option.delete()
        attribute.refetch()
        search_options = attribute.get_search_options()
        assert len(search_options) == 0

    def test_prefix_search(attribute):
        # Enable prefix search option
        attribute.enable_prefix_search()
        search_options = attribute.get_search_options()
        assert len(search_options) == 1
        search_option : PrefixAttributeSearchOption = attribute.get_search_options_of_type(SearchType.PREFIX)[0]
        assert search_option.type == SearchType.PREFIX
        assert isinstance(search_option, PrefixAttributeSearchOption)

        # Disable prefix search option
        search_option.delete()
        attribute.refetch()
        search_options = attribute.get_search_options()
        assert len(search_options) == 0

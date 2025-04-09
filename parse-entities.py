import xml.etree.ElementTree as ET
import os
import sys
import argparse

# Default publisher prefixes
DEFAULT_PREFIXES = ["mcdev", "new"]  ## add your custom publisher prefixes here

def strip_prefix(name, prefixes):
    """Remove the prefix and the following underscore from the name."""
    for prefix in prefixes:
        if name.startswith(prefix + "_"):
            return name[len(prefix) + 1:]
    return name

def parse_entities(xml_file, prefixes):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    ns = {'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}

    entities = []

    for entity in root.findall(".//Entity"):
        entity_name = entity.find("./Name").text
        stripped_entity_name = strip_prefix(entity_name, prefixes)
        attributes = []
        relationships = []
        primary_keys = []
        foreign_keys = []
        ownership = entity.find("./Ownership").text if entity.find("./Ownership") is not None else "None"

        # Extract attributes with custom publisher prefixes
        for attribute in entity.findall(".//attribute"):
            physical_name = attribute.get("PhysicalName")
            if physical_name:
                stripped_physical_name = strip_prefix(physical_name, prefixes)
                attribute_type = attribute.get("Type", "Unknown")
                description = attribute.get("Description", "No description")
                attributes.append({"name": stripped_physical_name, "type": attribute_type, "description": description})

        # Extract relationships involving the current entity
        for relationship in root.findall(".//EntityRelationship"):
            referencing_entity = relationship.find("ReferencingEntityName")
            referenced_entity = relationship.find("ReferencedEntityName")
            relationship_type = relationship.find("EntityRelationshipType")
            
            if (
                referencing_entity is not None and 
                referenced_entity is not None and 
                relationship_type is not None and
                (referencing_entity.text == entity_name or referenced_entity.text == entity_name) and
                referenced_entity.text not in ["SystemUser", "Owner", "BusinessUnit", "Team", "TransactionCurrency"]
            ):
                relationships.append({
                    "type": relationship_type.text,
                    "referencing_entity": strip_prefix(referencing_entity.text, prefixes),
                    "referenced_entity": strip_prefix(referenced_entity.text, prefixes)
                })

        # Extract primary keys
        for pk in entity.findall(".//PrimaryKey"):
            primary_keys.append(strip_prefix(pk.get("Name"), prefixes))

        # Extract foreign keys
        for fk in entity.findall(".//ForeignKey"):
            foreign_keys.append({
                "name": strip_prefix(fk.get("Name"), prefixes),
                "referenced_entity": strip_prefix(fk.get("ReferencedEntity"), prefixes)
            })

        # Add entity details to the list
        entities.append({
            "entity_name": stripped_entity_name,
            "attributes": attributes,
            "relationships": relationships,
            "primary_keys": primary_keys,
            "foreign_keys": foreign_keys,
            "ownership": ownership
        })

    return entities

def parse_workflows(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    workflows = []

    for workflow in root.findall(".//Workflow"):
        workflow_name = workflow.get("Name")
        primary_entity = workflow.find("PrimaryEntity").text
        workflows.append({"name": workflow_name, "primary_entity": primary_entity})

    return workflows

def main():
    parser = argparse.ArgumentParser(description="Parse Dynamics 365 solution entities and workflows.")
    parser.add_argument("solution_folder", help="The folder containing the customizations.xml file.")
    parser.add_argument("--prefixes", nargs="+", default=DEFAULT_PREFIXES, help="Custom publisher prefixes to strip (default: %(default)s).")
    args = parser.parse_args()

    solution_folder = args.solution_folder
    prefixes = args.prefixes
    base_path = os.getcwd()
    xml_file = os.path.join(base_path, solution_folder, "customizations.xml")

    if not os.path.exists(os.path.join(base_path, solution_folder)):
        print(f"Error: The folder '{os.path.join(base_path, solution_folder)}' does not exist.")
        sys.exit(1)

    if not os.path.exists(xml_file):
        print(f"Error: The file '{xml_file}' does not exist.")
        sys.exit(1)

    entities = parse_entities(xml_file, prefixes)
    workflows = parse_workflows(xml_file)

    # Print the parsed entities
    for entity in entities:
        print(f"Entity: {entity['entity_name']}")
        print(f"  Attributes:")
        for attribute in entity['attributes']:
            print(f"    - {attribute['name']} ({attribute['type']}): {attribute['description']}")
        print(f"  Relationships:")
        for relationship in entity['relationships']:
            print(f"    - {relationship['type']} between {relationship['referencing_entity']} and {relationship['referenced_entity']}")
        print(f"  Primary Keys: {', '.join(entity['primary_keys'])}")
        print(f"  Foreign Keys:")
        for fk in entity['foreign_keys']:
            print(f"    - {fk['name']} references {fk['referenced_entity']}")
        print(f"  Ownership: {entity['ownership']}")
        print()

    # Print the parsed workflows
    print("Workflows:")
    for workflow in workflows:
        print(f"  - {workflow['name']} (Primary Entity: {workflow['primary_entity']})")

if __name__ == "__main__":
    main()
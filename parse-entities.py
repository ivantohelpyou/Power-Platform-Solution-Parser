import xml.etree.ElementTree as ET
import os
import sys

def parse_entities(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    ns = {'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}

    entities = []

    for entity in root.findall(".//Entity"):
        entity_name = entity.find("./Name").text
        stripped_entity_name = entity_name.replace("mcdev_", "").replace("new_", "")
        attributes = []
        relationships = []
        primary_keys = []
        foreign_keys = []
        ownership = entity.find("./Ownership").text if entity.find("./Ownership") is not None else "None"

        # Extract attributes with custom publisher prefixes
        for attribute in entity.findall(".//attribute"):
            physical_name = attribute.get("PhysicalName")
            if physical_name and (physical_name.startswith("mcdev_") or physical_name.startswith("new_")):
                attribute_type = attribute.get("Type", "Unknown")
                description = attribute.get("Description", "No description")
                attributes.append({"name": physical_name, "type": attribute_type, "description": description})

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
                    "referencing_entity": referencing_entity.text,
                    "referenced_entity": referenced_entity.text
                })

        # Extract primary keys
        for pk in entity.findall(".//PrimaryKey"):
            primary_keys.append(pk.get("Name"))

        # Extract foreign keys
        for fk in entity.findall(".//ForeignKey"):
            foreign_keys.append({
                "name": fk.get("Name"),
                "referenced_entity": fk.get("ReferencedEntity")
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
    if len(sys.argv) != 2:
        print("Usage: python parse-entities.py <SolutionFolderName>")
        sys.exit(1)

    solution_folder = sys.argv[1]
    base_path = os.getcwd()
    xml_file = os.path.join(base_path, solution_folder, "customizations.xml")

    if not os.path.exists(os.path.join(base_path, solution_folder)):
        print(f"Error: The folder '{os.path.join(base_path, solution_folder)}' does not exist.")
        sys.exit(1)

    if not os.path.exists(xml_file):
        print(f"Error: The file '{xml_file}' does not exist.")
        sys.exit(1)

    entities = parse_entities(xml_file)
    workflows = parse_workflows(xml_file)

    # Print the parsed entities
    for entity in entities:
        print(f"Entity: {entity['entity_name']}")
        print(f"  Attributes:")
        for attribute in entity['attributes']:
            stripped_name = attribute['name'].replace("mcdev_", "").replace("new_", "")  # Remove prefixes
            print(f"    - {stripped_name} ({attribute['type']}): {attribute['description']}")
        print(f"  Relationships:")
        for relationship in entity['relationships']:
            stripped_referencing = relationship['referencing_entity'].replace("mcdev_", "").replace("new_", "")
            stripped_referenced = relationship['referenced_entity'].replace("mcdev_", "").replace("new_", "")
            print(f"    - {relationship['type']} between {stripped_referencing} and {stripped_referenced}")
        print(f"  Primary Keys: {', '.join(entity['primary_keys'])}")
        print(f"  Foreign Keys:")
        for fk in entity['foreign_keys']:
            stripped_fk_name = fk['name'].replace("mcdev_", "").replace("new_", "")
            stripped_referenced_entity = fk['referenced_entity'].replace("mcdev_", "").replace("new_", "")
            print(f"    - {stripped_fk_name} references {stripped_referenced_entity}")
        print(f"  Ownership: {entity['ownership']}")
        print()

    # Print the parsed workflows
    print("Workflows:")
    for workflow in workflows:
        print(f"  - {workflow['name']} (Primary Entity: {workflow['primary_entity']})")

if __name__ == "__main__":
    main()
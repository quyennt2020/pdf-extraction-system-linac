"""
Demonstration of Enhanced Entity Models and Ontology Foundation
Shows the complete functionality of the hierarchical ontology system
"""

import sys
import os
import json
from datetime import datetime

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from models.ontology_models import (
    MechatronicSystem, Subsystem, Component, SparePart,
    OntologyRelationship, RelationshipType, SystemType, SubsystemType,
    ValidationStatus, create_mechatronic_system, create_subsystem,
    create_component, create_spare_part, create_ontology_relationship,
    get_ontology_statistics
)

def create_sample_linac_ontology():
    """Create a comprehensive sample LINAC ontology"""
    print("🏗️ Creating Sample LINAC Ontology")
    print("=" * 50)
    
    # 1. Create the main LINAC system
    linac_system = create_mechatronic_system(
        label="TrueBeam STx LINAC",
        system_type=SystemType.LINAC,
        model_number="TrueBeam STx",
        manufacturer="Varian Medical Systems",
        description="Linear Accelerator for stereotactic radiation therapy"
    )
    linac_system.serial_number = "TB001-2024"
    linac_system.software_version = "2.7.1"
    linac_system.hardware_version = "STx-v3"
    
    print(f"✅ Created LINAC System: {linac_system.label}")
    
    # 2. Create subsystems
    subsystems = []
    
    # Beam Delivery Subsystem
    beam_delivery = create_subsystem(
        label="Beam Delivery System",
        subsystem_type=SubsystemType.BEAM_DELIVERY,
        parent_system_id=linac_system.id,
        description="System responsible for generating and shaping the therapeutic radiation beam"
    )
    subsystems.append(beam_delivery)
    
    # Patient Positioning Subsystem
    patient_positioning = create_subsystem(
        label="Patient Positioning System",
        subsystem_type=SubsystemType.PATIENT_POSITIONING,
        parent_system_id=linac_system.id,
        description="Robotic couch system for precise patient positioning"
    )
    subsystems.append(patient_positioning)
    
    # Imaging Subsystem
    imaging = create_subsystem(
        label="On-Board Imaging System",
        subsystem_type=SubsystemType.IMAGING,
        parent_system_id=linac_system.id,
        description="kV and MV imaging systems for patient setup verification"
    )
    subsystems.append(imaging)
    
    # Treatment Control Subsystem
    treatment_control = create_subsystem(
        label="Treatment Control System",
        subsystem_type=SubsystemType.TREATMENT_CONTROL,
        parent_system_id=linac_system.id,
        description="Central control system for treatment planning and execution"
    )
    subsystems.append(treatment_control)
    
    # Safety Interlock Subsystem
    safety_interlock = create_subsystem(
        label="Safety Interlock System",
        subsystem_type=SubsystemType.SAFETY_INTERLOCK,
        parent_system_id=linac_system.id,
        description="Comprehensive safety systems and radiation protection interlocks"
    )
    subsystems.append(safety_interlock)
    
    print(f"✅ Created {len(subsystems)} subsystems")
    
    # 3. Create components for Beam Delivery System
    components = []
    
    # Multi-Leaf Collimator
    mlc = create_component(
        label="Millennium MLC",
        component_type="Multi-Leaf Collimator",
        parent_subsystem_id=beam_delivery.id,
        part_number="MLC-120-HD",
        manufacturer="Varian Medical Systems",
        description="120-leaf high-definition multi-leaf collimator for precise beam shaping"
    )
    mlc.model = "Millennium 120HD"
    mlc.lifecycle_status = "active"
    components.append(mlc)
    
    # Linear Accelerator Head
    linac_head = create_component(
        label="Accelerator Head",
        component_type="Accelerator",
        parent_subsystem_id=beam_delivery.id,
        part_number="LINAC-HEAD-STx",
        manufacturer="Varian Medical Systems",
        description="Linear accelerator head assembly for photon and electron beam generation"
    )
    components.append(linac_head)
    
    # Gantry Assembly
    gantry = create_component(
        label="Gantry Assembly",
        component_type="Mechanical Assembly",
        parent_subsystem_id=beam_delivery.id,
        part_number="GANTRY-STx-360",
        manufacturer="Varian Medical Systems",
        description="360-degree rotating gantry for beam delivery positioning"
    )
    components.append(gantry)
    
    # Patient Couch
    couch = create_component(
        label="Exact Couch",
        component_type="Patient Support",
        parent_subsystem_id=patient_positioning.id,
        part_number="COUCH-EXACT-6DOF",
        manufacturer="Varian Medical Systems",
        description="6-degree-of-freedom robotic patient positioning couch"
    )
    components.append(couch)
    
    # kV Imaging Panel
    kv_panel = create_component(
        label="kV Imaging Panel",
        component_type="Imaging Detector",
        parent_subsystem_id=imaging.id,
        part_number="KV-PANEL-4030CB",
        manufacturer="Varian Medical Systems",
        description="Flat panel detector for kV cone-beam CT imaging"
    )
    components.append(kv_panel)
    
    print(f"✅ Created {len(components)} components")
    
    # 4. Create spare parts
    spare_parts = []
    
    # MLC Leaf Motors
    leaf_motor = create_spare_part(
        label="MLC Leaf Drive Motor",
        parent_component_id=mlc.id,
        part_number="MOTOR-LEAF-SERVO-001",
        manufacturer="Varian Medical Systems",
        supplier="Varian Service Parts",
        description="High-precision servo motor for individual MLC leaf positioning"
    )
    leaf_motor.maintenance_cycle = "12 months"
    leaf_motor.replacement_frequency = "5-7 years"
    leaf_motor.stock_level = 5
    leaf_motor.reorder_point = 2
    spare_parts.append(leaf_motor)
    
    # Gantry Bearing
    gantry_bearing = create_spare_part(
        label="Gantry Main Bearing",
        parent_component_id=gantry.id,
        part_number="BEARING-GANTRY-MAIN-001",
        manufacturer="SKF",
        supplier="Varian Service Parts",
        description="Main rotational bearing for gantry assembly"
    )
    gantry_bearing.maintenance_cycle = "24 months"
    gantry_bearing.replacement_frequency = "10-15 years"
    spare_parts.append(gantry_bearing)
    
    # Couch Motor
    couch_motor = create_spare_part(
        label="Couch Drive Motor",
        parent_component_id=couch.id,
        part_number="MOTOR-COUCH-SERVO-001",
        manufacturer="Kollmorgen",
        supplier="Varian Service Parts",
        description="Servo motor for couch positioning axes"
    )
    couch_motor.maintenance_cycle = "18 months"
    spare_parts.append(couch_motor)
    
    print(f"✅ Created {len(spare_parts)} spare parts")
    
    # 5. Create relationships
    relationships = []
    
    # System-Subsystem relationships
    for subsystem in subsystems:
        rel = create_ontology_relationship(
            RelationshipType.HAS_SUBSYSTEM,
            linac_system.id,
            subsystem.id,
            f"LINAC system contains {subsystem.label.lower()}",
            confidence=1.0
        )
        relationships.append(rel)
    
    # Subsystem-Component relationships
    subsystem_component_mapping = [
        (beam_delivery, [mlc, linac_head, gantry]),
        (patient_positioning, [couch]),
        (imaging, [kv_panel])
    ]
    
    for subsystem, subsystem_components in subsystem_component_mapping:
        for component in subsystem_components:
            rel = create_ontology_relationship(
                RelationshipType.HAS_COMPONENT,
                subsystem.id,
                component.id,
                f"{subsystem.label} contains {component.label}",
                confidence=1.0
            )
            relationships.append(rel)
    
    # Component-Spare Part relationships
    component_part_mapping = [
        (mlc, [leaf_motor]),
        (gantry, [gantry_bearing]),
        (couch, [couch_motor])
    ]
    
    for component, component_parts in component_part_mapping:
        for spare_part in component_parts:
            rel = create_ontology_relationship(
                RelationshipType.HAS_SPARE_PART,
                component.id,
                spare_part.id,
                f"{component.label} uses {spare_part.label} as spare part",
                confidence=1.0
            )
            relationships.append(rel)
    
    # Functional relationships
    # MLC controls beam shape
    mlc_control_rel = create_ontology_relationship(
        RelationshipType.CONTROLS,
        mlc.id,
        linac_head.id,
        "MLC controls beam shape from accelerator head",
        confidence=0.95
    )
    relationships.append(mlc_control_rel)
    
    # Gantry contains accelerator head
    gantry_contains_rel = create_ontology_relationship(
        RelationshipType.CONTAINS,
        gantry.id,
        linac_head.id,
        "Gantry assembly contains accelerator head",
        confidence=1.0
    )
    relationships.append(gantry_contains_rel)
    
    print(f"✅ Created {len(relationships)} relationships")
    
    return {
        'system': linac_system,
        'subsystems': subsystems,
        'components': components,
        'spare_parts': spare_parts,
        'relationships': relationships
    }

def demonstrate_ontology_features(ontology_data):
    """Demonstrate various ontology features"""
    print("\n🔍 Demonstrating Ontology Features")
    print("=" * 50)
    
    # 1. Statistics
    stats = get_ontology_statistics(
        [ontology_data['system']],
        ontology_data['subsystems'],
        ontology_data['components'],
        ontology_data['spare_parts'],
        ontology_data['relationships']
    )
    
    print("📊 Ontology Statistics:")
    print(f"  Total Entities: {stats['total_entities']}")
    print(f"  Systems: {stats['entity_counts']['systems']}")
    print(f"  Subsystems: {stats['entity_counts']['subsystems']}")
    print(f"  Components: {stats['entity_counts']['components']}")
    print(f"  Spare Parts: {stats['entity_counts']['spare_parts']}")
    print(f"  Relationships: {stats['total_relationships']}")
    print(f"  Average Confidence: {stats['average_confidence']:.2f}")
    
    # 2. OWL Serialization Examples
    print("\n🔗 OWL Serialization Examples:")
    
    # System OWL
    system_owl = ontology_data['system'].to_owl_dict()
    print(f"  System OWL Type: {system_owl['@type']}")
    print(f"  System URI: {system_owl['@id']}")
    print(f"  System Label: {system_owl['rdfs:label']}")
    
    # Component OWL
    mlc = next(comp for comp in ontology_data['components'] if 'MLC' in comp.label)
    mlc_owl = mlc.to_owl_dict()
    print(f"  MLC Component Type: {mlc_owl['componentType']}")
    print(f"  MLC Part Number: {mlc_owl['partNumber']}")
    
    # 3. Relationship Analysis
    print("\n🔗 Relationship Analysis:")
    relationship_types = {}
    for rel in ontology_data['relationships']:
        rel_type = rel.relationship_type.value
        relationship_types[rel_type] = relationship_types.get(rel_type, 0) + 1
    
    for rel_type, count in relationship_types.items():
        print(f"  {rel_type.replace('_', ' ').title()}: {count}")
    
    # 4. Hierarchy Visualization
    print("\n🌳 Hierarchy Structure:")
    system = ontology_data['system']
    print(f"📦 {system.label} ({system.system_type.value})")
    
    for subsystem in ontology_data['subsystems']:
        print(f"  ├── 📁 {subsystem.label} ({subsystem.subsystem_type.value})")
        
        # Find components for this subsystem
        subsystem_components = [
            comp for comp in ontology_data['components'] 
            if comp.parent_subsystem_id == subsystem.id
        ]
        
        for i, component in enumerate(subsystem_components):
            is_last_component = i == len(subsystem_components) - 1
            component_prefix = "  └──" if is_last_component else "  ├──"
            print(f"  │   {component_prefix} ⚙️ {component.label} ({component.component_type})")
            
            # Find spare parts for this component
            component_parts = [
                part for part in ontology_data['spare_parts']
                if part.parent_component_id == component.id
            ]
            
            for j, spare_part in enumerate(component_parts):
                is_last_part = j == len(component_parts) - 1
                part_prefix = "      └──" if is_last_part else "      ├──"
                indent = "  │   │   " if not is_last_component else "      "
                print(f"{indent}{part_prefix} 🔧 {spare_part.label} (PN: {spare_part.part_number})")

def create_json_ld_export(ontology_data):
    """Create and display JSON-LD export"""
    print("\n📄 JSON-LD Export Sample")
    print("=" * 50)
    
    # Create a simplified JSON-LD structure
    json_ld = {
        "@context": {
            "owl": "http://www.w3.org/2002/07/owl#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "mdo": "http://medical-device-ontology.org/"
        },
        "@type": "owl:Ontology",
        "@id": "http://medical-device-ontology.org/linac-demo",
        "rdfs:label": "LINAC Demo Ontology",
        "rdfs:comment": "Demonstration ontology for TrueBeam LINAC system",
        "created": datetime.now().isoformat(),
        "@graph": []
    }
    
    # Add system
    json_ld["@graph"].append(ontology_data['system'].to_owl_dict())
    
    # Add first few subsystems and components as examples
    for subsystem in ontology_data['subsystems'][:2]:
        json_ld["@graph"].append(subsystem.to_owl_dict())
    
    for component in ontology_data['components'][:2]:
        json_ld["@graph"].append(component.to_owl_dict())
    
    # Display formatted JSON-LD
    print(json.dumps(json_ld, indent=2)[:1000] + "...")
    print(f"\n✅ Full JSON-LD would contain {len(ontology_data['subsystems']) + len(ontology_data['components']) + len(ontology_data['spare_parts']) + len(ontology_data['relationships']) + 1} entities")

def main():
    """Main demonstration function"""
    print("🚀 Enhanced Entity Models and Ontology Foundation Demo")
    print("=" * 60)
    print("This demonstration shows the complete functionality of the")
    print("hierarchical ontology system for medical device troubleshooting.")
    print("=" * 60)
    
    # Create sample ontology
    ontology_data = create_sample_linac_ontology()
    
    # Demonstrate features
    demonstrate_ontology_features(ontology_data)
    
    # Show JSON-LD export
    create_json_ld_export(ontology_data)
    
    print("\n" + "=" * 60)
    print("✅ DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("The Enhanced Entity Models and Ontology Foundation provides:")
    print("• Hierarchical entity models (System → Subsystem → Component → SparePart)")
    print("• OWL ontology data models with proper class hierarchy")
    print("• Comprehensive relationship modeling")
    print("• Validation framework with consistency checking")
    print("• JSON-LD export capabilities")
    print("• Statistical analysis and reporting")
    print("\nThis foundation is ready for integration with:")
    print("• AI entity extraction systems")
    print("• Schematic processing pipelines")
    print("• Expert review interfaces")
    print("• Knowledge graph databases")

if __name__ == "__main__":
    main()
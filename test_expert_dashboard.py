"""
Test script for Expert Review Dashboard
Populates sample ontology data and starts the web server
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from backend.models.ontology_models import (
    create_mechatronic_system, create_subsystem, create_component, create_spare_part,
    create_ontology_relationship, SystemType, SubsystemType, RelationshipType,
    ValidationStatus
)
from backend.api.expert_review_api import ontology_data

def populate_sample_data():
    """Populate sample ontology data for testing"""
    
    print("🔄 Populating sample ontology data...")
    
    # Create LINAC system
    linac_system = create_mechatronic_system(
        label="TrueBeam STx LINAC",
        system_type=SystemType.LINAC,
        model_number="TrueBeam STx",
        manufacturer="Varian Medical Systems",
        description="Linear Accelerator for radiation therapy treatments"
    )
    linac_system.metadata.validation_status = ValidationStatus.EXPERT_APPROVED
    linac_system.metadata.confidence_score = 0.95
    
    # Create subsystems
    beam_delivery = create_subsystem(
        label="Beam Delivery System",
        subsystem_type=SubsystemType.BEAM_DELIVERY,
        parent_system_id=linac_system.id,
        description="System responsible for generating and shaping the radiation beam"
    )
    beam_delivery.metadata.validation_status = ValidationStatus.PENDING_REVIEW
    beam_delivery.metadata.confidence_score = 0.88
    
    patient_positioning = create_subsystem(
        label="Patient Positioning System",
        subsystem_type=SubsystemType.PATIENT_POSITIONING,
        parent_system_id=linac_system.id,
        description="System for precise patient positioning and immobilization"
    )
    patient_positioning.metadata.validation_status = ValidationStatus.EXPERT_APPROVED
    patient_positioning.metadata.confidence_score = 0.92
    
    imaging_system = create_subsystem(
        label="Imaging System",
        subsystem_type=SubsystemType.IMAGING,
        parent_system_id=linac_system.id,
        description="On-board imaging system for patient verification"
    )
    imaging_system.metadata.validation_status = ValidationStatus.NOT_VALIDATED
    imaging_system.metadata.confidence_score = 0.75
    
    # Create components
    mlc_component = create_component(
        label="Multi-Leaf Collimator (MLC)",
        component_type="Beam Shaping Device",
        parent_subsystem_id=beam_delivery.id,
        part_number="MLC-120-HD",
        manufacturer="Varian",
        description="120-leaf high-definition multi-leaf collimator for precise beam shaping"
    )
    mlc_component.metadata.validation_status = ValidationStatus.EXPERT_APPROVED
    mlc_component.metadata.confidence_score = 0.96
    
    gantry_motor = create_component(
        label="Gantry Rotation Motor",
        component_type="Servo Motor",
        parent_subsystem_id=beam_delivery.id,
        part_number="GM-2000-SR",
        manufacturer="Varian",
        description="High-precision servo motor for gantry rotation"
    )
    gantry_motor.metadata.validation_status = ValidationStatus.NEEDS_REVISION
    gantry_motor.metadata.confidence_score = 0.82
    
    couch_motor = create_component(
        label="Treatment Couch Motor",
        component_type="Linear Actuator",
        parent_subsystem_id=patient_positioning.id,
        part_number="TCM-500-LA",
        manufacturer="Varian",
        description="Linear actuator for treatment couch positioning"
    )
    couch_motor.metadata.validation_status = ValidationStatus.PENDING_REVIEW
    couch_motor.metadata.confidence_score = 0.79
    
    kv_imager = create_component(
        label="kV Imaging Panel",
        component_type="Flat Panel Detector",
        parent_subsystem_id=imaging_system.id,
        part_number="KV-FPD-4030",
        manufacturer="Varian",
        description="Flat panel detector for kV imaging"
    )
    kv_imager.metadata.validation_status = ValidationStatus.EXPERT_REJECTED
    kv_imager.metadata.confidence_score = 0.65
    
    # Create spare parts
    leaf_motor = create_spare_part(
        label="MLC Leaf Drive Motor",
        parent_component_id=mlc_component.id,
        part_number="LDM-001-V2",
        manufacturer="Varian",
        supplier="Varian Medical Systems",
        description="Individual leaf drive motor for MLC positioning"
    )
    leaf_motor.metadata.validation_status = ValidationStatus.EXPERT_APPROVED
    leaf_motor.metadata.confidence_score = 0.91
    
    encoder_assembly = create_spare_part(
        label="Gantry Position Encoder",
        parent_component_id=gantry_motor.id,
        part_number="GPE-2000-ENC",
        manufacturer="Heidenhain",
        supplier="Varian Medical Systems",
        description="High-resolution rotary encoder for gantry position feedback"
    )
    encoder_assembly.metadata.validation_status = ValidationStatus.PENDING_REVIEW
    encoder_assembly.metadata.confidence_score = 0.87
    
    # Create relationships
    relationships = [
        create_ontology_relationship(
            RelationshipType.HAS_SUBSYSTEM,
            linac_system.id,
            beam_delivery.id,
            "LINAC system contains beam delivery subsystem",
            0.98
        ),
        create_ontology_relationship(
            RelationshipType.HAS_SUBSYSTEM,
            linac_system.id,
            patient_positioning.id,
            "LINAC system contains patient positioning subsystem",
            0.97
        ),
        create_ontology_relationship(
            RelationshipType.HAS_SUBSYSTEM,
            linac_system.id,
            imaging_system.id,
            "LINAC system contains imaging subsystem",
            0.89
        ),
        create_ontology_relationship(
            RelationshipType.HAS_COMPONENT,
            beam_delivery.id,
            mlc_component.id,
            "Beam delivery subsystem contains MLC component",
            0.95
        ),
        create_ontology_relationship(
            RelationshipType.HAS_COMPONENT,
            beam_delivery.id,
            gantry_motor.id,
            "Beam delivery subsystem contains gantry motor",
            0.93
        ),
        create_ontology_relationship(
            RelationshipType.HAS_COMPONENT,
            patient_positioning.id,
            couch_motor.id,
            "Patient positioning subsystem contains couch motor",
            0.91
        ),
        create_ontology_relationship(
            RelationshipType.HAS_COMPONENT,
            imaging_system.id,
            kv_imager.id,
            "Imaging subsystem contains kV imager",
            0.88
        ),
        create_ontology_relationship(
            RelationshipType.HAS_SPARE_PART,
            mlc_component.id,
            leaf_motor.id,
            "MLC component uses leaf drive motors",
            0.94
        ),
        create_ontology_relationship(
            RelationshipType.HAS_SPARE_PART,
            gantry_motor.id,
            encoder_assembly.id,
            "Gantry motor uses position encoder",
            0.92
        )
    ]
    
    # Add to global storage
    ontology_data["systems"] = [linac_system]
    ontology_data["subsystems"] = [beam_delivery, patient_positioning, imaging_system]
    ontology_data["components"] = [mlc_component, gantry_motor, couch_motor, kv_imager]
    ontology_data["spare_parts"] = [leaf_motor, encoder_assembly]
    ontology_data["relationships"] = relationships
    
    print(f"✅ Sample data populated:")
    print(f"   - Systems: {len(ontology_data['systems'])}")
    print(f"   - Subsystems: {len(ontology_data['subsystems'])}")
    print(f"   - Components: {len(ontology_data['components'])}")
    print(f"   - Spare Parts: {len(ontology_data['spare_parts'])}")
    print(f"   - Relationships: {len(ontology_data['relationships'])}")

def main():
    """Main function to populate data and start server"""
    
    print("🏥 Expert Review Dashboard Test")
    print("=" * 50)
    
    # Populate sample data
    populate_sample_data()
    
    print("\n🚀 Starting web server...")
    print("📊 Dashboard will be available at: http://localhost:8003")
    print("🔧 API endpoints available at: http://localhost:8003/api/expert-review/")
    print("\n💡 Test the following features:")
    print("   - Overview dashboard with statistics")
    print("   - Entity review and validation")
    print("   - Relationship management")
    print("   - Ontology visualization")
    print("   - Bulk edit operations")
    
    print("\n⚠️  Note: This is a test environment with sample data")
    print("🛑 Press Ctrl+C to stop the server")
    
    # Import and run the FastAPI app
    try:
        import uvicorn
        from backend.api.main import app
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8003,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        print("💡 Make sure you have installed the required dependencies:")
        print("   pip install fastapi uvicorn jinja2 python-multipart")

if __name__ == "__main__":
    main()
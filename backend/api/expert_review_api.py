"""
Expert Review API for Ontology Dashboard
Provides REST endpoints for expert review and validation interface
"""

from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import json
import os
import shutil
from datetime import datetime
import uuid
from pathlib import Path

# Import ontology models
from backend.models.ontology_models import (
    MechatronicSystem, Subsystem, Component, SparePart,
    OntologyRelationship, ValidationStatus, RelationshipType,
    OntologyMetadata, SystemType, SubsystemType,
    get_ontology_statistics, validate_hierarchy_consistency
)
from backend.core.ontology_builder import OntologyBuilder
from backend.verification.ontology_validator import OntologyValidator

router = APIRouter(prefix="/api/expert-review", tags=["expert-review"])

# Pydantic models for API requests/responses
class EntityUpdateRequest(BaseModel):
    entity_id: str
    entity_type: str  # system, subsystem, component, spare_part
    updates: Dict[str, Any]
    expert_id: str
    review_comment: Optional[str] = None

class ValidationRequest(BaseModel):
    entity_id: str
    validation_status: str  # ValidationStatus enum value
    expert_id: str
    review_comment: str
    confidence_override: Optional[float] = None

class RelationshipRequest(BaseModel):
    relationship_type: str
    source_entity_id: str
    target_entity_id: str
    description: Optional[str] = None
    expert_id: str

class BulkEditRequest(BaseModel):
    entity_ids: List[str]
    updates: Dict[str, Any]
    expert_id: str
    review_comment: str

class ImportRequest(BaseModel):
    data: Dict[str, Any]
    expert_id: str
    import_mode: str = "merge"  # "merge", "replace", "append"
    validate_only: bool = False

# Global storage (in production, this would be a proper database)
ontology_data = {
    "systems": [],
    "subsystems": [],
    "components": [],
    "spare_parts": [],
    "relationships": []
}

# Flag to track if PDF results have been loaded
pdf_results_loaded = False

def load_pdf_results_into_dashboard():
    """Load the latest PDF processing results into the dashboard"""
    import os
    import glob
    from pathlib import Path
    
    global pdf_results_loaded
    
    try:
        # Look for the latest results in the output directory
        results_dir = Path("data/real_pdf_results")
        if not results_dir.exists():
            return False
        
        # Find the most recent entities file
        entities_files = glob.glob(str(results_dir / "*_entities_*.json"))
        if not entities_files:
            return False
        
        # Get the most recent file
        latest_entities_file = max(entities_files, key=os.path.getctime)
        
        # Load entities data
        with open(latest_entities_file, 'r', encoding='utf-8') as f:
            entities_data = json.load(f)
        
        # Clear existing data
        ontology_data["systems"].clear()
        ontology_data["subsystems"].clear()
        ontology_data["components"].clear()
        ontology_data["spare_parts"].clear()
        ontology_data["relationships"].clear()
        
        # Keep track of loaded entity IDs and content to prevent duplicates
        loaded_entity_ids = set()
        loaded_entity_content = set()
        
        # Convert entities to ontology models
        from backend.models.entity import ErrorCode, Component as EntityComponent, Procedure
        
        for entity_data in entities_data.get('entities', []):
            try:
                # Skip if we've already loaded this entity (prevent duplicates by ID)
                entity_id = entity_data.get('id')
                if entity_id in loaded_entity_ids:
                    continue
                
                # Also check for content-based duplicates
                content_key = _generate_content_key(entity_data)
                if content_key in loaded_entity_content:
                    continue
                
                loaded_entity_ids.add(entity_id)
                loaded_entity_content.add(content_key)
                
                # Determine entity type - check for specific fields to identify type
                entity_type = None
                if 'code' in entity_data and entity_data.get('code'):
                    entity_type = 'error_code'
                elif 'name' in entity_data:
                    entity_type = 'component'
                else:
                    entity_type = 'component'  # Default fallback
                
                # Create component for dashboard display (all entities shown as components for now)
                if entity_type == 'error_code':
                    component = Component(
                        label=f"Error Code: {entity_data.get('code', 'Unknown')}",
                        description=entity_data.get('description', 'No description available'),
                        component_type="Error Code"
                    )
                else:
                    component = Component(
                        label=entity_data.get('name', entity_data.get('label', 'Unknown Component')),
                        description=entity_data.get('description', 'No description available'),
                        component_type=entity_data.get('component_type', 'Generic'),
                        part_number=entity_data.get('part_number', ''),
                        manufacturer=entity_data.get('manufacturer', '')
                    )
                
                # Set confidence score
                confidence = entity_data.get('confidence', entity_data.get('confidence_score', 0.5))
                component.metadata.confidence_score = float(confidence)
                
                # Set validation status based on confidence
                if confidence >= 0.8:
                    component.metadata.validation_status = ValidationStatus.EXPERT_APPROVED
                elif confidence >= 0.6:
                    component.metadata.validation_status = ValidationStatus.PENDING_REVIEW
                else:
                    component.metadata.validation_status = ValidationStatus.NEEDS_REVISION
                
                # Use the original entity ID if available
                if entity_id:
                    component.id = entity_id
                
                ontology_data["components"].append(component)
                    
            except Exception as e:
                print(f"Error processing entity: {e}")
                continue
        
        # Try to load ontology file for relationships
        ontology_files = glob.glob(str(results_dir / "*_ontology_*.json"))
        if ontology_files:
            latest_ontology_file = max(ontology_files, key=os.path.getctime)
            try:
                with open(latest_ontology_file, 'r', encoding='utf-8') as f:
                    ontology_result = json.load(f)
                
                # Create relationships from ontology structure
                if 'hierarchical_structure' in ontology_result:
                    create_relationships_from_structure(ontology_result['hierarchical_structure'])
                    
            except Exception as e:
                print(f"Error loading ontology file: {e}")
        
        # Mark as loaded to prevent reloading
        pdf_results_loaded = True
        return True
        
    except Exception as e:
        print(f"Error loading PDF results: {e}")
        return False

def create_relationships_from_structure(structure, parent_id=None, level=0):
    """Create relationships from hierarchical structure"""
    if not isinstance(structure, dict):
        return
    
    for key, value in structure.items():
        if isinstance(value, dict):
            # Create relationship if we have a parent
            if parent_id and ontology_data["components"]:
                # Find components that match the key
                matching_components = [c for c in ontology_data["components"] 
                                     if key.lower() in c.label.lower()]
                if matching_components:
                    target_id = matching_components[0].id
                    relationship = OntologyRelationship(
                        relationship_type=RelationshipType.HAS_COMPONENT,
                        source_entity_id=parent_id,
                        target_entity_id=target_id,
                        description=f"Hierarchical relationship: {key}"
                    )
                    ontology_data["relationships"].append(relationship)
            
            # Recurse into nested structure
            create_relationships_from_structure(value, parent_id, level + 1)

def _generate_content_key(entity_data: dict) -> str:
    """Generate a content-based key for deduplication"""
    
    # For error codes, use code + message
    if 'code' in entity_data and entity_data.get('code'):
        code = entity_data.get('code', '').strip()
        message = entity_data.get('message', '').strip()
        return f"error_code:{code}:{message}".lower()
    
    # For components, use name + type
    elif 'name' in entity_data:
        name = entity_data.get('name', '').strip()
        comp_type = entity_data.get('component_type', '').strip()
        return f"component:{name}:{comp_type}".lower()
    
    # For other entities, use description
    else:
        description = entity_data.get('description', '')[:100].strip()  # First 100 chars
        return f"other:{description}".lower()



@router.post("/load-pdf-results")
async def load_pdf_results():
    """Load the latest PDF processing results into the dashboard"""
    try:
        global pdf_results_loaded
        # Reset the flag to allow manual reloading
        pdf_results_loaded = False
        
        success = load_pdf_results_into_dashboard()
        if success:
            return JSONResponse(content={
                "success": True,
                "message": "PDF results loaded successfully",
                "entities_loaded": len(ontology_data["components"]),
                "relationships_loaded": len(ontology_data["relationships"])
            })
        else:
            return JSONResponse(content={
                "success": False,
                "message": "No PDF results found or failed to load"
            })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading PDF results: {str(e)}")

@router.post("/clear-data")
async def clear_data():
    """Clear all ontology data from the dashboard"""
    try:
        global pdf_results_loaded
        
        print("Clearing ontology data...")  # Debug log
        
        # Clear all data
        ontology_data["systems"].clear()
        ontology_data["subsystems"].clear()
        ontology_data["components"].clear()
        ontology_data["spare_parts"].clear()
        ontology_data["relationships"].clear()
        
        # Reset the loaded flag
        pdf_results_loaded = False
        
        print("Data cleared successfully")  # Debug log
        
        return JSONResponse(content={
            "success": True,
            "message": "All data cleared successfully"
        })
    except Exception as e:
        print(f"Error in clear_data: {e}")  # Debug log
        raise HTTPException(status_code=500, detail=f"Error clearing data: {str(e)}")

@router.post("/import-entities")
async def import_entities_file(file: UploadFile = File(...), expert_id: str = "current_expert", import_mode: str = "merge"):
    """Import entities from uploaded JSON file"""
    try:
        # Validate file type
        if not file.filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="Only JSON files are supported")
        
        # Read and parse JSON
        content = await file.read()
        try:
            data = json.loads(content.decode('utf-8'))
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")
        
        # Process import
        result = await process_import_data(data, expert_id, import_mode)
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error importing file: {str(e)}")

@router.post("/import-entities-json")
async def import_entities_json(request: ImportRequest):
    """Import entities from JSON data"""
    try:
        result = await process_import_data(
            request.data, 
            request.expert_id, 
            request.import_mode,
            request.validate_only
        )
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error importing data: {str(e)}")

async def process_import_data(data: Dict[str, Any], expert_id: str, import_mode: str = "merge", validate_only: bool = False):
    """Process imported entity data"""
    
    import_stats = {
        "entities_processed": 0,
        "entities_imported": 0,
        "entities_skipped": 0,
        "relationships_processed": 0,
        "relationships_imported": 0,
        "errors": [],
        "warnings": []
    }
    
    try:
        # Validate data structure
        if not isinstance(data, dict):
            raise ValueError("Import data must be a JSON object")
        
        # Clear existing data if replace mode
        if import_mode == "replace" and not validate_only:
            ontology_data["systems"].clear()
            ontology_data["subsystems"].clear()
            ontology_data["components"].clear()
            ontology_data["spare_parts"].clear()
            ontology_data["relationships"].clear()
        
        # Process entities
        entities_data = data.get('entities', [])
        if not isinstance(entities_data, list):
            import_stats["errors"].append("'entities' field must be an array")
        else:
            for i, entity_data in enumerate(entities_data):
                try:
                    import_stats["entities_processed"] += 1
                    
                    # Validate required fields
                    if not isinstance(entity_data, dict):
                        import_stats["errors"].append(f"Entity {i}: Must be an object")
                        continue
                    
                    entity_type = entity_data.get('entity_type', 'component')
                    label = entity_data.get('label', entity_data.get('name', ''))
                    
                    if not label:
                        import_stats["errors"].append(f"Entity {i}: Missing required 'label' or 'name' field")
                        continue
                    
                    # Check for duplicates if merge mode
                    if import_mode == "merge":
                        content_key = _generate_content_key_for_import(entity_data)
                        if _is_duplicate_entity(content_key, entity_type):
                            import_stats["entities_skipped"] += 1
                            import_stats["warnings"].append(f"Entity '{label}': Skipped duplicate")
                            continue
                    
                    # Create entity based on type
                    if not validate_only:
                        entity = _create_entity_from_import(entity_data, entity_type, expert_id)
                        if entity:
                            _add_entity_to_collection(entity, entity_type)
                            import_stats["entities_imported"] += 1
                        else:
                            import_stats["errors"].append(f"Entity '{label}': Failed to create")
                    else:
                        import_stats["entities_imported"] += 1
                        
                except Exception as e:
                    import_stats["errors"].append(f"Entity {i}: {str(e)}")
        
        # Process relationships
        relationships_data = data.get('relationships', [])
        if relationships_data and isinstance(relationships_data, list):
            for i, rel_data in enumerate(relationships_data):
                try:
                    import_stats["relationships_processed"] += 1
                    
                    if not isinstance(rel_data, dict):
                        import_stats["errors"].append(f"Relationship {i}: Must be an object")
                        continue
                    
                    # Validate required fields
                    required_fields = ['relationship_type', 'source_entity_id', 'target_entity_id']
                    missing_fields = [f for f in required_fields if not rel_data.get(f)]
                    if missing_fields:
                        import_stats["errors"].append(f"Relationship {i}: Missing fields: {missing_fields}")
                        continue
                    
                    if not validate_only:
                        relationship = _create_relationship_from_import(rel_data, expert_id)
                        if relationship:
                            ontology_data["relationships"].append(relationship)
                            import_stats["relationships_imported"] += 1
                        else:
                            import_stats["errors"].append(f"Relationship {i}: Failed to create")
                    else:
                        import_stats["relationships_imported"] += 1
                        
                except Exception as e:
                    import_stats["errors"].append(f"Relationship {i}: {str(e)}")
        
        # Generate summary
        success = len(import_stats["errors"]) == 0
        message = "Import completed successfully" if success else "Import completed with errors"
        if validate_only:
            message = "Validation completed - " + message
        
        return {
            "success": success,
            "message": message,
            "stats": import_stats,
            "validation_only": validate_only
        }
        
    except Exception as e:
        import_stats["errors"].append(f"Import failed: {str(e)}")
        return {
            "success": False,
            "message": f"Import failed: {str(e)}",
            "stats": import_stats,
            "validation_only": validate_only
        }

def _generate_content_key_for_import(entity_data: dict) -> str:
    """Generate content key for import deduplication"""
    entity_type = entity_data.get('entity_type', 'component')
    label = entity_data.get('label', entity_data.get('name', ''))
    description = entity_data.get('description', '')[:100]
    
    return f"{entity_type}:{label}:{description}".lower().strip()

def _is_duplicate_entity(content_key: str, entity_type: str) -> bool:
    """Check if entity already exists based on content"""
    collection_map = {
        'system': ontology_data["systems"],
        'subsystem': ontology_data["subsystems"], 
        'component': ontology_data["components"],
        'spare_part': ontology_data["spare_parts"]
    }
    
    entities = collection_map.get(entity_type, ontology_data["components"])
    
    for entity in entities:
        existing_key = f"{entity_type}:{entity.label}:{entity.description[:100]}".lower().strip()
        if existing_key == content_key:
            return True
    return False

def _create_entity_from_import(entity_data: dict, entity_type: str, expert_id: str):
    """Create entity object from import data"""
    try:
        # Common fields
        label = entity_data.get('label', entity_data.get('name', ''))
        description = entity_data.get('description', '')
        
        # Create metadata
        metadata = OntologyMetadata()
        metadata.extraction_method = "import"
        metadata.expert_reviews.append({
            "expert_id": expert_id,
            "timestamp": datetime.now().isoformat(),
            "comment": "Entity imported",
            "action": "import"
        })
        
        # Set confidence and validation status
        if 'metadata' in entity_data:
            meta = entity_data['metadata']
            if 'confidence_score' in meta:
                metadata.confidence_score = float(meta['confidence_score'])
            if 'validation_status' in meta:
                try:
                    metadata.validation_status = ValidationStatus(meta['validation_status'])
                except ValueError:
                    metadata.validation_status = ValidationStatus.NOT_VALIDATED
        
        # Create entity based on type
        if entity_type == 'system':
            from backend.models.ontology_models import SystemType
            system_type = SystemType.GENERIC
            if 'system_type' in entity_data:
                try:
                    system_type = SystemType(entity_data['system_type'])
                except ValueError:
                    pass
            
            entity = MechatronicSystem(
                label=label,
                description=description,
                system_type=system_type,
                model_number=entity_data.get('model_number', ''),
                manufacturer=entity_data.get('manufacturer', ''),
                metadata=metadata
            )
            
        elif entity_type == 'subsystem':
            from backend.models.ontology_models import SubsystemType
            subsystem_type = SubsystemType.MECHANICAL
            if 'subsystem_type' in entity_data:
                try:
                    subsystem_type = SubsystemType(entity_data['subsystem_type'])
                except ValueError:
                    pass
            
            entity = Subsystem(
                label=label,
                description=description,
                subsystem_type=subsystem_type,
                parent_system_id=entity_data.get('parent_system_id', ''),
                metadata=metadata
            )
            
        elif entity_type == 'spare_part':
            entity = SparePart(
                label=label,
                description=description,
                parent_component_id=entity_data.get('parent_component_id', ''),
                part_number=entity_data.get('part_number', ''),
                manufacturer=entity_data.get('manufacturer', ''),
                supplier=entity_data.get('supplier', ''),
                metadata=metadata
            )
            
        else:  # Default to component
            entity = Component(
                label=label,
                description=description,
                component_type=entity_data.get('component_type', 'Generic'),
                parent_subsystem_id=entity_data.get('parent_subsystem_id', ''),
                part_number=entity_data.get('part_number', ''),
                manufacturer=entity_data.get('manufacturer', ''),
                metadata=metadata
            )
        
        # Set custom ID if provided
        if 'id' in entity_data:
            entity.id = entity_data['id']
        
        return entity
        
    except Exception as e:
        print(f"Error creating entity: {e}")
        return None

def _create_relationship_from_import(rel_data: dict, expert_id: str):
    """Create relationship object from import data"""
    try:
        relationship_type = RelationshipType(rel_data['relationship_type'])
        
        metadata = OntologyMetadata()
        metadata.extraction_method = "import"
        metadata.expert_reviews.append({
            "expert_id": expert_id,
            "timestamp": datetime.now().isoformat(),
            "comment": "Relationship imported",
            "action": "import"
        })
        
        relationship = OntologyRelationship(
            relationship_type=relationship_type,
            source_entity_id=rel_data['source_entity_id'],
            target_entity_id=rel_data['target_entity_id'],
            description=rel_data.get('description', ''),
            metadata=metadata
        )
        
        if 'id' in rel_data:
            relationship.id = rel_data['id']
            
        return relationship
        
    except Exception as e:
        print(f"Error creating relationship: {e}")
        return None

def _add_entity_to_collection(entity, entity_type: str):
    """Add entity to appropriate collection"""
    collection_map = {
        'system': ontology_data["systems"],
        'subsystem': ontology_data["subsystems"],
        'component': ontology_data["components"],
        'spare_part': ontology_data["spare_parts"]
    }
    
    collection = collection_map.get(entity_type, ontology_data["components"])
    collection.append(entity)

@router.get("/dashboard/overview")
async def get_dashboard_overview():
    """Get overview statistics for the expert review dashboard""" 
    try:
        # If no data exists and PDF results haven't been loaded yet, try to load PDF results
        total_entities = (len(ontology_data["systems"]) + len(ontology_data["subsystems"]) + 
                         len(ontology_data["components"]) + len(ontology_data["spare_parts"]))
        
        if total_entities == 0 and not pdf_results_loaded:
            load_pdf_results_into_dashboard()
        
        stats = get_ontology_statistics(
            ontology_data["systems"],
            ontology_data["subsystems"], 
            ontology_data["components"],
            ontology_data["spare_parts"],
            ontology_data["relationships"]
        )
        
        # Add review-specific metrics
        pending_review_count = sum(
            1 for entities in [ontology_data["systems"], ontology_data["subsystems"], 
                             ontology_data["components"], ontology_data["spare_parts"]]
            for entity in entities
            if entity.metadata.validation_status == ValidationStatus.PENDING_REVIEW
        )
        
        stats["pending_review_count"] = pending_review_count
        stats["last_updated"] = datetime.now().isoformat()
        
        return JSONResponse(content=stats)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting overview: {str(e)}")

@router.get("/entities")
async def get_entities(
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    validation_status: Optional[str] = Query(None, description="Filter by validation status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page")
):
    """Get paginated list of entities for review"""
    try:
        all_entities = []
        
        # Collect all entities with type information
        for entity in ontology_data["systems"]:
            entity_dict = entity.to_dict() if hasattr(entity, 'to_dict') else entity.__dict__
            entity_dict["entity_type"] = "system"
            all_entities.append(entity_dict)
        for entity in ontology_data["subsystems"]:
            entity_dict = entity.to_dict() if hasattr(entity, 'to_dict') else entity.__dict__
            entity_dict["entity_type"] = "subsystem"
            all_entities.append(entity_dict)
        for entity in ontology_data["components"]:
            entity_dict = entity.to_dict() if hasattr(entity, 'to_dict') else entity.__dict__
            entity_dict["entity_type"] = "component"
            all_entities.append(entity_dict)
        for entity in ontology_data["spare_parts"]:
            entity_dict = entity.to_dict() if hasattr(entity, 'to_dict') else entity.__dict__
            entity_dict["entity_type"] = "spare_part"
            all_entities.append(entity_dict)
        
        # Apply filters
        if entity_type:
            all_entities = [e for e in all_entities if e["entity_type"] == entity_type]
        
        if validation_status:
            status_enum = ValidationStatus(validation_status)
            all_entities = [e for e in all_entities 
                          if e["metadata"].validation_status == status_enum]
        
        # Pagination
        total_count = len(all_entities)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_entities = all_entities[start_idx:end_idx]
        
        return JSONResponse(content={
            "entities": paginated_entities,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": (total_count + page_size - 1) // page_size
            }
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting entities: {str(e)}")

@router.get("/entities/{entity_id}")
async def get_entity_details(entity_id: str):
    """Get detailed information about a specific entity"""
    try:
        # Search for entity in all collections
        for collection_name, entities in ontology_data.items():
            if collection_name == "relationships":
                continue
            for entity in entities:
                if entity.id == entity_id:
                    # Get related entities and relationships
                    related_relationships = [
                        rel for rel in ontology_data["relationships"]
                        if rel.source_entity_id == entity_id or rel.target_entity_id == entity_id
                    ]
                    
                    return JSONResponse(content={
                        "entity": entity.to_dict() if hasattr(entity, 'to_dict') else entity.__dict__,
                        "entity_type": collection_name[:-1],  # Remove 's' from plural
                        "relationships": [rel.to_dict() if hasattr(rel, 'to_dict') else rel.__dict__ for rel in related_relationships]
                    })
        
        raise HTTPException(status_code=404, detail="Entity not found")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting entity details: {str(e)}")

@router.post("/entities/{entity_id}/upload-image")
async def upload_entity_image(entity_id: str, file: UploadFile = File(...)):
    """Upload an image for an entity"""
    try:
        # Validate file type
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/gif", "image/webp"]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Only image files (JPEG, PNG, GIF, WebP) are allowed")
        
        # Create uploads directory if it doesn't exist
        uploads_dir = Path("frontend/static/uploads/entity_images")
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        unique_filename = f"{entity_id}_{uuid.uuid4().hex[:8]}.{file_extension}"
        file_path = uploads_dir / unique_filename
        
        # Save the file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Update entity with image URL
        image_url = f"/static/uploads/entity_images/{unique_filename}"
        entity_updated = False
        
        # Find and update the entity
        for collection_name, entities in ontology_data.items():
            if collection_name == "relationships":
                continue
            for entity in entities:
                if entity.id == entity_id:
                    entity.image_url = image_url
                    entity.metadata.last_modified = datetime.now()
                    entity_updated = True
                    break
            if entity_updated:
                break
        
        if not entity_updated:
            # Clean up uploaded file if entity not found
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(status_code=404, detail="Entity not found")
        
        return JSONResponse(content={
            "success": True,
            "message": "Image uploaded successfully",
            "image_url": image_url,
            "filename": unique_filename
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading image: {str(e)}")

@router.delete("/entities/{entity_id}/image")
async def delete_entity_image(entity_id: str):
    """Delete an entity's image"""
    try:
        entity_updated = False
        old_image_url = None
        
        # Find and update the entity
        for collection_name, entities in ontology_data.items():
            if collection_name == "relationships":
                continue
            for entity in entities:
                if entity.id == entity_id:
                    old_image_url = entity.image_url
                    entity.image_url = None
                    entity.metadata.last_modified = datetime.now()
                    entity_updated = True
                    break
            if entity_updated:
                break
        
        if not entity_updated:
            raise HTTPException(status_code=404, detail="Entity not found")
        
        # Delete the physical file if it exists
        if old_image_url:
            try:
                # Extract filename from URL
                filename = old_image_url.split('/')[-1]
                file_path = Path("frontend/static/uploads/entity_images") / filename
                if file_path.exists():
                    file_path.unlink()
            except Exception as e:
                print(f"Warning: Could not delete image file: {e}")
        
        return JSONResponse(content={
            "success": True,
            "message": "Image deleted successfully"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting image: {str(e)}")

@router.get("/entities/{entity_id}/image")
async def get_entity_image(entity_id: str):
    """Get an entity's image URL"""
    try:
        # Find the entity
        for collection_name, entities in ontology_data.items():
            if collection_name == "relationships":
                continue
            for entity in entities:
                if entity.id == entity_id:
                    return JSONResponse(content={
                        "image_url": entity.image_url,
                        "has_image": entity.image_url is not None
                    })
        
        raise HTTPException(status_code=404, detail="Entity not found")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting entity image: {str(e)}")

@router.put("/entities/{entity_id}")
async def update_entity(entity_id: str, request: EntityUpdateRequest):
    """Update entity properties"""
    try:
        # Find and update entity
        for collection_name, entities in ontology_data.items():
            if collection_name == "relationships":
                continue
            for i, entity in enumerate(entities):
                if entity.id == entity_id:
                    # Update entity properties
                    for key, value in request.updates.items():
                        if '.' in key:
                            # Handle nested attributes like 'metadata.validation_status'
                            parts = key.split('.')
                            obj = entity
                            for part in parts[:-1]:
                                if hasattr(obj, part):
                                    obj = getattr(obj, part)
                                else:
                                    break
                            else:
                                if hasattr(obj, parts[-1]):
                                    if parts[-1] == 'validation_status' and isinstance(value, str):
                                        # Convert string to ValidationStatus enum
                                        setattr(obj, parts[-1], ValidationStatus(value))
                                    else:
                                        setattr(obj, parts[-1], value)
                        else:
                            # Handle direct attributes
                            if hasattr(entity, key):
                                setattr(entity, key, value)
                    
                    # Update metadata
                    entity.metadata.last_modified = datetime.now()
                    if request.review_comment:
                        entity.metadata.expert_reviews.append({
                            "expert_id": request.expert_id,
                            "timestamp": datetime.now().isoformat(),
                            "comment": request.review_comment,
                            "action": "update"
                        })
                    
                    return JSONResponse(content={"success": True, "entity": entity.to_dict() if hasattr(entity, 'to_dict') else entity.__dict__})
        
        raise HTTPException(status_code=404, detail="Entity not found")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating entity: {str(e)}")

@router.post("/entities/{entity_id}/validate")
async def validate_entity(entity_id: str, request: ValidationRequest):
    """Validate or reject an entity""" 
    try:
        # Find entity and update validation status
        for collection_name, entities in ontology_data.items():
            if collection_name == "relationships":
                continue
            for entity in entities:
                if entity.id == entity_id:
                    # Update validation status
                    entity.metadata.validation_status = ValidationStatus(request.validation_status)
                    entity.metadata.last_modified = datetime.now()
                    
                    # Override confidence if provided
                    if request.confidence_override is not None:
                        entity.metadata.confidence_score = request.confidence_override
                    
                    # Add expert review
                    entity.metadata.expert_reviews.append({
                        "expert_id": request.expert_id,
                        "timestamp": datetime.now().isoformat(),
                        "comment": request.review_comment,
                        "action": "validation",
                        "status": request.validation_status
                    })
                    
                    return JSONResponse(content={
                        "success": True, 
                        "entity": entity.to_dict() if hasattr(entity, 'to_dict') else entity.__dict__,
                        "validation_status": request.validation_status
                    })
        
        raise HTTPException(status_code=404, detail="Entity not found")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating entity: {str(e)}")

@router.get("/relationships")
async def get_relationships(
    source_entity_id: Optional[str] = Query(None),
    target_entity_id: Optional[str] = Query(None),
    relationship_type: Optional[str] = Query(None)
):
    """Get relationships with optional filtering"""
    try:
        relationships = ontology_data["relationships"]
        
        # Apply filters
        if source_entity_id:
            relationships = [r for r in relationships if r.source_entity_id == source_entity_id]
        if target_entity_id:
            relationships = [r for r in relationships if r.target_entity_id == target_entity_id]
        if relationship_type:
            rel_type = RelationshipType(relationship_type)
            relationships = [r for r in relationships if r.relationship_type == rel_type]
        
        return JSONResponse(content={
            "relationships": [rel.to_dict() if hasattr(rel, 'to_dict') else rel.__dict__ for rel in relationships]
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting relationships: {str(e)}")

@router.post("/relationships")
async def create_relationship(request: RelationshipRequest):
    """Create a new relationship between entities"""
    try:
        # Validate that source and target entities exist
        all_entity_ids = set()
        for collection_name, entities in ontology_data.items():
            if collection_name == "relationships":
                continue
            all_entity_ids.update(entity.id for entity in entities)
        
        if request.source_entity_id not in all_entity_ids:
            raise HTTPException(status_code=400, detail="Source entity not found")
        if request.target_entity_id not in all_entity_ids:
            raise HTTPException(status_code=400, detail="Target entity not found")
        
        # Create relationship
        relationship = OntologyRelationship(
            relationship_type=RelationshipType(request.relationship_type),
            source_entity_id=request.source_entity_id,
            target_entity_id=request.target_entity_id,
            description=request.description or ""
        )
        
        # Add expert review metadata
        relationship.metadata.expert_reviews.append({
            "expert_id": request.expert_id,
            "timestamp": datetime.now().isoformat(),
            "comment": "Relationship created",
            "action": "create"
        })
        
        ontology_data["relationships"].append(relationship)
        
        return JSONResponse(content={
            "success": True,
            "relationship": relationship.__dict__
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating relationship: {str(e)}")

@router.post("/bulk-edit")
async def bulk_edit_entities(request: BulkEditRequest):
    """Perform bulk edits on multiple entities"""
    try:
        updated_entities = []
        
        for entity_id in request.entity_ids:
            # Find and update each entity
            for collection_name, entities in ontology_data.items():
                if collection_name == "relationships":
                    continue
                for entity in entities:
                    if entity.id == entity_id:
                        # Apply updates
                        for key, value in request.updates.items():
                            if hasattr(entity, key):
                                setattr(entity, key, value)
                        
                        # Update metadata
                        entity.metadata.last_modified = datetime.now()
                        entity.metadata.expert_reviews.append({
                            "expert_id": request.expert_id,
                            "timestamp": datetime.now().isoformat(),
                            "comment": request.review_comment,
                            "action": "bulk_edit"
                        })
                        
                        updated_entities.append(entity.__dict__)
                        break
        
        return JSONResponse(content={
            "success": True,
            "updated_count": len(updated_entities),
            "updated_entities": updated_entities
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in bulk edit: {str(e)}")

@router.get("/validation/summary")
async def get_validation_summary():
    """Get summary of validation status across all entities"""
    try:
        summary = {}
        
        for status in ValidationStatus:
            summary[status.value] = 0
        
        # Count entities by validation status
        for collection_name, entities in ontology_data.items():
            if collection_name == "relationships":
                continue
            for entity in entities:
                status = entity.metadata.validation_status.value
                summary[status] += 1
        
        return JSONResponse(content=summary)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting validation summary: {str(e)}")

@router.post("/entities/{entity_id}/validation-report")
async def get_entity_validation_report(entity_id: str):
    """Get detailed validation report for an entity"""
    try:
        # Find entity
        entity = None
        entity_type = None
        
        for collection_name, entities in ontology_data.items():
            if collection_name == "relationships":
                continue
            for e in entities:
                if e.id == entity_id:
                    entity = e
                    entity_type = collection_name[:-1]  # Remove 's' from plural
                    break
            if entity:
                break
        
        if not entity:
            raise HTTPException(status_code=404, detail="Entity not found")
        
        # Import validator and generate report
        from backend.verification.entity_validator import create_entity_validator
        validator = create_entity_validator()
        
        validation_result = validator.validate_entity(entity, entity_type)
        
        return JSONResponse(content={
            "entity_id": entity_id,
            "entity_type": entity_type,
            "validation_result": {
                "is_valid": validation_result.is_valid,
                "confidence_score": validation_result.confidence_score,
                "issues": [issue.__dict__ for issue in validation_result.issues],
                "recommendations": validation_result.recommendations,
                "validation_timestamp": validation_result.validation_timestamp.isoformat()
            }
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating validation report: {str(e)}")

@router.post("/entities/{entity_id}/expert-review")
async def submit_expert_review(entity_id: str, request: dict):
    """Submit expert review for an entity"""
    try:
        # Find entity
        entity = None
        entity_type = None
        
        for collection_name, entities in ontology_data.items():
            if collection_name == "relationships":
                continue
            for e in entities:
                if e.id == entity_id:
                    entity = e
                    entity_type = collection_name[:-1]
                    break
            if entity:
                break
        
        if not entity:
            raise HTTPException(status_code=404, detail="Entity not found")
        
        # Import validator and submit review
        from backend.verification.entity_validator import create_entity_validator, ValidationAction
        validator = create_entity_validator()
        
        # Map action string to enum
        action_mapping = {
            "approve": ValidationAction.APPROVE,
            "reject": ValidationAction.REJECT,
            "request_revision": ValidationAction.REQUEST_REVISION,
            "update_confidence": ValidationAction.UPDATE_CONFIDENCE,
            "edit_properties": ValidationAction.EDIT_PROPERTIES,
            "add_comment": ValidationAction.ADD_COMMENT
        }
        
        action = action_mapping.get(request.get("action"), ValidationAction.ADD_COMMENT)
        
        review = validator.submit_expert_review(
            entity_id=entity_id,
            expert_id=request.get("expert_id", "current_expert"),
            action=action,
            comment=request.get("comment", ""),
            confidence_override=request.get("confidence_override"),
            field_changes=request.get("field_changes", {}),
            session_id=request.get("session_id")
        )
        
        # Update entity status based on review
        entity.metadata.validation_status = review.new_status
        entity.metadata.last_modified = datetime.now()
        
        # Add review to entity metadata
        entity.metadata.expert_reviews.append({
            "review_id": review.review_id,
            "expert_id": review.expert_id,
            "action": review.action.value,
            "comment": review.comment,
            "timestamp": review.timestamp.isoformat()
        })
        
        return JSONResponse(content={
            "success": True,
            "review_id": review.review_id,
            "new_status": review.new_status.value,
            "entity": entity.__dict__
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting expert review: {str(e)}")

@router.get("/entities/{entity_id}/review-history")
async def get_entity_review_history(entity_id: str):
    """Get review history for an entity"""
    try:
        # Find entity
        entity = None
        
        for collection_name, entities in ontology_data.items():
            if collection_name == "relationships":
                continue
            for e in entities:
                if e.id == entity_id:
                    entity = e
                    break
            if entity:
                break
        
        if not entity:
            raise HTTPException(status_code=404, detail="Entity not found")
        
        # Return review history from entity metadata
        reviews = entity.metadata.expert_reviews if hasattr(entity.metadata, 'expert_reviews') else []
        
        return JSONResponse(content={
            "entity_id": entity_id,
            "review_history": reviews
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting review history: {str(e)}")

@router.get("/validation/queue")
async def get_validation_queue(
    priority: Optional[str] = Query("high", description="Priority level: high, medium, low"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of entities to return")
):
    """Get prioritized queue of entities needing validation"""
    try:
        validation_queue = []
        
        # Collect all entities that need validation
        for collection_name, entities in ontology_data.items():
            if collection_name == "relationships":
                continue
            
            for entity in entities:
                # Prioritize based on validation status and confidence
                priority_score = 0
                
                if entity.metadata.validation_status == ValidationStatus.NOT_VALIDATED:
                    priority_score += 10
                elif entity.metadata.validation_status == ValidationStatus.NEEDS_REVISION:
                    priority_score += 8
                elif entity.metadata.validation_status == ValidationStatus.PENDING_REVIEW:
                    priority_score += 5
                
                # Lower confidence = higher priority
                priority_score += (1.0 - entity.metadata.confidence_score) * 5
                
                # Add to queue if needs attention
                if entity.metadata.validation_status in [
                    ValidationStatus.NOT_VALIDATED,
                    ValidationStatus.NEEDS_REVISION,
                    ValidationStatus.PENDING_REVIEW
                ]:
                    validation_queue.append({
                        "entity_id": entity.id,
                        "entity_type": collection_name[:-1],
                        "label": entity.label,
                        "confidence_score": entity.metadata.confidence_score,
                        "validation_status": entity.metadata.validation_status.value,
                        "priority_score": priority_score,
                        "last_modified": entity.metadata.last_modified.isoformat()
                    })
        
        # Sort by priority score (highest first)
        validation_queue.sort(key=lambda x: x["priority_score"], reverse=True)
        
        # Apply limit
        validation_queue = validation_queue[:limit]
        
        return JSONResponse(content={
            "validation_queue": validation_queue,
            "total_pending": len(validation_queue),
            "queue_generated": datetime.now().isoformat()
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting validation queue: {str(e)}")

@router.post("/validation/auto-fix")
async def auto_fix_validation_issues(request: dict):
    """Automatically fix validation issues where possible"""
    try:
        entity_ids = request.get("entity_ids", [])
        fix_types = request.get("fix_types", ["normalize_text", "format_part_numbers"])
        
        fixed_entities = []
        
        for entity_id in entity_ids:
            # Find entity
            entity = None
            entity_type = None
            
            for collection_name, entities in ontology_data.items():
                if collection_name == "relationships":
                    continue
                for e in entities:
                    if e.id == entity_id:
                        entity = e
                        entity_type = collection_name[:-1]
                        break
                if entity:
                    break
            
            if not entity:
                continue
            
            # Apply auto-fixes
            fixes_applied = {}
            
            if "normalize_text" in fix_types:
                # Normalize label and description
                if entity.label:
                    original_label = entity.label
                    entity.label = entity.label.strip().title()
                    if original_label != entity.label:
                        fixes_applied["label"] = {"from": original_label, "to": entity.label}
                
                if entity.description:
                    original_desc = entity.description
                    entity.description = entity.description.strip()
                    if original_desc != entity.description:
                        fixes_applied["description"] = {"from": original_desc, "to": entity.description}
            
            if "format_part_numbers" in fix_types and hasattr(entity, 'part_number'):
                if entity.part_number:
                    original_part = entity.part_number
                    entity.part_number = entity.part_number.upper().replace(' ', '-')
                    if original_part != entity.part_number:
                        fixes_applied["part_number"] = {"from": original_part, "to": entity.part_number}
            
            if fixes_applied:
                entity.metadata.last_modified = datetime.now()
                entity.metadata.expert_reviews.append({
                    "expert_id": "auto_fix_system",
                    "action": "auto_fix",
                    "comment": f"Auto-fixed: {', '.join(fixes_applied.keys())}",
                    "timestamp": datetime.now().isoformat(),
                    "fixes_applied": fixes_applied
                })
                
                fixed_entities.append({
                    "entity_id": entity_id,
                    "entity_type": entity_type,
                    "fixes_applied": fixes_applied
                })
        
        return JSONResponse(content={
            "success": True,
            "fixed_entities": fixed_entities,
            "total_fixed": len(fixed_entities)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error applying auto-fixes: {str(e)}")

@router.post("/relationships/{relationship_id}/validate")
async def validate_relationship(relationship_id: str):
    """Validate a specific relationship"""
    try:
        # Find relationship
        relationship = None
        for rel in ontology_data["relationships"]:
            if rel.id == relationship_id:
                relationship = rel
                break
        
        if not relationship:
            raise HTTPException(status_code=404, detail="Relationship not found")
        
        # Find source and target entities
        source_entity = None
        target_entity = None
        source_type = None
        target_type = None
        
        for collection_name, entities in ontology_data.items():
            if collection_name == "relationships":
                continue
            for entity in entities:
                if entity.id == relationship.source_entity_id:
                    source_entity = entity
                    source_type = collection_name[:-1]
                elif entity.id == relationship.target_entity_id:
                    target_entity = entity
                    target_type = collection_name[:-1]
        
        if not source_entity or not target_entity:
            raise HTTPException(status_code=400, detail="Source or target entity not found")
        
        # Import validator and validate
        from backend.verification.relationship_validator import create_relationship_validator
        validator = create_relationship_validator()
        
        validation_result = validator.validate_relationship(
            relationship, source_entity, target_entity, source_type, target_type,
            ontology_data["relationships"]
        )
        
        return JSONResponse(content={
            "relationship_id": relationship_id,
            "validation_result": {
                "is_valid": validation_result.is_valid,
                "issues": [issue.__dict__ for issue in validation_result.issues],
                "suggestions": [suggestion.__dict__ for suggestion in validation_result.suggestions],
                "validation_timestamp": validation_result.validation_timestamp.isoformat()
            }
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating relationship: {str(e)}")

@router.post("/relationships/infer")
async def infer_relationships(request: dict):
    """Infer potential relationships based on domain knowledge"""
    try:
        confidence_threshold = request.get("confidence_threshold", 0.6)
        entity_scope = request.get("entity_scope", "all")  # all, system, subsystem, selected
        relationship_types = request.get("relationship_types", ["hierarchical", "functional"])
        
        # Collect entities based on scope
        entities = {}
        
        if entity_scope == "all":
            for collection_name, entity_list in ontology_data.items():
                if collection_name == "relationships":
                    continue
                for entity in entity_list:
                    entities[entity.id] = (entity, collection_name[:-1])
        
        # Import validator and generate suggestions
        from backend.verification.relationship_validator import create_relationship_validator
        validator = create_relationship_validator()
        
        suggestions = validator.infer_relationships(entities, ontology_data["relationships"])
        
        # Filter by confidence threshold
        filtered_suggestions = [
            s for s in suggestions 
            if s.confidence_score >= confidence_threshold
        ]
        
        return JSONResponse(content={
            "suggestions": [suggestion.__dict__ for suggestion in filtered_suggestions],
            "total_suggestions": len(filtered_suggestions),
            "confidence_threshold": confidence_threshold,
            "generated_timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inferring relationships: {str(e)}")

@router.put("/relationships/{relationship_id}")
async def update_relationship(relationship_id: str, request: dict):
    """Update relationship properties"""
    try:
        # Find relationship
        relationship = None
        for i, rel in enumerate(ontology_data["relationships"]):
            if rel.id == relationship_id:
                relationship = rel
                break
        
        if not relationship:
            raise HTTPException(status_code=404, detail="Relationship not found")
        
        # Update properties
        updates = request.get("updates", {})
        for key, value in updates.items():
            if hasattr(relationship, key):
                setattr(relationship, key, value)
        
        # Update metadata
        relationship.metadata.last_modified = datetime.now()
        if request.get("expert_comment"):
            relationship.metadata.expert_reviews.append({
                "expert_id": request.get("expert_id", "current_expert"),
                "timestamp": datetime.now().isoformat(),
                "comment": request.get("expert_comment"),
                "action": "update"
            })
        
        return JSONResponse(content={
            "success": True,
            "relationship": relationship.__dict__
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating relationship: {str(e)}")

@router.delete("/relationships/{relationship_id}")
async def delete_relationship(relationship_id: str):
    """Delete a relationship"""
    try:
        # Find and remove relationship
        for i, rel in enumerate(ontology_data["relationships"]):
            if rel.id == relationship_id:
                del ontology_data["relationships"][i]
                return JSONResponse(content={"success": True, "deleted_id": relationship_id})
        
        raise HTTPException(status_code=404, detail="Relationship not found")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting relationship: {str(e)}")

@router.post("/relationships/validate-all")
async def validate_all_relationships():
    """Validate all relationships in the ontology"""
    try:
        from backend.verification.relationship_validator import create_relationship_validator
        validator = create_relationship_validator()
        
        validation_results = []
        total_issues = 0
        
        for relationship in ontology_data["relationships"]:
            # Find source and target entities
            source_entity = None
            target_entity = None
            source_type = None
            target_type = None
            
            for collection_name, entities in ontology_data.items():
                if collection_name == "relationships":
                    continue
                for entity in entities:
                    if entity.id == relationship.source_entity_id:
                        source_entity = entity
                        source_type = collection_name[:-1]
                    elif entity.id == relationship.target_entity_id:
                        target_entity = entity
                        target_type = collection_name[:-1]
            
            if source_entity and target_entity:
                result = validator.validate_relationship(
                    relationship, source_entity, target_entity, source_type, target_type,
                    ontology_data["relationships"]
                )
                
                validation_results.append({
                    "relationship_id": relationship.id,
                    "is_valid": result.is_valid,
                    "issue_count": len(result.issues),
                    "issues": [issue.__dict__ for issue in result.issues]
                })
                
                total_issues += len(result.issues)
        
        return JSONResponse(content={
            "validation_results": validation_results,
            "summary": {
                "total_relationships": len(ontology_data["relationships"]),
                "valid_relationships": len([r for r in validation_results if r["is_valid"]]),
                "invalid_relationships": len([r for r in validation_results if not r["is_valid"]]),
                "total_issues": total_issues
            },
            "validation_timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating all relationships: {str(e)}")

@router.post("/relationships/detect-duplicates")
async def detect_duplicate_relationships():
    """Detect duplicate relationships"""
    try:
        duplicates = []
        relationships = ontology_data["relationships"]
        
        for i, rel1 in enumerate(relationships):
            for j, rel2 in enumerate(relationships[i+1:], i+1):
                if (rel1.source_entity_id == rel2.source_entity_id and
                    rel1.target_entity_id == rel2.target_entity_id and
                    rel1.relationship_type == rel2.relationship_type):
                    
                    duplicates.append({
                        "relationship_1": rel1.__dict__,
                        "relationship_2": rel2.__dict__,
                        "duplicate_type": "exact_match"
                    })
        
        return JSONResponse(content={
            "duplicates": duplicates,
            "duplicate_count": len(duplicates),
            "detection_timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting duplicates: {str(e)}")

@router.post("/relationships/detect-cycles")
async def detect_circular_dependencies():
    """Detect circular dependencies in hierarchical relationships"""
    try:
        from backend.verification.relationship_validator import create_relationship_validator
        validator = create_relationship_validator()
        
        # Build graph of hierarchical relationships
        hierarchical_types = ["has_subsystem", "has_component", "has_spare_part", "part_of"]
        graph = {}
        
        for rel in ontology_data["relationships"]:
            if rel.relationship_type.value in hierarchical_types:
                if rel.source_entity_id not in graph:
                    graph[rel.source_entity_id] = []
                graph[rel.source_entity_id].append({
                    "target": rel.target_entity_id,
                    "relationship_id": rel.id,
                    "relationship_type": rel.relationship_type.value
                })
        
        # Detect cycles using DFS
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node, path):
            if node in rec_stack:
                # Found cycle
                cycle_start = path.index(node)
                cycle_path = path[cycle_start:] + [node]
                cycles.append(cycle_path)
                return
            
            if node in visited:
                return
            
            visited.add(node)
            rec_stack.add(node)
            
            for edge in graph.get(node, []):
                dfs(edge["target"], path + [node])
            
            rec_stack.remove(node)
        
        for node in graph:
            if node not in visited:
                dfs(node, [])
        
        return JSONResponse(content={
            "cycles": cycles,
            "cycle_count": len(cycles),
            "detection_timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting cycles: {str(e)}")

@router.get("/visualization/graph")
async def get_visualization_graph():
    """Get graph data for ontology visualization"""
    try:
        nodes = []
        edges = []
        
        # Add system nodes
        for system in ontology_data["systems"]:
            nodes.append({
                "id": system.id,
                "label": system.label or "Unnamed System",
                "group": "system",
                "level": 0,
                "title": f"System: {system.label}\nType: {system.system_type.value}\nConfidence: {system.metadata.confidence_score:.1%}",
                "confidence": system.metadata.confidence_score,
                "validation_status": system.metadata.validation_status.value
            })
        
        # Add subsystem nodes
        for subsystem in ontology_data["subsystems"]:
            nodes.append({
                "id": subsystem.id,
                "label": subsystem.label or "Unnamed Subsystem",
                "group": "subsystem", 
                "level": 1,
                "title": f"Subsystem: {subsystem.label}\nType: {subsystem.subsystem_type.value}\nConfidence: {subsystem.metadata.confidence_score:.1%}",
                "confidence": subsystem.metadata.confidence_score,
                "validation_status": subsystem.metadata.validation_status.value
            })
        
        # Add component nodes
        for component in ontology_data["components"]:
            nodes.append({
                "id": component.id,
                "label": component.label or "Unnamed Component",
                "group": "component",
                "level": 2,
                "title": f"Component: {component.label}\nType: {component.component_type}\nConfidence: {component.metadata.confidence_score:.1%}",
                "confidence": component.metadata.confidence_score,
                "validation_status": component.metadata.validation_status.value
            })
        
        # Add spare part nodes
        for spare_part in ontology_data["spare_parts"]:
            nodes.append({
                "id": spare_part.id,
                "label": spare_part.label or "Unnamed Spare Part",
                "group": "spare_part",
                "level": 3,
                "title": f"Spare Part: {spare_part.label}\nPart Number: {spare_part.part_number}\nConfidence: {spare_part.metadata.confidence_score:.1%}",
                "confidence": spare_part.metadata.confidence_score,
                "validation_status": spare_part.metadata.validation_status.value
            })
        
        # Add relationship edges
        for relationship in ontology_data["relationships"]:
            edges.append({
                "id": relationship.id,
                "from": relationship.source_entity_id,
                "to": relationship.target_entity_id,
                "label": relationship.relationship_type.value.replace('_', ' '),
                "title": f"Relationship: {relationship.relationship_type.value}\nDescription: {relationship.description or 'No description'}\nConfidence: {relationship.metadata.confidence_score:.1%}",
                "confidence": relationship.metadata.confidence_score,
                "arrows": "to"
            })
        
        return JSONResponse(content={
            "nodes": nodes,
            "edges": edges,
            "statistics": {
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "systems": len(ontology_data["systems"]),
                "subsystems": len(ontology_data["subsystems"]),
                "components": len(ontology_data["components"]),
                "spare_parts": len(ontology_data["spare_parts"])
            }
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting visualization data: {str(e)}")
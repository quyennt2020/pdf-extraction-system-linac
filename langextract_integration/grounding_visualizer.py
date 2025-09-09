"""
Grounding Visualizer for LangExtract Integration

Provides enhanced visualization capabilities that highlight extracted entities
in their original context with source grounding information.
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path
import html
from datetime import datetime


class GroundingVisualizer:
    """Creates interactive HTML visualizations with source grounding"""
    
    def __init__(self):
        self.entity_colors = {
            "error_codes": "#ff6b6b",      # Red
            "components": "#4ecdc4",        # Teal  
            "procedures": "#45b7d1",        # Blue
            "safety_protocols": "#f9ca24",  # Yellow
            "systems": "#6c5ce7",           # Purple
            "subsystems": "#a29bfe",        # Light purple
            "relationships": "#fd79a8",     # Pink
            "technical_specifications": "#00b894"  # Green
        }
    
    def create_grounded_visualization(
        self,
        extraction_results: Dict[str, Any],
        original_text: str,
        output_file: str = "grounded_visualization.html",
        title: str = "LINAC Entity Extraction with Source Grounding"
    ) -> str:
        """
        Create an interactive HTML visualization showing entities in their original context
        
        Args:
            extraction_results: Results from LangExtract extraction
            original_text: Original source text
            output_file: Output HTML file path
            title: Visualization title
            
        Returns:
            Path to generated HTML file
        """
        
        try:
            # Collect all entities with their source locations
            grounded_entities = self._collect_grounded_entities(extraction_results)
            
            # Generate HTML content
            html_content = self._generate_grounded_html(
                entities=grounded_entities,
                original_text=original_text,
                title=title,
                extraction_metadata=extraction_results.get("extraction_metadata", {})
            )
            
            # Save to file
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return str(output_path)
            
        except Exception as e:
            raise Exception(f"Error creating grounded visualization: {str(e)}")
    
    def _collect_grounded_entities(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Collect all entities with their grounding information"""
        
        grounded_entities = []
        
        # Process consolidated entities if available
        consolidated = results.get("consolidated_entities", results)
        
        for entity_type, entities in consolidated.items():
            if isinstance(entities, list):
                for entity in entities:
                    if isinstance(entity, dict):
                        grounded_entity = {
                            "type": entity_type,
                            "text": entity.get("text", entity.get("name", entity.get("code", ""))),
                            "confidence": entity.get("confidence", 0.0),
                            "attributes": entity.get("attributes", {}),
                            "source_location": entity.get("source_location", {}),
                            "color": self.entity_colors.get(entity_type, "#95a5a6")
                        }
                        grounded_entities.append(grounded_entity)
        
        # Sort by confidence (highest first)
        grounded_entities.sort(key=lambda x: x["confidence"], reverse=True)
        
        return grounded_entities
    
    def _generate_grounded_html(
        self,
        entities: List[Dict[str, Any]],
        original_text: str,
        title: str,
        extraction_metadata: Dict[str, Any]
    ) -> str:
        """Generate the complete HTML content with grounding visualization"""
        
        # Create highlighted text
        highlighted_text = self._create_highlighted_text(original_text, entities)
        
        # Generate entity cards
        entity_cards = self._generate_entity_cards(entities)
        
        # Generate statistics
        statistics = self._generate_statistics(entities, extraction_metadata)
        
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)}</title>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{html.escape(title)}</h1>
            <div class="metadata">
                {self._format_metadata(extraction_metadata)}
            </div>
        </header>
        
        <div class="main-content">
            <div class="text-panel">
                <div class="panel-header">
                    <h2>Source Text with Highlighted Entities</h2>
                    <div class="legend">
                        {self._generate_legend()}
                    </div>
                </div>
                <div class="highlighted-text">
                    {highlighted_text}
                </div>
            </div>
            
            <div class="entities-panel">
                <div class="panel-header">
                    <h2>Extracted Entities</h2>
                    {statistics}
                </div>
                <div class="entity-filters">
                    {self._generate_filters()}
                </div>
                <div class="entities-container">
                    {entity_cards}
                </div>
            </div>
        </div>
        
        <footer>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} using LangExtract Integration</p>
        </footer>
    </div>
    
    <script>
        {self._get_javascript()}
    </script>
</body>
</html>
"""
        
        return html_template
    
    def _create_highlighted_text(self, text: str, entities: List[Dict[str, Any]]) -> str:
        """Create text with highlighted entities"""
        
        # Sort entities by position to avoid overlap issues
        entities_with_positions = []
        
        for entity in entities:
            source_location = entity.get("source_location", {})
            start_char = source_location.get("start_char")
            end_char = source_location.get("end_char")
            
            if start_char is not None and end_char is not None:
                entities_with_positions.append({
                    "start": start_char,
                    "end": end_char,
                    "entity": entity
                })
            else:
                # Fallback: try to find entity text in the original text
                entity_text = entity["text"]
                start_pos = text.find(entity_text)
                if start_pos != -1:
                    entities_with_positions.append({
                        "start": start_pos,
                        "end": start_pos + len(entity_text),
                        "entity": entity
                    })
        
        # Sort by start position
        entities_with_positions.sort(key=lambda x: x["start"])
        
        # Create highlighted text
        highlighted = ""
        current_pos = 0
        
        for item in entities_with_positions:
            start = item["start"]
            end = item["end"]
            entity = item["entity"]
            
            # Add text before entity
            if start > current_pos:
                highlighted += html.escape(text[current_pos:start])
            
            # Add highlighted entity
            entity_html = self._create_entity_highlight(
                text[start:end], 
                entity["type"], 
                entity["color"],
                entity["confidence"],
                entity.get("attributes", {})
            )
            highlighted += entity_html
            
            current_pos = end
        
        # Add remaining text
        if current_pos < len(text):
            highlighted += html.escape(text[current_pos:])
        
        return highlighted
    
    def _create_entity_highlight(
        self, 
        text: str, 
        entity_type: str, 
        color: str, 
        confidence: float,
        attributes: Dict[str, Any]
    ) -> str:
        """Create HTML for a highlighted entity"""
        
        # Create tooltip content
        tooltip_content = f"Type: {entity_type.replace('_', ' ').title()}<br>"
        tooltip_content += f"Confidence: {confidence:.2f}<br>"
        
        # Add key attributes
        key_attrs = ["message", "function", "type", "severity", "category"]
        for attr in key_attrs:
            if attr in attributes:
                value = attributes[attr]
                if isinstance(value, str) and value:
                    tooltip_content += f"{attr.title()}: {html.escape(value)}<br>"
        
        return f"""
        <span class="entity-highlight {entity_type}" 
              style="background-color: {color}; opacity: {0.3 + confidence * 0.4}"
              data-entity-type="{entity_type}"
              data-confidence="{confidence}"
              title="{tooltip_content}">
            {html.escape(text)}
        </span>
        """
    
    def _generate_entity_cards(self, entities: List[Dict[str, Any]]) -> str:
        """Generate HTML cards for each entity"""
        
        cards_html = ""
        
        for i, entity in enumerate(entities):
            card_html = f"""
            <div class="entity-card {entity['type']}" 
                 data-entity-type="{entity['type']}"
                 data-confidence="{entity['confidence']}">
                <div class="card-header" style="border-left: 4px solid {entity['color']}">
                    <h3>{html.escape(entity['text'])}</h3>
                    <div class="entity-badges">
                        <span class="entity-type-badge" style="background-color: {entity['color']}">{entity['type'].replace('_', ' ').title()}</span>
                        <span class="confidence-badge">{entity['confidence']:.2f}</span>
                    </div>
                </div>
                <div class="card-content">
                    {self._format_entity_attributes(entity['attributes'])}
                    {self._format_source_location(entity.get('source_location', {}))}
                </div>
            </div>
            """
            cards_html += card_html
        
        return cards_html
    
    def _format_entity_attributes(self, attributes: Dict[str, Any]) -> str:
        """Format entity attributes for display"""
        
        if not attributes:
            return ""
        
        attrs_html = "<div class='attributes'>"
        
        for key, value in attributes.items():
            if value and str(value).strip():  # Skip empty values
                formatted_key = key.replace('_', ' ').title()
                
                if isinstance(value, list):
                    if value:  # Non-empty list
                        value_str = ", ".join(str(v) for v in value)
                        attrs_html += f"<div class='attribute'><strong>{formatted_key}:</strong> {html.escape(value_str)}</div>"
                elif isinstance(value, dict):
                    if value:  # Non-empty dict
                        value_str = json.dumps(value, indent=2)
                        attrs_html += f"<div class='attribute'><strong>{formatted_key}:</strong><pre>{html.escape(value_str)}</pre></div>"
                else:
                    attrs_html += f"<div class='attribute'><strong>{formatted_key}:</strong> {html.escape(str(value))}</div>"
        
        attrs_html += "</div>"
        return attrs_html
    
    def _format_source_location(self, source_location: Dict[str, Any]) -> str:
        """Format source location information"""
        
        if not source_location:
            return ""
        
        location_html = "<div class='source-location'>"
        location_html += "<h4>Source Location:</h4>"
        
        if "start_char" in source_location and "end_char" in source_location:
            location_html += f"<div>Characters: {source_location['start_char']} - {source_location['end_char']}</div>"
        
        if "context" in source_location:
            context = source_location["context"][:200] + ("..." if len(source_location["context"]) > 200 else "")
            location_html += f"<div class='context'><strong>Context:</strong> {html.escape(context)}</div>"
        
        location_html += "</div>"
        return location_html
    
    def _generate_legend(self) -> str:
        """Generate color legend for entity types"""
        
        legend_html = "<div class='legend-items'>"
        
        for entity_type, color in self.entity_colors.items():
            display_name = entity_type.replace('_', ' ').title()
            legend_html += f"""
            <div class="legend-item">
                <span class="legend-color" style="background-color: {color}"></span>
                <span class="legend-label">{display_name}</span>
            </div>
            """
        
        legend_html += "</div>"
        return legend_html
    
    def _generate_filters(self) -> str:
        """Generate filter controls"""
        
        return """
        <div class="filter-controls">
            <div class="filter-group">
                <label>Entity Type:</label>
                <select id="entity-type-filter">
                    <option value="all">All Types</option>
                    <option value="error_codes">Error Codes</option>
                    <option value="components">Components</option>
                    <option value="procedures">Procedures</option>
                    <option value="safety_protocols">Safety Protocols</option>
                    <option value="systems">Systems</option>
                    <option value="subsystems">Subsystems</option>
                </select>
            </div>
            <div class="filter-group">
                <label>Min Confidence:</label>
                <input type="range" id="confidence-filter" min="0" max="1" step="0.1" value="0">
                <span id="confidence-value">0.0</span>
            </div>
        </div>
        """
    
    def _generate_statistics(self, entities: List[Dict[str, Any]], metadata: Dict[str, Any]) -> str:
        """Generate statistics summary"""
        
        # Count entities by type
        type_counts = {}
        confidence_sum = 0
        
        for entity in entities:
            entity_type = entity["type"]
            type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
            confidence_sum += entity["confidence"]
        
        avg_confidence = confidence_sum / len(entities) if entities else 0
        
        stats_html = f"""
        <div class="statistics">
            <div class="stat-item">
                <span class="stat-number">{len(entities)}</span>
                <span class="stat-label">Total Entities</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">{len(type_counts)}</span>
                <span class="stat-label">Entity Types</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">{avg_confidence:.2f}</span>
                <span class="stat-label">Avg Confidence</span>
            </div>
        </div>
        """
        
        return stats_html
    
    def _format_metadata(self, metadata: Dict[str, Any]) -> str:
        """Format extraction metadata"""
        
        if not metadata:
            return ""
        
        metadata_html = "<div class='extraction-metadata'>"
        
        if "model" in metadata:
            metadata_html += f"<span>Model: {metadata['model']}</span>"
        
        if "extraction_passes" in metadata:
            metadata_html += f"<span>Passes: {metadata['extraction_passes']}</span>"
        
        if "examples_used" in metadata:
            metadata_html += f"<span>Examples: {metadata['examples_used']}</span>"
        
        metadata_html += "</div>"
        return metadata_html
    
    def _get_css_styles(self) -> str:
        """Get CSS styles for the visualization"""
        
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        
        header h1 {
            color: #2c3e50;
            margin-bottom: 10px;
        }
        
        .extraction-metadata {
            display: flex;
            gap: 20px;
            font-size: 14px;
            color: #7f8c8d;
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 1fr 400px;
            gap: 20px;
        }
        
        .panel-header {
            background: #34495e;
            color: white;
            padding: 15px;
            border-radius: 8px 8px 0 0;
        }
        
        .panel-header h2 {
            margin-bottom: 10px;
        }
        
        .text-panel, .entities-panel {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .highlighted-text {
            padding: 20px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.8;
            white-space: pre-wrap;
            max-height: 600px;
            overflow-y: auto;
            border: 1px solid #ecf0f1;
        }
        
        .entity-highlight {
            padding: 2px 4px;
            border-radius: 3px;
            cursor: pointer;
            position: relative;
            transition: opacity 0.3s;
        }
        
        .entity-highlight:hover {
            opacity: 1 !important;
            box-shadow: 0 0 0 2px rgba(0,0,0,0.3);
        }
        
        .legend {
            margin-top: 10px;
        }
        
        .legend-items {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 12px;
        }
        
        .legend-color {
            width: 12px;
            height: 12px;
            border-radius: 2px;
        }
        
        .entities-container {
            max-height: 600px;
            overflow-y: auto;
            padding: 10px;
        }
        
        .entity-card {
            margin-bottom: 15px;
            border: 1px solid #ecf0f1;
            border-radius: 6px;
            overflow: hidden;
            transition: transform 0.2s;
        }
        
        .entity-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        .card-header {
            padding: 10px 15px;
            background: #f8f9fa;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .card-header h3 {
            font-size: 16px;
            color: #2c3e50;
            margin: 0;
        }
        
        .entity-badges {
            display: flex;
            gap: 5px;
        }
        
        .entity-type-badge, .confidence-badge {
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
            color: white;
        }
        
        .confidence-badge {
            background-color: #95a5a6;
        }
        
        .card-content {
            padding: 15px;
        }
        
        .attributes {
            margin-bottom: 10px;
        }
        
        .attribute {
            margin-bottom: 8px;
            font-size: 13px;
        }
        
        .attribute strong {
            color: #34495e;
        }
        
        .source-location {
            border-top: 1px solid #ecf0f1;
            padding-top: 10px;
            margin-top: 10px;
            font-size: 12px;
            color: #7f8c8d;
        }
        
        .context {
            background: #f8f9fa;
            padding: 8px;
            border-radius: 4px;
            margin-top: 5px;
            font-family: 'Courier New', monospace;
        }
        
        .filter-controls {
            padding: 15px;
            background: #f8f9fa;
            display: flex;
            gap: 20px;
            align-items: center;
        }
        
        .filter-group {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .filter-group label {
            font-size: 13px;
            font-weight: 500;
        }
        
        .statistics {
            display: flex;
            gap: 15px;
            margin-top: 10px;
        }
        
        .stat-item {
            text-align: center;
        }
        
        .stat-number {
            display: block;
            font-size: 18px;
            font-weight: bold;
            color: #3498db;
        }
        
        .stat-label {
            font-size: 12px;
            color: #bdc3c7;
        }
        
        footer {
            text-align: center;
            padding: 20px;
            color: #7f8c8d;
            font-size: 12px;
            margin-top: 20px;
        }
        
        pre {
            font-size: 11px;
            background: #f8f9fa;
            padding: 5px;
            border-radius: 3px;
            margin-top: 5px;
        }
        """
    
    def _get_javascript(self) -> str:
        """Get JavaScript for interactive features"""
        
        return """
        // Filter functionality
        document.addEventListener('DOMContentLoaded', function() {
            const typeFilter = document.getElementById('entity-type-filter');
            const confidenceFilter = document.getElementById('confidence-filter');
            const confidenceValue = document.getElementById('confidence-value');
            
            // Update confidence display
            confidenceFilter.addEventListener('input', function() {
                confidenceValue.textContent = this.value;
                filterEntities();
            });
            
            typeFilter.addEventListener('change', filterEntities);
            
            function filterEntities() {
                const selectedType = typeFilter.value;
                const minConfidence = parseFloat(confidenceFilter.value);
                
                const cards = document.querySelectorAll('.entity-card');
                
                cards.forEach(card => {
                    const entityType = card.dataset.entityType;
                    const confidence = parseFloat(card.dataset.confidence);
                    
                    const typeMatch = selectedType === 'all' || entityType === selectedType;
                    const confidenceMatch = confidence >= minConfidence;
                    
                    if (typeMatch && confidenceMatch) {
                        card.style.display = 'block';
                    } else {
                        card.style.display = 'none';
                    }
                });
            }
            
            // Highlight synchronization
            const highlights = document.querySelectorAll('.entity-highlight');
            const cards = document.querySelectorAll('.entity-card');
            
            highlights.forEach(highlight => {
                highlight.addEventListener('mouseenter', function() {
                    const entityType = this.dataset.entityType;
                    // Highlight corresponding cards
                    cards.forEach(card => {
                        if (card.dataset.entityType === entityType) {
                            card.style.background = '#e8f4fd';
                        }
                    });
                });
                
                highlight.addEventListener('mouseleave', function() {
                    cards.forEach(card => {
                        card.style.background = '';
                    });
                });
            });
            
            cards.forEach(card => {
                card.addEventListener('mouseenter', function() {
                    const entityType = this.dataset.entityType;
                    // Highlight corresponding text
                    highlights.forEach(highlight => {
                        if (highlight.dataset.entityType === entityType) {
                            highlight.style.boxShadow = '0 0 0 2px #3498db';
                        }
                    });
                });
                
                card.addEventListener('mouseleave', function() {
                    highlights.forEach(highlight => {
                        highlight.style.boxShadow = '';
                    });
                });
            });
        });
        """


if __name__ == "__main__":
    # Test the grounding visualizer
    
    sample_results = {
        "consolidated_entities": {
            "error_codes": [
                {
                    "code": "7002",
                    "text": "7002",
                    "confidence": 0.95,
                    "attributes": {
                        "message": "MOVEMENT",
                        "description": "Leaf movement direction mismatch",
                        "category": "Mechanical"
                    },
                    "source_location": {
                        "start_char": 10,
                        "end_char": 14,
                        "context": "Error Code 7002: MOVEMENT"
                    }
                }
            ],
            "components": [
                {
                    "name": "leaf motors",
                    "text": "leaf motors", 
                    "confidence": 0.88,
                    "attributes": {
                        "type": "actuator",
                        "function": "control leaf movement"
                    },
                    "source_location": {
                        "start_char": 45,
                        "end_char": 56,
                        "context": "Check the drive to the leaf motors"
                    }
                }
            ]
        },
        "extraction_metadata": {
            "model": "gemini-2.5-flash",
            "extraction_passes": 2,
            "examples_used": 8
        }
    }
    
    sample_text = "Error Code 7002: MOVEMENT. Check the drive to the leaf motors for proper operation."
    
    visualizer = GroundingVisualizer()
    
    try:
        output_file = visualizer.create_grounded_visualization(
            sample_results,
            sample_text,
            "test_grounding_visualization.html",
            "Test LINAC Extraction"
        )
        print(f"✅ Grounding visualization created: {output_file}")
    except Exception as e:
        print(f"❌ Grounding visualizer test failed: {str(e)}")
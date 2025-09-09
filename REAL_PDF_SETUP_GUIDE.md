# Real Service Manual PDF Processing Guide

This guide explains how to process real medical device service manuals through the complete ontology extraction pipeline.

## Prerequisites

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Set it as an environment variable:

```bash
# Windows
set GEMINI_API_KEY=your_api_key_here

# Linux/Mac
export GEMINI_API_KEY=your_api_key_here
```

### 3. Prepare Your PDF

Place your service manual PDF in one of these locations:
- `data/input_pdfs/` (recommended)
- Any accessible file path

## Quick Start

### Basic Processing

```bash
python run_with_real_pdf.py "data/input_pdfs/your_manual.pdf"
```

### Advanced Processing

```bash
python run_with_real_pdf.py "path/to/manual.pdf" \
    --device-type linear_accelerator \
    --max-pages 50 \
    --output-dir "results/my_analysis" \
    --start-dashboard
```

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `pdf_path` | Path to PDF file (required) | - |
| `--device-type` | Medical device type | `linear_accelerator` |
| `--max-pages` | Maximum pages to process | `20` |
| `--output-dir` | Output directory | `data/real_pdf_results` |
| `--api-key` | Gemini API key | From environment |
| `--start-dashboard` | Launch expert dashboard | `False` |

### Device Types

- `linear_accelerator` - LINAC systems (Varian, Elekta, etc.)
- `ct_scanner` - CT imaging systems
- `mri` - MRI systems  
- `ultrasound` - Ultrasound systems

## Processing Pipeline

The system processes your PDF through these steps:

### 1. PDF Text Extraction
- Extracts text from each page
- Handles complex layouts and tables
- Filters out headers/footers

### 2. AI Entity Extraction
- Uses Gemini Flash for intelligent extraction
- Identifies components, error codes, procedures
- Extracts hierarchical relationships

### 3. Ontology Building
- Builds hierarchical structure
- Infers relationships between entities
- Creates semantic connections

### 4. Validation & Quality Check
- Validates entity consistency
- Checks ontology structure
- Generates quality metrics

### 5. Expert Review Interface
- Web dashboard for validation
- Entity editing and approval
- Relationship visualization

## Output Files

The system generates several output files:

### Entity Data
- `{filename}_entities_{timestamp}.json` - Raw extracted entities
- Includes confidence scores and source references

### Ontology Structure  
- `{filename}_ontology_{timestamp}.json` - Built ontology
- Hierarchical structure and relationships

### Validation Results
- `{filename}_validation_{timestamp}.json` - Quality checks
- Validation errors and recommendations

### Comprehensive Report
- `{filename}_report_{timestamp}.json` - Complete analysis
- Statistics, metrics, and next steps

## Example Usage Scenarios

### Scenario 1: Quick Analysis
Process first 10 pages for initial assessment:

```bash
python run_with_real_pdf.py "manual.pdf" --max-pages 10
```

### Scenario 2: Complete Processing
Full manual with expert dashboard:

```bash
python run_with_real_pdf.py "manual.pdf" \
    --max-pages 100 \
    --start-dashboard
```

### Scenario 3: Batch Processing
Process multiple manuals:

```bash
for pdf in data/input_pdfs/*.pdf; do
    python run_with_real_pdf.py "$pdf" --max-pages 30
done
```

## Expert Dashboard

When using `--start-dashboard`, you get access to:

### Overview Dashboard
- Processing statistics
- Entity distribution charts
- Validation status summary

### Entity Review
- Browse extracted entities
- Edit and validate entries
- Bulk operations

### Relationship Editor
- Visualize entity relationships
- Create/edit connections
- Validate relationship rules

### Ontology Visualization
- Interactive network graphs
- Hierarchical views
- Export capabilities

## Troubleshooting

### Common Issues

#### API Rate Limits
```
Error: Rate limit exceeded
```
**Solution**: The system includes automatic delays. For large PDFs, consider processing in smaller batches.

#### Low Quality Extractions
```
Warning: Low average confidence (45%)
```
**Solutions**:
- Check PDF text quality (scanned vs native text)
- Adjust device type parameter
- Use expert dashboard for manual validation

#### Memory Issues
```
Error: Out of memory
```
**Solutions**:
- Reduce `--max-pages` parameter
- Process PDF in sections
- Increase system memory

### PDF Quality Requirements

**Best Results**:
- Native text PDFs (not scanned images)
- Clear formatting and structure
- Technical service manuals with:
  - Component lists
  - Error code tables
  - Troubleshooting procedures
  - Parts diagrams with text

**Acceptable**:
- High-quality scanned PDFs with OCR
- Mixed text/image content
- Structured technical documents

**Poor Results**:
- Low-resolution scans
- Handwritten content
- Pure image files without text
- Heavily formatted marketing materials

## Performance Optimization

### For Large PDFs (>100 pages)
1. Start with `--max-pages 20` for testing
2. Process in sections if needed
3. Use batch processing for multiple files

### For Better Accuracy
1. Ensure correct `--device-type`
2. Use high-quality PDF sources
3. Review and validate results in dashboard

### For Production Use
1. Set up proper API key management
2. Configure logging and monitoring
3. Implement error handling and retries

## Integration with Expert Dashboard

After processing, use the expert dashboard to:

1. **Review Extractions**: Validate AI-extracted entities
2. **Edit Entities**: Correct errors and add missing information  
3. **Build Relationships**: Create semantic connections
4. **Export Results**: Generate final ontology files

Access dashboard at: `http://localhost:8000`

## Next Steps

After successful processing:

1. Review the comprehensive report
2. Use expert dashboard for validation
3. Export validated ontology to OWL format
4. Integrate with your knowledge management system

## Support

For issues or questions:
1. Check the generated log files in `logs/`
2. Review the comprehensive report for recommendations
3. Use the expert dashboard for manual corrections
4. Adjust processing parameters based on results

## Example Output Structure

```
data/real_pdf_results/
├── manual_entities_20241204_143022.json
├── manual_ontology_20241204_143022.json  
├── manual_validation_20241204_143022.json
├── manual_report_20241204_143022.json
└── logs/
    └── real_pdf_processing_20241204_143022.log
```

Each file contains detailed information about different aspects of the processing pipeline, allowing for comprehensive analysis and validation of the extracted ontology.
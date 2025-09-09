# Medical Device Ontology Extraction - Real PDF Processing

This system processes real medical device service manuals to extract structured ontologies using AI and expert validation workflows.

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Install dependencies
pip install -r requirements.txt

# Set API key (get from https://makersuite.google.com/app/apikey)
export GEMINI_API_KEY=your_api_key_here
```

### 2. Test Setup

```bash
# Verify installation
python test_setup.py
```

### 3. Create Sample PDF (Optional)

```bash
# Generate sample service manual
python create_sample_pdf.py

# Convert the HTML file to PDF using your browser:
# 1. Open data/input_pdfs/sample_service_manual.html
# 2. Print -> Save as PDF
# 3. Save as sample_service_manual.pdf
```

### 4. Process Real PDF

```bash
# Basic processing
python run_with_real_pdf.py "path/to/your/service_manual.pdf"

# With expert dashboard
python run_with_real_pdf.py "path/to/your/manual.pdf" --start-dashboard

# Advanced options
python run_with_real_pdf.py "manual.pdf" \
    --device-type linear_accelerator \
    --max-pages 50 \
    --output-dir "results/analysis_2024"
```

## 📁 File Structure

```
├── run_with_real_pdf.py          # Main processing script
├── test_setup.py                 # Setup verification
├── create_sample_pdf.py          # Sample PDF generator
├── requirements.txt              # Dependencies
├── REAL_PDF_SETUP_GUIDE.md      # Detailed setup guide
├── data/
│   ├── input_pdfs/               # Place your PDFs here
│   └── real_pdf_results/         # Processing results
├── backend/                      # Core processing modules
├── frontend/                     # Expert dashboard
└── logs/                         # Processing logs
```

## 🔧 Processing Pipeline

### Stage 1: PDF Text Extraction
- Extracts text from each page
- Handles complex layouts and tables
- Filters noise (headers, footers, page numbers)

### Stage 2: AI Entity Extraction  
- Uses Google Gemini Flash for intelligent parsing
- Identifies medical device components
- Extracts error codes and procedures
- Finds part numbers and specifications

### Stage 3: Ontology Construction
- Builds hierarchical entity structure
- Infers relationships between components
- Creates semantic connections
- Validates domain rules

### Stage 4: Expert Validation
- Web-based review dashboard
- Entity editing and approval workflow
- Relationship visualization and editing
- Collaborative validation tools

## 📊 Output Files

Each processing run generates:

- **Entities JSON**: Raw extracted entities with confidence scores
- **Ontology JSON**: Structured hierarchy and relationships  
- **Validation JSON**: Quality checks and validation results
- **Report JSON**: Comprehensive analysis and recommendations
- **Processing Log**: Detailed execution information

## 🖥️ Expert Dashboard Features

Access at `http://localhost:8000` when using `--start-dashboard`:

### Overview Dashboard
- Processing statistics and metrics
- Entity distribution charts
- Validation status summary
- Quality indicators

### Entity Review Interface
- Browse and filter extracted entities
- Edit entity properties and metadata
- Validate with confidence indicators
- Bulk operations for efficiency

### Relationship Editor
- Visual relationship mapping
- Create and edit entity connections
- Validate relationship rules
- AI-powered relationship suggestions

### Ontology Visualization
- Interactive network graphs
- Hierarchical tree views
- Export capabilities (PNG, SVG, JSON)
- Filtering and layout options

## 🎯 Use Cases

### Service Manual Analysis
Process technical service manuals to extract:
- Component hierarchies
- Error code databases
- Maintenance procedures
- Spare parts catalogs

### Knowledge Base Construction
Build structured knowledge bases from:
- Technical documentation
- Troubleshooting guides
- Training materials
- Regulatory documents

### Quality Assurance
Validate and improve:
- Documentation completeness
- Technical accuracy
- Consistency across manuals
- Compliance requirements

## 📈 Performance Guidelines

### PDF Quality Requirements

**Optimal Results:**
- Native text PDFs (not scanned)
- Clear structure and formatting
- Technical service manuals with:
  - Component lists and hierarchies
  - Error code tables
  - Troubleshooting procedures
  - Parts diagrams with text labels

**Good Results:**
- High-quality OCR'd PDFs
- Mixed text/image content
- Structured technical documents
- Clear typography and layout

**Poor Results:**
- Low-resolution scans
- Handwritten content
- Pure image files
- Marketing materials without technical content

### Processing Recommendations

**For Large PDFs (>100 pages):**
- Start with `--max-pages 20` for initial testing
- Process in sections if memory constrained
- Use batch processing for multiple files

**For Better Accuracy:**
- Ensure correct `--device-type` parameter
- Use high-quality source PDFs
- Review results in expert dashboard
- Validate and correct AI extractions

**For Production Use:**
- Set up proper API key management
- Configure logging and monitoring
- Implement error handling and retries
- Use expert validation workflows

## 🔍 Troubleshooting

### Common Issues

**API Rate Limits:**
```
Error: Rate limit exceeded
```
- System includes automatic delays
- Consider smaller batch sizes
- Check API quota and billing

**Low Extraction Quality:**
```
Warning: Low average confidence (45%)
```
- Verify PDF text quality
- Check device type parameter
- Use expert dashboard for validation
- Consider manual annotation

**Memory Issues:**
```
Error: Out of memory
```
- Reduce `--max-pages` parameter
- Process in smaller sections
- Increase system memory
- Close other applications

**PDF Processing Errors:**
```
Error: Cannot extract text from PDF
```
- Check PDF file integrity
- Try different PDF processing library
- Convert scanned PDFs with OCR
- Verify file permissions

### Getting Help

1. **Check Logs**: Review files in `logs/` directory
2. **Run Tests**: Execute `python test_setup.py`
3. **Review Report**: Check comprehensive report JSON
4. **Use Dashboard**: Manual validation and correction
5. **Adjust Parameters**: Modify processing settings

## 🔧 Configuration Options

### Device Types
- `linear_accelerator`: LINAC systems (Varian, Elekta)
- `ct_scanner`: CT imaging systems
- `mri`: MRI systems
- `ultrasound`: Ultrasound equipment

### Processing Parameters
- `--max-pages`: Limit pages processed (default: 20)
- `--output-dir`: Results directory
- `--api-key`: Gemini API key override
- `--start-dashboard`: Launch expert interface

### Quality Settings
- Confidence thresholds for entity validation
- Relationship inference parameters
- Validation rule strictness
- Expert review requirements

## 🚀 Advanced Usage

### Batch Processing Multiple PDFs

```bash
#!/bin/bash
for pdf in data/input_pdfs/*.pdf; do
    echo "Processing: $pdf"
    python run_with_real_pdf.py "$pdf" \
        --max-pages 30 \
        --output-dir "batch_results/$(basename "$pdf" .pdf)"
done
```

### Custom Device Types

Modify `backend/ai_extraction/prompt_templates.py` to add new device types and extraction patterns.

### Integration with External Systems

The JSON outputs can be integrated with:
- Knowledge management systems
- CMMS (Computerized Maintenance Management Systems)
- Technical documentation platforms
- Training and certification systems

## 📋 Example Workflow

1. **Prepare PDF**: Place service manual in `data/input_pdfs/`
2. **Initial Processing**: Run with limited pages for testing
3. **Review Results**: Check extraction quality and statistics
4. **Expert Validation**: Use dashboard for manual review
5. **Full Processing**: Process complete manual if quality is good
6. **Export Results**: Generate final ontology files
7. **Integration**: Import into target knowledge system

## 🎓 Best Practices

### Before Processing
- Verify PDF text quality and structure
- Choose appropriate device type
- Set realistic page limits for testing
- Ensure adequate API quota

### During Processing
- Monitor logs for errors and warnings
- Check intermediate results
- Adjust parameters if needed
- Use expert dashboard for validation

### After Processing
- Review comprehensive report
- Validate high-impact entities
- Export validated ontology
- Document any manual corrections

This system provides a complete pipeline from raw service manuals to validated, structured ontologies ready for integration into knowledge management systems.
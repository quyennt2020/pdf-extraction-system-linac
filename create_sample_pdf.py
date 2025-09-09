"""
Create Sample Service Manual PDF for Testing
Generates a realistic medical device service manual PDF for testing the extraction pipeline
"""

import os
from pathlib import Path

def create_sample_pdf_content():
    """Create sample service manual content"""
    
    content = """
VARIAN MEDICAL SYSTEMS
TrueBeam STx Linear Accelerator
Service Manual - Version 2.7

Chapter 4: Multi-Leaf Collimator (MLC) System

4.1 System Overview

The Multi-Leaf Collimator (MLC) system consists of 120 tungsten leaves arranged in two banks of 60 leaves each. The system provides precise beam shaping capabilities for intensity-modulated radiation therapy (IMRT) and volumetric modulated arc therapy (VMAT).

Key Components:
- MLC Controller Unit (Part Number: MLC-CTRL-2000)
- Leaf Drive Motors (Part Number: LDM-001-V3) - 120 units
- Position Encoders (Part Number: ENC-HD-500) - 120 units
- Motor Driver Cards (Part Number: MDC-24V-100) - 10 units
- Safety Interlock System (Part Number: SIS-MLC-200)

4.2 Error Codes and Troubleshooting

Error Code: 7002
Message: LEAF MOVEMENT ERROR
Description: The actual direction of movement of a leaf does not match the expected direction, or a leaf has moved that should be stationary.
Possible Causes:
- Faulty leaf drive motor
- Damaged position encoder
- Loose motor connections
- Motor driver card failure
Response: Check drive connections to leaf motors and verify free movement of leaves.

Error Code: 7003  
Message: LEAF POSITION TIMEOUT
Description: A leaf has not reached its commanded position within the specified time limit.
Possible Causes:
- Mechanical obstruction
- Motor power supply failure
- Encoder calibration error
Response: Inspect leaf bank for obstructions and verify motor power supply voltages.

Error Code: 7004
Message: MLC INTERLOCK FAILURE
Description: Safety interlock system has detected an unsafe condition.
Possible Causes:
- Door position sensor failure
- Emergency stop activation
- Interlock circuit malfunction
Response: Check all safety interlocks and door positions before resetting.

4.3 Maintenance Procedures

4.3.1 Daily Checks
- Verify leaf position accuracy using QA phantom
- Check motor temperatures (should be < 45°C)
- Inspect leaf surfaces for damage

4.3.2 Weekly Maintenance
- Lubricate leaf guide rails (Use lubricant: LUB-MLC-001)
- Check motor mounting bolts (Torque: 8.5 Nm)
- Verify encoder calibration

4.3.3 Monthly Maintenance
- Replace air filters (Part Number: FILT-AIR-MLC)
- Check cooling system operation
- Perform comprehensive position accuracy test

4.4 Spare Parts List

Critical Spare Parts (Keep in Stock):
- Leaf Drive Motor (LDM-001-V3) - Quantity: 5
- Position Encoder (ENC-HD-500) - Quantity: 5  
- Motor Driver Card (MDC-24V-100) - Quantity: 2
- Air Filter (FILT-AIR-MLC) - Quantity: 10
- Leaf Guide Rail (LGR-TUNG-120) - Quantity: 2

Recommended Spare Parts:
- MLC Controller Unit (MLC-CTRL-2000) - Quantity: 1
- Safety Interlock Module (SIM-MLC-001) - Quantity: 1
- Power Supply Unit (PSU-24V-500W) - Quantity: 1

Chapter 5: Gantry System

5.1 Gantry Drive System

The gantry rotation system uses a servo motor drive with high-precision encoder feedback to provide accurate angular positioning.

Components:
- Gantry Drive Motor (Part Number: GDM-5KW-SR)
- Gantry Position Encoder (Part Number: GPE-ABS-19BIT)
- Motor Controller (Part Number: MC-SERVO-5K)
- Brake System (Part Number: BRK-ELEC-500)

5.2 Error Codes

Error Code: 8001
Message: GANTRY POSITION ERROR
Description: Gantry position feedback does not match commanded position.
Response: Check encoder connections and recalibrate if necessary.

Error Code: 8002
Message: GANTRY OVERSPEED
Description: Gantry rotation speed exceeds safety limits.
Response: Check motor controller parameters and brake system operation.

Chapter 6: Patient Support System

6.1 Treatment Couch

The treatment couch provides 6-degree-of-freedom positioning with the following components:

- Couch Drive Motors (Part Number: CDM-SERVO-2K) - 6 units
- Position Sensors (Part Number: PS-LINEAR-500) - 6 units  
- Couch Controller (Part Number: CC-6DOF-MAIN)
- Load Cell Assembly (Part Number: LC-2000KG)

6.2 Safety Systems

- Patient Collision Detection (Part Number: PCD-LASER-360)
- Emergency Stop System (Part Number: ESS-COUCH-001)
- Weight Limit Monitor (Part Number: WLM-200KG)

Maintenance Schedule:
- Daily: Check emergency stops and collision detection
- Weekly: Lubricate drive mechanisms
- Monthly: Calibrate position sensors and load cells
- Quarterly: Replace drive belts (Part Number: BELT-COUCH-XL)

This completes the MLC, Gantry, and Patient Support system documentation.
For additional technical support, contact Varian Service at 1-800-VARIAN-1.

Document Version: 2.7.3
Last Updated: March 2024
Classification: Service Personnel Only
"""
    
    return content

def save_as_text_file():
    """Save content as text file that can be converted to PDF"""
    
    # Create directories
    os.makedirs("data/input_pdfs", exist_ok=True)
    
    content = create_sample_pdf_content()
    
    # Save as text file
    text_file = "data/input_pdfs/sample_service_manual.txt"
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Sample service manual content saved to: {text_file}")
    print(f"\n📄 To create a PDF:")
    print(f"   1. Open the text file in a word processor")
    print(f"   2. Save/Export as PDF")
    print(f"   3. Place the PDF in data/input_pdfs/")
    print(f"\n🔧 Or use online converter:")
    print(f"   - https://www.ilovepdf.com/txt_to_pdf")
    print(f"   - https://smallpdf.com/txt-to-pdf")
    
    return text_file

def create_simple_html_version():
    """Create HTML version that can be printed to PDF"""
    
    content = create_sample_pdf_content()
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Sample Service Manual</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        h3 {{ color: #7f8c8d; }}
        .error-code {{ background-color: #f8f9fa; padding: 10px; border-left: 4px solid #e74c3c; margin: 10px 0; }}
        .part-number {{ font-family: monospace; background-color: #ecf0f1; padding: 2px 4px; }}
        .maintenance {{ background-color: #e8f5e8; padding: 10px; border-radius: 5px; margin: 10px 0; }}
    </style>
</head>
<body>
"""
    
    # Convert content to HTML with basic formatting
    lines = content.split('\n')
    in_error_section = False
    
    for line in lines:
        line = line.strip()
        if not line:
            html_content += "<br>\n"
            continue
        
        # Headers
        if line.startswith('VARIAN MEDICAL SYSTEMS'):
            html_content += f"<h1>{line}</h1>\n"
        elif line.startswith('Chapter'):
            html_content += f"<h2>{line}</h2>\n"
        elif any(line.startswith(x) for x in ['4.1', '4.2', '4.3', '5.1', '5.2', '6.1', '6.2']):
            html_content += f"<h3>{line}</h3>\n"
        
        # Error codes
        elif line.startswith('Error Code:'):
            html_content += f'<div class="error-code"><strong>{line}</strong>'
            in_error_section = True
        elif in_error_section and line.startswith('Response:'):
            html_content += f"<br><strong>{line}</strong></div>\n"
            in_error_section = False
        elif in_error_section:
            html_content += f"<br>{line}"
        
        # Part numbers
        elif 'Part Number:' in line:
            line = line.replace('Part Number:', '<span class="part-number">Part Number:')
            line = line.replace(')', ')</span>')
            html_content += f"<p>{line}</p>\n"
        
        # Maintenance sections
        elif any(x in line for x in ['Daily:', 'Weekly:', 'Monthly:', 'Quarterly:']):
            html_content += f'<div class="maintenance"><strong>{line}</strong></div>\n'
        
        # Regular paragraphs
        else:
            html_content += f"<p>{line}</p>\n"
    
    html_content += """
</body>
</html>
"""
    
    # Save HTML file
    html_file = "data/input_pdfs/sample_service_manual.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML version saved to: {html_file}")
    print(f"\n🖨️ To create PDF from HTML:")
    print(f"   1. Open {html_file} in a web browser")
    print(f"   2. Print -> Save as PDF")
    print(f"   3. Save as 'sample_service_manual.pdf' in data/input_pdfs/")
    
    return html_file

def main():
    """Create sample service manual files"""
    
    print("📄 Creating Sample Service Manual for Testing")
    print("=" * 50)
    
    # Create text version
    text_file = save_as_text_file()
    
    # Create HTML version  
    html_file = create_simple_html_version()
    
    print(f"\n🎯 Next Steps:")
    print(f"   1. Convert one of the files to PDF")
    print(f"   2. Place PDF in data/input_pdfs/")
    print(f"   3. Run: python run_with_real_pdf.py 'data/input_pdfs/sample_service_manual.pdf'")
    
    print(f"\n📋 Sample Content Includes:")
    print(f"   - Multi-Leaf Collimator (MLC) system")
    print(f"   - Error codes and troubleshooting")
    print(f"   - Component part numbers")
    print(f"   - Maintenance procedures")
    print(f"   - Spare parts lists")
    print(f"   - Gantry and patient support systems")

if __name__ == "__main__":
    main()
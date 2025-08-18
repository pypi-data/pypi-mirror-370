from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from plantuml import PlantUML
import os, subprocess, platform

def parse_text_file(file_path, script_dir):
    """
    Parses a structured text file and converts it to a list of formatted elements
    for PDF generation.
    """
    elements = []
    styles = getSampleStyleSheet()
    bold_style = ParagraphStyle(name="Bold", parent=styles['Normal'], fontSize=12, leading=14, spaceAfter=10, fontName="Helvetica-Bold")
    paragraph_style = styles['BodyText']
    list_item_style = ParagraphStyle(name="List", parent=styles['BodyText'], bulletIndent=10)

    plantuml_server = PlantUML(url='http://www.plantuml.com/plantuml/img/')
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    
    plantuml_code = []
    in_plantuml_block = False
    diagram_count = 0

    for line in lines:
        line = line.strip()
        
        # Handle PlantUML blocks
        if line.startswith("@startuml"):
            in_plantuml_block = True
            plantuml_code = [line]
        elif line.startswith("@enduml") and in_plantuml_block:
            plantuml_code.append(line)
            in_plantuml_block = False

            # Generate diagram and add it as an image
            diagram_count += 1
            diagram_file = os.path.join(script_dir, f"diagram_{diagram_count}.png") # f"diagram_{diagram_count}.png"
            diagram_txt_file = os.path.join(script_dir, f"diagram_{diagram_count}.puml") # f"diagram_{diagram_count}.txt"

            plantuml_code_str = "\n".join(plantuml_code)
            # Generate text file with PlantUML code
            with open(diagram_txt_file, "w") as txt_file:
                txt_file.write(plantuml_code_str)
                        
            try:
                with open(diagram_file, "wb") as f:
                    f.write(plantuml_server.processes(plantuml_code_str))
            except Exception as e:
                raise RuntimeError(f"Failed to generate PlantUML diagram {diagram_file}: {e}")

            # Add the image to the PDF elements
            elements.append(Image(diagram_file, width=400, height=300))  # Adjust size as needed
            elements.append(Spacer(1, 12))
        elif in_plantuml_block:
            plantuml_code.append(line)

        # Identify and style headings
        elif line.startswith("###"):  # Sub-heading
            elements.append(Paragraph(f"<b>{line[4:].strip()}</b>", paragraph_style))
            elements.append(Spacer(1, 12))
        
        elif line.startswith("##"):  # Main heading
            elements.append(Paragraph(f"<b>{line[3:].strip()}</b>", bold_style))
            elements.append(Spacer(1, 12))
        
        # Identify list items
        elif line.startswith("-"):  # List item
            elements.append(Paragraph(f"- {line[1:].strip()}", list_item_style))
            elements.append(Spacer(1, 12))
        
        # Regular text (paragraphs)
        elif line:
            elements.append(Paragraph(line, paragraph_style))
            elements.append(Spacer(1, 12))
    
    return elements
    
def generate_pdf(gptOutput, script_dir, fileName):
    """
    Reads a structured text file and generates a PDF from it.
    """
    # Parse the text file into PDF elements
    content = parse_text_file(gptOutput, script_dir)
    # pdf_path = os.path.join(script_dir, fileName)
    try:
        doc = SimpleDocTemplate(fileName, pagesize=letter)
        # Define a title style for the document title
        title_style = ParagraphStyle(
            name="Title",
            fontSize=24,        # Larger font size
            leading=28,
            fontName="Helvetica-Bold",
            alignment=TA_CENTER  # Center align the title
        )
         # Add the title as the first element in the content
        content.insert(0, Paragraph("Software Design Document", title_style))
        content.insert(1, Spacer(1, 20))  # Add space after the title
        doc.build(content)
    except Exception as e:
        return f"❌ Failed to generate PDF document: {str(e)}"

    # delete the diagram files that were generated
    #for diagram_file in os.listdir(script_dir):
    #    if diagram_file.startswith("diagram") and diagram_file.endswith(".png"):
    #        os.remove(os.path.join(script_dir, diagram_file))


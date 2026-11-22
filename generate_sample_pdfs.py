"""
Utility script to create sample PDF question papers for testing PDF upload.
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def txt_to_pdf(txt_path, pdf_path, title_header):
    with open(txt_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor('#1E3A8A'),
        alignment=1 # Center
    )
    sub_header_style = ParagraphStyle(
        'SubHeaderStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#4B5563'),
        alignment=1
    )
    q_style = ParagraphStyle(
        'QuestionStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=15,
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=6
    )
    
    story = []
    story.append(Paragraph(title_header, header_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Pune University / Autonomous Engineering Examination • Department of Computer Engineering", sub_header_style))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1E3A8A'), spaceAfter=12))
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            story.append(Spacer(1, 4))
            continue
        if stripped.startswith('#'):
            clean = stripped.lstrip('#').strip()
            story.append(Paragraph(f"<b>{clean}</b>", ParagraphStyle('Heading', parent=header_style, fontSize=12, leading=15, alignment=0)))
            story.append(Spacer(1, 6))
        elif stripped.startswith("Total Marks:") or stripped.startswith("Instructions:"):
            story.append(Paragraph(f"<i>{stripped}</i>", sub_header_style))
            story.append(Spacer(1, 4))
        else:
            story.append(Paragraph(stripped, q_style))
            
    doc.build(story)
    print(f"Generated PDF: {pdf_path}")

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sample_dir = os.path.join(base_dir, 'sample_papers')
    
    papers = [
        ('DBMS_2022_EndSem.txt', 'DBMS_2022_EndSem.pdf', 'Database Management Systems - End Sem 2022'),
        ('DBMS_2023_EndSem.txt', 'DBMS_2023_EndSem.pdf', 'Database Management Systems - End Sem 2023'),
        ('DBMS_2024_EndSem.txt', 'DBMS_2024_EndSem.pdf', 'Database Management Systems - End Sem 2024'),
    ]
    
    for txt_name, pdf_name, title in papers:
        t_path = os.path.join(sample_dir, txt_name)
        p_path = os.path.join(sample_dir, pdf_name)
        txt_to_pdf(t_path, p_path, title)

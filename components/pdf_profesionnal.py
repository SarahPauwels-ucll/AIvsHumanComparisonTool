import io
import math
from datetime import date

import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, HRFlowable, Image, TableStyle
)

from components.pdf import make_scaled_image, tooth_image
from components.teeth import get_tooth_image

# Constants
PAGE_W, PAGE_H = letter
SIDE_MARGIN    = 0.5 * inch
TOP_MARGIN     = 0.5 * inch
BOT_MARGIN     = 0.75 * inch
USABLE_WIDTH        = PAGE_W - SIDE_MARGIN * 2
HALF_W         = USABLE_WIDTH / 2

MAX_PANO_H = 3.8 * inch
TOOTH_H_PT = math.floor(0.8 * inch)
RASTER_SCALE = 3 # factor to scale PIL images to make them less blurry
DIFF_IMG_W  = 0.45 * inch


# --- main function ---

def create_pdf_professional(
        patient_id: str,
        patient_name: str,
        scan_date: str,
        birth_date: str,
        age: str,
        gender: str,
        pano_bytes: bytes,
        manual_teeth: dict,
        *,
        top_row: list[int],
        bottom_row: list[int],
) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=SIDE_MARGIN,
        rightMargin=SIDE_MARGIN,
        topMargin=TOP_MARGIN,
        bottomMargin=BOT_MARGIN,
    )

    styles = getSampleStyleSheet()
    center8 = ParagraphStyle("center8", parent=styles["Normal"], fontSize=8, alignment=1)
    header_style = ParagraphStyle("header_style", parent=center8, fontSize=9, fontName='Helvetica-Bold')

    story: list = []

    story.append(Paragraph("Radiology Report", styles["Title"]))

    story.append(Spacer(1, 6))

    patient_id_color = "black"
    patient_name_color = "black"
    scan_date_color = "black"
    birth_date_color = "black"
    age_color = "black"
    gender_color = "black"

    if patient_id == "Unknown":
        patient_id_color = "red"

    if scan_date == "Unknown":
        scan_date_color = "red"

    if age == "Unknown":
        age_color = "red"

    if gender == "Unknown":
        gender_color = "red"

    if birth_date == "Unknown":
        birth_date_color = "red"

    if patient_name == "Unknown":
        patient_name_color = "red"

    # --- patient details ---
    data = [
        [
            Paragraph(f'<b>Patient ID:</b> <font color="{patient_id_color}">{patient_id}</font>', styles['Normal']),
            Paragraph(f'<b>DOB:</b> <font color="{birth_date_color}">{birth_date}</font>', styles['Normal']),
            Paragraph(f'<b>Gender:</b> <font color="{gender_color}">{gender}</font>', styles['Normal']),
        ],
        [
            Paragraph(f'<b>Name:</b> <font color="{patient_name_color}">{patient_name}</font>', styles['Normal']),
            Paragraph(f'<b>Scan date:</b> <font color="{scan_date_color}">{scan_date}</font>', styles['Normal']),
            Paragraph(f'<b>Age:</b> <font color="{age_color}">{age}</font>', styles['Normal']),
        ]
    ]

    table = Table(
        data,
        colWidths=[USABLE_WIDTH / 3.0] * 3,
        hAlign='LEFT',
        spaceBefore=3,
        spaceAfter=12,
    )

    table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('BOX', (0,0), (-1,-1), 1, colors.black),
        # debugging purposes
        #('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ]))

    story.append(table)


    # --- panoramic image ---
    pano1 = make_scaled_image(pano_bytes, max_w=USABLE_WIDTH, max_h=MAX_PANO_H)

    panostable_data = [[pano1]]

    panostable = Table(
        panostable_data,
        colWidths=[USABLE_WIDTH],
        hAlign='CENTER'
    )

    panostable.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(panostable)
    story.append(Spacer(1, 12))

    # --- full mouth teeth lineup ---
    def full_lineup(teeth_map: dict[int, str]):
        rows: list[list] = []
        rows.append([Paragraph(str(n), center8) for n in top_row])
        rows.append([tooth_image(n, teeth_map.get(n, "normal")) for n in top_row])
        rows.append([tooth_image(n, teeth_map.get(n, "normal")) for n in bottom_row])
        rows.append([Paragraph(str(n), center8) for n in bottom_row])

        tbl = Table(rows)
        tbl.setStyle(TableStyle([
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            # keep in case teeth should have black background
            #('BACKGROUND', (0, 1), (-1, 2), colors.black),
        ]))
        return tbl

    manual_tbl = full_lineup(manual_teeth)

    lineups = Table([[manual_tbl]],
                    colWidths=[USABLE_WIDTH],
                    hAlign="CENTER")
    lineups.setStyle(TableStyle([
        ('LINEBEFORE', (1, 0), (1, 0), 0.5, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(lineups)

    # Text
    top_left_row_start = 11
    top_left_row_end = 18
    top_right_row_start = 21
    top_right_row_end = 28

    top_row_present_teeth_left = [
        str(key)
        for key, value in manual_teeth.items()
        if top_left_row_start <= key <= top_left_row_end and (value is None or "normal" in str(value))
    ]
    top_row_present_teeth_right = [
        str(key)
        for key, value in manual_teeth.items()
        if top_right_row_start <= key <= top_right_row_end and (value is None or "normal" in str(value))
    ]

    top_row_present_teeth_left.reverse()
    top_row_present_teeth = top_row_present_teeth_left + top_row_present_teeth_right


    top_row_missing_teeth = [
        str(key)
        for key, value in manual_teeth.items()
        if top_left_row_start <= key <= top_right_row_end and "missing" in str(value)
    ]

    bottom_right_row_start = 31
    bottom_right_row_end = 38
    bottom_left_row_start = 41
    bottom_left_row_end = 48

    bottom_row_present_teeth_right = [
        str(key)
        for key, value in manual_teeth.items()
        if bottom_right_row_start <= key <= bottom_right_row_end and (value is None or "normal" in str(value))
    ]
    bottom_row_present_teeth_left = [
        str(key)
        for key, value in manual_teeth.items()
        if bottom_left_row_start <= key <= bottom_left_row_end and (value is None or "normal" in str(value))
    ]

    bottom_row_present_teeth_left.reverse()
    bottom_row_present_teeth = bottom_row_present_teeth_left + bottom_row_present_teeth_right

    bottom_row_missing_teeth = [
        str(key)
        for key, value in manual_teeth.items()
        if bottom_right_row_start <= key <= bottom_left_row_end and "missing" in str(value)
    ]

    present_teeth_count = len(top_row_present_teeth) + len(bottom_row_present_teeth)
    print(present_teeth_count)
    dental_filling_teeth = [str(key) for key, value in manual_teeth.items() if "df" in str(value)]
    root_canal_filling_teeth = [str(key) for key, value in manual_teeth.items() if "rcf" in str(value)]
    crown_teeth = [str(key) for key, value in manual_teeth.items() if "crown" in str(value)]
    bridge_teeth = [str(key) for key, value in manual_teeth.items() if "bridge" in str(value)]
    implant_teeth = [str(key) for key, value in manual_teeth.items() if "implant" in str(value)]
    impacted_teeth = [str(key) for key, value in manual_teeth.items() if "impacted" in str(value)]
    data = [
        Paragraph(f'The panoramic radiograph reveals {present_teeth_count} teeth are present. The following teeth are present:', styles['Normal']),
        Paragraph(f'Maxilla: {", ".join(top_row_present_teeth) if top_row_present_teeth else "-"}'),
        Paragraph(f'Mandible: {", ".join(bottom_row_present_teeth) if bottom_row_present_teeth else "-"}'),
        Paragraph('The following teeth are missing:'),
        Paragraph(f'Maxilla: {", ".join(top_row_missing_teeth) if top_row_missing_teeth else "-"}'),
        Paragraph(f'Mandible: {", ".join(bottom_row_missing_teeth) if bottom_row_missing_teeth else "-"}'),
        Spacer(1, 12),
        Paragraph(f'Dental fillings are detected in: {", ".join(dental_filling_teeth) if dental_filling_teeth else "-"}'),
        Paragraph(f'Root canal fillings are detected in: {", ".join(root_canal_filling_teeth) if root_canal_filling_teeth else "-"}'),
        Paragraph(f'Crowns are detected in: {", ".join(crown_teeth) if crown_teeth else "-"}'),
        Paragraph(f'Bridges are detected in: {", ".join(bridge_teeth) if bridge_teeth else "-"}'),
        Paragraph(f'Implants are detected in: {",".join(implant_teeth) if implant_teeth else "-"}'),
        Paragraph(f'Impacted teeth are detected in: {", ".join(impacted_teeth) if implant_teeth else "-"}')
    ]

    for paragraph in data:
        story.append(paragraph)

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

# external function
def pdf_button_professional():
    manual_teeth = getattr(st.session_state, 'manual_teeth', {})

    top_row    = list(reversed(range(11,19))) + list(range(21,29))
    bottom_row = list(reversed(range(41,49))) + list(range(31,39))

    # ID
    stored_id = st.session_state.get("profile_number")
    patient_id = stored_id if stored_id else "Unknown"

    # Name
    stored_first_name = st.session_state.get("first_name")
    stored_last_name = st.session_state.get("last_name")
    if stored_first_name and stored_last_name:
        patient_name = f"{stored_first_name} {stored_last_name}"
    else:
        patient_name = "Unknown"

    # Consultation date
    stored_scandate = st.session_state.get("consultation_date")
    if stored_scandate:
        scandate_str = stored_scandate.strftime("%Y-%m-%d") if stored_scandate else ""
    else:
        scandate_str = "Unknown"

    # Age
    stored_birthdate = st.session_state.get("birthdate")
    if stored_birthdate:
        birthdate = stored_birthdate
    else:
        birthdate = "Unknown"

    if stored_birthdate and stored_scandate:
        age = stored_scandate.year - birthdate.year
        if (stored_scandate.month, stored_scandate.day) < (birthdate.month, birthdate.day):
            age -= 1
        age = str(age)
    else:
        age = "Unknown"

    # Gender
    stored_gender = st.session_state.get("gender")
    gender = stored_gender if stored_gender else "Unknown"

    manual_image_bytes = st.session_state["manual_image_bytes"]

    pdf_bytes = create_pdf_professional(
        patient_id=patient_id,
        patient_name=patient_name,
        scan_date=scandate_str,
        birth_date=birthdate,
        age=age,
        gender=gender,
        pano_bytes=manual_image_bytes,
        manual_teeth=manual_teeth,
        top_row=top_row,
        bottom_row=bottom_row,
    )

    st.download_button(
        label="📥 Download Report as PDF",
        data=pdf_bytes,
        file_name="radiology_report.pdf",
        mime="application/pdf",
    )

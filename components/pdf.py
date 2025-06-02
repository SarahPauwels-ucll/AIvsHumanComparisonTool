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
from components.teeth import get_tooth_image

# Constants
PAGE_W, PAGE_H = letter
SIDE_MARGIN    = 0.1 * inch
TOP_MARGIN     = 0.75 * inch
BOT_MARGIN     = 0.75 * inch
USABLE_WIDTH        = PAGE_W - SIDE_MARGIN * 2
HALF_W         = USABLE_WIDTH / 2

MAX_PANO_H = 2.5 * inch
TOOTH_H_PT = math.floor(0.4 * inch)
RASTER_SCALE = 3 # factor to scale PIL images to make them less blurry
DIFF_IMG_W  = 0.45 * inch

# --- helpers ---
def make_scaled_image(source_bytes, *, max_w: float, max_h: float) -> Image:
    source = io.BytesIO(source_bytes)
    img = Image(source)
    iw, ih = float(img.imageWidth), float(img.imageHeight)
    scale = min(max_w/iw, max_h/ih, 1.0)
    img.drawWidth  = iw * scale
    img.drawHeight = ih * scale
    return img

def tooth_image(number: int, status: str, *, height_pt: float = TOOTH_H_PT) -> Image:
    # Generate a PIL image with higher pixel height for crispness
    height_px = int(height_pt * RASTER_SCALE)
    pil = get_tooth_image(number, status, height=height_px, icon_variant="white")

    buf = io.BytesIO()
    pil.save(buf, format="PNG")
    buf.seek(0)

    img = Image(buf)
    # Keep aspect ratio but display at correct height
    iw_px, ih_px = float(img.imageWidth), float(img.imageHeight)
    aspect = iw_px / ih_px or 1.0
    img.drawHeight = height_pt
    img.drawWidth  = height_pt * aspect
    return img


# --- main function ---
def create_pdf(
        patient_id: str,
        scan_date: str,
        age: str,
        gender: str,
        pano1_bytes: bytes,
        pano2_bytes: bytes,
        manual_teeth: dict,
        ai_teeth: dict,
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
    story.append(Spacer(1, 12))

    patient_id_color = "black"
    scan_date_color = "black"
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

    # --- patient details ---
    story.append(Paragraph(
        f'<b> Patient ID: </b><font color="{patient_id_color}"> {patient_id} </font><br/>'
        f'<b> Scan date: </b><font color="{scan_date_color}"> {scan_date} </font><br/>'
        f'<b> Age: </b><font color="{age_color}"> {age} </font><br/>'
        f'<b> Gender: </b><font color="{gender_color}"> {gender} </font><br/>',
        styles["Normal"],
    ))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1))
    story.append(Spacer(1, 12))

    # --- panoramic images ---
    pano1 = make_scaled_image(pano1_bytes, max_w=HALF_W, max_h=MAX_PANO_H)
    pano2 = make_scaled_image(pano2_bytes, max_w=HALF_W, max_h=MAX_PANO_H)

    panostable_data = [[pano1, pano2]]
    panostable = Table(panostable_data,
                       colWidths=[HALF_W, HALF_W],
                       hAlign='CENTER')

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
            ('LINEBEFORE', (8, 0), (8, -1), 0.5, colors.grey),
            ('LINEBELOW', (0, 1), (-1, 1), 0.5, colors.grey),
            # keep in case teeth should have black background
            #('BACKGROUND', (0, 1), (-1, 2), colors.black),
        ]))
        return tbl

    manual_tbl = full_lineup(manual_teeth)
    ai_tbl = full_lineup(ai_teeth)

    lineups = Table([[manual_tbl, ai_tbl]],
                    colWidths=[HALF_W, HALF_W],
                    hAlign="CENTER")
    lineups.setStyle(TableStyle([
        ('LINEBEFORE', (1, 0), (1, 0), 0.5, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(lineups)

    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=1))
    story.append(Spacer(1, 6))

    # --- differences ---
    norm = lambda x: (x or "normal").lower()
    diffs = [n for n in (*top_row, *bottom_row) if norm(manual_teeth.get(n)) != norm(ai_teeth.get(n))]

    norm = lambda x: (x or "normal").lower()
    diffs = [n for n in (*top_row, *bottom_row) if norm(manual_teeth.get(n)) != norm(ai_teeth.get(n))]

    if diffs:
        story.append(Paragraph("Differences", styles["Heading2"]))
        story.append(Spacer(1, 6))  # Spacer after the "Differences" title

        diff_table_data = []

        # Header row
        diff_table_data.append([
            Paragraph("Tooth", header_style),
            Paragraph("Manual", header_style),
            Paragraph("AI", header_style)
        ])

        # Data row
        for n in diffs:
            mn_status = manual_teeth.get(n, "normal")
            ai_status = ai_teeth.get(n, "normal")

            diff_table_data.append([
                Paragraph(str(n), center8),
                tooth_image(n, mn_status, height_pt=TOOTH_H_PT),
                tooth_image(n, ai_status, height_pt=TOOTH_H_PT)
            ])

        id_col_width = 0.7 * inch
        img_col_width = DIFF_IMG_W + 0.2 * inch  # Add tiny amount to not wrap "manual"
        diff_col_widths = [id_col_width, img_col_width, img_col_width]

        diff_table = Table(diff_table_data,
                           colWidths=diff_col_widths,
                           hAlign="LEFT")

        diff_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),

            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
        ]))
        story.append(diff_table)
        story.append(Spacer(1, 12))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

# external function
def pdf_button():
    manual_teeth = getattr(st.session_state, 'manual_teeth', {})
    ai_teeth     = getattr(st.session_state, 'ai_teeth', {})

    top_row    = list(reversed(range(11,19))) + list(range(21,29))
    bottom_row = list(reversed(range(41,49))) + list(range(31,39))

    # ID
    stored_id = st.session_state.get("profile_number")
    patient_id = stored_id if stored_id else "Unknown"

    # Consultation date
    stored_scandate = st.session_state.get("consultation date")
    if stored_scandate:
        scandate_str = stored_scandate.strftime("%Y-%m-%d") if stored_scandate else ""
    else:
        scandate_str = "Unknown"

    # Age
    stored_birthdate = st.session_state.get("birthdate")
    if stored_birthdate:
        birthdate = stored_birthdate
    else:
        birthdate = None

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

    pdf_bytes = create_pdf(
        patient_id=patient_id,
        scan_date=scandate_str,
        age=age,
        gender=gender,
        pano1_bytes=st.session_state["manual_image_bytes"],
        pano2_bytes=st.session_state["AI_image_bytes"],
        manual_teeth=manual_teeth,
        ai_teeth=ai_teeth,
        top_row=top_row,
        bottom_row=bottom_row,
    )

    st.download_button(
        label="📥 Download Report as PDF",
        data=pdf_bytes,
        file_name="radiology_report.pdf",
        mime="application/pdf",
    )
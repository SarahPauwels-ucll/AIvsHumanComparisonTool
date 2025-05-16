import io
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, HRFlowable, Image
)
from teeth import get_tooth_image

def pdf_button():

    def create_pdf(
        patient_id, scan_date, age, gender,
        pano1_path, pano2_path,
        manual_teeth: dict,
        ai_teeth: dict,
        top_row: list,
        bottom_row: list,
        score: int,
        tooth_img_height: int = 80
    ) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=0.5*inch, rightMargin=0.5*inch,
            topMargin=0.75*inch, bottomMargin=0.75*inch,
        )
        styles = getSampleStyleSheet()
        center_small = ParagraphStyle(
            "center_small", parent=styles["Normal"],
            fontSize=8, alignment=1
        )
        story = []

        # --- Header ---
        story.append(Paragraph("Radiology Report", styles["Title"]))
        story.append(Spacer(1, 12))
        info = (
            f"<b>Patient ID:</b> {patient_id}<br/>"
            f"<b>Scan date:</b> {scan_date}<br/>"
            f"<b>Age:</b> {age}<br/>"
            f"<b>Gender:</b> {gender}"
        )
        story.append(Paragraph(info, styles["Normal"]))
        story.append(Spacer(1, 6))
        story.append(HRFlowable(width="100%", thickness=1))
        story.append(Spacer(1, 12))

        # --- Panoramic images side by side ---
        pano1 = Image(pano1_path, width=3.2*inch, height=2.0*inch)
        pano2 = Image(pano2_path, width=3.2*inch, height=2.0*inch)
        story.append(Table(
            [[pano1, pano2]],
            colWidths=[3.75*inch, 3.75*inch],
            hAlign="CENTER"
        ))
        story.append(Spacer(1, 12))

        # --- Full-mouth lineups (manual vs AI) ---
        def full_lineup_table(teeth_dict):
            rows = []
            # top labels
            rows.append([Paragraph(str(n), center_small) for n in top_row])
            # top images
            img_cells = []
            for n in top_row:
                props = teeth_dict.get(n) or "normal"
                pil = get_tooth_image(n, props, height=tooth_img_height)
                buf = io.BytesIO()
                pil.save(buf, format="PNG")
                buf.seek(0)
                img_cells.append(Image(buf, width=0.2*inch, height=0.2*inch))
            rows.append(img_cells)
            # bottom labels
            rows.append([Paragraph(str(n), center_small) for n in bottom_row])
            # bottom images
            img_cells = []
            for n in bottom_row:
                props = teeth_dict.get(n) or "normal"
                pil = get_tooth_image(n, props, height=tooth_img_height)
                buf = io.BytesIO()
                pil.save(buf, format="PNG")
                buf.seek(0)
                img_cells.append(Image(buf, width=0.2*inch, height=0.2*inch))
            rows.append(img_cells)
            return Table(rows, colWidths=[0.2*inch]*len(top_row), hAlign="CENTER")

        manual_table = full_lineup_table(manual_teeth)
        ai_table     = full_lineup_table(ai_teeth)

        story.append(Table(
            [[manual_table, ai_table]],
            colWidths=[3.75*inch, 3.75*inch],
            hAlign="CENTER"
        ))
        story.append(Spacer(1, 12))
        story.append(HRFlowable(width="100%", thickness=1))
        story.append(Spacer(1, 6))

        # --- Differences (if any) ---
        def norm(x): return (x or "normal").lower()
        diffs = [
            n for n in (top_row + bottom_row)
            if norm(manual_teeth.get(n)) != norm(ai_teeth.get(n))
        ]

        if diffs:
            story.append(Paragraph("Differences", styles["Heading2"]))
            diff_rows = []
            for n in diffs:
                mn_p = manual_teeth.get(n) or "normal"
                ai_p = ai_teeth.get(n)     or "normal"
                pil_mn = get_tooth_image(n, mn_p, height=tooth_img_height)
                buf_mn = io.BytesIO()
                pil_mn.save(buf_mn, format="PNG")
                buf_mn.seek(0)
                pil_ai = get_tooth_image(n, ai_p, height=tooth_img_height)
                buf_ai = io.BytesIO()
                pil_ai.save(buf_ai, format="PNG")
                buf_ai.seek(0)
                diff_rows.append([
                    Paragraph(str(n), center_small),
                    Image(buf_mn, width=0.2*inch, height=0.2*inch),
                    Image(buf_ai, width=0.2*inch, height=0.2*inch),
                ])
            story.append(Table(
                diff_rows,
                colWidths=[0.3*inch, 0.5*inch, 0.5*inch],
                hAlign="LEFT"
            ))
            story.append(Spacer(1, 12))

        # --- Score ---
        story.append(Paragraph(f"Score: {score}%", styles["Heading2"]))

        # build PDF
        doc.build(story)
        buf = buffer.getvalue()
        buffer.close()
        return buf


    # ─── Streamlit app ───

    patient_id   = "12345"
    scan_date    = "2025-05-16"
    age          = "45"
    gender       = "F"
    pano1_path   = "image/image.jpeg"
    pano2_path   = "image/image_ai.jpeg"

    manual_teeth = st.session_state.manual_teeth
    ai_teeth     = st.session_state.ai_teeth

    top_row    = list(reversed(range(11,19))) + list(range(21,29))
    bottom_row = list(reversed(range(31,39))) + list(range(41,49))
    score      = 97

    pdf_bytes = create_pdf(
        patient_id, scan_date, age, gender,
        pano1_path, pano2_path,
        manual_teeth, ai_teeth,
        top_row, bottom_row,
        score
    )

    st.download_button(
        label="📥 Download Report as PDF",
        data=pdf_bytes,
        file_name="radiology_report.pdf",
        mime="application/pdf",
    )

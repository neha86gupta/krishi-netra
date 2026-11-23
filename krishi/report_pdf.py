"""Diagnosis PDF (ReportLab). English only: ReportLab cannot shape Devanagari
conjuncts correctly, so a Hindi PDF would be misleading."""
from __future__ import annotations

import io
from datetime import datetime
from xml.sax.saxutils import escape

from PIL import Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Image as RLImage
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from krishi.diagnosis import Diagnosis
from krishi.i18n import t
from krishi.imaging import to_jpeg_bytes
from krishi.knowledge import DiseaseInfo, pretty

FOREST, EMERALD, SAND = colors.HexColor("#14532d"), colors.HexColor("#059669"), colors.HexColor("#f4f1e6")


def _img(img: Image.Image, width_mm: float) -> RLImage:
    w, h = img.size
    ri = RLImage(io.BytesIO(to_jpeg_bytes(img)), width=width_mm * mm, height=width_mm * mm * h / w)
    return ri


def build_report(diag: Diagnosis, original: Image.Image, info: DiseaseInfo | None, when: datetime | None = None) -> bytes:
    when = when or datetime.now()
    ss = getSampleStyleSheet()
    body = ParagraphStyle("b", parent=ss["BodyText"], fontSize=9.5, leading=13)
    h2 = ParagraphStyle("h2", parent=ss["Heading2"], textColor=FOREST, fontSize=12.5, spaceBefore=10, spaceAfter=4)
    small = ParagraphStyle("s", parent=body, fontSize=8, textColor=colors.HexColor("#5b6b5d"))
    P = lambda txt, st=body: Paragraph(escape(txt), st)  # noqa: E731

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=16 * mm, rightMargin=16 * mm, topMargin=14 * mm,
                            bottomMargin=16 * mm, title="Krishi Netra diagnosis report", author="Krishi Netra")
    el = []
    head = Table([[Paragraph('<font color="white" size="19"><b>Krishi Netra</b></font><br/>'
                             '<font color="#d1fae5" size="10">AI-based crop leaf disease detection - diagnosis report</font>', body)]],
                 colWidths=[178 * mm])
    head.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), FOREST), ("LEFTPADDING", (0, 0), (-1, -1), 10),
                              ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 10)]))
    el += [head, Spacer(1, 4), P(f"Generated: {when:%Y-%m-%d %H:%M}", small)]

    status = t(f"st_{diag.status}", "en")
    headline = t("not_sure_head", "en") if diag.is_uncertain else pretty(diag.condition)
    val_status = "Field-Tested (Real Farm Photos, PlantDoc)" if (info and getattr(info, "validation_level", "field_tested") == "field_tested") else "Lab-Validated Only (PlantVillage - Field Test Pending)"
    rows = [["Predicted crop", pretty(diag.crop) if not diag.is_uncertain else f"{pretty(diag.crop)} (best guess)"],
            ["Predicted condition", headline],
            ["Model confidence", f"{diag.confidence:.0%}"],
            ["Prediction status", status],
            ["Validation tier", val_status]]
    tbl = Table([[P(a), P(b)] for a, b in rows], colWidths=[45 * mm, 133 * mm])
    tbl.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cfd8c8")), ("BACKGROUND", (0, 0), (0, -1), SAND),
                             ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    el += [Paragraph("Result", h2), tbl, Spacer(1, 3), P(t("interp_note", "en"), small)]
    if info and getattr(info, "validation_level", "") == "lab_only" and not diag.is_uncertain:
        el.append(P("Notice: This condition is currently validated on laboratory photography only. Outdoor field testing is actively underway.", small))
    if diag.is_uncertain:
        el.append(P(t("low_msg" if diag.status == "low" else "unsure_msg", "en")))

    pics = [[_img(original, 84), _img(diag.cam_overlay, 84) if diag.cam_overlay is not None else P("Grad-CAM not available")],
            [P("Uploaded photo", small), P("Grad-CAM overlay (where the model looked; not a measure of diseased area)", small)]]
    el += [Paragraph("Photograph and Grad-CAM", h2), Table(pics, colWidths=[89 * mm, 89 * mm])]

    top = [["#", "Prediction", "Confidence"]] + [[str(i + 1), f"{pretty(r['crop'])} - {pretty(r['condition'])}", f"{r['prob']:.0%}"]
                                                 for i, r in enumerate(diag.topk[:3])]
    tt = Table([[P(c) for c in row] for row in top], colWidths=[10 * mm, 138 * mm, 30 * mm])
    tt.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), SAND), ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cfd8c8"))]))
    el += [Paragraph("Top 3 predictions", h2), tt]

    el.append(Paragraph("Reference information (static knowledge base - not produced by the AI model)", h2))
    if diag.is_uncertain or info is None:
        el.append(P("No disease-specific information is shown because the model is not sure. " + t("kvk", "en")))
    else:
        if not info.in_kb:
            el.append(P(t("not_in_kb", "en")))
        for label, val in (("Symptoms", info.symptoms), ("Possible cause", info.causal_agent), ("Description", info.description),
                           ("Environmental factors", info.environment), ("Preventive measures", info.prevention),
                           ("General care (by cause group)", info.care)):
            if val:
                el.append(P(f"{label}: {val}"))
        if not info.symptoms:
            el.append(P(t("no_symptoms", "en")))
        for s in info.sources:
            el.append(P(f"Source: {s.get('name', s.get('url', ''))} {s.get('url', '')}", small))
        el += [P(t("no_pesticide", "en")), P(t("kvk", "en"))]

    el += [Spacer(1, 8), P("Disclaimer: " + t("disclaimer", "en") + " " + t("credits", "en"), small)]
    doc.build(el)
    return buf.getvalue()

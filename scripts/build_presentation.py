"""
Refined, Pixel-Perfect Simple & Pleasant SmartParking Presentation.
Updated with Jenkins CI/CD and Kubernetes Container Orchestration slides and screenshots.
Course: SWE4008 - Application Development & Deployment Architecture.
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
import os

# ── Color Palette: Simple, Pleasant, and Modern ─────────────────────────────
BG_PAGE      = RGBColor(0xF8, 0xFA, 0xFC)  # Soft pleasant slate-50
CARD_BG      = RGBColor(0xFF, 0xFF, 0xFF)  # Pure clean white card
CARD_BORDER  = RGBColor(0xE2, 0xE8, 0xF0)  # Slate-200 border
TEXT_MAIN    = RGBColor(0x0F, 0x17, 0x2A)  # Slate-900 (deep navy slate)
TEXT_MUTED   = RGBColor(0x47, 0x55, 0x69)  # Slate-600
TEXT_SUB     = RGBColor(0x64, 0x74, 0x8B)  # Slate-500
PRIMARY_BLUE = RGBColor(0x25, 0x63, 0xEB)  # Royal Blue
BLUE_TINT    = RGBColor(0xEF, 0xF6, 0xFF)  # Blue-50 soft pill tint
EMERALD      = RGBColor(0x05, 0x96, 0x69)  # Emerald-600
EMERALD_TINT = RGBColor(0xEC, 0xFD, 0xF5)  # Emerald-50 soft tint
AMBER        = RGBColor(0xD9, 0x77, 0x06)  # Amber-600
AMBER_TINT   = RGBColor(0xFF, 0xFB, 0xEB)  # Amber-50 tint
PURPLE       = RGBColor(0x7C, 0x3A, 0xED)  # Violet-600
PURPLE_TINT  = RGBColor(0xF5, 0xF3, 0xFF)  # Violet-50 tint

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)
MARGIN_L = Inches(0.8)
CONTENT_W = Inches(11.733)

SCREENSHOTS_DIR = r"c:\Users\sande\Downloads\SmartTraffic\screenshots"

def set_slide_bg(slide, color=BG_PAGE):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_header(slide, title_text, category_badge=None, subtitle_text=None):
    y = Inches(0.42)
    if category_badge:
        pill_w = Inches(len(category_badge) * 0.10 + 0.45)
        pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, MARGIN_L, y, pill_w, Inches(0.28))
        pill.fill.solid()
        pill.fill.fore_color.rgb = BLUE_TINT
        pill.line.color.rgb = PRIMARY_BLUE
        pill.line.width = Pt(1)
        p = pill.text_frame.paragraphs[0]
        p.text = category_badge.upper()
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_BLUE
        p.font.name = "Segoe UI"
        p.alignment = PP_ALIGN.CENTER
        y += Inches(0.35)

    tx = slide.shapes.add_textbox(MARGIN_L, y, CONTENT_W, Inches(0.52))
    tf = tx.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title_text
    p.font.size = Pt(26)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN
    p.font.name = "Segoe UI"

    if subtitle_text:
        y += Inches(0.46)
        tx_sub = slide.shapes.add_textbox(MARGIN_L, y, CONTENT_W, Inches(0.35))
        tf_sub = tx_sub.text_frame
        tf_sub.word_wrap = True
        p_sub = tf_sub.paragraphs[0]
        p_sub.text = subtitle_text
        p_sub.font.size = Pt(12)
        p_sub.font.color.rgb = TEXT_MUTED
        p_sub.font.name = "Segoe UI"

def add_pleasant_card(slide, left, top, width, height, title, body, badge_text=None,
                       accent_color=PRIMARY_BLUE, bg_color=CARD_BG, badge_tint=BLUE_TINT,
                       title_font_size=None):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    card.line.color.rgb = CARD_BORDER
    card.line.width = Pt(1.2)

    content_y = top + Inches(0.22)
    if badge_text:
        badge_w = Inches(len(badge_text) * 0.10 + 0.45)
        b = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                   left + Inches(0.25), content_y, badge_w, Inches(0.28))
        b.fill.solid()
        b.fill.fore_color.rgb = badge_tint
        b.line.fill.background()
        p = b.text_frame.paragraphs[0]
        p.text = badge_text
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = accent_color
        p.font.name = "Segoe UI"
        p.alignment = PP_ALIGN.CENTER
        content_y += Inches(0.36)

    # Estimate if title needs 1 or 2 lines
    is_two_line = len(title) > 20 and width < Inches(3.5)
    actual_font_size = title_font_size or (Pt(13) if is_two_line else Pt(14.5))
    title_h = Inches(0.65) if is_two_line else Inches(0.38)

    tx_t = slide.shapes.add_textbox(left + Inches(0.25), content_y, width - Inches(0.5), title_h)
    tf_t = tx_t.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = title
    p_t.font.size = actual_font_size
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_MAIN
    p_t.font.name = "Segoe UI"

    body_top = content_y + (Inches(0.66) if is_two_line else Inches(0.42))
    body_h = height - (body_top - top) - Inches(0.18)
    if body_h > Inches(0.3):
        tx_b = slide.shapes.add_textbox(left + Inches(0.25), body_top, width - Inches(0.5), body_h)
        tf_b = tx_b.text_frame
        tf_b.word_wrap = True
        p_b = tf_b.paragraphs[0]
        p_b.text = body
        p_b.font.size = Pt(11) if is_two_line else Pt(11.5)
        p_b.font.color.rgb = TEXT_MUTED
        p_b.font.name = "Segoe UI"

    return card

def add_browser_screenshot_slide(prs, blank_layout, title, subtitle, image_filename, badge="LIVE APPLICATION"):
    slide = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide, BG_PAGE)

    add_header(slide, title, category_badge=badge, subtitle_text=subtitle)

    mock_left = Inches(1.2)
    mock_top = Inches(1.85)
    mock_width = Inches(10.93)
    mock_height = Inches(5.15)
    bar_height = Inches(0.36)

    frame = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                   mock_left, mock_top, mock_width, mock_height)
    frame.fill.solid()
    frame.fill.fore_color.rgb = CARD_BG
    frame.line.color.rgb = CARD_BORDER
    frame.line.width = Pt(1.2)

    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                 mock_left, mock_top, mock_width, bar_height)
    bar.fill.solid()
    bar.fill.fore_color.rgb = RGBColor(0xF1, 0xF5, 0xF9)
    bar.line.fill.background()

    dot_y = mock_top + Inches(0.11)
    for i, clr in enumerate([RGBColor(0xEF, 0x44, 0x44), RGBColor(0xF5, 0x9E, 0x0B), RGBColor(0x10, 0xB9, 0x81)]):
        dot = slide.shapes.add_shape(MSO_SHAPE.OVAL,
                                     mock_left + Inches(0.18 + i * 0.18), dot_y, Inches(0.12), Inches(0.12))
        dot.fill.solid()
        dot.fill.fore_color.rgb = clr
        dot.line.fill.background()

    url_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                     mock_left + Inches(0.8), mock_top + Inches(0.06), Inches(4.5), Inches(0.24))
    url_box.fill.solid()
    url_box.fill.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    url_box.line.color.rgb = CARD_BORDER
    url_box.line.width = Pt(1)
    p_url = url_box.text_frame.paragraphs[0]
    p_url.text = "🔒 https://smartparking.local"
    p_url.font.size = Pt(8.5)
    p_url.font.color.rgb = TEXT_SUB
    p_url.font.name = "Segoe UI"

    img_path = os.path.join(SCREENSHOTS_DIR, image_filename)
    if os.path.exists(img_path):
        img_top = mock_top + bar_height
        img_height = mock_height - bar_height
        slide.shapes.add_picture(img_path, mock_left, img_top, width=mock_width, height=img_height)

    return slide

def add_terminal_screenshot_slide(prs, blank_layout, title, subtitle, image_filename, badge="TECHNICAL EVIDENCE"):
    slide = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide, BG_PAGE)

    add_header(slide, title, category_badge=badge, subtitle_text=subtitle)

    img_left = Inches(1.2)
    img_top = Inches(1.85)
    img_width = Inches(10.93)

    img_path = os.path.join(SCREENSHOTS_DIR, image_filename)
    if os.path.exists(img_path):
        slide.shapes.add_picture(img_path, img_left, img_top, width=img_width)

    return slide

def build_presentation():
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    blank = prs.slide_layouts[6]

    # ══════════════════════════════════════════════════════════════════════════
    #   SLIDE 1 — TITLE SLIDE
    # ══════════════════════════════════════════════════════════════════════════
    s1 = prs.slides.add_slide(blank)
    set_slide_bg(s1, BG_PAGE)

    accent_bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), SLIDE_W, Inches(0.1))
    accent_bar.fill.solid()
    accent_bar.fill.fore_color.rgb = PRIMARY_BLUE
    accent_bar.line.fill.background()

    pill1 = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, MARGIN_L, Inches(0.9), Inches(2.8), Inches(0.35))
    pill1.fill.solid()
    pill1.fill.fore_color.rgb = BLUE_TINT
    pill1.line.color.rgb = PRIMARY_BLUE
    pill1.line.width = Pt(1.2)
    p = pill1.text_frame.paragraphs[0]
    p.text = "SMART MOBILITY PLATFORM"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_BLUE
    p.font.name = "Segoe UI"
    p.alignment = PP_ALIGN.CENTER

    tx = s1.shapes.add_textbox(MARGIN_L, Inches(1.4), CONTENT_W, Inches(1.1))
    p = tx.text_frame.paragraphs[0]
    p.text = "SmartParking Platform"
    p.font.size = Pt(44)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN
    p.font.name = "Segoe UI"

    tx2 = s1.shapes.add_textbox(MARGIN_L, Inches(2.45), CONTENT_W, Inches(0.5))
    p2 = tx2.text_frame.paragraphs[0]
    p2.text = "AI-Powered Real-Time Parking Reservation, Jenkins CI Pipeline & Kubernetes Orchestration"
    p2.font.size = Pt(16.5)
    p2.font.color.rgb = TEXT_MUTED
    p2.font.name = "Segoe UI"

    grid_y = Inches(3.55)
    grid_h = Inches(3.0)
    col_w = Inches(2.78)
    gap = Inches(0.2)

    meta = [
        ("COURSE", "SWE4008", "Application Development & Deployment Architecture", PRIMARY_BLUE, BLUE_TINT),
        ("FACULTY", "Faculty Guide", "Prof. Dr. Madala Guru Brahmam Sir", EMERALD, EMERALD_TINT),
        ("SLOT", "L11 + L12", "Winter Semester Laboratory & Project Schedule", AMBER, AMBER_TINT),
        ("STUDENTS", "Project Team", "23MIC7268  •  23MIC7024\n23MIC7063  •  23MIC7255", PURPLE, PURPLE_TINT),
    ]

    for idx, (label, val, sub, clr, tint) in enumerate(meta):
        x = MARGIN_L + idx * (col_w + gap)
        card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, grid_y, col_w, grid_h)
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = CARD_BORDER
        card.line.width = Pt(1.2)

        lbl_box = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x + Inches(0.2), grid_y + Inches(0.22), Inches(1.1), Inches(0.26))
        lbl_box.fill.solid()
        lbl_box.fill.fore_color.rgb = tint
        lbl_box.line.fill.background()
        p_l = lbl_box.text_frame.paragraphs[0]
        p_l.text = label
        p_l.font.size = Pt(9.5)
        p_l.font.bold = True
        p_l.font.color.rgb = clr
        p_l.font.name = "Segoe UI"
        p_l.alignment = PP_ALIGN.CENTER

        tx_val = s1.shapes.add_textbox(x + Inches(0.2), grid_y + Inches(0.62), col_w - Inches(0.4), Inches(0.45))
        p_v = tx_val.text_frame.paragraphs[0]
        p_v.text = val
        p_v.font.size = Pt(18)
        p_v.font.bold = True
        p_v.font.color.rgb = TEXT_MAIN
        p_v.font.name = "Segoe UI"

        tx_sub = s1.shapes.add_textbox(x + Inches(0.2), grid_y + Inches(1.12), col_w - Inches(0.4), Inches(1.6))
        tf_s = tx_sub.text_frame
        tf_s.word_wrap = True
        p_s = tf_s.paragraphs[0]
        p_s.text = sub
        p_s.font.size = Pt(12)
        p_s.font.color.rgb = TEXT_MUTED
        p_s.font.name = "Segoe UI"

    # ══════════════════════════════════════════════════════════════════════════
    #   SLIDE 2 — PROBLEM STATEMENT
    # ══════════════════════════════════════════════════════════════════════════
    s2 = prs.slides.add_slide(blank)
    set_slide_bg(s2, BG_PAGE)
    add_header(s2, "Problem Statement", "URBAN MOBILITY CHALLENGES",
               "Urban parking congestion wastes productive hours, inflates fuel consumption, and creates widespread friction.")

    card_w = Inches(5.7)
    card_h = Inches(2.25)
    problems = [
        ("01", "Severe Traffic Congestion & Fuel Waste",
         "Urban motorists spend an average of 20+ minutes circling commercial corridors seeking an open spot. This cruising accounts for 30% of downtown traffic and substantial unnecessary carbon emissions.",
         PRIMARY_BLUE, BLUE_TINT),
        ("02", "Zero Real-Time Destination Visibility",
         "Drivers leave home with no verifiable information on whether their destination mall, metro terminal, or office deck has available bays, leading to unexpected delays and missed appointments.",
         EMERALD, EMERALD_TINT),
        ("03", "Manual Spreadsheets & Overbooking Conflicts",
         "Commercial parking facilities rely on manual paper tokens and fragmented logs. Lack of centralized synchronization causes double-booking, gate disputes, and lost revenue.",
         AMBER, AMBER_TINT),
        ("04", "Unfair & Rigid Rate Structures",
         "Two-wheelers are routinely charged car-level parking rates, and static fees fail to adapt to live demand peaks, leaving prime bays overcrowded while upper decks sit empty.",
         PURPLE, PURPLE_TINT),
    ]

    for idx, (num, title, desc, clr, tint) in enumerate(problems):
        row = idx // 2
        col = idx % 2
        x = MARGIN_L + col * (card_w + Inches(0.33))
        y = Inches(1.8) + row * (card_h + Inches(0.25))
        add_pleasant_card(s2, x, y, card_w, card_h, title, desc, badge_text=num,
                          accent_color=clr, badge_tint=tint)

    # ══════════════════════════════════════════════════════════════════════════
    #   SLIDE 3 — PROJECT OBJECTIVES
    # ══════════════════════════════════════════════════════════════════════════
    s3 = prs.slides.add_slide(blank)
    set_slide_bg(s3, BG_PAGE)
    add_header(s3, "Project Objectives", "SYSTEM SCOPE & TARGETS",
               "Building a full-stack, deterministic reservation system empowered by transparent AI and enterprise DevOps.")

    objectives = [
        ("01", "Real Google Maps Locations (Zero-Fake Guarantee)",
         "Integrate 49 verified commercial parking complexes across 7 major Indian cities with authentic basement deck slot codes and strict 5 km radius enforcement — no placeholder or synthetic entries.",
         PRIMARY_BLUE, BLUE_TINT),
        ("02", "Explainable AI Proximity-First Ranking",
         "Ensure searched malls prioritize at 0.0 km over distant bus or railway terminals, with normalized scoring across distance, price, real-time availability, and covered/EV perks.",
         EMERALD, EMERALD_TINT),
        ("03", "Calibrated Dynamic Pricing Engine",
         "Implement fair two-wheeler pricing (0.40x multiplier = ₹12/hr for bikes vs ₹30/hr for cars) alongside transparent occupancy demand bands and itemized checkout breakdowns.",
         AMBER, AMBER_TINT),
        ("04", "Enterprise Jenkins CI & Kubernetes CD",
         "Automate parallel unit testing and JUnit reporting with Jenkins, coupled with production-ready Kubernetes orchestration featuring autoscaling, persistent storage, and zero-downtime rollouts.",
         PURPLE, PURPLE_TINT),
    ]

    for idx, (num, title, desc, clr, tint) in enumerate(objectives):
        row = idx // 2
        col = idx % 2
        x = MARGIN_L + col * (card_w + Inches(0.33))
        y = Inches(1.8) + row * (card_h + Inches(0.25))
        add_pleasant_card(s3, x, y, card_w, card_h, title, desc, badge_text=num,
                          accent_color=clr, badge_tint=tint)

    # ══════════════════════════════════════════════════════════════════════════
    #   SLIDE 4 — WHAT IS SMART PARKING?
    # ══════════════════════════════════════════════════════════════════════════
    s4 = prs.slides.add_slide(blank)
    set_slide_bg(s4, BG_PAGE)
    add_header(s4, "What Is SmartParking?", "CORE VALUE PROPOSITIONS",
               "A connected platform serving the complete parking ecosystem with dedicated, role-specific workflows.")

    col3_w = Inches(3.75)
    pillars = [
        ("DRIVERS", "Find & Reserve in Seconds",
         "• 3-letter destination autocomplete\n• Proximity ranking prioritizes exact mall at 0.0 km\n• Authentic basement slots (B1-C01, B1-EV01)\n• Fair pricing: ₹12/hr bikes, ₹30/hr cars\n• Instant digital passes with QR code & status",
         PRIMARY_BLUE, BLUE_TINT),
        ("OPERATORS", "Live Inventory & Yield Control",
         "• Real-time venue occupancy percentage\n• Multi-tier deck slot management & bay blocking\n• Custom operating hours and facility toggles\n• Automated dynamic surge configuration\n• Net revenue recognition & trend analytics",
         EMERALD, EMERALD_TINT),
        ("ADMINS", "System Oversight & Governance",
         "• Commercial parking venue approval lifecycle\n• Complete user oversight (Driver, Operator, Admin)\n• Container health status & scheduler inspection\n• System-wide transaction audit logging\n• Dispute handling & slot unblocking authority",
         PURPLE, PURPLE_TINT),
    ]

    for idx, (badge, title, body, clr, tint) in enumerate(pillars):
        x = MARGIN_L + idx * (col3_w + Inches(0.24))
        add_pleasant_card(s4, x, Inches(1.8), col3_w, Inches(4.7), title, body, badge_text=badge,
                          accent_color=clr, badge_tint=tint)

    # ══════════════════════════════════════════════════════════════════════════
    #   SLIDE 5 — KEY FEATURES
    # ══════════════════════════════════════════════════════════════════════════
    s5 = prs.slides.add_slide(blank)
    set_slide_bg(s5, BG_PAGE)
    add_header(s5, "Key Platform Features", "FUNCTIONAL CAPABILITIES",
               "Engineered for simplicity, reliability, and real-world Indian urban parking requirements.")

    feats = [
        ("01", "Destination Autocomplete", "Triggers suggestions upon entering 3 letters; supports live GPS device detection and map-click pin placement.", PRIMARY_BLUE, BLUE_TINT),
        ("02", "Proximity-First Ranking", "Exact destination malls rank #1 (0.0 km) rather than being displaced by distant bus or train stations.", EMERALD, EMERALD_TINT),
        ("03", "Deck Slot Nomenclature", "Realistic mall basement codes (B1-C01 to B2-C06, B1-EV01, B1-M01) instead of generic single letters.", AMBER, AMBER_TINT),
        ("04", "Calibrated Two-Wheeler Rates", "0.40x multiplier for motorcycles (₹12/hr) vs 1.00x for cars (₹30/hr); transparent itemized billing.", PURPLE, PURPLE_TINT),
        ("05", "Deterministic Hold Pipeline", "10-minute hold window reserves 15-minute slot blocks in MySQL; background worker auto-sweeps unpaid holds.", PRIMARY_BLUE, BLUE_TINT),
        ("06", "Autonomous Preference Engine", "Rule-based background auto-booking evaluated on schedule; fallback forms ensure 100% uptime when AI is offline.", EMERALD, EMERALD_TINT),
    ]

    for idx, (num, title, body, clr, tint) in enumerate(feats):
        row = idx // 3
        col = idx % 3
        x = MARGIN_L + col * (col3_w + Inches(0.24))
        y = Inches(1.8) + row * (Inches(2.25) + Inches(0.25))
        add_pleasant_card(s5, x, y, col3_w, Inches(2.25), title, body, badge_text=num,
                          accent_color=clr, badge_tint=tint)

    # ══════════════════════════════════════════════════════════════════════════
    #   SLIDE 6 — SYSTEM ARCHITECTURE
    # ══════════════════════════════════════════════════════════════════════════
    s6 = prs.slides.add_slide(blank)
    set_slide_bg(s6, BG_PAGE)
    add_header(s6, "System Architecture", "CONTAINERIZED ARCHITECTURE",
               "Clean 5-tier decoupled design: deterministic backend core guarantees 100% booking reliability.")

    tiers = [
        ("TIER 1", "Presentation Layer", "React 18 SPA + Vite, Tailwind CSS, Leaflet OpenStreetMap interactive maps, TanStack Query", PRIMARY_BLUE, BLUE_TINT),
        ("TIER 2", "Reverse Proxy Gateway", "Nginx web server on Port 80: serves production bundle, reverse-proxies /api to FastAPI backend", EMERALD, EMERALD_TINT),
        ("TIER 3", "API & Business Logic", "FastAPI on Python 3.12 (Port 8000), aiomysql raw connection pooling, Pydantic v2 data validation", AMBER, AMBER_TINT),
        ("TIER 4", "AI & Background Workers", "FastAPI ML service (Port 8001), Ollama LLaMA-3.2 (Port 11434), APScheduler worker (hold expiry)", PURPLE, PURPLE_TINT),
        ("TIER 5", "Data & Persistence", "MySQL 8.4 LTS (spatial point geometry, UTC transactions) + Redis 7 Alpine (rate limits & geocode cache)", PRIMARY_BLUE, BLUE_TINT),
    ]

    tier_h = Inches(0.85)
    for idx, (badge, title, desc, clr, tint) in enumerate(tiers):
        y = Inches(1.75) + idx * (tier_h + Inches(0.18))
        add_pleasant_card(s6, MARGIN_L, y, CONTENT_W, tier_h, title, desc, badge_text=badge,
                          accent_color=clr, badge_tint=tint)

    # ══════════════════════════════════════════════════════════════════════════
    #   SLIDE 7 — TECHNOLOGY STACK (UPDATED WITH JENKINS & K8S)
    # ══════════════════════════════════════════════════════════════════════════
    s7 = prs.slides.add_slide(blank)
    set_slide_bg(s7, BG_PAGE)
    add_header(s7, "Technology Stack", "ENGINEERING FOUNDATION",
               "Modern open-source technologies selected for performance, type safety, automated CI, and container orchestration.")

    col4_w = Inches(2.78)
    stacks = [
        ("BACKEND", "FastAPI Backend", "• Python 3.12 & aiomysql pooling\n• Pydantic v2 data schemas\n• PyJWT auth with secure cookies\n• APScheduler background jobs\n• Starlette CORS & rate limits", PRIMARY_BLUE, BLUE_TINT),
        ("FRONTEND", "React 18 SPA", "• Vite & Tailwind CSS utilities\n• Leaflet + OpenStreetMap tiles\n• TanStack React Query cache\n• Lucide / Feather icon sets\n• React Router v6 navigation", EMERALD, EMERALD_TINT),
        ("AI / ML", "AI & ML Services", "• scikit-learn & pandas\n• Weighted candidate ranker\n• Random Forest forecaster\n• Ollama (llama3.2:3b LLM)\n• Resilient circuit breaker", AMBER, AMBER_TINT),
        ("DEVOPS & K8S", "CI/CD & Kubernetes", "• Jenkins Declarative Pipeline\n• Kubernetes (K8s) & Kustomize\n• Horizontal Pod Autoscaler (HPA)\n• 7-Service Docker Architecture\n• MySQL 8.4 LTS & Redis 7", PURPLE, PURPLE_TINT),
    ]

    for idx, (badge, title, body, clr, tint) in enumerate(stacks):
        x = MARGIN_L + idx * (col4_w + Inches(0.2))
        add_pleasant_card(s7, x, Inches(1.8), col4_w, Inches(4.7), title, body, badge_text=badge,
                          accent_color=clr, badge_tint=tint)

    # ══════════════════════════════════════════════════════════════════════════
    #   SLIDE 8 — DETERMINISTIC BOOKING WORKFLOW
    # ══════════════════════════════════════════════════════════════════════════
    s8 = prs.slides.add_slide(blank)
    set_slide_bg(s8, BG_PAGE)
    add_header(s8, "Deterministic Booking Lifecycle", "RESERVATION PIPELINE",
               "Strict hold-and-confirm lifecycle guarantees zero double-bookings with database-enforced row locks.")

    pipe_w = Inches(2.18)
    pipe_gap = Inches(0.2)
    pipeline = [
        ("STEP 1", "Search Venue", "Geocodes query against local registry or OpenStreetMap; enforces 5 km radius.", PRIMARY_BLUE, BLUE_TINT),
        ("STEP 2", "AI Proximity", "Ranks candidate slots; prioritizes destination venue at 0.0 km over distant hubs.", EMERALD, EMERALD_TINT),
        ("STEP 3", "10-Min Hold", "Creates temporary hold; locks 15-minute time intervals in booking_blocks table.", AMBER, AMBER_TINT),
        ("STEP 4", "Pay & Settle", "Checkout via Razorpay test mode; background worker cancels unpaid holds after 10 mins.", PURPLE, PURPLE_TINT),
        ("STEP 5", "Active Pass", "Status updates to CONFIRMED; driver receives active pass with slot code & QR badge.", PRIMARY_BLUE, BLUE_TINT),
    ]

    for idx, (step, title, desc, clr, tint) in enumerate(pipeline):
        x = MARGIN_L + idx * (pipe_w + pipe_gap)
        card = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.8), pipe_w, Inches(4.7))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = CARD_BORDER
        card.line.width = Pt(1.2)

        b = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x + Inches(0.2), Inches(2.05), Inches(0.9), Inches(0.28))
        b.fill.solid()
        b.fill.fore_color.rgb = tint
        b.line.fill.background()
        p = b.text_frame.paragraphs[0]
        p.text = step
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = clr
        p.font.name = "Segoe UI"
        p.alignment = PP_ALIGN.CENTER

        tx_t = s8.shapes.add_textbox(x + Inches(0.2), Inches(2.45), pipe_w - Inches(0.4), Inches(0.6))
        tf_t = tx_t.text_frame
        tf_t.word_wrap = True
        p_t = tf_t.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(14)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_MAIN
        p_t.font.name = "Segoe UI"

        tx_d = s8.shapes.add_textbox(x + Inches(0.2), Inches(3.15), pipe_w - Inches(0.4), Inches(3.0))
        tf_d = tx_d.text_frame
        tf_d.word_wrap = True
        p_d = tf_d.paragraphs[0]
        p_d.text = desc
        p_d.font.size = Pt(11.5)
        p_d.font.color.rgb = TEXT_MUTED
        p_d.font.name = "Segoe UI"

    # ══════════════════════════════════════════════════════════════════════════
    #   SLIDE 9 — DYNAMIC PRICING ENGINE
    # ══════════════════════════════════════════════════════════════════════════
    s9 = prs.slides.add_slide(blank)
    set_slide_bg(s9, BG_PAGE)
    add_header(s9, "Dynamic Pricing & Fair Rate Calibration", "TRANSPARENT BILLING",
               "Proportional vehicle-type multipliers combined with live occupancy surge bands.")

    card_half = Inches(5.7)
    s9_text_a = (
        "• Standard Band (0% – 60% occupancy): 1.00x multiplier (Base rate ₹30/hr for Car)\n\n"
        "• Moderate Band (60% – 85% occupancy): 1.15x multiplier (Fair peak rate ₹34/hr)\n\n"
        "• High Band (85% – 100% occupancy): 1.30x multiplier (Demand cap rate ₹39/hr)\n\n"
        "Surge multipliers are capped at a reasonable 1.30x maximum to prevent exploitative price gouging during high-traffic mall events."
    )
    s9_text_b = (
        "• MOTORCYCLE / TWO-WHEELER: 0.40x multiplier → ₹12/hr (fair authentic rate)\n\n"
        "• CAR / SEDAN / HATCHBACK: 1.00x multiplier → ₹30/hr (standard mall base rate)\n\n"
        "• SUV / LARGE VEHICLE: 1.20x multiplier → ₹36/hr (larger bay consumption)\n\n"
        "• ELECTRIC VEHICLE (EV): 1.10x multiplier → ₹33/hr (with charging access)\n\n"
        "Itemized formula: Total = Duration × Base Rate × Vehicle Discount × Demand Band."
    )

    add_pleasant_card(s9, MARGIN_L, Inches(1.8), card_half, Inches(4.7),
                      "Occupancy Demand Surge Bands", s9_text_a, badge_text="SURGE",
                      accent_color=PRIMARY_BLUE, badge_tint=BLUE_TINT)

    add_pleasant_card(s9, MARGIN_L + card_half + Inches(0.33), Inches(1.8), card_half, Inches(4.7),
                      "Vehicle-Type Multipliers", s9_text_b, badge_text="RATES",
                      accent_color=EMERALD, badge_tint=EMERALD_TINT)

    # ══════════════════════════════════════════════════════════════════════════
    #   SLIDE 10 — REAL GOOGLE MAPS LOCATIONS (NO FAKES)
    # ══════════════════════════════════════════════════════════════════════════
    s10 = prs.slides.add_slide(blank)
    set_slide_bg(s10, BG_PAGE)
    add_header(s10, "Real Google Maps Parking Complexes", "CANONICAL REGISTRY",
               "49 Real Google Maps venues across 7 Indian metro regions — strictly zero synthetic or placeholder locations.")

    cities = [
        ("HYDERABAD (10)", "Inorbit Mall Cyberabad, Nexus Mall (Forum Sujana), Sarath City Capital Mall, GVK One Mall, IKEA, Lulu Mall, Next Galleria Punjagutta, Cyber Towers, DLF Cybercity, Mindspace MLCP.", PRIMARY_BLUE, BLUE_TINT),
        ("VIJAYAWADA & AMARAVATI (5)", "PVP Square Mall Multi-Level, Trendset Mall Benz Circle, Pandit Nehru Bus Station (PNBS) MLCP, Vijayawada Railway West Plaza, Kanaka Durga Temple Ghat Road.", EMERALD, EMERALD_TINT),
        ("BENGALURU (4)", "Phoenix Marketcity Whitefield, Orion Mall Malleshwaram, Nexus Koramangala, Whitefield ITPL Transit.", AMBER, AMBER_TINT),
        ("MUMBAI, NCR, PUNE & CHENNAI (7)", "Inorbit Mall Malad, Phoenix Palladium Lower Parel, Palika Bazar Underground CP, Select CITYWALK Saket, Phoenix Marketcity Pune, Express Avenue Chennai.", PURPLE, PURPLE_TINT),
    ]

    for idx, (city, venues, clr, tint) in enumerate(cities):
        row = idx // 2
        col = idx % 2
        x = MARGIN_L + col * (card_w + Inches(0.33))
        y = Inches(1.8) + row * (card_h + Inches(0.25))
        add_pleasant_card(s10, x, y, card_w, card_h, city, venues, badge_text="CITY",
                          accent_color=clr, badge_tint=tint)

    # ══════════════════════════════════════════════════════════════════════════
    #   SLIDE 11 — ROLE-BASED ACCESS CONTROL (RBAC)
    # ══════════════════════════════════════════════════════════════════════════
    s11 = prs.slides.add_slide(blank)
    set_slide_bg(s11, BG_PAGE)
    add_header(s11, "Role-Based Access Control (RBAC)", "SECURITY & GOVERNANCE",
               "Clean role demarcation with generic account profiles: Driver, Operator, and Admin.")

    roles = [
        ("DRIVER", "Driver User", "driver@test.com",
         "• Search nearby parking across Indian cities\n• Hold, book, pay (Razorpay/venue), & cancel\n• View confirmed passes with Slot Code & QR\n• Configure auto-booking budget & distance rules\n• Access AI Chat conversational parking assistant",
         PRIMARY_BLUE, BLUE_TINT),
        ("OPERATOR", "Operator User", "operator@test.com",
         "• Add and update commercial parking locations\n• Configure deck slots inventory & vehicle types\n• View live bookings & venue occupancy\n• Configure operating hours, amenities, & base rates\n• Track live revenue recognition analytics",
         EMERALD, EMERALD_TINT),
        ("ADMIN", "Admin User", "admin@test.com",
         "• Approve, reject, or suspend commercial venues\n• Full platform user administration (all roles)\n• System-wide occupancy & transaction audit trails\n• Override disputed bookings or blocked slots\n• Inspect Docker container health & scheduler logs",
         PURPLE, PURPLE_TINT),
    ]

    for idx, (role, name, email, perms, clr, tint) in enumerate(roles):
        x = MARGIN_L + idx * (col3_w + Inches(0.24))
        desc = f"Demo Account: {email}\n\n{perms}"
        add_pleasant_card(s11, x, Inches(1.8), col3_w, Inches(4.7), f"{role} ({name})", desc, badge_text="ROLE",
                          accent_color=clr, badge_tint=tint)

    # ══════════════════════════════════════════════════════════════════════════
    #   SLIDE 12 (NEW) — CI/CD & CLOUD DEPLOYMENT ARCHITECTURE
    # ══════════════════════════════════════════════════════════════════════════
    s12 = prs.slides.add_slide(blank)
    set_slide_bg(s12, BG_PAGE)
    add_header(s12, "CI/CD & Cloud Deployment Pipeline", "AUTOMATED DEVOPS",
               "End-to-end continuous integration and deployment pipeline uniting Git, Jenkins, and Kubernetes.")

    cicd_phases = [
        ("PHASE 1", "Git Version Control",
         "• Monorepo housing Frontend, Backend, AI & K8s\n• Feature branch workflow with pull request gates\n• Webhook triggers Jenkins build on code commit\n• Declarative Jenkinsfile tracks pipeline state",
         PRIMARY_BLUE, BLUE_TINT),
        ("PHASE 2", "Jenkins CI Pipeline",
         "• Parallel execution of Backend & AI test suites\n• 14 Pytest assertions validated in isolation\n• Strict JUnit XML reporting (results.xml)\n• Zero-tolerance failure gate stops broken builds",
         EMERALD, EMERALD_TINT),
        ("PHASE 3", "Docker Registry",
         "• Multi-stage production container builds\n• Nginx-optimized SPA frontend artifact\n• Python 3.12 slim images with strict security\n• Version-tagged images pushed to local registry",
         AMBER, AMBER_TINT),
        ("PHASE 4", "Kubernetes CD",
         "• Kustomize manifest validation & dry-run linting\n• Zero-downtime rolling update deployment\n• Health probe verification before traffic cutover\n• Self-healing container restart on failure",
         PURPLE, PURPLE_TINT),
    ]

    for idx, (step, title, desc, clr, tint) in enumerate(cicd_phases):
        x = MARGIN_L + idx * (col4_w + Inches(0.2))
        add_pleasant_card(s12, x, Inches(1.8), col4_w, Inches(4.7), title, desc, badge_text=step,
                          accent_color=clr, badge_tint=tint)

    # ══════════════════════════════════════════════════════════════════════════
    #   SLIDE 13 (NEW) — KUBERNETES PRODUCTION ORCHESTRATION
    # ══════════════════════════════════════════════════════════════════════════
    s13 = prs.slides.add_slide(blank)
    set_slide_bg(s13, BG_PAGE)
    add_header(s13, "Kubernetes Production Orchestration", "CONTAINER ORCHESTRATION",
               "Cloud-native microservices orchestration ensuring high availability, persistence, and autoscaling.")

    k8s_pillars = [
        ("MICROSERVICES", "Deployments & Pod Replicas",
         "• Backend Deployment (3 replicas) handling REST traffic\n• Frontend Deployment (2 replicas) serving Nginx SPA\n• AI-Service Deployment (2 replicas) serving ML ranking\n• Dedicated Single-Replica Worker (APScheduler hold sweeper)\n• RollingUpdate strategy with zero downtime during upgrades",
         PRIMARY_BLUE, BLUE_TINT),
        ("TRAFFIC ROUTING", "Services & Ingress Controller",
         "• ClusterIP Services internalizing DB, Cache, API & AI ports\n• NodePort (30080) for direct cluster edge access\n• Nginx Ingress Controller routing smartparking.local\n• Path-based routing: /api to backend, / to frontend SPA\n• Integrated CORS, request sizing, and header sanitization",
         EMERALD, EMERALD_TINT),
        ("PERSISTENCE", "ConfigMaps, Secrets & PVC",
         "• ConfigMaps injecting environment-specific variables\n• Opaque Secrets protecting DB passwords, JWT & Razorpay keys\n• PersistentVolumeClaim (10Gi mysql-pvc) with ReadWriteOnce\n• Non-volatile MySQL data persistence across pod restarts\n• Redis in-memory storage with AOF persistence",
         AMBER, AMBER_TINT),
        ("RESILIENCE", "Probes & Horizontal Autoscaler (HPA)",
         "• Readiness & Liveness HTTP probes (/health, /api/v1/health)\n• Automatic replacement of unhealthy or crashed pods\n• HorizontalPodAutoscaler (HPA) for Backend (2 to 5 pods)\n• Autoscaling dynamically scales pods on 75% CPU load\n• Resource limits & requests prevent node resource starvation",
         PURPLE, PURPLE_TINT),
    ]

    for idx, (badge, title, desc, clr, tint) in enumerate(k8s_pillars):
        row = idx // 2
        col = idx % 2
        x = MARGIN_L + col * (card_w + Inches(0.33))
        y = Inches(1.8) + row * (card_h + Inches(0.25))
        add_pleasant_card(s13, x, y, card_w, card_h, title, desc, badge_text=badge,
                          accent_color=clr, badge_tint=tint)

    # ══════════════════════════════════════════════════════════════════════════
    #   SLIDE 14 (NEW) — JENKINS CI PIPELINE & TEST AUTOMATION
    # ══════════════════════════════════════════════════════════════════════════
    s14 = prs.slides.add_slide(blank)
    set_slide_bg(s14, BG_PAGE)
    add_header(s14, "Jenkins CI Pipeline & Test Automation", "CONTINUOUS INTEGRATION",
               "Declarative Jenkinsfile pipeline enforcing automated verification, JUnit test reporting, and artifact validation.")

    jenkins_cols = [
        ("DECLARATIVE", "Multi-Stage Execution Pipeline",
         "• Stage 1: Checkout SCM (Git tracking & clean workspace)\n• Stage 2: Parallel Testing (Backend + AI-Service Pytest)\n• Stage 3: JUnit Test Result Archival (test-results/*.xml)\n• Stage 4: Parallel Docker Image Compilation & Tagging\n• Stage 5: Kubernetes Manifest Dry-Run / Validation\n• Stage 6: Kubernetes Continuous Rollout & Status Gate",
         PRIMARY_BLUE, BLUE_TINT),
        ("14 TEST CASES", "Parallel Pytest Suites",
         "• Backend: Password hashing & JWT access token verification\n• Backend: 15-minute slot block interval generator\n• Backend: Vehicle discount rates & pricing clamp logic\n• AI-Service: Random Forest demand forecaster training\n• AI-Service: Heuristic intent parsing (select, confirm, cancel)\n• AI-Service: Min-max ranking normalization & ordering",
         EMERALD, EMERALD_TINT),
        ("JUNIT REPORTING", "Standardized Test Artifacts",
         "• Output: test-results/backend-results.xml (5/5 passed)\n• Output: test-results/ai-results.xml (9/9 passed)\n• Output: test-results/results.xml (14/14 merged)\n• Real-time pass/fail trend graphs in Jenkins dashboard\n• Immediate build failure notification on regression",
         PURPLE, PURPLE_TINT),
    ]

    for idx, (badge, title, body, clr, tint) in enumerate(jenkins_cols):
        x = MARGIN_L + idx * (col3_w + Inches(0.24))
        add_pleasant_card(s14, x, Inches(1.8), col3_w, Inches(4.7), title, body, badge_text=badge,
                          accent_color=clr, badge_tint=tint)

    # ══════════════════════════════════════════════════════════════════════════
    #   SLIDE 15 — SECTION DIVIDER: LIVE APPLICATION & TECHNICAL EVIDENCE
    # ══════════════════════════════════════════════════════════════════════════
    s15 = prs.slides.add_slide(blank)
    set_slide_bg(s15, BG_PAGE)

    pill15 = s15.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.8), Inches(2.2), Inches(3.7), Inches(0.38))
    pill15.fill.solid()
    pill15.fill.fore_color.rgb = BLUE_TINT
    pill15.line.color.rgb = PRIMARY_BLUE
    pill15.line.width = Pt(1.2)
    p = pill15.text_frame.paragraphs[0]
    p.text = "TECHNICAL VERIFICATION & PROOF"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_BLUE
    p.font.name = "Segoe UI"
    p.alignment = PP_ALIGN.CENTER

    tx15 = s15.shapes.add_textbox(MARGIN_L, Inches(2.8), CONTENT_W, Inches(1.0))
    p = tx15.text_frame.paragraphs[0]
    p.text = "Live Application & System Evidence"
    p.font.size = Pt(40)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN
    p.font.name = "Segoe UI"
    p.alignment = PP_ALIGN.CENTER

    tx15_sub = s15.shapes.add_textbox(MARGIN_L, Inches(3.8), CONTENT_W, Inches(0.5))
    p_sub = tx15_sub.text_frame.paragraphs[0]
    p_sub.text = "High-resolution product screenshots captured directly from the running production stack (Port 80 & 8000)"
    p_sub.font.size = Pt(15)
    p_sub.font.color.rgb = TEXT_MUTED
    p_sub.font.name = "Segoe UI"
    p_sub.alignment = PP_ALIGN.CENTER

    # ══════════════════════════════════════════════════════════════════════════
    #   SCREENSHOT SLIDES (SLIDES 16 TO 27) — WEB APP IN BROWSER MOCKUP
    # ══════════════════════════════════════════════════════════════════════════
    web_screens = [
        ("Homepage & Destination Search", "Landing interface featuring instant destination query, vehicle filter, and real-time smart availability metrics.", "01_homepage.png", "DRIVER PORTAL"),
        ("Live Autocomplete Suggestions", "Querying 'Inor' returns verified Google Maps locations: Inorbit Mall Cyberabad Basement and Inorbit Mall Malad.", "02_autocomplete_suggestions.png", "AUTOCOMPLETE"),
        ("Interactive Map & 0.0 km Mall Ranking", "Searching 'Inorbit Mall' prioritizes Inorbit Mall Cyberabad at 0.0 km with interactive Leaflet map markers.", "03_search_results.png", "PROXIMITY SEARCH"),
        ("Authentic Deck Slot Selection", "Displays mall basement slot designations (B1-C01, B1-C02, B1-EV01) with AI score tags and pricing.", "04_slot_selection.png", "SLOT INVENTORY"),
        ("Booking Modal & Rate Breakdown", "Reserving Slot B1-C01 with vehicle number input, time window, itemized billing, and Razorpay payment options.", "05_booking_modal.png", "BOOKING ENGINE"),
        ("Authentication & Role Login", "Clean JWT login screen configured with generic demo accounts: Driver, Operator, and Admin (no personal names).", "06_login_page.png", "SECURITY / AUTH"),
        ("Driver Portal — Confirmed Bookings", "Driver dashboard displaying active confirmed booking at Inorbit Mall (B1-C01) with digital QR badge and status.", "07_driver_my_bookings.png", "DRIVER PASSES"),
        ("Auto-Booking Preference Engine", "Configurable driver rules: preferred vehicle type, max budget, and walking distance for automated commuter matching.", "08_auto_booking_rules.png", "AUTOMATION"),
        ("Operator Dashboard — Analytics", "Commercial operator portal showing live venue occupancy percentage, active slot counts, and net recognized revenue.", "09_operator_dashboard.png", "OPERATOR CONSOLE"),
        ("Operator Facility & Slot Management", "Operators manage approved parking complexes, configure operating hours, amenities, and slot deck codes.", "10_operator_locations.png", "FACILITY MANAGEMENT"),
        ("Admin Panel — Venue & User Oversight", "Administrative console for approving or suspending commercial venues and auditing user accounts.", "11_admin_panel.png", "ADMIN CONSOLE"),
        ("FastAPI Interactive Swagger API Docs", "Interactive OpenAPI documentation running on Port 8000 (/docs), showing all auth, search, and booking routes.", "12_api_swagger.png", "SWAGGER API DOCS"),
    ]

    for title, subtitle, img, badge in web_screens:
        add_browser_screenshot_slide(prs, blank, title, subtitle, img, badge=badge)

    # ══════════════════════════════════════════════════════════════════════════
    #   SCREENSHOT SLIDES (SLIDES 28 TO 32) — TERMINAL WINDOWS (STANDALONE)
    # ══════════════════════════════════════════════════════════════════════════
    term_screens = [
        ("Docker Compose 7-Service Architecture", "PowerShell terminal showing all 7 containerized services running healthy: frontend, backend, worker, ai, ollama, mysql, redis.", "13_docker_containers.png", "CONTAINER ARCHITECTURE"),
        ("Database Verification — Canonical Malls", "Direct MySQL query output verifying 49 approved Google Maps complexes and authentic basement slot configurations.", "14_canonical_mysql_terminal.png", "MYSQL DATABASE"),
        ("Automated Test Suite (8/8 Passed)", "Full test suite execution verifying health, real suggestions, 5 km boundary enforcement, two-wheeler discounts, and hold-confirm.", "15_end_to_end_verification.png", "QUALITY ASSURANCE"),
        ("Jenkins CI Pipeline & JUnit Reports", "PowerShell terminal showing Jenkins test execution across Backend and AI-Service with 14/14 tests passed.", "16_jenkins_ci_pipeline.png", "JENKINS CI/CD"),
        ("Kubernetes Manifests & Kustomize Dry-Run", "PowerShell terminal validating Kubernetes Kustomize build, ClusterIP/NodePort Services, HPA, and Ingress dry-run.", "17_kubernetes_manifests.png", "KUBERNETES CD"),
    ]

    for title, subtitle, img, badge in term_screens:
        add_terminal_screenshot_slide(prs, blank, title, subtitle, img, badge=badge)

    # ══════════════════════════════════════════════════════════════════════════
    #   SLIDE 33 — RESULTS AND EVIDENCE
    # ══════════════════════════════════════════════════════════════════════════
    s33 = prs.slides.add_slide(blank)
    set_slide_bg(s33, BG_PAGE)
    add_header(s33, "Results and Evidence", "VERIFIED METRICS",
               "Key quantitative indicators and empirical verification from the running deployment.")

    metrics = [
        ("49", "Real Google Maps Venues", "Approved complexes across 7 major metro cities", PRIMARY_BLUE, BLUE_TINT),
        ("637", "Deck Slots Configured", "Authentic basement codes (B1-C01, B1-EV01, B1-M01)", EMERALD, EMERALD_TINT),
        ("14 / 14", "Pytest Suites Passing", "100% tests passed across Backend and AI-Service", AMBER, AMBER_TINT),
        ("9", "K8s Manifest Resources", "Complete Kustomize suite with HPA autoscaling", PURPLE, PURPLE_TINT),
    ]

    for idx, (num, label, sub, clr, tint) in enumerate(metrics):
        x = MARGIN_L + idx * (col4_w + Inches(0.2))
        card = s33.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.8), col4_w, Inches(1.6))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = CARD_BORDER
        card.line.width = Pt(1.2)

        tx_num = s33.shapes.add_textbox(x + Inches(0.15), Inches(1.9), col4_w - Inches(0.3), Inches(0.6))
        p_n = tx_num.text_frame.paragraphs[0]
        p_n.text = num
        p_n.font.size = Pt(32)
        p_n.font.bold = True
        p_n.font.color.rgb = clr
        p_n.font.name = "Segoe UI"

        tx_lbl = s33.shapes.add_textbox(x + Inches(0.15), Inches(2.5), col4_w - Inches(0.3), Inches(0.8))
        tf_l = tx_lbl.text_frame
        tf_l.word_wrap = True
        p_l = tf_l.paragraphs[0]
        p_l.text = f"{label}\n{sub}"
        p_l.font.size = Pt(11)
        p_l.font.color.rgb = TEXT_MUTED
        p_l.font.name = "Segoe UI"

    add_pleasant_card(
        s33, MARGIN_L, Inches(3.65), CONTENT_W, Inches(2.85),
        "Key Empirical Verification Highlights",
        "• Jenkins Declarative CI: Automated multi-stage pipeline executes parallel pytest suites for Backend and AI-Service, generating standardized JUnit XML reports (14/14 tests passed, 0 failures).\n\n"
        "• Kubernetes Orchestration: 9 production K8s manifests compiled cleanly via Kustomize; validated with client dry-run, HPA autoscaling (2-5 pods at 75% CPU), and self-healing health probes.\n\n"
        "• Proximity Mall Priority: Searching 'Inorbit Mall' returns Inorbit Mall Cyberabad at 0.0 km (₹30/hr, slot B1-C01) ahead of distant bus or railway stations.\n\n"
        "• Fair Two-Wheeler Rate: Searching with vehicle_type=MOTORCYCLE applies 0.40x multiplier → ₹12/hr for slot B1-M01.\n\n"
        "• Deterministic Core: Slot hold, 15-minute block constraints, and Razorpay checkout verified end-to-end with Booking ID 15 CONFIRMED.",
        badge_text="AUDIT",
        accent_color=PRIMARY_BLUE,
        badge_tint=BLUE_TINT
    )

    # ══════════════════════════════════════════════════════════════════════════
    #   SLIDE 34 — CONCLUSION
    # ══════════════════════════════════════════════════════════════════════════
    s34 = prs.slides.add_slide(blank)
    set_slide_bg(s34, BG_PAGE)
    add_header(s34, "Conclusion", "PROJECT SUMMARY",
               "SmartParking bridges urban mobility friction with transparent AI, fair pricing, and enterprise cloud DevOps.")

    concl = [
        ("01", "Authentic & Real-World", "49 verified Google Maps landmarks, authentic mall basement deck nomenclature, and fair rate calibration for Indian cities.", PRIMARY_BLUE, BLUE_TINT),
        ("02", "Intelligent & Adaptive", "Proximity-first ranking algorithm, commuter auto-booking, and demand-aware surge multipliers up to a safe 1.30x cap.", EMERALD, EMERALD_TINT),
        ("03", "CI/CD & Cloud Orchestrated", "Automated Jenkins declarative pipeline with parallel JUnit test gates, coupled with production-ready Kubernetes manifests and HPA autoscaling.", PURPLE, PURPLE_TINT),
        ("04", "Deterministic Reliability", "Decoupled 7-service architecture guarantees 100% search and booking uptime even during external AI or payment downtime.", AMBER, AMBER_TINT),
    ]

    for idx, (num, title, body, clr, tint) in enumerate(concl):
        row = idx // 2
        col = idx % 2
        x = MARGIN_L + col * (card_w + Inches(0.33))
        y = Inches(1.8) + row * (card_h + Inches(0.25))
        add_pleasant_card(s34, x, y, card_w, card_h, title, body, badge_text=num,
                          accent_color=clr, badge_tint=tint)

    # ══════════════════════════════════════════════════════════════════════════
    #   SLIDE 35 — QUESTIONS & ANSWERS
    # ══════════════════════════════════════════════════════════════════════════
    s35 = prs.slides.add_slide(blank)
    set_slide_bg(s35, BG_PAGE)

    pill35 = s35.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.5), Inches(2.2), Inches(2.3), Inches(0.38))
    pill35.fill.solid()
    pill35.fill.fore_color.rgb = BLUE_TINT
    pill35.line.color.rgb = PRIMARY_BLUE
    pill35.line.width = Pt(1.2)
    p = pill35.text_frame.paragraphs[0]
    p.text = "PROJECT DEFENSE"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_BLUE
    p.font.name = "Segoe UI"
    p.alignment = PP_ALIGN.CENTER

    tx35 = s35.shapes.add_textbox(MARGIN_L, Inches(2.8), CONTENT_W, Inches(1.0))
    p = tx35.text_frame.paragraphs[0]
    p.text = "Questions & Answers"
    p.font.size = Pt(44)
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN
    p.font.name = "Segoe UI"
    p.alignment = PP_ALIGN.CENTER

    tx35_sub = s35.shapes.add_textbox(MARGIN_L, Inches(3.9), CONTENT_W, Inches(0.5))
    p_sub = tx35_sub.text_frame.paragraphs[0]
    p_sub.text = "Thank You for Your Time & Attention"
    p_sub.font.size = Pt(20)
    p_sub.font.color.rgb = PRIMARY_BLUE
    p_sub.font.bold = True
    p_sub.font.name = "Segoe UI"
    p_sub.alignment = PP_ALIGN.CENTER

    tx35_foot = s35.shapes.add_textbox(MARGIN_L, Inches(4.6), CONTENT_W, Inches(0.4))
    p_f = tx35_foot.text_frame.paragraphs[0]
    p_f.text = "SmartParking Platform  •  Course SWE4008  •  Slot L11 + L12"
    p_f.font.size = Pt(14)
    p_f.font.color.rgb = TEXT_SUB
    p_f.font.name = "Segoe UI"
    p_f.alignment = PP_ALIGN.CENTER

    out_file = r"C:\Users\sande\Downloads\SmartTraffic\SmartParking_Presentation.pptx"
    prs.save(out_file)
    print(f"Refined Presentation with Jenkins & K8s generated successfully at: {out_file}")

if __name__ == "__main__":
    build_presentation()

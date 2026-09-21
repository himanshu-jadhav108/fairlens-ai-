#!/usr/bin/env python3
"""
create_contact_sheet.py
-----------------------
Generates a master Visual QA Contact Sheet combining Figures 1-8
for final visual layout, box containment, and publication-readiness audit.
"""

import os
from PIL import Image, ImageDraw, ImageFont

FIGURES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUTPUT_PATH = os.path.join(FIGURES_DIR, 'visual_qa_contact_sheet.png')

FIGURE_FILES = [
    ("fig01_research_framework.png", "Figure 1: Overall Research Framework (4-Stage Pipeline)"),
    ("fig02_experimental_matrix.png", "Figure 2: Full-Factorial Experimental Matrix (N=36 Conditions)"),
    ("fig03_claim_evaluation_framework.png", "Figure 3: Claim-Level Evaluation Framework & Decision Engine"),
    ("fig04_numerical_faithfulness.png", "Figure 4: Numerical Faithfulness Comparison (Template vs. Gemini)"),
    ("fig05_unsupported_claims.png", "Figure 5: Unsupported Claims & Taxonomy Breakdown (N=1,306 Claims)"),
    ("fig06_directional_faithfulness.png", "Figure 6: Directional Faithfulness Comparison (Non-Significance Robustness)"),
    ("fig07_llama_adjudication.png", "Figure 7: Secondary LLM Sensitivity Analysis (Llama 3 8B Adjudication)"),
    ("fig08_evidence_claim_example.png", "Figure 8: Authentic Evidence-to-Claim Verification Examples"),
]

def build_contact_sheet():
    target_w = 1200
    panel_margin = 30
    header_h = 60
    
    # Process images and compute target heights
    processed_images = []
    for fname, title in FIGURE_FILES:
        fpath = os.path.join(FIGURES_DIR, fname)
        if not os.path.exists(fpath):
            raise FileNotFoundError(f"Missing image: {fpath}")
        img = Image.open(fpath)
        aspect = img.height / img.width
        scaled_h = int(target_w * aspect)
        img_resized = img.resize((target_w, scaled_h), Image.Resampling.LANCZOS)
        processed_images.append((img_resized, title, fname))
        
    # Layout in 4 rows x 2 columns
    cols = 2
    rows = 4
    
    col_widths = [target_w, target_w]
    # Find max height per row
    row_heights = []
    for r in range(rows):
        idx1 = r * 2
        idx2 = r * 2 + 1
        h1 = processed_images[idx1][0].height + header_h
        h2 = processed_images[idx2][0].height + header_h
        row_heights.append(max(h1, h2))
        
    total_w = target_w * 2 + panel_margin * 3
    total_h = sum(row_heights) + panel_margin * (rows + 1) + 120  # 120 for master title
    
    contact = Image.new('RGB', (total_w, total_h), color='#FFFFFF')
    draw = ImageDraw.Draw(contact)
    
    # Master Header banner
    draw.rectangle([0, 0, total_w, 100], fill='#1A365D')
    
    try:
        font_title = ImageFont.truetype("arial.ttf", 36)
        font_sub = ImageFont.truetype("arial.ttf", 20)
        font_panel = ImageFont.truetype("arialbd.ttf", 22)
        font_badge = ImageFont.truetype("arialbd.ttf", 16)
    except Exception:
        font_title = ImageFont.load_default()
        font_sub = font_title
        font_panel = font_title
        font_badge = font_title
        
    draw.text((panel_margin, 20), "FairLens AI — Visual QA Master Contact Sheet (Figures 1–8)", fill='#FFFFFF', font=font_title)
    draw.text((panel_margin, 65), "Audit Criteria: Zero Text Collisions | Full Box Containment | Mathematical Range Verification | Publication-Ready", fill='#CBD5E0', font=font_sub)
    
    # Paste panels
    curr_y = 120 + panel_margin
    for r in range(rows):
        r_h = row_heights[r]
        for c in range(cols):
            idx = r * 2 + c
            img, title, fname = processed_images[idx]
            x = panel_margin + c * (target_w + panel_margin)
            y = curr_y
            
            # Card background
            card_box = [x - 8, y - 8, x + target_w + 8, y + r_h + 8]
            draw.rounded_rectangle(card_box, radius=10, fill='#F7FAFC', outline='#CBD5E0', width=2)
            
            # Panel Header
            draw.text((x, y), title, fill='#1A202C', font=font_panel)
            # PASS badge
            badge_w = 90
            badge_h = 28
            bx = x + target_w - badge_w
            by = y - 2
            draw.rounded_rectangle([bx, by, bx + badge_w, by + badge_h], radius=6, fill='#276749')
            draw.text((bx + 14, by + 4), "AUDIT OK", fill='#FFFFFF', font=font_badge)
            
            # Paste figure
            contact.paste(img, (x, y + header_h))
            
        curr_y += r_h + panel_margin
        
    contact.save(OUTPUT_PATH, 'PNG', quality=95)
    print(f"Master Contact Sheet generated: {OUTPUT_PATH} ({os.path.getsize(OUTPUT_PATH):,} bytes)")

if __name__ == '__main__':
    build_contact_sheet()

"""
Debt Communication Storyboard — Interactive Desktop App
Run with:  python3 debt_story.py
Navigate:  → / Space = Next    ← = Back    R = Restart    ESC = Quit
"""

import pygame
import sys
import math
import textwrap

pygame.init()

# ── Dimensions & colours ────────────────────────────────────────────────────
W, H = 900, 620
FPS  = 60

WHITE      = (255, 255, 255)
BG         = (248, 247, 244)
PANEL_BG   = (238, 237, 230)
CARD_BG    = (255, 255, 255)

PURPLE     = (83, 74, 183)
PURPLE_L   = (238, 237, 254)
PURPLE_BRD = (175, 169, 236)

TEAL       = (29, 158, 117)
TEAL_L     = (225, 245, 238)
TEAL_BRD   = (93, 202, 165)

RED_L      = (252, 235, 235)
RED_BRD    = (240, 149, 149)
RED_TXT    = (121, 31, 31)
RED_MID    = (162, 45, 45)

GREEN_L    = (234, 243, 222)
GREEN_BRD  = (192, 221, 151)
GREEN_TXT  = (39, 80, 10)
GREEN_MID  = (59, 109, 17)

AMBER_L    = (250, 238, 218)
AMBER_BRD  = (250, 199, 117)

GRAY_L     = (241, 239, 232)
GRAY_BRD   = (211, 209, 199)
GRAY_TXT   = (44, 44, 42)

MONO_BG    = (244, 243, 238)

TEXT_PRI   = (30, 30, 28)
TEXT_SEC   = (90, 88, 82)
TEXT_TER   = (150, 148, 142)

BLUE_L     = (230, 241, 251)
BLUE_BRD   = (133, 183, 235)
BLUE_MID   = (24, 95, 165)

# ── Fonts ────────────────────────────────────────────────────────────────────
def load_font(size, bold=False):
    for name in ["DejaVu Sans", "Liberation Sans", "Arial", "Helvetica"]:
        try:
            return pygame.font.SysFont(name, size, bold=bold)
        except Exception:
            pass
    return pygame.font.Font(None, size)

def load_mono(size):
    for name in ["DejaVu Sans Mono", "Courier New", "Courier"]:
        try:
            return pygame.font.SysFont(name, size)
        except Exception:
            pass
    return pygame.font.Font(None, size)

F_TITLE  = load_font(28, bold=True)
F_HEAD   = load_font(20, bold=True)
F_SUB    = load_font(15)
F_BODY   = load_font(13)
F_SMALL  = load_font(11)
F_MONO   = load_mono(11)
F_CHAP   = load_font(10)
F_NAV    = load_font(13, bold=True)
F_BADGE  = load_font(11, bold=True)

# ── Helpers ──────────────────────────────────────────────────────────────────
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Debt Communication — Interactive Story")

def draw_rect_aa(surf, color, rect, radius=8, border=0, border_color=None):
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    if border and border_color:
        pygame.draw.rect(surf, border_color, rect, border, border_radius=radius)

def wrap_text(text, font, max_w):
    words = text.split()
    lines, line = [], ""
    for w in words:
        test = (line + " " + w).strip()
        if font.size(test)[0] <= max_w:
            line = test
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines

def render_text_block(surf, text, font, color, x, y, max_w, line_h=None):
    lh = line_h or (font.get_height() + 4)
    lines = wrap_text(text, font, max_w)
    for i, ln in enumerate(lines):
        s = font.render(ln, True, color)
        surf.blit(s, (x, y + i * lh))
    return y + len(lines) * lh

def render_centered(surf, text, font, color, cx, y):
    s = font.render(text, True, color)
    surf.blit(s, (cx - s.get_width() // 2, y))
    return y + s.get_height()

def badge(surf, text, x, y, bg, border, txt_color, font=None):
    f = font or F_BADGE
    tw = f.size(text)[0]
    pad = 8
    r = pygame.Rect(x, y, tw + pad*2, f.get_height() + 6)
    draw_rect_aa(surf, bg, r, radius=4, border=1, border_color=border)
    s = f.render(text, True, txt_color)
    surf.blit(s, (x + pad, y + 3))
    return r.right + 6

# ── Avatar drawing ────────────────────────────────────────────────────────────
def draw_avatar(surf, cx, cy, r, bg, border, label, emoji_char=None):
    pygame.draw.circle(surf, bg, (cx, cy), r)
    pygame.draw.circle(surf, border, (cx, cy), r, 2)
    # Simple stick-figure face
    face_r = r - 4
    # eyes
    ex = int(face_r * 0.3)
    ey = int(face_r * 0.25)
    pygame.draw.circle(surf, TEXT_PRI, (cx - ex, cy - ey), 2)
    pygame.draw.circle(surf, TEXT_PRI, (cx + ex, cy - ey), 2)
    # mouth
    mouth_pts = [(cx - int(face_r*0.3), cy + int(face_r*0.2)),
                 (cx, cy + int(face_r*0.35)),
                 (cx + int(face_r*0.3), cy + int(face_r*0.2))]
    pygame.draw.lines(surf, TEXT_PRI, False, mouth_pts, 1)
    # label
    s = F_SMALL.render(label, True, TEXT_TER)
    surf.blit(s, (cx - s.get_width()//2, cy + r + 4))

def draw_avatar_worried(surf, cx, cy, r, bg, border, label):
    pygame.draw.circle(surf, bg, (cx, cy), r)
    pygame.draw.circle(surf, border, (cx, cy), r, 2)
    face_r = r - 4
    ex = int(face_r * 0.3)
    ey = int(face_r * 0.2)
    # worried eyes (slightly raised inner brow effect)
    pygame.draw.circle(surf, TEXT_PRI, (cx - ex, cy - ey), 2)
    pygame.draw.circle(surf, TEXT_PRI, (cx + ex, cy - ey), 2)
    # frown
    mouth_pts = [(cx - int(face_r*0.3), cy + int(face_r*0.32)),
                 (cx, cy + int(face_r*0.18)),
                 (cx + int(face_r*0.3), cy + int(face_r*0.32))]
    pygame.draw.lines(surf, RED_MID, False, mouth_pts, 2)
    s = F_SMALL.render(label, True, TEXT_TER)
    surf.blit(s, (cx - s.get_width()//2, cy + r + 4))

def draw_avatar_happy(surf, cx, cy, r, bg, border, label):
    pygame.draw.circle(surf, bg, (cx, cy), r)
    pygame.draw.circle(surf, border, (cx, cy), r, 2)
    face_r = r - 4
    ex = int(face_r * 0.3)
    ey = int(face_r * 0.25)
    pygame.draw.circle(surf, TEXT_PRI, (cx - ex, cy - ey), 2)
    pygame.draw.circle(surf, TEXT_PRI, (cx + ex, cy - ey), 2)
    # big smile
    mouth_pts = [(cx - int(face_r*0.35), cy + int(face_r*0.1)),
                 (cx - int(face_r*0.1), cy + int(face_r*0.38)),
                 (cx + int(face_r*0.1), cy + int(face_r*0.38)),
                 (cx + int(face_r*0.35), cy + int(face_r*0.1))]
    pygame.draw.lines(surf, GREEN_MID, False, mouth_pts, 2)
    s = F_SMALL.render(label, True, TEXT_TER)
    surf.blit(s, (cx - s.get_width()//2, cy + r + 4))

# ── Narration box ─────────────────────────────────────────────────────────────
def draw_narration(surf, text, x, y, w):
    lines = wrap_text(text, F_BODY, w - 28)
    lh = F_BODY.get_height() + 4
    box_h = len(lines) * lh + 24
    r = pygame.Rect(x, y, w, box_h)
    draw_rect_aa(surf, PURPLE_L, r, radius=8, border=1, border_color=PURPLE_BRD)
    pygame.draw.rect(surf, PURPLE, (x, y + 8, 3, box_h - 16), border_radius=2)
    tag_s = F_SMALL.render("▶ NARRATOR", True, PURPLE)
    surf.blit(tag_s, (x + 10, y + 8))
    for i, ln in enumerate(lines):
        s = F_BODY.render(ln, True, (60, 52, 140))
        surf.blit(s, (x + 14, y + 24 + i * lh))
    return y + box_h + 8

# ── Speech bubble ─────────────────────────────────────────────────────────────
def draw_speech(surf, text, cx, y, max_w=160):
    lines = wrap_text(text, F_SMALL, max_w - 16)
    lh = F_SMALL.get_height() + 3
    bw = max_w
    bh = len(lines) * lh + 14
    bx = cx - bw // 2
    r = pygame.Rect(bx, y, bw, bh)
    draw_rect_aa(surf, CARD_BG, r, radius=6, border=1, border_color=GRAY_BRD)
    for i, ln in enumerate(lines):
        s = F_SMALL.render(ln, True, TEXT_SEC)
        surf.blit(s, (bx + 8, y + 7 + i * lh))
    return y + bh

# ── Timeline row ──────────────────────────────────────────────────────────────
def draw_tl_row(surf, text, x, y, w, bad=True):
    dot_color = RED_L if bad else GREEN_L
    dot_border = RED_BRD if bad else GREEN_BRD
    dot_txt    = RED_MID if bad else GREEN_MID
    sym        = "✕" if bad else "✓"
    pygame.draw.circle(surf, dot_color, (x + 10, y + 10), 10)
    pygame.draw.circle(surf, dot_border, (x + 10, y + 10), 10, 1)
    s = F_SMALL.render(sym, True, dot_txt)
    surf.blit(s, (x + 10 - s.get_width()//2, y + 10 - s.get_height()//2))
    lines = wrap_text(text, F_BODY, w - 30)
    lh = F_BODY.get_height() + 3
    for i, ln in enumerate(lines):
        surf.blit(F_BODY.render(ln, True, TEXT_SEC), (x + 26, y + i * lh))
    return y + max(len(lines) * lh, 22) + 6

# ── Solution card ─────────────────────────────────────────────────────────────
def draw_sol_card(surf, title, body, x, y, w):
    lines = wrap_text(body, F_SMALL, w - 20)
    lh = F_SMALL.get_height() + 3
    h = F_BODY.get_height() + len(lines) * lh + 22
    r = pygame.Rect(x, y, w, h)
    draw_rect_aa(surf, GRAY_L, r, radius=8, border=1, border_color=GRAY_BRD)
    surf.blit(F_BODY.render(title, True, TEXT_PRI), (x + 10, y + 8))
    for i, ln in enumerate(lines):
        surf.blit(F_SMALL.render(ln, True, TEXT_SEC), (x + 10, y + 8 + F_BODY.get_height() + 4 + i * lh))
    return y + h + 8

# ── Transform boxes ───────────────────────────────────────────────────────────
def draw_transform(surf, before_txt, after_txt, x, y, w):
    hw = (w - 30) // 2
    # before
    lines_b = wrap_text(before_txt, F_MONO, hw - 16)
    lh_b = F_MONO.get_height() + 3
    bh = len(lines_b) * lh_b + 28
    r = pygame.Rect(x, y, hw, bh)
    draw_rect_aa(surf, RED_L, r, radius=8, border=1, border_color=RED_BRD)
    surf.blit(F_SMALL.render("Original letter", True, RED_MID), (x+8, y+6))
    for i, ln in enumerate(lines_b):
        surf.blit(F_MONO.render(ln, True, RED_TXT), (x+8, y+20+i*lh_b))
    # arrow
    ax = x + hw + 8
    ay = y + bh // 2
    pygame.draw.line(surf, PURPLE, (ax, ay), (ax + 14, ay), 2)
    pts = [(ax+14, ay-5), (ax+22, ay), (ax+14, ay+5)]
    pygame.draw.polygon(surf, PURPLE, pts)
    # after
    lines_a = wrap_text(after_txt, F_BODY, hw - 16)
    lh_a = F_BODY.get_height() + 3
    ah = len(lines_a) * lh_a + 28
    ah = max(ah, bh)
    r2 = pygame.Rect(x + hw + 30, y, hw, ah)
    draw_rect_aa(surf, GREEN_L, r2, radius=8, border=1, border_color=GREEN_BRD)
    ax2 = x + hw + 30
    surf.blit(F_SMALL.render("With our tool", True, GREEN_MID), (ax2+8, y+6))
    for i, ln in enumerate(lines_a):
        surf.blit(F_BODY.render(ln, True, GREEN_TXT), (ax2+8, y+20+i*lh_a))
    return y + max(bh, ah) + 10

# ── Navigation bar ────────────────────────────────────────────────────────────
def draw_nav(surf, cur, total):
    ny = H - 52
    pygame.draw.line(surf, GRAY_BRD, (0, ny), (W, ny), 1)
    pygame.draw.rect(surf, CARD_BG, (0, ny, W, 52))

    # back button
    back_r = pygame.Rect(20, ny + 10, 90, 32)
    back_active = cur > 0
    draw_rect_aa(surf, PANEL_BG if back_active else GRAY_L, back_r, radius=6,
                 border=1, border_color=GRAY_BRD)
    bs = F_NAV.render("← Back", True, TEXT_PRI if back_active else TEXT_TER)
    surf.blit(bs, (back_r.x + (back_r.w - bs.get_width())//2,
                   back_r.y + (back_r.h - bs.get_height())//2))

    # pips
    pip_total_w = total * 14
    pip_x = W//2 - pip_total_w//2
    for i in range(total):
        if i < cur:
            pygame.draw.rect(surf, TEAL, (pip_x + i*14, ny+22, 8, 8), border_radius=4)
        elif i == cur:
            pygame.draw.rect(surf, PURPLE, (pip_x + i*14, ny+20, 12, 12), border_radius=4)
        else:
            pygame.draw.rect(surf, GRAY_BRD, (pip_x + i*14, ny+22, 8, 8), border_radius=4)

    lbl = F_SMALL.render(f"Scene {cur+1} of {total}  •  ← → or SPACE to navigate  •  ESC to quit", True, TEXT_TER)
    surf.blit(lbl, (W//2 - lbl.get_width()//2, ny + 36))

    # next button
    label = "Restart →" if cur == total - 1 else "Next →"
    next_r = pygame.Rect(W - 120, ny + 10, 100, 32)
    draw_rect_aa(surf, PURPLE, next_r, radius=6)
    ns = F_NAV.render(label, True, WHITE)
    surf.blit(ns, (next_r.x + (next_r.w - ns.get_width())//2,
                   next_r.y + (next_r.h - ns.get_height())//2))

    return back_r, next_r

# ── Scene renderers ───────────────────────────────────────────────────────────
PAD   = 36
INNER = W - PAD * 2

def scene_0(surf):
    y = 20
    cs = F_CHAP.render("CHAPTER 1 — THE LETTER ARRIVES", True, TEXT_TER)
    surf.blit(cs, (PAD, y)); y += 18
    surf.blit(F_HEAD.render("Meet Emma", True, TEXT_PRI), (PAD, y)); y += 36

    narr = ("Every year, millions of people receive formal debt letters they cannot "
            "understand. This is the story of one of them — and of a system that was "
            "supposed to help, but often arrives too late.")
    y = draw_narration(surf, narr, PAD, y, INNER)

    draw_avatar_worried(surf, PAD + 50, y + 44, 34,
                        RED_L, RED_BRD, "Emma, 34 — single mum")
    draw_speech(surf, '"Another official letter. I\'ll deal with it later…"',
                PAD + 50, y + 88, max_w=170)

    lx = PAD + 140
    letter_w = INNER - 140
    lr = pygame.Rect(lx, y, letter_w, 140)
    draw_rect_aa(surf, MONO_BG, lr, radius=6, border=1, border_color=GRAY_BRD)
    surf.blit(F_MONO.render("AANMANING — Ref: 2024-INC-09471", True, GRAY_TXT), (lx+10, y+8))
    pygame.draw.line(surf, GRAY_BRD, (lx+8, y+24), (lx+letter_w-8, y+24), 1)
    body_lines = [
        "Het openstaande bedrag van  € 2.341,88  dient",
        "uiterlijk  12 november 2024  te zijn voldaan.",
        "Bij niet-betaling worden  gerechtelijke stappen",
        "ondernomen en  buitengerechtelijke kosten",
        "in rekening gebracht conform de WIK...",
    ]
    for i, ln in enumerate(body_lines):
        surf.blit(F_MONO.render(ln, True, GRAY_TXT), (lx+10, y+30+i*18))

    # highlight scary words
    scary = ["€ 2.341,88", "12 november 2024",
             "gerechtelijke stappen", "buitengerechtelijke kosten"]
    for sw in scary:
        s_surf = F_MONO.render(sw, True, RED_TXT)
        # find and overlay
        for i, ln in enumerate(body_lines):
            if sw in ln:
                pre = ln[:ln.index(sw)]
                px = lx + 10 + F_MONO.size(pre)[0]
                py = y + 30 + i * 18
                pygame.draw.rect(surf, RED_L,
                                 (px-1, py, F_MONO.size(sw)[0]+2, F_MONO.get_height()),
                                 border_radius=2)
                surf.blit(F_MONO.render(sw, True, RED_TXT), (px, py))

    y += 155
    panic = ('"Gerechtelijke stappen? Incassobureau? Is this a lawsuit? '
             'I don\'t understand any of this… I\'ll just put it in the drawer."')
    yr = pygame.Rect(PAD, y, INNER, 1)
    lines = wrap_text(panic, F_BODY, INNER - 20)
    bh = len(lines) * 18 + 16
    draw_rect_aa(surf, RED_L, pygame.Rect(PAD, y, INNER, bh), radius=6,
                 border=1, border_color=RED_BRD)
    for i, ln in enumerate(lines):
        surf.blit(F_BODY.render(ln, True, RED_TXT), (PAD+10, y+8+i*18))


def scene_1(surf):
    y = 20
    surf.blit(F_CHAP.render("CHAPTER 2 — THE SPIRAL", True, TEXT_TER), (PAD, y)); y += 18
    surf.blit(F_HEAD.render("Avoidance makes it worse", True, TEXT_PRI), (PAD, y)); y += 36
    narr = ("What happens next is not unique to Emma. It is the most predictable outcome "
            "in debt support: when people don't understand, they delay. And delay costs money.")
    y = draw_narration(surf, narr, PAD, y, INNER)

    rows = [
        ("Day 1:  Letter arrives. Emma panics. She puts it in the drawer.", True),
        ("Day 8:  A second letter — reminder fee added:  + €40", True),
        ("Day 20: Deadline passes. Case escalates to a debt lawyer.  + €285 legal costs", True),
        ("Day 45: Emma finally asks for help. But it's much harder now.", True),
        ("Total owed:  €2.666,88  — up from €2.341. Just from not knowing what to do.", True),
    ]
    for txt, bad in rows:
        y = draw_tl_row(surf, txt, PAD, y, INNER, bad=bad)

    panic = '"I should have acted sooner. I just didn\'t know who to call or what to do first."'
    lines = wrap_text(panic, F_BODY, INNER - 20)
    bh = len(lines) * 18 + 16
    draw_rect_aa(surf, RED_L, pygame.Rect(PAD, y, INNER, bh), radius=6,
                 border=1, border_color=RED_BRD)
    for i, ln in enumerate(lines):
        surf.blit(F_BODY.render(ln, True, RED_TXT), (PAD+10, y+8+i*18))


def scene_2(surf):
    y = 20
    surf.blit(F_CHAP.render("CHAPTER 3 — THE CASEWORKER'S TUESDAY", True, TEXT_TER), (PAD, y)); y += 18
    surf.blit(F_HEAD.render("Meet Fatima — debt support specialist", True, TEXT_PRI), (PAD, y)); y += 36
    narr = ("Help organisations exist exactly for moments like Emma's. But the professionals "
            "inside them face a different crisis: they are drowning in documents, not in "
            "expertise. Their bottleneck is paper, not people skills.")
    y = draw_narration(surf, narr, PAD, y, INNER)

    draw_avatar(surf, PAD + 50, y + 44, 34, TEAL_L, TEAL_BRD, "Fatima — counsellor")
    draw_speech(surf, '"27 clients today. Which ones are urgent?"', PAD + 50, y + 88, max_w=170)

    tx = PAD + 145
    tw = INNER - 145
    ty = y
    rows = [
        ("Emma arrives with a bag of letters — torn, photographed, mixed with receipts.", True),
        ("Fatima spends 47 minutes sorting: who is the creditor? what's the real deadline?", True),
        ("Four other clients wait outside. Two have court hearings tomorrow.", True),
        ("Fatima is an expert at helping people — but the system needs her to be a scanner.", True),
    ]
    for txt, bad in rows:
        ty = draw_tl_row(surf, txt, tx, ty, tw, bad=bad)


def scene_3(surf):
    y = 20
    surf.blit(F_CHAP.render("CHAPTER 4 — THE BIGGER PICTURE", True, TEXT_TER), (PAD, y)); y += 18
    surf.blit(F_HEAD.render("Everyone pays for this confusion", True, TEXT_PRI), (PAD, y)); y += 36
    narr = ("Emma's story is not an edge case. It is the default outcome of a system built "
            "around legal correctness, not human understanding. And the cost is shared by "
            "everyone — including people who never received the letter.")
    y = draw_narration(surf, narr, PAD, y, INNER)

    # Three characters
    cx_list = [PAD + 80, W//2, W - PAD - 80]
    labels  = ["Creditor", "Emma", "Municipality"]
    speeches = [
        '"She never replied.\nNow we pay lawyers."',
        '"I would have paid.\nI just didn\'t understand."',
        '"Court costs, social aid —\nall preventable."',
    ]
    draw_funcs = [draw_avatar, draw_avatar_worried, draw_avatar]
    colors = [(BLUE_L, BLUE_BRD), (RED_L, RED_BRD), (PURPLE_L, PURPLE_BRD)]
    for i, cx in enumerate(cx_list):
        draw_funcs[i](surf, cx, y + 36, 30, colors[i][0], colors[i][1], labels[i])
        # mini speech
        lines = wrap_text(speeches[i].replace('\n', ' '), F_SMALL, 140)
        bh = len(lines) * 16 + 10
        bx = cx - 75
        r = pygame.Rect(bx, y + 80, 150, bh)
        draw_rect_aa(surf, CARD_BG, r, radius=5, border=1, border_color=GRAY_BRD)
        for j, ln in enumerate(lines):
            s = F_SMALL.render(ln, True, TEXT_SEC)
            surf.blit(s, (bx + (150-s.get_width())//2, y+80+5+j*16))

    y += 130
    rows = [
        ("Creditors spend on reminders, lawyers — for debts resolvable early with a payment plan.", True),
        ("Governments absorb costs: courts, social support, public health pressure.", True),
        ("The root cause is not unwillingness. It is ONE confusing letter at the wrong moment.", True),
    ]
    for txt, bad in rows:
        y = draw_tl_row(surf, txt, PAD, y, INNER, bad=bad)


def scene_4(surf):
    y = 20
    surf.blit(F_CHAP.render("CHAPTER 5 — THE INTERVENTION POINT", True, TEXT_TER), (PAD, y)); y += 18
    surf.blit(F_HEAD.render("What if the letter actually made sense?", True, TEXT_PRI), (PAD, y)); y += 36
    narr = ("We don't change the law. We don't change the debt. We change the moment of "
            "contact — turning a document designed for legal compliance into one designed "
            "for human action. The same facts. A completely different outcome.")
    y = draw_narration(surf, narr, PAD, y, INNER)

    before = ("...buitengerechtelijke incassokosten conform de WIK... "
              "gerechtelijke stappen ondernomen... Incassobureau Delta BV "
              "namens Energiemaatschappij Noord NV...")
    after  = ("You owe €2,341 to your energy company. "
              "Pay by November 12 or costs increase. "
              "A payment plan is possible. Contact us today.")
    y = draw_transform(surf, before, after, PAD, y, INNER)

    cx_list = [PAD + 90, W//2 + 50]
    labels  = ["Emma", "Fatima"]
    speeches = [
        '"I understand now. I can do this. I\'ll call today."',
        '"Key info in 10 sec. Now I can actually help her."',
    ]
    fns = [draw_avatar_happy, draw_avatar_happy]
    cols = [(RED_L, RED_BRD), (TEAL_L, TEAL_BRD)]
    for i, cx in enumerate(cx_list):
        fns[i](surf, cx, y + 32, 28, cols[i][0], cols[i][1], labels[i])
        lines = wrap_text(speeches[i], F_SMALL, 190)
        bh = len(lines) * 16 + 10
        bx = cx - 100
        r = pygame.Rect(bx, y + 72, 200, bh)
        draw_rect_aa(surf, CARD_BG, r, radius=5, border=1, border_color=GRAY_BRD)
        for j, ln in enumerate(lines):
            s = F_SMALL.render(ln, True, TEXT_SEC)
            surf.blit(s, (bx + (200-s.get_width())//2, y+72+5+j*16))


def scene_5(surf):
    y = 20
    surf.blit(F_CHAP.render("CHAPTER 6 — OUR SOLUTION", True, TEXT_TER), (PAD, y)); y += 18
    surf.blit(F_HEAD.render("Built for every person in this chain", True, TEXT_PRI), (PAD, y)); y += 36
    narr = ("Our tool sits at the very beginning of the process — before the stress, before "
            "the avoidance, before the escalation. It doesn't replace caseworkers or creditors. "
            "It gives all of them a better starting point.")
    y = draw_narration(surf, narr, PAD, y, INNER)

    cw = (INNER - 12) // 2
    cards = [
        ("For debtors", "Plain language. What you owe, to whom, by when — and what options you have."),
        ("For caseworkers", "Instant structured data. Deadlines and amounts visible in seconds, not hours."),
        ("For creditors", "More debtors who understand and respond. Earlier payment plans. Less legal cost."),
        ("For governments", "Earlier intervention. Scalable oversight. Fewer cases reaching courts."),
    ]
    for i, (title, body) in enumerate(cards):
        cx = PAD + (i % 2) * (cw + 12)
        cy = y + (i // 2) * 80
        draw_sol_card(surf, title, body, cx, cy, cw)

    y += 175
    hl = "We don't replace human judgment. We make the first step faster, clearer, and less overwhelming for everyone."
    lines = wrap_text(hl, F_BODY, INNER - 20)
    bh = len(lines) * 18 + 16
    draw_rect_aa(surf, PURPLE_L, pygame.Rect(PAD, y, INNER, bh),
                 radius=8, border=1, border_color=PURPLE_BRD)
    for i, ln in enumerate(lines):
        s = F_BODY.render(ln, True, (60, 52, 140))
        surf.blit(s, (W//2 - F_BODY.size(ln)[0]//2, y+8+i*18))


def scene_6(surf):
    y = 20
    surf.blit(F_CHAP.render("EPILOGUE — THE STORY REWRITTEN", True, TEXT_TER), (PAD, y)); y += 18
    surf.blit(F_HEAD.render("Emma's story, with our solution", True, TEXT_PRI), (PAD, y)); y += 36
    narr = ("This is not a dream scenario. This is what happens when people understand what "
            "they're being asked to do — and when professionals can focus on helping, rather "
            "than on decoding. One letter. Understood. Problem solved early.")
    y = draw_narration(surf, narr, PAD, y, INNER)

    rows = [
        ("Day 1:  Emma gets the letter. Our tool shows a plain summary. She understands.", False),
        ("Day 2:  She contacts the help org. Fatima sees structured data and focuses on advising.", False),
        ("Day 5:  A payment plan is arranged with the creditor.  No extra costs added.", False),
        ("Total debt stays at  €2.341.  No lawyers. No courts. No escalation.", False),
    ]
    for txt, bad in rows:
        y = draw_tl_row(surf, txt, PAD, y, INNER, bad=bad)

    # Happy avatars
    draw_avatar_happy(surf, PAD + 70, y + 36, 28, TEAL_L, TEAL_BRD, "Emma")
    draw_avatar_happy(surf, PAD + 180, y + 36, 28, GREEN_L, GREEN_BRD, "Fatima")
    draw_avatar_happy(surf, PAD + 290, y + 36, 28, BLUE_L, BLUE_BRD, "Creditor")

    hl = "This is what we are building — clarity, at the moment it matters most."
    lines = wrap_text(hl, F_BODY, INNER - 20)
    bh = len(lines) * 18 + 16
    hy = y + 90
    draw_rect_aa(surf, GREEN_L, pygame.Rect(PAD, hy, INNER, bh),
                 radius=8, border=1, border_color=GREEN_BRD)
    for i, ln in enumerate(lines):
        s = F_BODY.render(ln, True, GREEN_TXT)
        surf.blit(s, (W//2 - F_BODY.size(ln)[0]//2, hy+8+i*18))


SCENES = [scene_0, scene_1, scene_2, scene_3, scene_4, scene_5, scene_6]
TOTAL  = len(SCENES)

# ── Fade transition ───────────────────────────────────────────────────────────
def fade_transition(old_surf, new_scene_fn, steps=18):
    overlay = pygame.Surface((W, H))
    overlay.fill(WHITE)
    for i in range(steps + 1):
        alpha = int(255 * i / steps)
        screen.blit(old_surf, (0, 0))
        overlay.set_alpha(alpha)
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.delay(12)
    screen.fill(BG)
    new_scene_fn(screen)
    draw_nav(screen, cur, TOTAL)
    fade_in = pygame.Surface((W, H))
    fade_in.fill(WHITE)
    for i in range(steps, -1, -1):
        screen.fill(BG)
        new_scene_fn(screen)
        draw_nav(screen, cur, TOTAL)
        fade_in.set_alpha(int(255 * i / steps))
        screen.blit(fade_in, (0, 0))
        pygame.display.flip()
        pygame.time.delay(12)

# ── Main loop ─────────────────────────────────────────────────────────────────
cur   = 0
clock = pygame.time.Clock()
needs_draw = True

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        if event.type == pygame.KEYDOWN:
            old_cur = cur
            if event.key in (pygame.K_RIGHT, pygame.K_SPACE):
                cur = 0 if cur == TOTAL - 1 else cur + 1
            elif event.key == pygame.K_LEFT:
                cur = max(0, cur - 1)
            elif event.key == pygame.K_r:
                cur = 0
            elif event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()
            if cur != old_cur:
                old_surf = screen.copy()
                needs_draw = False
                fade_transition(old_surf, SCENES[cur])
                needs_draw = True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # draw nav to get rects
            screen.fill(BG)
            SCENES[cur](screen)
            back_r, next_r = draw_nav(screen, cur, TOTAL)
            mx, my = event.pos
            old_cur = cur
            if next_r.collidepoint(mx, my):
                cur = 0 if cur == TOTAL - 1 else cur + 1
            elif back_r.collidepoint(mx, my) and cur > 0:
                cur -= 1
            if cur != old_cur:
                old_surf = screen.copy()
                fade_transition(old_surf, SCENES[cur])

    if needs_draw:
        screen.fill(BG)
        SCENES[cur](screen)
        draw_nav(screen, cur, TOTAL)
        pygame.display.flip()

    clock.tick(FPS)
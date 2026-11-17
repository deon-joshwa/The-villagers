# P5 pitch asset: render the OFFICIAL YuE2 "Text to Music" ComfyUI node graph
# from the official workflow JSON (audio_yue2_text2music.json, Comfy-Org/workflow_templates).
# No invented nodes, positions, or widget values -- everything is read from the JSON.
#
# Run:  python pitch/render_nodegraph.py
# Out:  pitch/slide1_yue2_comfyui_nodegraph.png

import json
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
WF = os.path.join(HERE, "audio_yue2_text2music.json")
OUT = os.path.join(HERE, "slide1_yue2_comfyui_nodegraph.png")

SCALE = 0.60            # world -> pixels
PAD = 70                # canvas padding (px)
TITLE_H = 34            # node title bar height (px)
SLOT_GAP = 22           # vertical spacing between slots (px)
NODE_W_MIN = 150        # minimum node body width (px)

WIRE_COLORS = {
    "AUDIO": (236, 100, 165), "CLIP": (255, 214, 66), "CONDITIONING": (176, 106, 255),
    "STRING": (110, 214, 120), "FLOAT": (80, 200, 230), "INT": (90, 170, 250),
    "COMBO": (200, 200, 200), "*": (170, 170, 170),
}
NODE_FILL = (28, 30, 40)
NODE_EDGE = (90, 96, 120)
TITLE_COLORS = {
    "YuE2GenerateABC": (150, 60, 30), "YuE2GenerateMusic": (150, 60, 30),
    "KSampler": (60, 90, 150), "CheckpointLoaderSimple": (80, 120, 70),
}

try:
    F_TITLE = ImageFont.truetype("segoeuib.ttf", 17)
    F_BODY = ImageFont.truetype("consola.ttf", 14)
    F_CAP = ImageFont.truetype("segoeuib.ttf", 30)
    F_CAP2 = ImageFont.truetype("segoeui.ttf", 22)
except OSError:
    F_TITLE = F_BODY = F_CAP = F_CAP2 = ImageFont.load_default()


def world(x):
    return x * SCALE + PAD


def widget_lines(node):
    named = node.get("widgets_values_named")
    if not named:
        return []
    lines = []
    for k, v in named.items():
        s = str(v).replace("\n", " \\n ")
        lines.append("%s: %s" % (k, s))
    return lines[:9]


def main():
    d = json.load(open(WF, encoding="utf-8"))
    sg = d["definitions"]["subgraphs"][0]
    nodes = sg["nodes"]
    links = sg["links"]

    xs = [p for n in nodes for p in (n["pos"][0], n["pos"][0] + n["size"][0])]
    ys = [p for n in nodes for p in (n["pos"][1], n["pos"][1] + n["size"][1])]
    W = int((max(xs) - min(xs)) * SCALE) + 2 * PAD
    H = int((max(ys) - min(ys)) * SCALE) + 2 * PAD + 120

    ox, oy = min(xs), min(ys)
    img = Image.new("RGB", (W, H), (16, 17, 24))
    dr = ImageDraw.Draw(img)

    # banner
    dr.text((PAD, 18), 'Official YuE2 "Text to Music" ComfyUI workflow (%d nodes, JSON rendered)'
            % len(nodes), font=F_CAP, fill=(240, 240, 250))
    dr.text((PAD, 58), "Source: Comfy-Org/workflow_templates - audio_yue2_text2music.json   |   "
            "This is what an indie game dev faces.", font=F_CAP2, fill=(255, 120, 120))

    def nx(n, x):
        return (x - ox) * SCALE + PAD

    def ny(n, y):
        return (y - oy) * SCALE + PAD + 120

    # ---- wires first (under the boxes)
    by_id = {n["id"]: n for n in nodes}
    for lk in links:
        lid, a, aslot, b, bslot, typ = lk["id"], lk["origin_id"], lk["origin_slot"], lk["target_id"], lk["target_slot"], lk["type"]
        na, nb = by_id.get(a), by_id.get(b)
        if not na or not nb:
            continue
        x1 = nx(na, na["pos"][0] + na["size"][0])
        y1 = ny(na, na["pos"][1]) + TITLE_H + aslot * SLOT_GAP + 12
        x2 = nx(nb, nb["pos"][0])
        y2 = ny(nb, nb["pos"][1]) + TITLE_H + bslot * SLOT_GAP + 12
        c = WIRE_COLORS.get(typ, (170, 170, 170))
        mid = (x1 + x2) / 2
        dr.line(
            [(x1, y1), (mid, y1), (mid, y2), (x2, y2)],
            fill=c, width=3, joint="curve")

    # ---- node boxes
    for n in nodes:
        x, y = nx(n, n["pos"][0]), ny(n, n["pos"][1])
        w = max(int(n["size"][0] * SCALE), NODE_W_MIN)
        lines = widget_lines(n)
        h = TITLE_H + len(lines) * 19 + max(len(n.get("inputs", [])), len(n.get("outputs", []))) * SLOT_GAP + 10
        h = max(h, int(n["size"][1] * SCALE), 56)
        tc = TITLE_COLORS.get(n["type"], (70, 74, 96))
        dr.rounded_rectangle([x, y, x + w, y + h], 8, fill=NODE_FILL, outline=NODE_EDGE, width=2)
        dr.rounded_rectangle([x, y, x + w, y + TITLE_H], 8, fill=tc)
        dr.rectangle([x, y + TITLE_H - 10, x + w, y + TITLE_H], fill=tc)
        dr.text((x + 8, y + 7), "#%s %s" % (n["id"], n["type"]), font=F_TITLE, fill=(255, 255, 255))
        ty = y + TITLE_H + 4
        for i, inp in enumerate(n.get("inputs", [])):
            iy = ty + i * SLOT_GAP
            dr.ellipse([x - 4, iy + 5, x + 4, iy + 13], fill=WIRE_COLORS.get(inp.get("type"), (170, 170, 170)))
            dr.text((x + 8, iy + 2), "in: %s" % inp["name"], font=F_BODY, fill=(150, 155, 175))
        for i, out in enumerate(n.get("outputs", [])):
            iy = ty + i * SLOT_GAP
            dr.ellipse([x + w - 4, iy + 5, x + w + 4, iy + 13], fill=WIRE_COLORS.get(out.get("type"), (170, 170, 170)))
            txt = "out: %s" % out["name"]
            tw = dr.textlength(txt, font=F_BODY)
            dr.text((x + w - tw - 8, iy + 2), txt, font=F_BODY, fill=(150, 155, 175))
        for j, line in enumerate(lines):
            # truncate to the node body width so nothing overflows
            while len(line) > 4 and dr.textlength(line, font=F_BODY) > w - 16:
                line = line[:-4] + "..."
            dr.text((x + 8, ty + max(len(n.get("inputs", [])), len(n.get("outputs", []))) * SLOT_GAP + j * 19 + 2),
                    line, font=F_BODY, fill=(215, 220, 235))

    img.save(OUT)
    print("saved", OUT, img.size)


if __name__ == "__main__":
    main()

"""
generate_asset_guide.py — Exports a complete catalog of image names, descriptions,
and exact renaming formats for all 100 Course Lessons and Tech Facts.
"""
import json
import os

CURRICULUM_PATH = "curriculum.json"
FACTS_PATH = "tech_facts.json"

with open(CURRICULUM_PATH, "r", encoding="utf-8") as f:
    curriculum = json.load(f)

with open(FACTS_PATH, "r", encoding="utf-8") as f:
    facts = json.load(f)

lines = []
lines.append("# 🖼️ Complete Image Catalog & Renaming Guide")
lines.append("## 100 Days CS Course + Tech Fun Facts\n")
lines.append("### 📁 Supported Formats: `.jpg`, `.jpeg`, `.png`, `.webp`, `.avif`, `.bmp`, `.tiff`\n")
lines.append("---")
lines.append("### 📚 Part 1: 100 Days Computer Science Course\n")

for t in curriculum.get("topics", []):
    day = t.get("day")
    tid = t.get("id")
    title = t.get("title")
    module = t.get("module")
    tags = ", ".join(t.get("tags", []))
    
    lines.append(f"#### **Day {day}: {title}** (`{tid}`)")
    lines.append(f"- **Module**: {module}")
    lines.append(f"- **Recommended Visuals**:")
    lines.append(f"  - Image 1 (Overview / Intro): `{tid}_1.jpg` (or `day{day}_1.png`) ➔ *High-level overview of {title}*")
    lines.append(f"  - Image 2 (Core Detail / Mechanism): `{tid}_2.jpg` (or `day{day}_2.webp`) ➔ *Close-up internal detail/diagram of {title}*")
    lines.append(f"  - Image 3 (Real-world Application): `{tid}_3.jpg` (or `day{day}_3.jpeg`) ➔ *Practical application / setup related to {tags}*")
    lines.append(f"- **Folder Option**: `assets/custom_vault/day{day}/` or `assets/custom_vault/{tid}/`")
    lines.append("")

lines.append("\n---\n### 💡 Part 2: Viral Tech Fun Facts\n")
for f in facts.get("facts", []):
    num = f.get("number")
    fid = f.get("id")
    title = f.get("title")
    hook = f.get("hook")
    
    lines.append(f"#### **Fact #{num}: {title}** (`{fid}`)")
    lines.append(f"- **Hook**: {hook}")
    lines.append(f"- **Recommended Visuals**:")
    lines.append(f"  - Image 1: `{fid}_1.jpg` (or `fact{num}_1.png`) ➔ *Historical or concept photo representing '{title}'*")
    lines.append(f"  - Image 2: `{fid}_2.jpg` (or `fact{num}_2.webp`) ➔ *Detailed shot or comparison visual*")
    lines.append(f"- **Folder Option**: `assets/custom_vault/fact{num}/` or `assets/custom_vault/{fid}/`")
    lines.append("")

with open("IMAGE_ASSET_GUIDE.md", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("Created IMAGE_ASSET_GUIDE.md successfully!")

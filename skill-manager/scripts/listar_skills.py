#!/usr/bin/env python3
"""
Lista as skills do projeto (.agents/skills/) e aponta possíveis
sobreposições de gatilho entre as descriptions.

Uso:
    python3 scripts/listar_skills.py [caminho-para-.agents/skills]

Sem argumento, assume "./.agents/skills" a partir do diretório atual
(rode a partir da raiz do projeto).
"""

import sys
import re
from pathlib import Path
from itertools import combinations

STOPWORDS = {
    "a", "o", "as", "os", "de", "da", "do", "das", "dos", "e", "ou", "um",
    "uma", "uns", "umas", "para", "por", "com", "sem", "no", "na", "nos",
    "nas", "que", "se", "quando", "usar", "use", "the", "of", "to", "and",
    "or", "for", "with", "when",
}


def parse_frontmatter(skill_md_path: Path):
    text = skill_md_path.read_text(encoding="utf-8", errors="ignore")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return None, None
    lines = match.group(1).splitlines()
    name = None
    description = None
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("name:"):
            name = line.split("name:", 1)[1].strip().strip('"').strip("'")
        elif line.startswith("description:"):
            desc_parts = [line.split("description:", 1)[1].strip()]
            j = i + 1
            while j < len(lines) and lines[j].startswith((" ", "\t")):
                desc_parts.append(lines[j].strip())
                j += 1
            description = " ".join(desc_parts).strip().strip('"').strip("'")
            i = j - 1
        i += 1
    return name, description


def keywords(text: str):
    words = re.findall(r"[a-zà-ú0-9\-]+", text.lower())
    return {w for w in words if w not in STOPWORDS and len(w) > 2}


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def main():
    base = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".agents/skills")
    if not base.exists():
        print(f"Pasta não encontrada: {base}")
        sys.exit(1)

    skills = []
    for skill_dir in sorted(p for p in base.iterdir() if p.is_dir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        name, description = parse_frontmatter(skill_md)
        if not description:
            print(f"[aviso] {skill_dir.name}: sem 'description' válida no frontmatter")
            continue
        skills.append({
            "folder": skill_dir.name,
            "name": name or skill_dir.name,
            "description": description,
            "keywords": keywords(description),
        })

    if not skills:
        print("Nenhuma skill encontrada.")
        return

    print(f"\n{len(skills)} skill(s) encontrada(s) em {base}\n")
    print(f"{'Nome':<30} Description")
    print("-" * 100)
    for s in skills:
        desc = s["description"]
        desc_short = (desc[:70] + "...") if len(desc) > 70 else desc
        print(f"{s['name']:<30} {desc_short}")

    print("\nChecando sobreposição de gatilhos...\n")
    threshold = 0.35
    found_overlap = False
    for a, b in combinations(skills, 2):
        score = jaccard(a["keywords"], b["keywords"])
        if score >= threshold:
            found_overlap = True
            print(f"[possível sobreposição {score:.0%}] '{a['name']}' vs '{b['name']}'")
            print(f"   - {a['name']}: {a['description']}")
            print(f"   - {b['name']}: {b['description']}\n")

    if not found_overlap:
        print("Nenhuma sobreposição significativa encontrada.")


if __name__ == "__main__":
    main()

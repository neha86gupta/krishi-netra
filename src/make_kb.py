"""Create/extend src/knowledge_base.json from the class list. Never overwrites existing class entries.
Causal agents: Table 1 of Hughes & Salathe (2015), arXiv:1511.08060. Symptoms/sources are LEFT EMPTY on purpose."""
from src.utils import *

AGENTS = [  # (crop keyword, condition keyword, agent, group)
    ("apple", "scab", "Venturia inaequalis", "fungal"), ("apple", "black rot", "Botryosphaeria obtusa", "fungal"),
    ("apple", "rust", "Gymnosporangium juniperi-virginianae", "fungal"), ("cherry", "powdery", "Podosphaera spp.", "fungal"),
    ("corn", "gray", "Cercospora zeae-maydis", "fungal"), ("corn", "rust", "Puccinia sorghi", "fungal"),
    ("corn", "blight", "Exserohilum turcicum", "fungal"), ("grape", "black rot", "Guignardia bidwellii", "fungal"),
    ("grape", "esca", "Phaeomoniella spp.", "fungal"), ("grape", "blight", "Pseudocercospora vitis", "fungal"),
    ("orange", "haunglongbing", "Candidatus Liberibacter", "bacterial"), ("orange", "citrus", "Candidatus Liberibacter", "bacterial"),
    ("peach", "bacterial", "Xanthomonas campestris", "bacterial"), ("pepper", "bacterial", "Xanthomonas campestris", "bacterial"),
    ("potato", "early", "Alternaria solani", "fungal"), ("potato", "late", "Phytophthora infestans", "oomycete"),
    ("squash", "powdery", "Erysiphe cichoracearum / Sphaerotheca fuliginea", "fungal"),
    ("strawberry", "scorch", "Diplocarpon earlianum", "fungal"), ("tomato", "early", "Alternaria solani", "fungal"),
    ("tomato", "septoria", "Septoria lycopersici", "fungal"), ("tomato", "target", "Corynespora cassiicola", "fungal"),
    ("tomato", "mold", "Fulvia fulva", "fungal"), ("tomato", "bacterial", "Xanthomonas campestris pv. vesicatoria", "bacterial"),
    ("tomato", "late", "Phytophthora infestans", "oomycete"), ("tomato", "yellow", "Tomato yellow leaf curl virus", "viral"),
    ("tomato", "mosaic", "Tomato mosaic virus", "viral"), ("tomato", "spider", "Tetranychus urticae", "mite")]


def agent_for(label):
    crop, cond = (s.lower() for s in split_class(label))
    if "healthy" in cond:
        return None, "healthy"
    for ck, dk, agent, grp in AGENTS:
        if ck in crop and dk in cond:
            return agent, grp
    return None, "unknown"


if __name__ == "__main__":
    kb = load_json(SRC / "knowledge_base.json")
    for c in load_json(PROCESSED / "class_info.json")["classes"]:
        if c in kb["classes"]:
            continue
        agent, grp = agent_for(c); crop, cond = split_class(c)
        kb["classes"][c] = {"crop": crop, "condition": cond, "cause_group": grp, "causal_agent": agent,
                            "symptoms_en": None, "symptoms_hi": None, "sources": [], "verified": False}
    save_json(kb, SRC / "knowledge_base.json")
    print(f"{len(kb['classes'])} class entries; symptoms and sources still need to be added and verified by you.")

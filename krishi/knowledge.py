"""Disease knowledge base access. Reads ``src/knowledge_base.json`` only; it never
invents symptoms, treatments or doses. Optional fields (description_*, environment_*,
prevention_*) are shown only if the knowledge base itself contains them."""
from __future__ import annotations

from dataclasses import dataclass, field

from krishi.config import CLASS_INFO_PATH, KB_PATH, load_json, log, split_class


FIELD_VALIDATED_CLASSES = {
    "Apple___Apple_scab",
    "Apple___Cedar_apple_rust",
    "Apple___healthy",
    "Blueberry___healthy",
    "Cherry_(including_sour)___healthy",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight",
    "Grape___Black_rot",
    "Grape___healthy",
    "Peach___healthy",
    "Pepper,_bell___Bacterial_spot",
    "Pepper,_bell___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Raspberry___healthy",
    "Soybean___healthy",
    "Squash___Powdery_mildew",
    "Strawberry___healthy",
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy",
    "Rice___Bacterial_leaf_blight",
    "Rice___Brown_spot",
    "Rice___Leaf_blast",
    "Rice___healthy",
}


@dataclass
class DiseaseInfo:
    cls: str
    crop: str
    condition: str
    in_kb: bool = False
    validation_level: str = "field_tested"  # "field_tested" | "lab_only"
    causal_agent: str = ""
    cause_group: str = ""
    description: str = ""
    symptoms: str = ""
    environment: str = ""
    prevention: str = ""
    care: str = ""
    sources: list[dict] = field(default_factory=list)

    @property
    def healthy(self) -> bool:
        return self.condition.lower().startswith("healthy")


def load_kb() -> dict:
    """Return the knowledge base, or an empty skeleton if it is missing/corrupt."""
    if not KB_PATH.exists():
        return {"classes": {}, "cause_groups": {}}
    try:
        kb = load_json(KB_PATH)
        kb.setdefault("classes", {})
        kb.setdefault("cause_groups", {})
        return kb
    except Exception as exc:  # noqa: BLE001
        log.error("Knowledge base unreadable: %s", exc)
        return {"classes": {}, "cause_groups": {}}


def _loc(entry: dict, base: str, lang: str) -> str:
    return (entry.get(f"{base}_{lang}") or entry.get(f"{base}_en") or "") if entry else ""


def get_info(kb: dict, cls: str, lang: str = "en") -> DiseaseInfo:
    crop, cond = split_class(cls)
    entry = kb.get("classes", {}).get(cls)
    groups = kb.get("cause_groups", {})
    key = entry.get("cause_group") if entry else "unknown"
    group = groups.get(key or "unknown", groups.get("unknown", {}))
    return DiseaseInfo(
        cls=cls, crop=crop, condition=cond, in_kb=entry is not None,
        validation_level="field_tested" if cls in FIELD_VALIDATED_CLASSES else "lab_only",
        causal_agent=(entry or {}).get("causal_agent", "") or "",
        cause_group=(key or "") if entry else "",
        description=_loc(entry, "description", lang),
        symptoms=_loc(entry, "symptoms", lang),
        environment=_loc(entry, "environment", lang),
        prevention=_loc(entry, "prevention", lang),
        care=_loc(group, "advice", lang),
        sources=list((entry or {}).get("sources", [])),
    )


def list_classes(kb: dict) -> list[str]:
    """Class names from class_info.json (preferred, as in the original app) or the KB."""
    if CLASS_INFO_PATH.exists():
        try:
            return list(load_json(CLASS_INFO_PATH)["classes"])
        except Exception as exc:  # noqa: BLE001
            log.error("class_info.json unreadable: %s", exc)
    return list(kb.get("classes", {}))


def pretty(text: str) -> str:
    return text.replace("_", " ").strip()

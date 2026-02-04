from __future__ import annotations

from dataclasses import dataclass
import math
from typing import List, Optional

MAX_POST_CHARS = 300


@dataclass
class TemplateContext:
    respondent_id: str
    age_bucket: Optional[str]
    gender: Optional[str]
    ethnicity: Optional[str]
    education: Optional[str]
    housing: Optional[str]
    urban_rural: Optional[str]
    party_vote: Optional[str]
    ideology: Optional[str]


def _clean_value(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, str) and value.strip() == "":
        return None
    return value


def _join_phrases(phrases: List[str]) -> str:
    if len(phrases) == 1:
        return phrases[0]
    if len(phrases) == 2:
        return f"{phrases[0]} and {phrases[1]}"
    return ", ".join(phrases[:-1]) + f", and {phrases[-1]}"


def _article(word: str) -> str:
    if word[:1].lower() in {"a", "e", "i", "o", "u"}:
        return "an"
    return "a"


def _normalize_gender(value: Optional[str]) -> Optional[str]:
    cleaned = _clean_value(value)
    if cleaned is None:
        return None
    return cleaned.lower()


def _normalize_education(value: Optional[str]) -> Optional[str]:
    cleaned = _clean_value(value)
    if cleaned is None:
        return None
    mapping = {
        "No Formal": "no formal qualifications",
        "Level 1": "Level 1 qualifications",
        "Level 2 or 3": "Level 2 or 3 qualifications",
        "Level 4": "Level 4 qualifications",
        "University": "a university qualification",
        "Unclassfied": "an unclassified qualification",
    }
    return mapping.get(cleaned, cleaned)


def _normalize_housing(value: Optional[str]) -> Optional[str]:
    cleaned = _clean_value(value)
    if cleaned is None:
        return None
    mapping = {
        "Own your house or flat mortgage free": "own their home mortgage-free",
        "Own your house or flat with a mortgage": "own their home with a mortgage",
        "Rent your house or flat privately": "rent privately",
        "Rent a house or flat with a group of individuals": "rent with others",
        "Live at your parents' or other family members' home": "live with family",
        "Board or live in a hotel / hostel / rest home / temporary housing": "board or live in temporary housing",
        "Rent a house or flat from Kāinga Ora: Home and Communities, a local authority or trust": "rent from Kāinga Ora or a public provider",
    }
    return mapping.get(cleaned, cleaned)


def _normalize_party_vote(value: Optional[str]) -> Optional[str]:
    cleaned = _clean_value(value)
    if cleaned is None:
        return None
    mapping = {
        "Nonvote": "did not cast a party vote",
        "Maori": "voted for Te Pāti Māori",
    }
    return mapping.get(cleaned, f"voted for {cleaned}")


def _normalize_ideology(value: Optional[str]) -> Optional[str]:
    cleaned = _clean_value(value)
    if cleaned is None:
        return None
    return cleaned


def build_sentences(context: TemplateContext) -> List[str]:
    sentences: List[str] = []

    intro_parts: List[str] = []
    if _clean_value(context.age_bucket):
        intro_parts.append(f"aged {context.age_bucket}")
    gender = _normalize_gender(context.gender)
    if gender:
        intro_parts.append(f"identifies as {gender}")
    if _clean_value(context.ethnicity):
        intro_parts.append(f"reports {context.ethnicity} ethnicity")
    if intro_parts:
        sentences.append(f"This respondent is {_join_phrases(intro_parts)}.")

    living_parts: List[str] = []
    education = _normalize_education(context.education)
    if education:
        living_parts.append(f"have {education}")
    housing = _normalize_housing(context.housing)
    if housing:
        living_parts.append(housing)
    if _clean_value(context.urban_rural):
        article = _article(context.urban_rural)
        living_parts.append(f"live in {article} {context.urban_rural} area")
    if living_parts:
        sentences.append(f"They {_join_phrases(living_parts)}.")

    party_vote = _normalize_party_vote(context.party_vote)
    if party_vote:
        if party_vote.startswith("did not"):
            sentences.append(f"They {party_vote} in 2023.")
        else:
            sentences.append(f"They {party_vote} in 2023.")

    ideology = _normalize_ideology(context.ideology)
    if ideology:
        sentences.append(f"On the left-right scale they place themselves on the {ideology}.")

    return sentences


def render_profile(context: TemplateContext, max_chars: int = MAX_POST_CHARS) -> str:
    prefix = "NZES 2023 profile."
    sentences = build_sentences(context)

    if not sentences:
        text = prefix
    else:
        selected = sentences.copy()
        while selected:
            candidate = " ".join([prefix] + selected)
            if len(candidate) <= max_chars:
                text = candidate
                break
            selected.pop()
        else:
            text = prefix

    hashtag = " #NZES2023"
    if len(text) + len(hashtag) <= max_chars:
        text += hashtag

    return text


def context_from_row(row: Dict[str, object]) -> TemplateContext:
    return TemplateContext(
        respondent_id=str(row.get("respondent_id")),
        age_bucket=row.get("age_bucket"),
        gender=row.get("gender"),
        ethnicity=row.get("ethnicity"),
        education=row.get("education"),
        housing=row.get("housing"),
        urban_rural=row.get("urban_rural"),
        party_vote=row.get("party_vote"),
        ideology=row.get("ideology"),
    )

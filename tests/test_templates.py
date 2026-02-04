from src.templates import TemplateContext, render_profile, MAX_POST_CHARS


def test_render_profile_length_and_prefix():
    ctx = TemplateContext(
        respondent_id="1",
        age_bucket="25-34",
        gender="Female",
        ethnicity="Māori",
        education="University",
        housing="Rent privately",
        urban_rural="urban",
        party_vote="Green",
        ideology="left",
    )
    text = render_profile(ctx)
    assert text.startswith("NZES 2023 profile")
    assert len(text) <= MAX_POST_CHARS
    assert "#NZES2023" in text

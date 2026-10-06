"""Route listings whose photos show people to privacy review.

Photos of people are personal data under the Kenya Data Protection Act;
retail use does not waive that. Tags are a coarse net: they route to a
human, they do not decide.
"""
SENSITIVE_TAGS = {"person", "face", "child"}


def needs_privacy_review(tags: list[str] | None) -> bool:
    return any(t in SENSITIVE_TAGS for t in (tags or []))


if __name__ == "__main__":
    assert needs_privacy_review(["kiondo", "bag"]) is False
    assert needs_privacy_review(["leso", "person"]) is True
    assert needs_privacy_review(None) is False
    print("privacy flag OK")
from mm.validator import validate_meta


def test_valid_meta():
    validate_meta("template/meta.json")

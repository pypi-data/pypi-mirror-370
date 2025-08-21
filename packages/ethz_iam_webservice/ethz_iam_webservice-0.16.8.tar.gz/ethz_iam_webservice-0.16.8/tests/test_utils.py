import pytest
from ethz_iam_webservice import utils


@pytest.mark.parametrize("password", [("ABCabc0123455;:"), ("aAbBcD123,;.:-(){}/")])
def test_check_password(password):
    assert utils.check_password(password)


@pytest.mark.parametrize("password", [("ABCABCabcabcabc"), ("123456abcdef")])
def test_check_invalid_password(password):
    with pytest.raises(ValueError, match=r"a password must contain"):
        utils.check_password(password)


@pytest.mark.parametrize("password", [("ABCabc123"), (".;-123ABC")])
def test_check_too_short_password(password):
    with pytest.raises(ValueError, match=r"Password is too short"):
        utils.check_password(password)


def test_generated_passwords():
    for i in range(1, 1000):
        password = utils.gen_password()
        assert utils.check_password(password)


@pytest.mark.parametrize(
    "leitzahl,formatted",
    [
        ("T1234", "T1234"),
        ("55", "00055"),
        ("6005", "06005"),
        (55, "00055"),
        ("T123", "T0123"),
    ],
)
def test_format_leitzahl(leitzahl, formatted):
    assert utils.format_leitzahl(leitzahl) == formatted


@pytest.mark.parametrize(
    "leitzahl,formatted",
    [("55555", "55555"), ("F1234", "F1234"), ("1234T", "T1234"), ("T12345", "T12345")],
)
def test_format_invalid_leitzahl(leitzahl, formatted):
    with pytest.raises(ValueError, match=r"not a valid Leitzahl"):
        utils.format_leitzahl(leitzahl)


@pytest.mark.parametrize(
    "code,text",
    [
        ("gh", "To guest and host"),
        ("htg", "To guest, host and technical contact"),
        ("th", "To host and technical contact"),
        ("g", "To guest only"),
        ("tg", "To guest and technical contact"),
        ("h", "To host"),
        ("t", "To technical contact"),
    ],
)
def test_format_notification(code, text):
    assert utils.format_notification(code) == text


@pytest.mark.parametrize(
    "date,formatted_date",
    [
        ("1.6.2021", "2021-06-01"),
        ("01.06.2021", "2021-06-01"),
        ("2021-06-01", "2021-06-01"),
        ("31-DEC-9999", "9999-12-31"),
    ],
)
def test_format_date(date, formatted_date):
    dt = utils.to_date(date)
    assert dt.strftime("%Y-%m-%d") == formatted_date

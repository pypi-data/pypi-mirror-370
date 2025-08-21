import secrets
import string
import re
import dateutil.parser
from dateutil import tz

allowed_special_chars = "# , - + . / : = ? ! $ @ [ ] { }".split()

notification_code = {
    "gh": "To guest and host",
    "ght": "To guest, host and technical contact",
    "ht": "To host and technical contact",
    "g": "To guest only",
    "gt": "To guest and technical contact",
    "h": "To host",
    "t": "To technical contact",
}


def check_password(password):
    if len(password) < 12:
        raise ValueError(
            "Password is too short, it should contain at least 12 characters"
        )

    match = re.search(r"\s+", password)
    if match:
        raise ValueError("Password must not contain any whitespace")

    match = re.search(r"([^a-zA-Z0-9\,\;\.\:\-\(\)\{\}\/\\]+)", password)
    if match:
        raise ValueError(
            "Password contains illegal character: {}".format(", ".join(match.groups()))
        )

    has_uppercase = 0
    if any(char.lower() != char for char in password):
        has_uppercase = 1

    has_lowercase = 0
    if any(char.upper() != char for char in password):
        has_lowercase = 1

    has_number = 0
    if any(char.isdigit() for char in password):
        has_number = 1

    has_special_char = 0
    if any(char in allowed_special_chars for char in password):
        has_special_char = 1

    score = has_uppercase + has_lowercase + has_number + has_special_char
    if score > 2:
        return True
    else:
        raise ValueError(
            "a password must contain at least three of the following character types: Lowercase, uppercase, number, special char: , ; . : - ( ) { } / \\ "
        )


def gen_password():
    alphabet = string.ascii_letters + string.digits + "".join(allowed_special_chars)
    password = ""
    while True:
        password = "".join(secrets.choice(alphabet) for i in range(15))
        try:
            check_password(password)
            break
        except ValueError:
            pass
    return password


def to_date(date, astz="CET"):
    """Converts a given date format into a datetime object
    and adjusts the timezone to local timezone.
    Assumes 1.5.2021 is actually May 1st 2021.
    """
    if date == "":
        return ""
    local_tz = tz.tzlocal()
    date_formats = [
        r"^(?P<dd>\d{1,2})\.(?P<mm>\d{1,2})\.(?P<yyyy>\d{4})",
        r"^(?P<yyyy>\d{4})\-(?P<mm>\d{1,2})\-(?P<dd>\d{1,2})",
    ]
    date = str(date)
    for i, date_format in enumerate(date_formats):
        match = re.search(date_format, date)
        if match:
            break

    if match:
        if i == 0:
            dt = dateutil.parser.parse(
                date, parserinfo=dateutil.parser.parserinfo(dayfirst=True)
            )
        elif i == 1:
            # ISO-Format, dayfirst=False
            try:
                dt = dateutil.parser.parse(date)
            except Exception as exc:
                raise ValueError(f"{date} is not a known date format.") from exc
        new_date = dt.replace(tzinfo=local_tz)
        return new_date.date()
    else:
        try:
            dt = dateutil.parser.parse(date)
        except Exception as exc:
            raise ValueError(f"{date} is not a known date format.") from exc
        new_date = dt.replace(tzinfo=local_tz)
        return new_date.date()


def format_leitzahl(leitzahl):
    leitzahl = str(leitzahl)
    match = re.search(r"^(T|0)?(\d{1,4})$", leitzahl)
    if match:
        lzs = match.groups()
        if lzs[0]:
            return f"{lzs[0]}{int(lzs[1]):04d}"
        else:
            return f"{int(lzs[1]):05d}"
    else:
        raise ValueError(f"{leitzahl} is not a valid Leitzahl")


def format_notification(notification):
    if notification in notification_code.values():
        return notification
    notifications = [char for char in notification.lower()]
    notifications.sort()
    code = "".join(notifications)
    if code in notification_code:
        return notification_code[code]
    raise ValueError(
        "Please provide any combination of «g» (guest), «h» (host) or «t» (technical contact) for notification"
    )

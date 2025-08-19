import re

import idna
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


def comma_separated_period_validator(val):
    SPLIT_LENGTH = 2

    values = val.split(",")
    if len(values) != SPLIT_LENGTH:
        raise ValidationError("", "invalid")
    if values[0].isdigit() and values[1].isdigit():
        return val
    raise ValidationError("", "invalid")


def age_range_validator(data: dict, key_from: str, key_to: str):
    age_from, age_to = data.get(key_from), data.get(key_to)
    if age_from and age_to:
        if age_from <= age_to:
            return
        raise ValidationError({key_to: f'"{key_to}" should be greater or equal than "{key_from}".'})
    if not age_from and not age_to:
        return
    raise ValidationError({key_to if not age_to else key_from: "This field is required."})


class DomainNameValidator(RegexValidator):
    """
    see https://code.djangoproject.com/ticket/18119
    """

    # from URLValidator + there can be most 127 labels (at most 255 total chars)
    regex = re.compile(
        r"^(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.){0,126}(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?))$",
        re.IGNORECASE,
    )
    message = _("Enter a valid domain name only (without protocol like http://)")

    def __init__(self, *args, **kwargs):
        self.accept_idna = kwargs.pop("accept_idna", True)
        super().__init__(*args, **kwargs)

    def __call__(self, value):
        # validate
        try:
            super().__call__(value)
        except ValidationError as validation_exc:
            # maybe this is a unicode-encoded IDNA string?
            if not self.accept_idna:
                raise
            if not value:
                raise

            # convert it unicode -> ascii
            try:
                asciival = idna.encode(value).decode()
            except UnicodeError as unicode_exc:
                # raise the original ASCII error
                raise validation_exc from unicode_exc

            # validate the ascii encoding of it
            super().__call__(asciival)


# TO be removed while support for V1 is removed
class ExtendedDomainNameValidator(RegexValidator):
    message = _("Enter a valid plain or internationalized domain name value")
    regex = re.compile(
        (
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}(?<!-)\.?)|"
            r"localhost|"  # localhost...
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|"  # ...or ipv4
            r"\[?[A-F0-9]*:[A-F0-9:]+\]?)"  # ...or ipv6
        ),
        re.IGNORECASE,
    )

    def __init__(self, accept_idna=True, **kwargs):
        message = kwargs.get("message")
        self.accept_idna = accept_idna
        super().__init__(**kwargs)
        if not self.accept_idna and message is None:
            self.message = _("Enter a valid domain name value")

    def __call__(self, value):
        try:
            super().__call__(value)
        except ValidationError as exc:
            if not self.accept_idna:
                raise
            if not value:
                raise
            try:
                idnavalue = value.encode("idna")
            except UnicodeError as e:
                raise exc from e
            super().__call__(idnavalue)


class HexColorValidator(RegexValidator):
    regex = re.compile(r"^\#([a-fA-F0-9]{6}|[a-fA-F0-9]{3})$")
    message = _('Enter a valid hex color (starting with a "#" sign)')

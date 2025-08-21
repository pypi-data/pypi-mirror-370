import re
from typing import cast

from django.core.validators import _lazy_re_compile

# Regex to match URLs used by Django's URLValidator (slightly modified to match
# all URLs in a string rather than match if the string is a valid URL)

# To achieve this, the `^` was removed from the start of the regex, and `\Z`
# was removed from the end of the regex
ul = "\u00a1-\uffff"  # unicode letters range (must not be a raw string)

# IP patterns
ipv4_re = r"(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}"
ipv6_re = r"\[[0-9a-f:\.]+\]"  # (simple regex, validated later)

# Host patterns
hostname_re = r"[a-z" + ul + r"0-9](?:[a-z" + ul + r"0-9-]{0,61}[a-z" + ul + r"0-9])?"
# Max length for domain name labels is 63 characters per RFC 1034 sec. 3.1
domain_re = r"(?:\.(?!-)[a-z" + ul + r"0-9-]{1,63}(?<!-))*"
tld_re = (
    r"\."  # dot
    r"(?!-)"  # can't start with a dash
    r"(?:[a-z" + ul + "-]{2,63}"  # domain label
    r"|xn--[a-z0-9]{1,59})"  # or punycode label
    r"(?<!-)"  # can't end with a dash
    r"\.?"  # may have a trailing dot
)
host_re = "(" + hostname_re + domain_re + tld_re + "|localhost)"

URL_REGEX = _lazy_re_compile(
    r"(?:[a-z0-9\.\-\+]*)://"  # scheme is validated separately
    r"(?:[^\s:@/]+(?::[^\s:@/]*)?@)?"  # user:pass authentication
    r"(?:" + ipv4_re + "|" + ipv6_re + "|" + host_re + ")"
    r"(?::\d{2,5})?"  # port
    r"(?:[/?#][^\s]*)?",  # resource path
    re.IGNORECASE,
)
URL_REGEX = cast(re.Pattern, URL_REGEX)

# TODO: make configurable?
MESSAGE_SIZE_LIMIT = 2 * 1024 * 1024

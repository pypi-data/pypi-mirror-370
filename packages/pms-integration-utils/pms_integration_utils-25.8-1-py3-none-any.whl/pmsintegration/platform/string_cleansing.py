import re

__camel_to_snake_case_p1 = re.compile('(.)([A-Z][a-z]+)')
__camel_to_snake_case_p3 = re.compile('([a-z0-9])([A-Z])')


def remove_chars(__value: str, __chars: str, /):
    return __value.translate(str.maketrans("", "", __chars))


def camel_to_snake_case(__value: str, /) -> str:
    s = __value.strip()

    s = __camel_to_snake_case_p1.sub(r'\1_\2', s)
    s = __camel_to_snake_case_p3.sub(r'\1_\2', s)

    return s.lower()


remove_whitespace = str.strip
capitalize = str.capitalize
casefold = str.casefold
center = str.center
encode = str.encode
expandtabs = str.expandtabs
format_map = str.format_map
join = str.join
ljust = str.ljust
lower = str.lower
lstrip = str.lstrip
maketrans = str.maketrans
removeprefix = str.removeprefix
removesuffix = str.removesuffix
replace = str.replace
rfind = str.rfind
rindex = str.rindex
rjust = str.rjust
rpartition = str.rpartition
rsplit = str.rsplit
rstrip = str.rstrip
split = str.split
splitlines = str.splitlines
strip = str.strip
swapcase = str.swapcase
title = str.title
translate = str.translate
upper = str.upper
zfill = str.zfill

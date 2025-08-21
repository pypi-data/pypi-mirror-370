from django.conf import settings

IS_BAP = getattr(settings, "BECKNLD_BAP̈_ENV", False)
IS_BPP = getattr(settings, "BECKNLD_BPP̈_ENV", False)

BAP_URI = (
    getattr(settings, "BASE_URL", None)
    if IS_BAP
    else getattr(settings, "BECKNLD_BAP_URI", None)
)
if BAP_URI and BAP_URI[-1] != "/":
    BAP_URI += "/"

BPP_URI = (
    getattr(settings, "BASE_URL", None)
    if IS_BPP
    else getattr(settings, "BECKNLD_BPP_URI", None)
)
if BPP_URI and BPP_URI[-1] != "/":
    BPP_URI += "/"

BECKNLD_CONTEXT = {
    "as": "https://www.w3.org/ns/activitystreams#",
    "schema": "http://schema.org/",
    "dc": "http://purl.org/dc/terms/",
    "geo": "http://www.w3.org/2003/01/geo/wgs84_pos#",
    "beckn": "https://ontology.beckn.org/core/v1#",
}

if not BAP_URI and not IS_BAP:
    raise RuntimeError("BECKNLD_BAP_URI must be set or djangoldp_becknld_bap should be enabled")

if not BPP_URI and not IS_BPP:
    raise RuntimeError("BECKNLD_BPP_URI must be set or djangoldp_becknld_bpp should be enabled")

import os

__version__ = "1.4.2"

GFP_DOWEB_HTTPS = (
    os.environ.get("GFP_DOWEB_HTTPS", os.environ.get("GFP_KWEB_HTTPS", "false")).strip()
    == "true"
)

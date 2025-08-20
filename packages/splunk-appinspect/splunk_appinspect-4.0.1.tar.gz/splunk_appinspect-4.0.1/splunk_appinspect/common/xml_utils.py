import warnings

try:
    # FIXME: Remove try-except after deprecating python 3.7 and upgrading beautifulsoup4>=3.11.0
    from bs4 import XMLParsedAsHTMLWarning

    def ignore_XMLParsedAsHTMLWarning():
        warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

except ImportError:

    def ignore_XMLParsedAsHTMLWarning(): ...

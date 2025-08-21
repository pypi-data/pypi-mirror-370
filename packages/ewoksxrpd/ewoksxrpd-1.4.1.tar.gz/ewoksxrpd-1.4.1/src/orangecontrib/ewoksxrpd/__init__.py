import sysconfig

NAME = "XRPD"

DESCRIPTION = "X-ray Powder Diffraction"

LONG_DESCRIPTION = "X-ray Powder Diffraction"

ICON = "icons/category.png"

BACKGROUND = "light-blue"

WIDGET_HELP_PATH = (
    # Development documentation (make htmlhelp in ./doc)
    ("{DEVELOP_ROOT}/doc/_build/htmlhelp/index.html", None),
    # Documentation included in wheel
    ("{}/help/orange3-xrpd/index.html".format(sysconfig.get_path("data")), None),
    # Online documentation url
    ("http://orange3-xrpd.readthedocs.io/en/latest/", ""),
)

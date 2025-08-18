from util_common.package import get_package_info

APP_NAME = "py-agent-tools"
__info__ = get_package_info(APP_NAME)

VERSION = __info__.get("version")
AUTHOR_EMAIL = __info__.get("author_email")
AUTHOR_NAME = __info__.get("author_name")

from __future__ import annotations

import os
import secrets
from pathlib import Path
from typing import Any

from php_framework_detector.core.models import FrameworkType

from php_framework_scaffolder.utils.logger import get_logger
from php_framework_scaffolder.utils.template import copy_and_replace_template

logger = get_logger(__name__)


def render_framework_template(
    framework_type: FrameworkType,
    target_folder: Path,
    php_version: str | None = None,
    app_port: int = 8000,
    database_name: str = 'app',
    database_user: str = 'user',
    database_password: str | None = None,
    apk_packages: list[str] | None = None,
    php_extensions: list[str] | None = None,
    pecl_extensions: list[str] | None = None,
    install_dependencies: bool = True,
    swagger_php_legacy: bool = False,
) -> dict[str, Any]:
    """Render templates for a given PHP framework into ``target_folder``.

    This high-level API prepares a sensible default context (APK packages,
    PHP/PECL extensions, ports and DB credentials) and renders the selected
    framework templates into the provided ``target_folder`` using Jinja2.

    Returns the final context used for rendering so callers can persist or
    inspect it if needed.
    """
    if database_password is None:
        database_password = secrets.token_hex(8)

    merged_apk_packages = apk_packages or []
    merged_php_extensions = php_extensions or []
    merged_pecl_extensions = pecl_extensions or []

    logger.info(f"Using APK packages: {merged_apk_packages}")
    logger.info(f"Using PHP extensions: {merged_php_extensions}")
    logger.info(f"Using PECL extensions: {merged_pecl_extensions}")

    context: dict[str, Any] = {
        'php_version': php_version,
        'app_port': app_port,
        'db_database': database_name,
        'db_username': database_user,
        'db_password': database_password,
        'apk_packages': merged_apk_packages,
        'php_extensions': merged_php_extensions,
        'pecl_extensions': merged_pecl_extensions,
        'install_dependencies': install_dependencies,
        'swagger_php_version': '4.7.16' if swagger_php_legacy else '5.1.4',
    }

    template_path = Path(os.path.dirname(__file__)).parent / Path(
        f"templates/{str(framework_type)}",
    )
    logger.info(f"Template path: {template_path}")

    logger.info(f"Copying template to {target_folder}")
    copy_and_replace_template(template_path, target_folder, context)
    logger.info(f"Copied template to {target_folder}")

    return context

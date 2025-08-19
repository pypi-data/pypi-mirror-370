from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as version_finder

from packaging import version

from galtea.infrastructure.clients.http_client import Client


def validate_installed_version(client: Client, supress_updatable_version_message: bool = False) -> None:
    try:
        PACKAGE_NAME = "galtea"
        installed_version = version_finder(PACKAGE_NAME)
        response = client.get("minimum-sdk-version")
    except PackageNotFoundError:
        print(f"The package {PACKAGE_NAME} is not found.")
        return
    except Exception:
        return

    if response:
        response_body = response.json()
        latest_sdk_version_published = response_body.get("latestSdkVersionPublished")
        minimum_sdk_version_supported = response_body.get("minimumSdkVersionSupported")
        # Compare versions
        if minimum_sdk_version_supported and version.parse(installed_version) < version.parse(
            minimum_sdk_version_supported
        ):
            raise RuntimeError(
                f"The installed version of {PACKAGE_NAME} ({installed_version}) is below "
                "the minimum supported version for the API.\n"
                f"Minimum supported version is ({minimum_sdk_version_supported}). "
                "Please, upgrade to the minimum supported version or higher to ensure compatibility."
            )
        if (
            not supress_updatable_version_message
            and latest_sdk_version_published
            and version.parse(installed_version) < version.parse(latest_sdk_version_published)
        ):
            print(
                f"There is a new version available. The installed version of {PACKAGE_NAME} is {installed_version} "
                f"and the latest version is {latest_sdk_version_published}. "
                f"Please, upgrade to the latest version."
            )

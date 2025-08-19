from validio_sdk.exception import ValidioError


class ManifestConfigurationError(ValidioError):
    """Raised when there is an invalid configuration in the manifest."""


def updated_resource_type_mismatch_exception(
    resource_name: str, manifest_resource: object, server_resource: object
) -> ManifestConfigurationError:
    return ManifestConfigurationError(
        f"invalid configuration for resource '{resource_name}': manifest resource type "
        f"'{manifest_resource.__class__.__name__}' does not match server resource "
        f"type '{server_resource.__class__.__name__}'; consider first commenting out "
        "the resource in the manifest in order to apply a delete on the server "
        "resource, before specifying the new version in manifest to recreate it"
    )


def max_resource_depth_exceeded(
    resource_name: str,
) -> ManifestConfigurationError:
    return ManifestConfigurationError(
        f"invalid configuration for resource '{resource_name}': "
        "potential circular reference detected: "
        "(configuration exceeded the max field depth)"
    )

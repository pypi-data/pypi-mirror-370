"""Main process for the demo."""

import logging
from pathlib import Path

from basyx.aas import model

from aas_http_client.client import AasHttpClient, create_client_by_config
from aas_http_client.utilities import model_builder
from aas_http_client.wrapper.sdk_wrapper import SdkWrapper, create_wrapper_by_config

logger = logging.getLogger(__name__)


def start() -> None:
    """Start the demo process."""
    # create a submodel element
    sme_short_id: str = model_builder.create_unique_short_id("poc_sme")
    sme = model_builder.create_base_submodel_element_Property(sme_short_id, model.datatypes.String, "Sample Value")

    # create a submodel
    sm_short_id: str = model_builder.create_unique_short_id("poc_sm")
    submodel = model_builder.create_base_submodel(sm_short_id)
    # add submodel element to submodel
    # submodel.submodel_element.add(sme)

    # create an AAS
    aas_short_id: str = model_builder.create_unique_short_id("poc_aas")
    aas = model_builder.create_base_ass(aas_short_id)

    # add submodel to AAS
    model_builder.add_submodel_to_aas(aas, submodel)

    wrapper = _create_sdk_wrapper(Path("./aas_http_client/demo/python_server_config.json"))
    # dotnet_sdk_wrapper = _create_sdk_wrapper(Path("./aas_http_client/demo/dotnet_server_config.json"))

    for existing_shell in wrapper.get_all_asset_administration_shells():
        logger.warning(f"Delete shell '{existing_shell.id}'")
        wrapper.delete_asset_administration_shell_by_id(existing_shell.id)

    for existing_submodel in wrapper.get_all_submodels():
        logger.warning(f"Delete submodel '{existing_submodel.id}'")
        wrapper.delete_submodel_by_id(existing_submodel.id)

    wrapper.post_asset_administration_shell(aas)
    wrapper.post_submodel(submodel)

    tmp = wrapper.get_asset_administration_shell_by_id_reference_aas_repository(aas.id)

    shell = wrapper.get_asset_administration_shell_by_id(aas.id)
    submodel = wrapper.get_submodel_by_id(submodel.id)

    wrapper.post_submodel_element_submodel_repo(submodel.id, sme)

    submodel = wrapper.get_submodel_by_id(submodel.id)

    for existing_shell in wrapper.get_all_asset_administration_shells():
        logger.warning(f"Delete shell '{existing_shell.id}'")
        wrapper.delete_asset_administration_shell_by_id(existing_shell.id)

    for existing_submodel in wrapper.get_all_submodels():
        logger.warning(f"Delete submodel '{existing_submodel.id}'")
        wrapper.delete_submodel_by_id(existing_submodel.id)


def _create_client(config: Path) -> AasHttpClient:
    """Create a HTTP client from a given configuration file.

    :param config: Given configuration file
    :return: HTTP client
    """
    try:
        file = config
        client = create_client_by_config(file, password="")

    except Exception as e:
        logger.error(f"Failed to create client for {file}: {e}")

    return client


def _create_sdk_wrapper(config: Path) -> SdkWrapper:
    """Create a SDK wrapper from a given configuration file.

    :param config: Given configuration file
    :return: SDK wrapper
    """
    try:
        file = config
        client = create_wrapper_by_config(file, password="")

    except Exception as e:
        logger.error(f"Failed to create client for {file}: {e}")

    return client

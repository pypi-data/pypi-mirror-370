import logging
import aas_http_client.utilities.model_builder as model_builder
from aas_http_client.client import create_client_by_config, AasHttpClient
from aas_http_client.wrapper.sdk_wrapper import SdkWrapper, create_wrapper_by_config
from pathlib import Path
import json
import basyx.aas.adapter.json
import basyx.aas.model

from basyx.aas import model

logger = logging.getLogger(__name__)

def start():
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
    
    java_sdk_wrapper = _create_sdk_wrapper(Path("./aas_http_client/demo/java_server_config.json"))
    # dotnet_sdk_wrapper = _create_sdk_wrapper(Path("./aas_http_client/demo/dotnet_server_config.json"))

    for existing_shell in java_sdk_wrapper.get_all_asset_administration_shells():
        logger.warning(f"Delete shell '{existing_shell.id}'")
        java_sdk_wrapper.delete_asset_administration_shell_by_id(existing_shell.id)

    for existing_submodel in java_sdk_wrapper.get_all_submodels():
        logger.warning(f"Delete submodel '{existing_submodel.id}'")
        java_sdk_wrapper.delete_submodel_by_id(existing_submodel.id)

    java_sdk_wrapper.post_asset_administration_shell(aas)
    java_sdk_wrapper.post_submodel(submodel)

    tmp = java_sdk_wrapper.get_asset_administration_shell_by_id_reference_aas_repository(aas.id)

    shell = java_sdk_wrapper.get_asset_administration_shell_by_id(aas.id)    
    submodel = java_sdk_wrapper.get_submodel_by_id(submodel.id)

    java_sdk_wrapper.post_submodel_element_submodel_repo(submodel.id, sme)

    submodel = java_sdk_wrapper.get_submodel_by_id(submodel.id)
    

def _create_shell() -> basyx.aas.model.AssetAdministrationShell:
    # create an AAS
    aas_short_id: str = model_builder.create_unique_short_id("poc_aas")
    aas = model_builder.create_base_ass(aas_short_id)

    # create a Submodel
    sm_short_id: str = model_builder.create_unique_short_id("poc_sm")
    submodel = model_builder.create_base_submodel(sm_short_id)

    # add Submodel to AAS
    model_builder.add_submodel_to_aas(aas, submodel)
    
    return aas

def _create_client(config: Path) -> AasHttpClient:
    """Create client for java servers."""

    try:
        file = config
        client = create_client_by_config(file, password="")
    except Exception as e:
        logger.error(f"Failed to create client for {file}: {e}")
        pass

    return client
        
def _create_sdk_wrapper(config: Path) -> SdkWrapper:
    """Create client for java servers."""

    try:
        file = config
        client = create_wrapper_by_config(file, password="")
    except Exception as e:
        logger.error(f"Failed to create client for {file}: {e}")
        pass

    return client
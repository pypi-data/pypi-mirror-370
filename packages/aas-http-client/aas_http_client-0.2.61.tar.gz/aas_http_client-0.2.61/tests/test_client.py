import pytest
from pathlib import Path
from aas_http_client.client import create_client_by_config, AasHttpClient
from basyx.aas import model
import aas_http_client.utilities.model_builder as model_builder
import json
import basyx.aas.adapter.json

JAVA_SERVER_PORT = "8075"

CONFIG_FILES = [
    "./tests/server_configs/test_dotnet_server_config.json",
    "./tests/server_configs/test_java_server_config.json",
]

@pytest.fixture(params=CONFIG_FILES, scope="module")
def client(request) -> AasHttpClient:
    try:
        file = Path(request.param).resolve()

        if not file.exists():
            raise FileNotFoundError(f"Configuration file {file} does not exist.")

        client = create_client_by_config(file, password="")
    except Exception as e:
        raise RuntimeError("Unable to connect to server.")

    shells = client.get_all_asset_administration_shells()
    if shells is None:
        raise RuntimeError("No shells found on server. Please check the server configuration.")

    return client

@pytest.fixture(scope="module")
def shared_sme() -> model.Property:
    # create a Submodel
    return model_builder.create_base_submodel_element_Property("sme_http_client_unit_tests", model.datatypes.String, "Sample Value")

@pytest.fixture(scope="module")
def shared_sm() -> model.Submodel:
    # create a Submodel
    return model_builder.create_base_submodel("sm_http_client_unit_tests", "")

@pytest.fixture(scope="module")
def shared_aas(shared_sm: model.Submodel) -> model.AssetAdministrationShell:
    # create an AAS
    aas = model_builder.create_base_ass(id_short="aas_http_client_unit_tests", namespace="")

    # add Submodel to AAS
    model_builder.add_submodel_to_aas(aas, shared_sm)

    return aas

def test_001_connect(client: AasHttpClient):
    assert client is not None

def test_002_get_all_asset_administration_shells(client: AasHttpClient):
    result = client.get_all_asset_administration_shells()
    assert result is not None
    shells = result.get("result", [])
    assert len(shells) == 0

def test_003_post_asset_administration_shell(client: AasHttpClient, shared_aas: model.AssetAdministrationShell):
    aas_data_string = json.dumps(shared_aas, cls=basyx.aas.adapter.json.AASToJsonEncoder)
    aas_data = json.loads(aas_data_string)
    result = client.post_asset_administration_shell(aas_data)

    assert result is not None
    result_id_short = result.get("idShort", "")
    assert result_id_short == shared_aas.id_short

    get_result = client.get_all_asset_administration_shells()
    assert get_result is not None
    shells = get_result.get("result", [])
    assert len(shells) == 1
    assert shells[0].get("idShort", "") == shared_aas.id_short

def test_004a_get_asset_administration_shell_by_id(client: AasHttpClient, shared_aas: model.AssetAdministrationShell):
    result = client.get_asset_administration_shell_by_id(shared_aas.id)

    assert result is not None
    assert result.get("idShort", "") == shared_aas.id_short

def test_004b_get_asset_administration_shell_by_id(client: AasHttpClient):
    result = client.get_asset_administration_shell_by_id("non_existent_id")

    assert result is None

def test_005a_put_asset_administration_shell_by_id(client: AasHttpClient, shared_aas: model.AssetAdministrationShell):
    aas = model.AssetAdministrationShell(id_=shared_aas.asset_information.global_asset_id, asset_information=shared_aas.asset_information)
    aas.id_short = shared_aas.id_short

    description_text = "Put description for unit tests"
    aas.description = model.MultiLanguageTextType({"en": description_text})
    aas.submodel = shared_aas.submodel  # Keep existing submodels

    aas_data_string = json.dumps(aas, cls=basyx.aas.adapter.json.AASToJsonEncoder)
    aas_data = json.loads(aas_data_string)

    result = client.put_asset_administration_shell_by_id(shared_aas.id, aas_data)

    assert result

    get_result = client.get_asset_administration_shell_by_id(shared_aas.id)

    assert get_result
    assert get_result.get("idShort", "") == shared_aas.id_short
    assert get_result.get("id", "") == shared_aas.id
    # description must have changed
    assert get_result.get("description", {})[0].get("text", "") == description_text
    assert get_result.get("description", {})[0].get("text", "") != shared_aas.description.get("en", "")
    # submodels must be retained
    assert len(get_result.get("submodels", [])) == len(shared_aas.submodel)

    # The display name must be empty
    # currently not working in dotnet
    # assert len(get_result.get("displayName", {})) == 0

def test_005b_put_asset_administration_shell_by_id(client: AasHttpClient, shared_aas: model.AssetAdministrationShell):
    # put with other ID
    id_short = "put_short_id"
    asset_info = model_builder.create_base_asset_information(id_short)
    aas = model.AssetAdministrationShell(id_=asset_info.global_asset_id, asset_information=asset_info)
    aas.id_short = id_short

    description_text = {"en": "Updated description for unit tests"}
    aas.description = model.MultiLanguageTextType(description_text)

    aas_data_string = json.dumps(aas, cls=basyx.aas.adapter.json.AASToJsonEncoder)
    aas_data = json.loads(aas_data_string)

    result = client.put_asset_administration_shell_by_id(shared_aas.id, aas_data)

    assert not result

def test_006_get_asset_administration_shell_by_id_reference_aas_repository(client: AasHttpClient, shared_aas: model.AssetAdministrationShell):
    result = client.get_asset_administration_shell_by_id_reference_aas_repository(shared_aas.id)

    if JAVA_SERVER_PORT in client.base_url:
        # Basyx java server do not provide this endpoint
        assert result is None
    else:
        assert result is not None
        keys = result.get("keys", [])
        assert len(keys) == 1
        assert keys[0].get("value", "") == shared_aas.id

def test_007_get_submodel_by_id_aas_repository(client: AasHttpClient, shared_aas: model.AssetAdministrationShell, shared_sm: model.Submodel):
    result = client.get_submodel_by_id_aas_repository(shared_aas.id, shared_sm.id)

    assert result is None

def test_008_get_all_submodels(client: AasHttpClient):
    result = client.get_all_submodels()
    assert result is not None
    submodels = result.get("result", [])
    assert len(submodels) == 0

def test_009_post_submodel(client: AasHttpClient, shared_sm: model.Submodel):
    sm_data_string = json.dumps(shared_sm, cls=basyx.aas.adapter.json.AASToJsonEncoder)
    sm_data = json.loads(sm_data_string)

    result = client.post_submodel(sm_data)

    assert result is not None
    result_id_short = result.get("idShort", "")
    assert result_id_short == shared_sm.id_short

    get_result = client.get_all_submodels()
    assert get_result is not None
    submodels = get_result.get("result", [])
    assert len(submodels) == 1
    assert submodels[0].get("idShort", "") == shared_sm.id_short

def test_010_get_submodel_by_id_aas_repository(client: AasHttpClient, shared_aas: model.AssetAdministrationShell, shared_sm: model.Submodel):
    result = client.get_submodel_by_id_aas_repository(shared_aas.id, shared_sm.id)

    if JAVA_SERVER_PORT in client.base_url:
        # Basyx java server do not provide this endpoint
        assert result is None
    else:
        assert result is not None
        result_id_short = result.get("idShort", "")
        assert result_id_short == shared_sm.id_short

def test_011a_get_submodel_by_id(client: AasHttpClient, shared_sm: model.Submodel):
    result = client.get_submodel_by_id(shared_sm.id)

    assert result is not None
    result_id_short = result.get("idShort", "")
    assert result_id_short == shared_sm.id_short

def test_011b_get_submodel_by_id(client: AasHttpClient):
    result = client.get_submodel_by_id("non_existent_id")

    assert result is None

def test_012_patch_submodel_by_id(client: AasHttpClient, shared_sm: model.Submodel):
    sm = model.Submodel(shared_sm.id_short)
    sm.id_short = shared_sm.id_short

    description_text = "Patched description for unit tests"
    sm.description = model.MultiLanguageTextType({"en": description_text})

    sm_data_string = json.dumps(sm, cls=basyx.aas.adapter.json.AASToJsonEncoder)
    sm_data = json.loads(sm_data_string)

    result = client.patch_submodel_by_id(shared_sm.id, sm_data)

    if JAVA_SERVER_PORT in client.base_url:
        # Basyx java server do not provide this endpoint
        assert not result
    else:
        assert result

        get_result = client.get_submodel_by_id(shared_sm.id)
        assert get_result is not None
        assert get_result.get("idShort", "") == shared_sm.id_short
        assert get_result.get("id", "") == shared_sm.id
        # Only the description may change in patch.
        assert get_result.get("description", {})[0].get("text", "") == description_text
        assert get_result.get("description", {})[0].get("text", "") != shared_sm.description.get("en", "")
        # The display name must remain the same.
        assert get_result.get("displayName", {})[0].get("text", "") == shared_sm.display_name.get("en", "")

def test_013_put_submodel_by_id_aas_repository(client: AasHttpClient, shared_aas: model.AssetAdministrationShell, shared_sm: model.Submodel):
    sm = model.Submodel(shared_sm.id_short)
    sm.id_short = shared_sm.id_short

    description_text = "Put via shell description for unit tests"
    sm.description = model.MultiLanguageTextType({"en": description_text})

    sm_data_string = json.dumps(sm, cls=basyx.aas.adapter.json.AASToJsonEncoder)
    sm_data = json.loads(sm_data_string)

    result = client.put_submodel_by_id_aas_repository(shared_aas.id, shared_sm.id, sm_data)

    if JAVA_SERVER_PORT in client.base_url:
        # Basyx java server do not provide this endpoint
        assert not result
    else:
        assert result

        get_result = client.get_submodel_by_id_aas_repository(shared_aas.id, shared_sm.id)
        assert get_result is not None
        assert get_result.get("idShort", "") == shared_sm.id_short
        assert get_result.get("id", "") == shared_sm.id
        # description must have changed
        assert get_result.get("description", {})[0].get("text", "") == description_text
        assert get_result.get("description", {})[0].get("text", "") != shared_sm.description.get("en", "")
        assert len(get_result.get("displayName", {})) == 0

    # restore to its original state
    sm_data_string = json.dumps(shared_sm, cls=basyx.aas.adapter.json.AASToJsonEncoder)
    sm_data = json.loads(sm_data_string)
    client.put_submodel_by_id_aas_repository(shared_aas.id, shared_sm.id, sm_data)  # Restore original submodel

def test_014_put_submodels_by_id(client: AasHttpClient, shared_sm: model.Submodel):
    sm = model.Submodel(shared_sm.id_short)
    sm.id_short = shared_sm.id_short

    description_text = "Put description for unit tests"
    sm.description = model.MultiLanguageTextType({"en": description_text})

    sm_data_string = json.dumps(sm, cls=basyx.aas.adapter.json.AASToJsonEncoder)
    sm_data = json.loads(sm_data_string)

    result = client.put_submodels_by_id(shared_sm.id, sm_data)

    assert result

    get_result = client.get_submodel_by_id(shared_sm.id)
    assert get_result is not None
    assert get_result.get("idShort", "") == shared_sm.id_short
    assert get_result.get("id", "") == shared_sm.id
    # description must have changed
    assert get_result.get("description", {})[0].get("text", "") == description_text
    assert get_result.get("description", {})[0].get("text", "") != shared_sm.description.get("en", "")
    assert len(get_result.get("displayName", {})) == 0

    # restore to its original state
    sm_data_string = json.dumps(shared_sm, cls=basyx.aas.adapter.json.AASToJsonEncoder)
    sm_data = json.loads(sm_data_string)
    client.put_submodels_by_id(shared_sm.id, sm_data)  # Restore original submodel

def test_015_get_all_submodel_elements_submodel_repository(client: AasHttpClient, shared_sm: model.Submodel):
    submodel_elements = client.get_all_submodel_elements_submodel_repository(shared_sm.id)

    assert submodel_elements is not None
    assert len(submodel_elements.get("result", [])) == 0

def test_016_post_submodel_element_submodel_repo(client: AasHttpClient, shared_sm: model.Submodel, shared_sme: model.Property):
    sme_data_string = json.dumps(shared_sme, cls=basyx.aas.adapter.json.AASToJsonEncoder)
    sme_data = json.loads(sme_data_string)

    result = client.post_submodel_element_submodel_repo(shared_sm.id, sme_data)

    assert result is not None
    assert result.get("idShort", "") == shared_sme.id_short
    assert result.get("description", {})[0].get("text", "") == shared_sme.description.get("en", "")
    assert result.get("displayName", {})[0].get("text", "") == shared_sme.display_name.get("en", "")

    get_result = client.get_all_submodel_elements_submodel_repository(shared_sm.id)

    assert get_result is not None
    assert len(get_result.get("result", [])) == 1

def test_098_delete_asset_administration_shell_by_id(client: AasHttpClient, shared_aas: model.AssetAdministrationShell):
    result = client.delete_asset_administration_shell_by_id(shared_aas.id)

    assert result

    get_result = client.get_all_asset_administration_shells()
    assert get_result is not None
    shells = get_result.get("result", [])
    assert len(shells) == 0

def test_099_delete_submodel_by_id(client: AasHttpClient, shared_sm: model.Submodel):
    result = client.delete_submodel_by_id(shared_sm.id)

    assert result

    get_result = client.get_all_submodels()
    assert get_result is not None
    submodels = get_result.get("result", [])
    assert len(submodels) == 0

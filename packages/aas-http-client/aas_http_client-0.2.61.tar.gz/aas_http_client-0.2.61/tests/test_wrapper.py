import pytest
from pathlib import Path
from aas_http_client.wrapper.sdk_wrapper import create_wrapper_by_config, SdkWrapper
from basyx.aas import model
import aas_http_client.utilities.model_builder as model_builder

JAVA_SERVER_PORT = "8075"

CONFIG_FILES = [
    "./tests/server_configs/test_dotnet_server_config.json",
    "./tests/server_configs/test_java_server_config.json"
]

@pytest.fixture(params=CONFIG_FILES, scope="module")
def wrapper(request) -> SdkWrapper:
    try:
        file = Path(request.param).resolve()

        if not file.exists():
            raise FileNotFoundError(f"Configuration file {file} does not exist.")

        wrapper = create_wrapper_by_config(file, password="")
    except Exception as e:
        raise RuntimeError("Unable to connect to server.")

    shells = wrapper.get_all_asset_administration_shells()
    if shells is None:
        raise RuntimeError("No shells found on server. Please check the server configuration.")

    return wrapper

@pytest.fixture(scope="module")
def shared_sme() -> model.Property:
    # create a Submodel
    return model_builder.create_base_submodel_element_Property("sme_http_client_unit_tests", model.datatypes.String, "Sample Value")

@pytest.fixture(scope="module")
def shared_sm() -> model.Submodel:
    # create a Submodel
    submodel = model_builder.create_base_submodel("sm_http_client_unit_tests", "")
    submodel.category = "Unit Test"
    return submodel

@pytest.fixture(scope="module")
def shared_aas(shared_sm: model.Submodel) -> model.AssetAdministrationShell:
    # create an AAS
    aas = model_builder.create_base_ass(id_short="aas_http_client_unit_tests", namespace="")

    # add Submodel to AAS
    model_builder.add_submodel_to_aas(aas, shared_sm)

    return aas

def test_001_connect(wrapper: SdkWrapper):
    assert wrapper is not None

def test_002_get_all_asset_administration_shells(wrapper: SdkWrapper):
    shells = wrapper.get_all_asset_administration_shells()
    assert shells is not None
    assert len(shells) == 0

def test_003_post_asset_administration_shell(wrapper: SdkWrapper, shared_aas: model.AssetAdministrationShell):
    shell = wrapper.post_asset_administration_shell(shared_aas)

    assert shell is not None
    assert shell.id == shared_aas.id
    assert shell.id_short == shared_aas.id_short

    shells = wrapper.get_all_asset_administration_shells()
    assert shells is not None
    assert len(shells) == 1
    assert shells[0].id_short == shared_aas.id_short
    assert shells[0].id == shared_aas.id

def test_004a_get_asset_administration_shell_by_id(wrapper: SdkWrapper, shared_aas: model.AssetAdministrationShell):
    shell = wrapper.get_asset_administration_shell_by_id(shared_aas.id)

    assert shell is not None
    assert shell.id_short == shared_aas.id_short
    assert shell.id == shared_aas.id

def test_004b_get_asset_administration_shell_by_id(wrapper: SdkWrapper):
    shell = wrapper.get_asset_administration_shell_by_id("non_existent_id")

    assert shell is None

def test_005a_put_asset_administration_shell_by_id(wrapper: SdkWrapper, shared_aas: model.AssetAdministrationShell):
    aas = model.AssetAdministrationShell(id_=shared_aas.asset_information.global_asset_id, asset_information=shared_aas.asset_information)
    aas.id_short = shared_aas.id_short

    description_text = "Put description for unit tests"
    aas.description = model.MultiLanguageTextType({"en": description_text})
    aas.submodel = shared_aas.submodel  # Keep existing submodels

    result = wrapper.put_asset_administration_shell_by_id(shared_aas.id, aas)

    assert result

    shell = wrapper.get_asset_administration_shell_by_id(shared_aas.id)

    assert shell is not None
    assert shell.id_short == shared_aas.id_short
    assert shell.id == shared_aas.id
    # description must have changed
    assert shell.description.get("en", "") == description_text
    assert shell.description.get("en", "") != shared_aas.description.get("en", "")
    # submodels must be retained
    assert len(shell.submodel) == len(shared_aas.submodel)

    # The display name must be empty
    # currently not working in dotnet
    # assert len(get_result.get("displayName", {})) == 0

def test_005b_put_asset_administration_shell_by_id(wrapper: SdkWrapper, shared_aas: model.AssetAdministrationShell):
    # put with other ID
    id_short = "put_short_id"
    asset_info = model_builder.create_base_asset_information(id_short)
    aas = model.AssetAdministrationShell(id_=asset_info.global_asset_id, asset_information=asset_info)
    aas.id_short = id_short

    description_text = {"en": "Updated description for unit tests"}
    aas.description = model.MultiLanguageTextType(description_text)

    result = wrapper.put_asset_administration_shell_by_id(shared_aas.id, aas)

    assert not result

def test_006_get_asset_administration_shell_by_id_reference_aas_repository(wrapper: SdkWrapper, shared_aas: model.AssetAdministrationShell):
    reference = wrapper.get_asset_administration_shell_by_id_reference_aas_repository(shared_aas.id)

    assert reference is not None
    assert len(reference.key) == 1
    assert reference.key[0].value == shared_aas.id

def test_007_get_submodel_by_id_aas_repository(wrapper: SdkWrapper, shared_aas: model.AssetAdministrationShell, shared_sm: model.Submodel):
    submodel = wrapper.get_submodel_by_id_aas_repository(shared_aas.id, shared_sm.id)

    assert submodel is None

def test_008_get_all_submodels(wrapper: SdkWrapper):
    submodels = wrapper.get_all_submodels()
    assert submodels is not None
    assert len(submodels) == 0

def test_009_post_submodel(wrapper: SdkWrapper, shared_sm: model.Submodel):
    submodel = wrapper.post_submodel(shared_sm)

    assert submodel is not None
    assert submodel.id == shared_sm.id
    assert submodel.id_short == shared_sm.id_short

    submodels = wrapper.get_all_submodels()
    assert submodels is not None
    assert len(submodels) == 1
    assert submodels[0].id_short == shared_sm.id_short
    assert submodels[0].id == shared_sm.id

def test_010_get_submodel_by_id_aas_repository(wrapper: SdkWrapper, shared_aas: model.AssetAdministrationShell, shared_sm: model.Submodel):
    submodel = wrapper.get_submodel_by_id_aas_repository(shared_aas.id, shared_sm.id)

    if JAVA_SERVER_PORT in wrapper.base_url:
        # Basyx java server do not provide this endpoint
        assert submodel is None
    else:
        assert submodel is not None
        assert submodel.id_short == shared_sm.id_short
        assert submodel.id == shared_sm.id

def test_011a_get_submodel_by_id(wrapper: SdkWrapper, shared_sm: model.Submodel):
    submodel = wrapper.get_submodel_by_id(shared_sm.id)

    assert submodel is not None
    assert submodel.id_short == shared_sm.id_short
    assert submodel.id == shared_sm.id

def test_011b_get_submodel_by_id(wrapper: SdkWrapper):
    result = wrapper.get_submodel_by_id("non_existent_id")

    assert result is None

def test_012_patch_submodel_by_id(wrapper: SdkWrapper, shared_sm: model.Submodel):
    sm = model.Submodel(shared_sm.id_short)
    sm.id_short = shared_sm.id_short

    description_text = "Patched description for unit tests"
    sm.description = model.MultiLanguageTextType({"en": description_text})

    result = wrapper.patch_submodel_by_id(shared_sm.id, sm)

    if JAVA_SERVER_PORT in wrapper.base_url:
        # Basyx java server do not provide this endpoint
        assert not result
    else:
        assert result

        submodel = wrapper.get_submodel_by_id(shared_sm.id)
        assert submodel is not None
        assert submodel.id_short == shared_sm.id_short
        assert submodel.id == shared_sm.id
        # Only the description may change in patch.
        assert submodel.description.get("en", "") == description_text
        assert submodel.description.get("en", "") != shared_sm.description.get("en", "")
        # The display name must remain the same.
        assert submodel.display_name == shared_sm.display_name
        assert len(submodel.submodel_element) == len(shared_sm.submodel_element)

def test_013_put_submodel_by_id_aas_repository(wrapper: SdkWrapper, shared_aas: model.AssetAdministrationShell, shared_sm: model.Submodel):
    sm = model.Submodel(shared_sm.id_short)
    sm.id_short = shared_sm.id_short

    description_text = "Put via shell description for unit tests"
    sm.description = model.MultiLanguageTextType({"en": description_text})
    sm.display_name = shared_sm.display_name  # Keep existing display name because of problems with empty lists

    result = wrapper.put_submodel_by_id_aas_repository(shared_aas.id, shared_sm.id, sm)

    if JAVA_SERVER_PORT in wrapper.base_url:
        # Basyx java server do not provide this endpoint
        assert not result
    else:
        assert result

        submodel = wrapper.get_submodel_by_id_aas_repository(shared_aas.id, shared_sm.id)
        assert submodel is not None
        assert submodel.id_short == shared_sm.id_short
        assert submodel.id == shared_sm.id
        # description must have changed
        assert submodel.description.get("en", "") == description_text
        assert submodel.description.get("en", "") != shared_sm.description.get("en", "")
        # display name stays
        assert submodel.display_name == shared_sm.display_name
        # category was not set an must be empty
        assert submodel.category is None
        assert len(submodel.submodel_element) == 0

        # restore to its original state
        wrapper.put_submodel_by_id_aas_repository(shared_aas.id, shared_sm.id, shared_sm)  # Restore original submodel

def test_014_put_submodels_by_id(wrapper: SdkWrapper, shared_sm: model.Submodel):
    sm = model.Submodel(shared_sm.id_short)
    sm.id_short = shared_sm.id_short

    description_text = "Put description for unit tests"
    sm.description = model.MultiLanguageTextType({"en": description_text})
    sm.display_name = shared_sm.display_name  # Keep existing display name because of problems with empty lists

    result = wrapper.put_submodels_by_id(shared_sm.id, sm)

    assert result

    submodel = wrapper.get_submodel_by_id(shared_sm.id)
    assert submodel is not None
    assert submodel.id_short == shared_sm.id_short
    assert submodel.id == shared_sm.id
    # description must have changed
    assert submodel.description.get("en", "") == description_text
    assert submodel.description.get("en", "") != shared_sm.description.get("en", "")
    # display name stays
    # assert submodel.display_name == shared_sm.display_name
    # category was not set an must be empty
    assert submodel.category is None
    assert len(submodel.submodel_element) == 0

    # restore to its original state
    wrapper.put_submodels_by_id(shared_sm.id, shared_sm)  # Restore original submodel

def test_015_get_all_submodel_elements_submodel_repository(wrapper: SdkWrapper, shared_sm: model.Submodel):
    submodel_elements = wrapper.get_all_submodel_elements_submodel_repository(shared_sm.id)

    assert submodel_elements is not None
    assert len(submodel_elements) == 0

def test_016_post_submodel_element_submodel_repo(wrapper: SdkWrapper, shared_sm: model.Submodel, shared_sme: model.Property):
    submodel_element = wrapper.post_submodel_element_submodel_repo(shared_sm.id, shared_sme)

    assert submodel_element is not None

    # currently only dict is returned

    # property: model.Property = submodel_element

    # assert property.id_short == shared_sme.id_short
    # assert property.description.get("em", "") == shared_sme.description.get("en", "")
    # assert property.display_name.get("em", "")  == shared_sme.display_name.get("en", "")
    # assert property.value == shared_sme.value

    submodel_elements = wrapper.get_all_submodel_elements_submodel_repository(shared_sm.id)

    assert submodel_elements is not None
    assert len(submodel_elements) == 1

def test_098_delete_asset_administration_shell_by_id(wrapper: SdkWrapper, shared_aas: model.AssetAdministrationShell):
    result = wrapper.delete_asset_administration_shell_by_id(shared_aas.id)

    assert result

    shells = wrapper.get_all_asset_administration_shells()
    assert shells is not None
    assert len(shells) == 0

def test_099_delete_submodel_by_id(wrapper: SdkWrapper, shared_sm: model.Submodel):
    result = wrapper.delete_submodel_by_id(shared_sm.id)

    assert result

    submodels = wrapper.get_all_submodels()
    assert submodels is not None
    assert len(submodels) == 0

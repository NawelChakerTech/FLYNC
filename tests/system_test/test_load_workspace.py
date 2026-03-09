import pytest
from pathlib import Path
from flync.sdk.workspace.flync_workspace import FLYNCWorkspace
import shutil
from pydantic import ValidationError
from .helper import *
import allure

# ---------------- Allure Test Metadata ----------------
EPIC = "Workspace Loading"
FEATURE = [
    "Workspace Loads Successfully",
    "Workspace Missing Required Elements",
    "Workspace Configuration Validation"
]

# ---------------- Workspace Loads Successfully ----------------

# Verify loading workspace multiple times
absolute_path = Path(__file__).parents[2] / "examples" / "flync_example"
@allure.epic(EPIC)
@allure.feature(FEATURE[0])
@allure.title("Load Workspace Multiple Times")
@allure.description("Verify that the workspace can be loaded repeatedly without errors or state corruption.")
def test_load_workspace_multiple_times(tmpdir):
    for i in range(1, 4):
        destination_folder = Path(tmpdir) / f"copie{i}"
        shutil.copytree(absolute_path, destination_folder)
        workspace = FLYNCWorkspace.load_workspace(
            "flync_example", destination_folder
        )
        assert workspace is not None
        if destination_folder.exists():
            shutil.rmtree(destination_folder)


# Verify workspace loads with valid absolute path
@allure.epic(EPIC)
@allure.feature(FEATURE[0])
@allure.title("Load Workspace with Absolute Path")
@allure.description("Ensure the workspace loads correctly when an absolute path is provided.")
def test_load_workspace_valid_absolute_path():
    workspace = FLYNCWorkspace.load_workspace("flync_example", absolute_path)
    assert workspace is not None
    assert workspace.flync_model is not None
    assert workspace.flync_model.ecus
    assert workspace.flync_model.topology
    assert workspace.flync_model.topology.system_topology
    assert workspace.flync_model.general
    assert workspace.flync_model.general.someip_config
    assert workspace.flync_model.general.tcp_profiles
    assert workspace.flync_model.metadata
    assert model_has_socket(workspace)


# Verify workspace loads with valid relative path
relative_path = Path(Path(__file__).parent, "..", "..", "examples", "flync_example")
@allure.epic(EPIC)
@allure.feature(FEATURE[0])
@allure.title("Load Workspace with Relative Path")
@allure.description("Ensure the workspace loads correctly when a relative path is provided.")
def test_load_workspace_valid_relative_path():
    workspace = FLYNCWorkspace.load_workspace("flync_example", relative_path)
    assert workspace is not None
    assert workspace.flync_model is not None
    assert workspace.flync_model.ecus
    assert workspace.flync_model.topology
    assert workspace.flync_model.topology.system_topology
    assert workspace.flync_model.general
    assert workspace.flync_model.general.someip_config
    assert workspace.flync_model.general.tcp_profiles
    assert workspace.flync_model.metadata
    assert model_has_socket(workspace)


# Verify workspace loads with valid str path
@allure.epic(EPIC)
@allure.feature(FEATURE[0])
@allure.title("Load Workspace from String Path")
@allure.description("Test that the workspace can be loaded when a path is provided as a string.")
def test_load_workspace_valid_str_path():
    workspace = FLYNCWorkspace.load_workspace("flync_example", str(absolute_path))
    assert workspace is not None
    assert workspace.flync_model is not None
    assert workspace.flync_model.ecus
    assert workspace.flync_model.topology
    assert workspace.flync_model.topology.system_topology
    assert workspace.flync_model.general
    assert workspace.flync_model.general.someip_config
    assert workspace.flync_model.general.tcp_profiles
    assert workspace.flync_model.metadata
    assert model_has_socket(workspace)

# Verify documentation configuration example
@allure.epic(EPIC)
@allure.feature(FEATURE[0])
@allure.title("Load Workspace with Example Documentation")
@allure.description("Verify that the workspace example documentation loads correctly.")
def test_load_workspace_doc_exmaple(tmpdir):
    rst_file = (Path(__file__).parents[2] / "docs" / "source" / "flync_example.rst")
    example_folder = Path(tmpdir) / "copie"
    extract_example_from_rst(rst_file, example_folder, "Example Configuration")
    workspace = FLYNCWorkspace.load_workspace(str(example_folder.name), example_folder)
    assert workspace is not None
    assert example_folder.exists()
    if example_folder.exists():
        shutil.rmtree(example_folder)

# Verify workspace loading with added image (schema/diagram)
image_path = (Path(__file__).parents[2] / "docs" / "source"/ "_static"/ "technica-logo.png")
directories = [absolute_path] + [path for path in absolute_path.rglob("*") if path.is_dir()]
@pytest.mark.parametrize("dir", directories)
@allure.epic(EPIC)
@allure.feature(FEATURE[0])
@allure.title("Add Image to Workspace")
@allure.description("Verify that adding an image to the workspace {dir} succeeds and is recognized.")
def test_load_workspace_add_image(tmpdir, dir):
    destination_folder = Path(tmpdir) / "copie"
    shutil.copytree(absolute_path, destination_folder)
    path_to_add = destination_folder / dir.relative_to(absolute_path)
    shutil.copy(image_path, path_to_add)
    workspace = FLYNCWorkspace.load_workspace("flync_example", destination_folder)
    assert workspace is not None
    if destination_folder.exists():
        shutil.rmtree(destination_folder)

# ---------------- Workspace Missing Required Elements ----------------

# Verify the existence of attributes
required_attributes = [
    "name",
    "documents",
    "objects",
    "sources",
    "dependencies",
    "reverse_deps",
    "_diagnostics",
]
@pytest.mark.parametrize("attribute", required_attributes)
@allure.epic(EPIC)
@allure.feature(FEATURE[1])
@allure.title("Validate Workspace Attribute Existence")
@allure.description("Check that the workspace contains the required {attribute} attribute")
def test_load_workspace_exsistence_attribute(attribute):
    workspace = FLYNCWorkspace.load_workspace("flync_example", absolute_path)
    assert hasattr(workspace, attribute), f"Workspace is missing attribute: {attribute}"

# Verify handling missing mandatory directory
subfolders = [
    Path(absolute_path, "ecus"),
    *Path(absolute_path).glob("ecus/*/controllers"),
]
@pytest.mark.parametrize("subfolder", subfolders)
@allure.epic(EPIC)
@allure.feature(FEATURE[1])
@allure.title("Detect Missing Mandatory Folder")
@allure.description("Ensure an error is raised if a required workspace folder {subfolder} is missing.")
def test_load_workspace_missing_mandatory_folder(tmpdir, subfolder):
    destination_folder = Path(tmpdir) / "copie"
    shutil.copytree(absolute_path, destination_folder)
    shutil.rmtree(destination_folder / subfolder.relative_to(absolute_path))
    with pytest.raises(FileNotFoundError):
        FLYNCWorkspace.load_workspace("flync_example", destination_folder)
    if destination_folder.exists():
        shutil.rmtree(destination_folder)

# Verify handling missing mandatory file
files = [
    Path(absolute_path, "system_metadata.flync.yaml"),
    *Path(absolute_path).glob("ecus/*/ports.flync.yaml"),
    *Path(absolute_path).glob("ecus/*/topology.flync.yaml"),
    *Path(absolute_path).glob("ecus/*/ecu_metadata.flync.yaml"),
    *Path(absolute_path).glob("ecus/*/controllers/*"),
]
@pytest.mark.parametrize("file", files)
@allure.epic(EPIC)
@allure.feature(FEATURE[1])
@allure.title("Detect Missing Mandatory File")
@allure.description("Ensure an error is raised if a required workspace file {file} is missing.")
def test_load_workspace_missing_mandatory_file(tmpdir, file):
    destination_folder = Path(tmpdir) / "copie"
    shutil.copytree(absolute_path, destination_folder)
    path_to_remove = destination_folder / file.relative_to(absolute_path)
    path_to_remove.unlink()
    with pytest.raises(ValidationError) as exc:
        FLYNCWorkspace.load_workspace("flync_example", destination_folder)
    assert type(exc.value) is ValidationError
    if destination_folder.exists():
        shutil.rmtree(destination_folder)

# ---------------- Workspace Configuration Validation ----------------

# Verify handling invalid workspace name
@allure.epic(EPIC)
@allure.feature(FEATURE[2])
@allure.title("Handle Invalid Workspace Name")
@allure.description("Test workspace loading behavior when the name is invalid.")
def test_load_workspace_invalid_name():
    with pytest.raises(Exception):
        FLYNCWorkspace.load_workspace("", absolute_path)


# Verify handling invalid workspace directory path
@allure.epic(EPIC)
@allure.feature(FEATURE[2])
@allure.title("Load Workspace from String Path")
@allure.description("Test that the workspace can be loaded when a path is provided as a string.")
def test_load_workspace_invalid_yaml_path():
    with pytest.raises(FileNotFoundError):
        FLYNCWorkspace.load_workspace("flync_example", "/path/to/nonexistent/directory")

# Verify handling unsupported file format
files = [
    Path(absolute_path, "system_metadata.flync.yaml"),
    *Path(absolute_path).glob("ecus/*/ports.flync.yaml"),
    *Path(absolute_path).glob("ecus/*/topology.flync.yaml"),
    *Path(absolute_path).glob("ecus/*/ecu_metadata.flync.yaml"),
    *Path(absolute_path).glob("ecus/*/controllers/*"),
]
@pytest.mark.parametrize("file", files)
@allure.epic(EPIC)
@allure.feature(FEATURE[2])
@allure.title("Handle Invalid Workspace Format")
@allure.description("Ensure the workspace loader rejects unsupported formats {file}.")
def test_load_workspace_invalid_format(tmpdir, file):
    destination_folder = Path(tmpdir) / "copie"
    shutil.copytree(absolute_path, destination_folder)
    file_to_rename = destination_folder / file.relative_to(absolute_path)
    new_file_name = file_to_rename.name[: -len(".flync.yaml")] + "yaml"
    new_file_path = file_to_rename.with_name(new_file_name)
    file_to_rename.rename(new_file_path)
    with pytest.raises(ValidationError):
        FLYNCWorkspace.load_workspace("flync_example", destination_folder)
    if destination_folder.exists():
        shutil.rmtree(destination_folder)


# Verify handling case sensitivity for keys
@allure.epic(EPIC)
@allure.feature(FEATURE[2])
@allure.title("Handle Uppercase Keys in Workspace")
@allure.description("Validate that workspace keys must follow the expected lowercase format.")
def test_load_workspace_upper_key(tmpdir):
    destination_folder = Path(tmpdir) / "copie"
    shutil.copytree(absolute_path, destination_folder)
    file_to_update = (destination_folder/ "ecus"/ "eth_ecu"/ "controllers"/ "eth_ecu_controller1.flync.yaml")
    update_yaml_content(file_to_update, 
                        "name", "NAME"
    )
    with pytest.raises(ValidationError) as exc_info:
        FLYNCWorkspace.load_workspace("flync_example", destination_folder)
    assert "name\n  Field required" in str(exc_info.value)
    if destination_folder.exists():
        shutil.rmtree(destination_folder)


# Verify handling incorrect type for value
@allure.epic(EPIC)
@allure.feature(FEATURE[2])
@allure.title("Detect Incorrect Value Type")
@allure.description("Ensure workspace fails when a key has a value of the wrong type.")
def test_load_workspace_incorret_value_type(tmpdir):
    destination_folder = Path(tmpdir) / "copie"
    shutil.copytree(absolute_path, destination_folder)
    file_to_update = (destination_folder/ "ecus"/ "eth_ecu"/ "controllers"/ "eth_ecu_controller1.flync.yaml")
    update_yaml_content(file_to_update, 
                        "name: eth_ecu_controller1", "name: 123"
    )
    with pytest.raises(ValidationError) as exc_info:
        FLYNCWorkspace.load_workspace("flync_example", destination_folder)
    assert "name\n  Input should be a valid string" in str(exc_info.value)
    if destination_folder.exists():
        shutil.rmtree(destination_folder)


# Verify handling of incorrect MAC address format
invalid_format = {
    "001122334455": "mac_address_format\n  Must have the format",
    "00:11:22:33:xx:XX": "mac_address\n  Unrecognized format",
    "00:11:22": "mac_address\n  Length for a 00:11:22 MAC address must be 14",
}
@pytest.mark.parametrize("key, value", invalid_format.items())
@allure.epic(EPIC)
@allure.feature(FEATURE[2])
@allure.title("Detect Incorrect Value Format")
@allure.description("Verify validation error for invalid MAC address {key}. Message: {value}.")
def test_load_workspace_incorrect_mac_address_format(tmpdir, key, value):
    destination_folder = Path(tmpdir) / "copie"
    shutil.copytree(absolute_path, destination_folder)
    file_to_update = (destination_folder/ "ecus"/ "eth_ecu"/ "controllers"/ "eth_ecu_controller1.flync.yaml")
    update_yaml_content(file_to_update, 
                        "mac_address: 00:11:22:33:44:55", f"mac_address: {key}"
    )
    with pytest.raises(ValidationError) as exc_info:
        FLYNCWorkspace.load_workspace("flync_example", destination_folder)
    assert value in str(exc_info.value)
    if destination_folder.exists():
        shutil.rmtree(destination_folder)


# Validate handling of extra key/value
@allure.epic(EPIC)
@allure.feature(FEATURE[2])
@allure.title("Detect Extra Key/Value")
@allure.description("Ensure unexpected key-value pairs are handled correctly.")
def test_load_workspace_extra_key_value(tmpdir):
    destination_folder = Path(tmpdir) / "copie"
    shutil.copytree(absolute_path, destination_folder)
    file_to_update = (destination_folder/ "ecus"/ "eth_ecu"/ "controllers"/ "eth_ecu_controller1.flync.yaml")
    append_yaml_content(file_to_update, 
                        "\nnew_value: something\n"
    )
    with pytest.raises(ValidationError) as exc_info:
        FLYNCWorkspace.load_workspace("flync_example", destination_folder)
    assert "new_value\n  Extra inputs are not permitted" in str(exc_info.value)
    if destination_folder.exists():
        shutil.rmtree(destination_folder)


# Verify handling indentation fault
@allure.epic(EPIC)
@allure.feature(FEATURE[2])
@allure.title("Handle Misplaced Key/Value")
@allure.description("Validate that key-value pairs in the wrong location are flagged.")
def test_load_workspace_key_value_misplaced(tmpdir):
    destination_folder = Path(tmpdir) / "copie"
    shutil.copytree(absolute_path, destination_folder)
    file_to_update = (destination_folder/ "ecus"/ "eth_ecu"/ "controllers"/ "eth_ecu_controller1.flync.yaml")
    update_yaml_content(file_to_update, 
                        "  mode: mac", "mode: mac"
    )
    with pytest.raises(ValidationError) as exc_info:
        FLYNCWorkspace.load_workspace("flync_example", destination_folder)
    assert "interfaces.0.mii_config.sgmii.mode\n  Field required" in str(exc_info.value)
    assert "interfaces.0.mode\n  Extra inputs are not permitted" in str(exc_info.value)
    if destination_folder.exists():
        shutil.rmtree(destination_folder)


# Verify handling duplicate keys
@allure.epic(EPIC)
@allure.feature(FEATURE[2])
@allure.title("Detect Duplicate Key")
@allure.description("Ensure duplicate keys in the workspace configuration are not allowed.")
def test_load_workspace_duplicate_key(tmpdir):
    destination_folder = Path(tmpdir) / "copie"
    shutil.copytree(absolute_path, destination_folder)
    file_to_update = (destination_folder/ "ecus"/ "eth_ecu"/ "controllers"/ "eth_ecu_controller1.flync.yaml")
    update_yaml_content(
        file_to_update,
        "mac_address: 00:11:22:33:44:55",
        "mac_address: 00:11:22:33:44:55\n    mac_address: 11:22:33:44:55:66",
    )
    with pytest.raises(Exception):
        FLYNCWorkspace.load_workspace("flync_example", destination_folder)
    if destination_folder.exists():
        shutil.rmtree(destination_folder)


# Verify handling missing dashe in list items
@allure.epic(EPIC)
@allure.feature(FEATURE[2])
@allure.title("Detect Missing Dash in Keys")
@allure.description("Verify that missing dash formatting in keys triggers an error.")
def test_load_workspace_missing_dashe(tmpdir):
    destination_folder = Path(tmpdir) / "copie"
    shutil.copytree(absolute_path, destination_folder)
    file_to_update = (destination_folder/ "ecus"/ "eth_ecu"/ "controllers"/ "eth_ecu_controller1.flync.yaml")
    update_yaml_content(
        file_to_update,
        "multicast:\n          - 224.0.0.23",
        "multicast:\n           224.0.0.23",
    )
    with pytest.raises(ValidationError) as exc_info:
        FLYNCWorkspace.load_workspace("flync_example", destination_folder)
    assert "multicast\n  Input should be a valid list" in str(exc_info.value)
    if destination_folder.exists():
        shutil.rmtree(destination_folder)


# Verify handling missing key/value
@allure.epic(EPIC)
@allure.feature(FEATURE[2])
@allure.title("Detect Missing Key/Value")
@allure.description("Ensure that missing key-value pairs are detected and raise an error.")
def test_load_workspace_missing_key_value(tmpdir):
    destination_folder = Path(tmpdir) / "copie"
    shutil.copytree(absolute_path, destination_folder)
    file_to_update = (destination_folder/ "ecus"/ "eth_ecu"/ "controllers"/ "eth_ecu_controller1.flync.yaml")
    update_yaml_content(file_to_update, 
                        "name: eth_ecu_controller1", ""
    )
    with pytest.raises(ValidationError) as exc_info:
        FLYNCWorkspace.load_workspace("flync_example", destination_folder)
    assert "name\n  Field required" in str(exc_info.value)
    if destination_folder.exists():
        shutil.rmtree(destination_folder)
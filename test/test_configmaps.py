import os
import shutil
import tempfile
from unittest.mock import patch

import pytest as pytest

import data
from composition.storage import write_compose


@patch("composition.storage.append_to_app_config")
@patch("composition.storage.get_compose_path")
@patch("composition.storage.get_compose_loc")
def test_config_map_valid(mock_compose_loc, mock_compose_path, mock_app_config_append):
    temp_file = tempfile.mkdtemp()
    # The .composer location
    hidden_composer_file = os.path.join(temp_file, "composer_hidden")
    composer_app_files = os.path.join(hidden_composer_file, "app")
    os.mkdir(hidden_composer_file)
    mock_compose_loc.return_value = hidden_composer_file
    mock_compose_path.return_value = composer_app_files
    # The location of the templates
    template_file_location = os.path.join(temp_file, "templates")
    os.mkdir(template_file_location)
    # The location the config map templates
    config_map_dir = os.path.join(template_file_location, "subDir")
    os.mkdir(config_map_dir)
    config_map_location = os.path.join(config_map_dir, "myconfig.configmap")
    # docker-compose.yaml path
    compose_yaml_path = os.path.join(template_file_location, "docker-compose.yaml")
    # Call the function
    write_compose("anId", data.test_compose_string, data.test_details, compose_yaml_path, template_file_location, config_strs=[
        {
            "filename": config_map_location,
            "content": "{ 'hello': 'world' }"
        }
    ])
    assert os.path.exists(os.path.join(composer_app_files, "subDir", "myconfig.configmap"))
    # Remove the tmpfile
    shutil.rmtree(temp_file)

if __name__ == "__main__":
    pytest.main()
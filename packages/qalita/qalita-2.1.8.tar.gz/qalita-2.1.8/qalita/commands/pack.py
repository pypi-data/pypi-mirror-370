"""
# QALITA (c) COPYRIGHT 2025 - ALL RIGHTS RESERVED -
"""

import click
import json
import os
import sys
import subprocess
import yaml
import logging
import base64
import re
from threading import Thread
from tabulate import tabulate
from qalita.internal.error_patterns import ERROR_PATTERNS
from qalita.cli import pass_config
from qalita.internal.utils import logger, make_tarfile, ask_confirmation
from qalita.internal.request import send_request

loggerPack = logging.getLogger(__name__)


def handle_stderr_line(read):
    """
    Determine the appropriate logging level for a line from stderr.
    Returns a logging level based on the content of the line.
    """
    for pattern, log_level in ERROR_PATTERNS.items():
        if re.search(pattern, read, re.IGNORECASE):
            return log_level
    return "INFO"


def pack_logs(pipe, loggers, error=False):
    while True:
        line = pipe.readline()
        if line:
            line = line.strip()
            if error:
                log_level = handle_stderr_line(line)
                for logger in loggers:
                    if log_level == "INFO":
                        logger.info(line)
                    else:
                        logger.error(line)
                        global has_errors
                        has_errors = True
            else:
                for logger in loggers:
                    logger.info(line)
        else:
            break


def setup_logger(pack_file_path):
    loggerPack.setLevel(logging.INFO)
    # Remove existing file handlers
    for handler in loggerPack.handlers[:]:
        if isinstance(handler, logging.FileHandler):
            loggerPack.removeHandler(handler)

    # Create new log file path
    new_log_file_path = os.path.join(pack_file_path, "logs.txt")

    # Add new file handler
    handler = logging.FileHandler(new_log_file_path)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    loggerPack.addHandler(handler)
    return loggerPack


def run_pack(pack_file_path):
    global has_errors
    has_errors = False
    loggerPack = setup_logger(pack_file_path)
    loggerPack.info("------------- Pack Run -------------")
    logger.info("------------- Pack Run -------------")

    # Check if the run.sh file exists
    run_script = "run.sh"  # Only the script name is needed now
    if not os.path.isfile(os.path.join(pack_file_path, run_script)):
        loggerPack.error(
            f"run.sh script does not exist in the package folder {pack_file_path}"
        )
        return 1

    # Run the run.sh script and get the output
    process = subprocess.Popen(
        ["sh", run_script],
        cwd=pack_file_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )

    stdout_thread = Thread(
        target=pack_logs, args=(process.stdout, [loggerPack, logger])
    )
    stderr_thread = Thread(
        target=pack_logs, args=(process.stderr, [loggerPack, logger], True)
    )

    stdout_thread.start()
    stderr_thread.start()

    stdout_thread.join()
    stderr_thread.join()

    retcode = process.poll()

    # Decide the return value based on the has_errors flag
    if has_errors:
        loggerPack.error("Pack failed")
        logger.error("Pack failed")
        return 1
    else:
        loggerPack.info("Pack run completed")
        logger.info("Pack run completed")
        return 0


def check_name(name):
    all_check_pass = True
    if not name:
        logger.error("Error: Pack name is required!")
        logger.info("\tTo do so, you can set an Environment Variable : ")
        logger.info("\t\texport QALITA_PACK_NAME='mypack'")
        logger.info("\tor add the name as a commandline argument : ")
        logger.info("\t\tqalita pack --name 'mypack'")
        logger.info(
            "\tthe prefered way is to create a file '.env-local' with the values : "
        )
        logger.info("\t\tQALITA_PACK_NAME=mypack")
        logger.info("\tand source it : ")
        logger.info("\t\texport $(xargs < .env-local)")
        all_check_pass = False
    else:
        # Normalize the pack name by removing '_pack' or '_pack/' if present
        if name.endswith("_pack") or name.endswith("_pack/"):
            name = name.replace("_pack", "").rstrip("/")
        logger.info(f"Normalized pack name: {name}/")
    if all_check_pass:
        return name
    else:
        sys.exit(1)


@click.group()
@click.option("-p", "--pack", type=int, help="Pack ID")
@click.pass_context
def pack(ctx, pack):
    """Manage Qalita Platform Packs"""
    ctx.ensure_object(dict)
    ctx.obj["PACK"] = pack


@pack.command()
@pass_config
def list(config):
    """List all available packs"""
    tab_packs = []
    agent_conf = config.load_agent_config()
    headers = ["ID", "Name", "Description", "Visibility", "Type", "Partner"]

    partners = send_request(
        request=f"{agent_conf['context']['local']['url']}/api/v1/partners", mode="get"
    )

    if partners.status_code == 200:
        partners = partners.json()
        for partner in partners:
            headers.append(partner["name"])

            r = send_request(
                request=f"{agent_conf['context']['local']['url']}/api/v2/packs",
                mode="get",
            )
            if r.status_code == 200:
                packs = r.json()
                for pack in packs:
                    tab_packs.append(
                        [
                            pack.get("id", ""),
                            pack.get("name", ""),
                            pack.get("description", ""),
                            pack.get("visibility", ""),
                            pack.get("type", ""),
                            partner["name"],
                        ]
                    )
            elif r.status_code == 204:
                pass
            else:
                logger.error(
                    f"Error cannot fetch pack list, make sure you are logged in with > qalita agent login : {r.status_code} - {r.reason}"
                )
                return

    print(tabulate(tab_packs, headers, tablefmt="simple"))


@pass_config
def validate_pack(config, name):
    """Validates pack arborescence, configurations etc...."""
    logger.info("------------- Pack Validation -------------")
    error_count = 0
    pack_folder = f"{name}_pack"
    if not os.path.exists(pack_folder):
        logger.error(f"Pack folder '{pack_folder}' does not exist.")
        logger.error("Please run the command from the parent path of the pack folder.")
        sys.exit(1)
        error_count += 1

    mandatory_files = ["run.sh", "properties.yaml", "README.md"]
    for file in mandatory_files:
        file_path = os.path.join(pack_folder, file)
        if not os.path.exists(file_path):
            logger.error(f"Mandatory file '{file}' does not exist in the pack.")
            error_count += 1
        else:
            with open(file_path, "r") as f:
                content = f.read()
                if not content:
                    logger.error(f"File '{file}' is empty.")
                    error_count += 1
                if file == "properties.yaml":
                    properties = yaml.safe_load(content)
                    if "name" not in properties or properties["name"] != name:
                        logger.error(
                            f"Pack name in 'properties.yaml' is not set correctly."
                        )
                        error_count += 1
                    if "version" not in properties:
                        logger.error(f"Version in 'properties.yaml' is not set.")
                        error_count += 1

                    if "type" not in properties:
                        logger.error(f"Type in 'properties.yaml' is not set.")
                        error_count += 1

                    if "visibility" not in properties:
                        logger.warning(
                            f"Visibility in 'properties.yaml' is not set. Defaulting to [Private]"
                        )
                        properties["visibility"] = "private"

        # save file
        if file == "properties.yaml":
            try:
                with open(file_path, "w") as f:
                    yaml.dump(properties, f)
            except:
                logger.error(f"Error saving file '{file}'")
                error_count += 1

    if error_count == 0:
        logger.success(f"Pack [{name}] validated")
    else:
        logger.error(f"{error_count} error(s) found during pack validation.")

    return error_count


@pack.command()
@click.option(
    "-n",
    "--name",
    help="The name of the package, it will be used to identify the package in the Qalita platform",
    envvar="QALITA_PACK_NAME",
)
@pass_config
def validate(config, name):
    """validates pack arborescence, configurations etc...."""
    validate_pack(name)


def push_pack(api_url, registry_id, pack_name, pack_version):
    logger.info("Starting pack push...")
    output_filename = f"{pack_name}.tar.gz"
    make_tarfile(output_filename, f"./{pack_name}_pack")
    upload_response = send_request(
        request=f"{api_url}/api/v1/assets/upload",
        mode="post-multipart",
        file_path=output_filename,
        query_params={
            "registry_id": registry_id,
            "name": pack_name,
            "version": pack_version,
            "bucket": "packs",
            "type": "pack",
            "description": "pack binary asset",
        },
    )

    if os.path.exists(output_filename):
        os.remove(output_filename)

    if upload_response.status_code == 200:
        logger.success("Pack asset uploaded successfully.")
    else:
        logger.error(
            f"Failed to upload pack asset. Error: {upload_response.status_code} - {upload_response.text}"
        )

    return upload_response.json() if upload_response.status_code == 200 else None


def load_pack_properties(pack_directory):
    """Loads the properties.yaml file from the specified pack directory."""
    properties_file = f"{pack_directory}/properties.yaml"
    if not os.path.exists(properties_file):
        logger.error(f"Pack properties file '{properties_file}' not found.")
        return None
    try:
        with open(properties_file, "r") as file:
            return yaml.safe_load(file)
    except Exception as e:
        logger.error(f"Failed to load properties.yaml: {str(e)}")
        return None


def load_base64_encoded_image(file_path):
    """Loads an image file and returns its content as a base64-encoded string."""
    if os.path.exists(file_path):
        try:
            with open(file_path, "rb") as file:
                return base64.b64encode(file.read()).decode("utf-8")
        except Exception as e:
            logger.error(f"Error encoding image at {file_path}: {str(e)}")
            return ""
    return ""


def load_base64_encoded_text(file_path):
    """Loads a text file (e.g., README.md) and returns its content as a base64-encoded string."""
    if os.path.exists(file_path):
        try:
            with open(file_path, "rb") as file:
                return base64.b64encode(file.read()).decode("utf-8")
        except Exception as e:
            logger.error(f"Error encoding text at {file_path}: {str(e)}")
            return ""
    return ""


def load_json_config(file_path):
    """Loads a JSON configuration file from the specified path."""
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as file:
                return json.load(file)
        except Exception as e:
            logger.error(f"Error loading JSON config from {file_path}: {str(e)}")
            return {}
    return {}


def _normalize_pack_name_for_compare(name: str) -> str:
    """Normalize pack names for comparison.

    In properties.yaml, spaces are replaced by underscores.
    We mirror that logic here so that 'data compare' == 'data_compare'.
    """
    if not isinstance(name, str):
        return ""
    # Trim and replace any whitespace runs with single underscore
    normalized = re.sub(r"\s+", "_", name.strip())
    return normalized


def find_existing_pack(api_url, pack_name):
    """Checks if the pack already exists in the system and returns its ID and versions."""
    response = send_request(f"{api_url}/api/v2/packs", "get")
    if response and response.status_code == 200:
        existing_packs = response.json()
        wanted = _normalize_pack_name_for_compare(pack_name)
        for pack in existing_packs:
            existing_name = _normalize_pack_name_for_compare(pack.get("name", ""))
            if existing_name == wanted:
                return pack["id"], pack.get("versions", [])
    return None, []


def update_pack_metadata(
    api_url,
    pack_id,
    pack_icon,
    pack_config,
    pack_type,
    pack_description,
    pack_url,
    pack_version,
    pack_visibility,
    readme,
):
    """Updates the metadata of an existing pack."""
    update_data = {
        "avatar": pack_icon,
        "config": json.dumps(pack_config, separators=(",", ":")),
        "type": pack_type,
        "description": pack_description,
        "url": pack_url,
        "version": pack_version,
        "visibility": pack_visibility,
        "readme": readme,
    }
    update_response = send_request(
        f"{api_url}/api/v2/packs/{pack_id}", "put", data=update_data
    )
    if update_response and update_response.status_code == 200:
        return
    else:
        logger.error("Failed to update pack metadata.")


def publish_new_pack_version(api_url, pack_id, pack_version, registry_id, pack_name):
    """Pushes a new version of the pack."""
    asset_data = push_pack(api_url, registry_id, pack_name, pack_version)
    publish_response = send_request(
        f"{api_url}/api/v1/packs/{pack_id}/version",
        "put",
        query_params={
            "sem_ver_id": pack_version,
            "asset_id": asset_data["id"],
        },
    )
    if publish_response and publish_response.status_code == 200:
        logger.success("New pack version published successfully!")
    else:
        logger.error("Failed to publish new pack version.")


def create_new_pack(
    api_url,
    registry_id,
    pack_name,
    pack_icon,
    pack_config,
    pack_type,
    pack_description,
    pack_url,
    pack_version,
    pack_visibility,
    readme,
):
    """Creates a new pack and pushes it to the system."""
    create_data = {
        "name": pack_name.replace("_", " ").replace("-", " "),
        "type": pack_type,
        "avatar": pack_icon,
        "visibility": pack_visibility,
        "config": json.dumps(pack_config),
        "description": pack_description,
        "url": pack_url,
        "readme": readme,
    }
    create_response = send_request(
        f"{api_url}/api/v1/packs/publish", "post", data=create_data
    )
    if create_response and create_response.status_code == 200:
        logger.success("Pack created successfully!")
        pack_id = create_response.json().get("id")
        publish_new_pack_version(
            api_url,
            pack_id,
            pack_version,
            registry_id,
            pack_name,
        )

    else:
        logger.error("Failed to create new pack metadata.")


def handle_version_matching(existing_versions, new_version):
    """Handles the version matching logic and decides whether to update or add new version assets."""
    # Search for existing version in the list
    matching_versions = [v for v in existing_versions if v["sem_ver_id"] == new_version]

    if not matching_versions:
        # If the version does not exist, add the new version to the list
        return {"sem_ver_id": new_version}

    # Otherwise, none
    return None


@pack.command()
@click.option("-n", "--name", help="Name of the package", envvar="QALITA_PACK_NAME")
@pass_config
def push(config, name):
    """Pushes a package to the Qalita Platform"""

    try:
        name = check_name(name)
        error_count = validate_pack(name)
        if error_count > 0:
            logger.error(
                ">> There are errors with your pack, please resolve them before pushing it."
            )
            return

        if not name:
            logger.error("Invalid package name.")
            return

        logger.info("---------------- Pack Push ----------------")
        logger.info(f"Pushing pack '{name}' to Qalita Platform...")

        pack_directory = f"./{name}_pack" if not name.endswith("_pack") else f"./{name}"

        # Load pack properties
        pack_properties = load_pack_properties(pack_directory)
        if not pack_properties:
            logger.error("Failed to load pack properties.")
            return

        # Load agent configuration
        agent_conf = config.load_agent_config()
        if not agent_conf:
            logger.error("Failed to load agent configuration.")
            return

        # Extract pack details
        pack_name = pack_properties.get("name")
        pack_version = pack_properties.get("version")
        pack_description = pack_properties.get("description", "")
        pack_url = pack_properties.get("url", "")
        pack_type = pack_properties.get("type", "")
        pack_visibility = pack_properties.get("visibility", "private")

        # Handle pack icon
        pack_icon = load_base64_encoded_image(f"{pack_directory}/icon.png")

        # Handle README file
        readme = load_base64_encoded_text(f"{pack_directory}/README.md")

        # Load pack config
        pack_config = load_json_config(f"{pack_directory}/pack_conf.json")

        # Check existing packs and versions
        pack_id, existing_versions = find_existing_pack(
            agent_conf["context"]["local"]["url"], pack_name
        )

        if pack_id:
            # Handle version matching and decide whether to add a new asset or update metadata
            new_version_entry = handle_version_matching(existing_versions, pack_version)

            if not new_version_entry:
                update_pack_metadata(
                    agent_conf["context"]["local"]["url"],
                    pack_id,
                    pack_icon,
                    pack_config,
                    pack_type,
                    pack_description,
                    pack_url,
                    pack_version,
                    pack_visibility,
                    readme,
                )
                logger.success("Pack metadata updated successfully!")
            else:
                publish_new_pack_version(
                    agent_conf["context"]["local"]["url"],
                    pack_id,
                    pack_version,
                    agent_conf["registries"][0]["id"],
                    pack_name,
                )
        else:
            create_new_pack(
                agent_conf["context"]["local"]["url"],
                agent_conf["registries"][0]["id"],
                pack_name,
                pack_icon,
                pack_config,
                pack_type,
                pack_description,
                pack_url,
                pack_version,
                pack_visibility,
                readme,
            )
            logger.success("New pack created successfully!")

        logger.info("Pack pushed successfully.")

    except Exception as e:
        logger.error(f"Failed to push pack: {str(e)}")
        raise e


@pack.command()
@click.option(
    "-n",
    "--name",
    help="The name of the package, it will be used to identify the package in the Qalita platform",
    envvar="QALITA_PACK_NAME",
)
def run(name):
    """Dry run a pack"""
    # Validation of required options
    all_check_pass = True
    if not name:
        logger.error("Error: Pack name is required!")
        logger.info("\tTo do so, you can set an Environment Variable : ")
        logger.info("\t\texport QALITA_PACK_NAME='mypack'")
        logger.info("\tor add the name as a commandline argument : ")
        logger.info("\t\tqalita pack --name 'mypack'")
        logger.info(
            "\tthe prefered way is to create a file '.env-local' with the values : "
        )
        logger.info("\t\tQALITA_PACK_NAME=mypack")
        logger.info("\tand source it : ")
        logger.info("\t\texport $(xargs < .env-local)")
        all_check_pass = False
    if not all_check_pass:
        return

    # Check if the pack folder exists
    pack_folder = os.path.join(os.getcwd(), name) + "_pack"
    if not os.path.exists(pack_folder):
        logger.error(f"Package folder {pack_folder} does not exist")
        return

    # Check if the run.sh file exists
    run_script = "run.sh"  # Only the script name is needed now
    if not os.path.isfile(os.path.join(pack_folder, run_script)):
        logger.error(
            f"run.sh script does not exist in the package folder {pack_folder}"
        )
        return

    status = run_pack(pack_folder)

    if status == 0:
        logger.success("Pack Run Success")
    else:
        logger.error("Pack Run Failed")


@pack.command()
@click.option(
    "-n",
    "--name",
    help="The name of the package, it will be used to identify the package in the Qalita platform",
    envvar="QALITA_PACK_NAME",
)
@pass_config
def init(config, name):
    """Initialize a pack"""
    # Validation of required options
    all_check_pass = True
    if not name:
        logger.error("Error: Pack name is required!")
        logger.info("\tTo do so, you can set an Environment Variable : ")
        logger.info("\t\texport QALITA_PACK_NAME='mypack'")
        logger.info("\tor add the name as a commandline argument : ")
        logger.info("\t\tqalita pack --name 'mypack'")
        logger.info(
            "\tthe prefered way is to create a file '.env-local' with the values : "
        )
        logger.info("\t\tQALITA_PACK_NAME=mypack")
        logger.info("\tand source it : ")
        logger.info("\t\texport $(xargs < .env-local)")
        all_check_pass = False
    if all_check_pass:
        config.name = name
    else:
        return

    """Initialize a package"""
    package_folder = name + "_pack"
    package_yaml = "properties.yaml"
    package_json = "pack_conf.json"
    package_py = "main.py"
    package_sh = "run.sh"
    package_requirements = "requirements.txt"
    package_readme = "README.md"

    # Check if the package folder already exists
    if os.path.exists(package_folder):
        logger.warning(f"Package folder '{package_folder}' already exists")
    else:
        # Create a package folder
        os.makedirs(package_folder)
        logger.info(f"Created package folder: {package_folder}")

    # Check if the file already exists
    if os.path.exists(os.path.join(package_folder, package_yaml)):
        logger.warning(f"Package file '{package_yaml}' already exists")
    else:
        # Create a file
        with open(os.path.join(package_folder, package_yaml), "w") as file:
            file.write(
                f'name: {name}\nversion: "1.0.0"\ndescription: "default template pack"\nvisibility: private\ntype: "pack"'
            )
        logger.info(f"Created file: {package_yaml}")

    # Check if the file already exists
    if os.path.exists(os.path.join(package_folder, package_json)):
        logger.warning(f"Package file '{package_json}' already exists")
    else:
        # Create a file
        with open(os.path.join(package_folder, package_json), "w") as file:
            json_data = {"name": name, "version": "1.0.0"}
            file.write(json.dumps(json_data, indent=4))
        logger.info(f"Created file: {package_json}")

    # Check if the file already exists
    if os.path.exists(os.path.join(package_folder, package_py)):
        logger.warning(f"Package file '{package_py}' already exists")
    else:
        # Create a file
        with open(os.path.join(package_folder, package_py), "w") as file:
            file.write("# Python package code goes here\n")
            file.write(
                "print('hello world ! This is a script executed by a pack ! Do whatever process you want to check your data quality, happy coding ;)')"
            )
        logger.info(f"Created file: {package_py}")
        logger.warning("Please update the main.py file with the required code")

    # Check if the file already exists
    if os.path.exists(os.path.join(package_folder, package_sh)):
        logger.warning(f"Package file '{package_sh}' already exists")
    else:
        # Create a file
        with open(os.path.join(package_folder, package_sh), "w") as file:
            file.write("#/bin/bash\n")
            file.write("python -m pip install -r requirements.txt\n")
            file.write("python main.py")
        logger.info(f"Created file: {package_sh}")
        logger.warning("Please update the run.sh file with the required commands")

    if os.path.exists(os.path.join(package_folder, package_requirements)):
        logger.warning(f"Package file '{package_requirements}' already exists")
    else:
        # Create a file
        with open(os.path.join(package_folder, package_requirements), "w") as file:
            file.write("numpy")
        logger.info(f"Created file: {package_requirements}")
        logger.warning(
            "Please update the requirements.txt file with the required packages depdencies"
        )

    if os.path.exists(os.path.join(package_folder, package_readme)):
        logger.warning(f"Package file '{package_readme}' already exists")
    else:
        # Define content
        readme_content = """# Package

## Description of a pack

### Pack content

A pack is composed of different files :

### Mandatory files

- `run.sh` : the script to run the pack
- `properties.yaml` : the pack properties file
- `README.md` : this file

### Optional files

- `pack_conf.json` : the configuration file for the runtime program
- `requirements.txt` : the requirements file for the runtime program
"""

        # Create the file
        with open(os.path.join(package_folder, package_readme), "w") as file:
            file.write(readme_content)
        logger.info(f"Created file: {package_readme}")
        logger.warning(
            "Please READ and update the README.md file with the description of your pack"
        )

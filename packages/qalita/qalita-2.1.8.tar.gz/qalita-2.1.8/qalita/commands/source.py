"""
# QALITA (c) COPYRIGHT 2025 - ALL RIGHTS RESERVED -
"""

import os
import click
from tabulate import tabulate

from qalita.cli import pass_config
from qalita.internal.utils import logger, ask_confirmation, test_connection
from qalita.internal.request import send_api_request


@click.group()
@click.option("-s", "--source", type=int, help="Source ID")
@click.pass_context
def source(ctx, source):
    """Manage Qalita Platform Sources"""
    ctx.ensure_object(dict)
    ctx.obj["SOURCE"] = source


@source.command()
@pass_config
def list(config):
    """List sources that are accessible to the agent"""
    config.load_source_config()

    sources = []
    headers = [
        "ID",
        "Name",
        "Type",
        "Reference",
        "Sensitive",
        "Visibility",
        "Description",
        "Validity",
    ]

    for source in config.config["sources"]:
        sources.append(
            [
                source.get("id", ""),
                source.get("name", ""),
                source.get("type", ""),
                source.get("reference", ""),
                source.get("sensitive", ""),
                source.get("visibility", ""),
                source.get("description", ""),
                source.get("validate", ""),
            ]
        )

    print(tabulate(sources, headers, tablefmt="simple"))


def source_version(source):
    """Determine the source version"""
    # La version de la source est déterminée en fonction de sa typologie,
    # Si la source est d'une version non gérée, elle aura la version 1.0.0
    version = "1.0.0"
    return version


@pass_config
def validate_source(config):
    """Validate a source configuration"""
    logger.info("------------- Source Validation -------------")
    config.load_source_config()
    agent_conf = config.load_agent_config()

    total_sources = 0
    error_count = 0

    source_names = []

    for i, source in enumerate(config.config["sources"]):
        total_sources += 1
        is_source_valid = True  # Assuming the source is valid initially

        # check for name
        if "name" not in source:
            logger.error(f"Source number [{total_sources}] has no name")
            is_source_valid = False

        # check for type
        if "type" not in source:
            logger.error(f"Source number [{total_sources}] has no type")
            is_source_valid = False

        # Check for duplicate names
        if source["name"] in source_names:
            logger.error(f"Duplicate source name: [{source['name']}]")
            is_source_valid = False
        else:
            source_names.append(source["name"])

        # check for description
        if "description" not in source:
            logger.warning(
                f"Source [{source['name']}] has no description, defaulting to empty string"
            )
            config.config["sources"][i]["description"] = ""

        # check for reference
        if "reference" not in source:
            logger.warning(
                f"Source [{source['name']}] has no reference status, defaulting to False"
            )
            config.config["sources"][i]["reference"] = False

        # check for Sensitive
        if "sensitive" not in source:
            logger.warning(
                f"Source [{source['name']}] has no sensitive status, defaulting to False"
            )
            config.config["sources"][i]["sensitive"] = False

        # check for visibility
        if "visibility" not in source:
            logger.warning(
                f"Source [{source['name']}] has no visibility status, defaulting to private"
            )
            config.config["sources"][i]["visibility"] = "private"

        # check type
        type_for_test = source["type"]
        if type_for_test == "database":
            type_for_test = source["config"].get("type", "database")
        if type_for_test in [
            "mysql", "postgresql", "sqlite", "mongodb", "oracle", "s3", "gcs", "azure_blob", "hdfs", "sftp", "http", "https", "file", "folder"
        ]:
            if not test_connection(source["config"], type_for_test):
                logger.error(f"Connection test failed for source [{source['name']}] of type {type_for_test}")
                is_source_valid = False
        elif source["type"] == "database":
            if "config" in source:
                for key, value in source["config"].items():
                    # If the value starts with '$', assume it's an environment variable
                    if str(value).startswith("$"):
                        env_var = value[1:]
                        # Get the value of the environment variable
                        env_value = os.getenv(env_var)
                        if env_value is None:
                            logger.warning(
                                f"The environment variable [{env_var}] for the source [{source['name']}] is not set"
                            )
                            is_source_valid = False
        elif source["type"] == "file":
            # check if config parameter is present
            if "config" not in source:
                logger.error(
                    f"Source [{source['name']}] is of type file but has no config"
                )
                is_source_valid = False
            else:
                # check for path in config
                if "path" not in source["config"]:
                    logger.error(
                        f"Source [{source['name']}] is of type file but has no path in config"
                    )
                    is_source_valid = False
                else:
                    # check for read access to path
                    path = source["config"]["path"]
                    if not os.access(path, os.R_OK):
                        logger.error(
                            f"Source [{source['name']}] has a path in config, but it cannot be accessed"
                        )
                        is_source_valid = False

        # If all checks pass, mark the source as valid
        if is_source_valid:
            source["validate"] = "valid"
            logger.success(f"Source [{source['name']}] validated")
        else:
            source["validate"] = "invalid"
            logger.error(f"Source [{source['name']}] is invalid")
            error_count += 1

    if error_count == 0:
        logger.success("All sources validated")
    else:
        logger.error(f"{error_count} out of {total_sources} sources are invalid")

    # Write the config file
    config.save_source_config()


@source.command()
def validate():
    """Validate a source configuration"""
    validate_source()


@source.command()
@click.option(
    "--skip-validate",
    is_flag=True,
    default=False,
    envvar="QALITA_SKIP_VALIDATE",
    help="Skip validation of sources before pushing",
)
@pass_config
def push(config, skip_validate):
    """Publish a source to the Qalita Platform"""
    if not skip_validate:
        validate_source()
    else:
        logger.warning("Skipping source validation as requested.")
    logger.info("------------- Source Publishing -------------")
    logger.info("Publishing sources to the Qalita Platform...")

    invalid_count = 0  # To count failed publishing sources
    agent_conf = config.load_agent_config()
    config.load_source_config()

    if not config.config["sources"]:
        logger.warning("No sources to publish, add new sources > qalita source add")
        return

    if skip_validate:
        valid_source = len(config.config["sources"])
    else:
        valid_source = sum(
            1 for source in config.config["sources"] if source.get("validate") == "valid"
        )

    if valid_source == 0:
        logger.warning("No valid sources to publish")
        return

    r = send_api_request(
        request="/api/v2/sources",
        mode="get",
    )

    if r.status_code == 200:
        response_data = r.json()
        if not response_data:  # If response_data is an empty list
            logger.info("No sources found on the remote platform.")
            response_data = []  # Ensure it's always iterable
    else:
        raise

    for i, source in enumerate(config.config["sources"]):
        if skip_validate or source.get("validate") == "valid":
            logger.info(f"Processing source [{source['name']}] ...")

            # Find a matching source in response_data
            matched_source = next(
                (
                    s
                    for s in response_data
                    if s["name"] == source["name"] and s["type"] == source["type"]
                ),
                None,
            )

            if matched_source:
                # If source is already published, check for updates
                update_source = False

                if matched_source["versions"]:
                    if (
                        source_version(source)
                        == matched_source["versions"][0]["sem_ver_id"]
                    ):
                        if (
                            source["visibility"] == matched_source["visibility"]
                            and source["description"] == matched_source["description"]
                            and source["sensitive"] == matched_source["sensitive"]
                            and source["reference"] == matched_source["reference"]
                        ):
                            source_synced = False
                            if "id" in source and source["id"] == matched_source["id"]:
                                pass
                            else:
                                config.config["sources"][i]["id"] = matched_source["id"]
                                source_synced = True

                            if source_synced:
                                config.save_source_config()
                                logger.success(
                                    f"Source [{source['name']}] already published with id [{matched_source['id']}] synced with local config"
                                )
                            else:
                                logger.info(
                                    f"Source [{source['name']}] already published with id [{matched_source['id']}], no need to sync local config"
                                )
                        else:
                            update_source = True
                    else:
                        logger.info("Version mismatch")
                        update_source = True
                else:
                    logger.info("No version found")
                    update_source = True

                if update_source:
                    if source["visibility"] != matched_source["visibility"]:
                        if not ask_confirmation(
                            "Are you sure you want to publish a public source? Public sources are visible for partners. Be careful about what you share."
                        ):
                            continue

                    r = send_api_request(
                        request=f"/api/v2/sources/{matched_source['id']}",
                        mode="put",
                        data={
                            "description": source["description"],
                            "visibility": source["visibility"],
                            "sensitive": source["sensitive"],
                            "reference": source["reference"],
                        },
                    )
                    logger.success(f"Source [{source['name']}] updated")
                    continue
                else:
                    continue

            logger.info(f"Publishing new source [{source['name']}] ...")

            if source["visibility"] == "public":
                if not ask_confirmation(
                    "Are you sure you want to publish a public source? Public sources are visible for partners. Be careful about what you share."
                ):
                    continue

            r = send_api_request(
                request=f"/api/v1/sources/publish",
                mode="post",
                data={
                    "name": source["name"],
                    "type": source["type"],
                    "description": source["description"],
                    "reference": source["reference"],
                    "sensitive": source["sensitive"],
                    "visibility": source["visibility"],
                    "version": source_version(source),
                },
            )

            if r.status_code != 200:
                logger.warning(
                    f"Failed to publish source [{source['name']}] {r.status_code} - {r.text}"
                )
                invalid_count += 1
            else:
                source_id = r.json()["id"]
                logger.success(f"Source published with id [{source_id}]")
                config.config["sources"][i]["id"] = source_id
                config.save_source_config()

    if invalid_count > 0:
        logger.warning(f"{invalid_count} source(s) skipped due to validation errors.")


@source.command()
@pass_config
def add(config):
    """Add a source to the local Qalita Config"""

    # initialize the source dict
    source = {}

    # hardcode empty source config
    source["config"] = {}

    # ask for the source name
    source["name"] = click.prompt("Source name")

    # ask for the source type
    source["type"] = click.prompt(
        "Source type (file, folder, database, s3, gcs, azure_blob, hdfs, sftp, http, https, ...)",
    )

    # Paramétrage selon le type de source
    if source["type"] == "file":
        source["config"]["path"] = click.prompt("Source file path")
    elif source["type"] == "folder":
        source["config"]["path"] = click.prompt("Source folder path")
    elif source["type"] in ["database", "mysql", "postgresql", "oracle", "mssql"]:
        if source["type"] == "database":
            db_type = click.prompt(
                "Source database Type (mysql, postgresql, oracle, mssql, sqlite, mongodb, ...)",
            )
        else:
            db_type = source["type"]
        source["config"]["type"] = db_type
        if db_type == "sqlite":
            source["config"]["file_path"] = click.prompt("SQLite file path")
        elif db_type == "oracle":
            source["config"]["host"] = click.prompt("Oracle host")
            source["config"]["port"] = click.prompt("Oracle port")
            source["config"]["username"] = click.prompt("Oracle username")
            source["config"]["password"] = click.prompt("Oracle password")
            source["config"]["database"] = click.prompt("Oracle service name")
        else:
            source["config"]["host"] = click.prompt("Source host")
            source["config"]["port"] = click.prompt("Source port")
            source["config"]["username"] = click.prompt("Source username")
            source["config"]["password"] = click.prompt("Source password")
            source["config"]["database"] = click.prompt("Source database")
        # Specify a table or an SQL query to restrict the scan scope. By default, '*' scans the entire database
        source["config"]["table_or_query"] = click.prompt(
            "Table name, list of table names or SQL query (default '*' scans the entire database)",
            default="*",
        )
    elif source["type"] == "mongodb":
        source["config"]["host"] = click.prompt("MongoDB host")
        source["config"]["port"] = click.prompt("MongoDB port")
        source["config"]["username"] = click.prompt("MongoDB username")
        source["config"]["password"] = click.prompt("MongoDB password")
        source["config"]["database"] = click.prompt("MongoDB database")
    elif source["type"] == "s3":
        source["config"]["bucket"] = click.prompt("S3 bucket name")
        source["config"]["prefix"] = click.prompt("S3 prefix (optional)", default="")
        source["config"]["access_key"] = click.prompt("S3 access key")
        source["config"]["secret_key"] = click.prompt("S3 secret key")
        source["config"]["region"] = click.prompt("S3 region")
    elif source["type"] == "gcs":
        source["config"]["bucket"] = click.prompt("GCS bucket name")
        source["config"]["prefix"] = click.prompt("GCS prefix (optional)", default="")
        source["config"]["credentials_json"] = click.prompt("GCS credentials JSON path")
    elif source["type"] == "azure_blob":
        source["config"]["container"] = click.prompt("Azure Blob container name")
        source["config"]["prefix"] = click.prompt("Blob prefix (optional)", default="")
        source["config"]["connection_string"] = click.prompt("Azure Blob connection string")
    elif source["type"] == "hdfs":
        source["config"]["namenode_host"] = click.prompt("HDFS namenode host")
        source["config"]["port"] = click.prompt("HDFS port")
        source["config"]["user"] = click.prompt("HDFS user")
        source["config"]["path"] = click.prompt("HDFS path")
    elif source["type"] in ["sftp"]:
        source["config"]["host"] = click.prompt(f"SFTP host")
        source["config"]["port"] = click.prompt(f"SFTP port")
        source["config"]["username"] = click.prompt(f"SFTP username")
        source["config"]["password"] = click.prompt(f"SFTP password")
        source["config"]["path"] = click.prompt(f"SFTP path")
    elif source["type"] in ["http", "https"]:
        source["config"]["url"] = click.prompt("URL")
        auth_type = click.prompt("Auth type (none, basic, token)", default="none")
        source["config"]["auth_type"] = auth_type
        if auth_type == "basic":
            source["config"]["username"] = click.prompt("Username")
            source["config"]["password"] = click.prompt("Password")
        elif auth_type == "token":
            source["config"]["token"] = click.prompt("Token")
    else:
        # Fallback générique
        click.echo(f"Type de source inconnu ou non géré automatiquement : {source['type']}")
        click.echo("Vous pouvez ajouter manuellement des clés dans le fichier de configuration YAML si besoin.")

    # ask for the source description
    source["description"] = click.prompt("Source description")
    # ask for the source reference
    source["reference"] = click.prompt("Source reference", type=bool, default=False)
    # ask for the source sensitive
    source["sensitive"] = click.prompt("Source sensitive", type=bool, default=False)
    # ask for the source visibility
    source["visibility"] = click.prompt(
        "Source visibility",
        default="private",
        type=click.Choice(["private", "internal", "public"], case_sensitive=False),
    )

    config.load_source_config()
    if len(config.config["sources"]) > 0:
        # check if the source already exists
        for conf_source in config.config["sources"]:
            if conf_source["name"] == source["name"]:
                logger.error("Source already exists in config")
                return

    # add the source to the config
    config.config["sources"].append(
        {
            "name": source["name"],
            "config": source["config"],
            "type": source["type"],
            "description": source["description"],
            "reference": source["reference"],
            "sensitive": source["sensitive"],
            "visibility": source["visibility"],
        }
    )

    # save the config
    config.save_source_config()
    logger.success(f"Source [{source['name']}] added to the local config")

    validate_source()

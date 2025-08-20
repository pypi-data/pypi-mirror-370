import copy
import json
import os
from collections import deque
from typing import Any
from typing import Dict

import click
import inquirer
import jinja2

from synalinks.cli.constants import PROJECT_CONFIG_FILENAME
from synalinks.cli.constants import PROJECT_STRUCTURE_TEMPLATE
from synalinks.cli.utils.project_utils import get_synalinks_project_config
from synalinks.cli.utils.project_utils import is_inside_synalinks_project
from synalinks.src.utils.naming import to_pkg_name
from synalinks.src.version import version as get_version


def get_config_json(filename: str):
    """
    Reads and returns the JSON configuration from a specified file within the config
    folder.

    This function locates the configuration folder using the `synalinks.cli.config`
    module, opens the specified JSON file, and parses its contents into a Python
    dictionary.

    Args:
        filename (str): The name of the JSON configuration file to read.

    Returns:
        (dict): A dictionary containing the JSON configuration data.
    """
    from synalinks.cli import config

    config_folder_path = config.__file__[: -len("/__init__.py")]
    json_config = {}
    with open(os.path.join(config_folder_path, filename), "r", encoding="utf-8") as f:
        json_config = json.loads(f.read())
    return json_config


def base_setup_config() -> Dict[str, Any]:
    """
    Set up the base configuration for a synalinks project.

    Returns:
        (dict): The base configuration for the project.
    """
    questions = []
    config = get_config_json("default_project_config.json")
    default_project_name = config.get("project_name")
    default_project_description = config.get("project_description")
    questions.append(
        inquirer.Text(
            "project_name",
            message=f"What is the project name [{default_project_name}]",
        ),
    )
    questions.append(
        inquirer.Text(
            "project_description",
            message=f"What is the project description [{default_project_description}]",
        ),
    )
    answers = inquirer.prompt(questions)
    questions = []
    if answers:
        for key, answer in answers.items():
            if answer:
                if key == "project_name":
                    config[key] = answer
                    config["package_name"] = to_pkg_name(answer)
                else:
                    config[key] = answer
    else:
        exit(0)
    config["synalinks_version"] = get_version()
    return config


def models_setup_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Set up the language and embedding model configuration for a synalinks project.

    Args:
        config (dict): The existing project configuration.

    Returns:
        (dict): The updated project configuration with language model settings.
    """
    questions = []
    lm_config = get_config_json("language_models.json")
    em_config = get_config_json("embedding_models.json")
    model_providers = list(lm_config.keys())
    questions.append(
        inquirer.List(
            "model_provider",
            message="Select the model provider to use",
            choices=model_providers,
        ),
    )
    answers = inquirer.prompt(questions)
    questions = []
    if answers:
        config = {**config, **answers}
        if answers.get("model_provider") in lm_config:
            questions.append(
                inquirer.List(
                    "language_model",
                    message="Select the language model to use",
                    choices=lm_config.get(answers.get("model_provider")),
                )
            )
        if answers.get("model_provider") in em_config:
            questions.append(
                inquirer.List(
                    "embedding_model",
                    message="Select the embedding model to use",
                    choices=em_config.get(answers.get("model_provider")),
                )
            )
        answers = inquirer.prompt(questions)
        if answers:
            for key, answer in answers.items():
                if key in ("language_model", "embedding_model"):
                    config[key] = answer.split()[0]
                else:
                    config[key] = answer
        else:
            exit(0)
    else:
        exit(0)
    return config


def secrets_setup_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Set up the secrets configuration for a synalinks project.

    Args:
        config (dict): The existing project configuration.

    Returns:
        (dict): The secrets configuration for the project.
    """
    secrets = copy.deepcopy(get_config_json("api_key_config.json"))
    lm_provider = config.get("model_provider", None)
    if lm_provider:
        if lm_provider != "ollama":
            questions = []
            for env_var_name in secrets[lm_provider].keys():
                questions.append(inquirer.Password(env_var_name, message=env_var_name))
            answers = inquirer.prompt(questions)
            if answers:
                for env_var_name, env_var_value in answers.items():
                    if env_var_value:
                        secrets[lm_provider][env_var_name] = env_var_value
    return secrets


def setup_project(config: Dict[str, Any], secrets: Dict[str, Any] = {}):
    """
    Set up a new synalinks project with the given configuration and secrets.

    Args:
        config (dict): The project configuration.
        secrets (dict): The secrets to be stored in the .env file.
    """
    project_dir = os.path.join(os.getcwd(), config["project_name"])
    # Setup project
    queue = deque([(project_dir, PROJECT_STRUCTURE_TEMPLATE)])

    while queue:
        node_dir, node_structure = queue.pop()
        if not os.path.exists(node_dir):
            os.mkdir(node_dir)
        if node_dir == project_dir:
            with open(
                os.path.join(project_dir, PROJECT_CONFIG_FILENAME), "w", encoding="utf-8"
            ) as f:
                f.write(json.dumps(config, indent=2))
        for filename, template in node_structure.items():
            filename = jinja2.Template(filename).render(config=config)
            path = os.path.join(node_dir, filename)
            if isinstance(template, dict):
                queue.append((path, template))
            elif isinstance(template, str):
                with open(path, "w", encoding="utf-8") as f:
                    template = jinja2.Template(template).render(config=config)
                    f.write(template)
    # Setup secrets into an .env file
    model_provider = config.get("model_provider")
    language_model = model_provider + "/" + config.get("language_model")
    embedding_model = model_provider + "/" + config.get("embedding_model")
    variables = [
        f"LANGUAGE_MODEL={language_model}",
        f"EMBEDDING_MODEL={embedding_model}",
    ]
    if model_provider == "ollama":
        variables.append(
            "# To enable your container to communicate with your local ollama "
            "instance, uncomment the following line",
        )
        variables.append("MODEL_API_BASE=http://host.docker.internal:11434")
    else:
        variables.append(
            "# To enable your container to communicate with your local ollama "
            "instance, uncomment the following line",
        )
        variables.append("# MODEL_API_BASE=http://host.docker.internal:11434")
    for lm_provider, env_variables in secrets.items():
        for env_var, env_var_value in env_variables.items():
            variables.append(f"{env_var}={env_var_value}")
    with open(os.path.join(project_dir, ".env"), "w", encoding="utf-8") as f:
        f.write("\n".join(variables))


def maybe_setup_project() -> Dict[str, Any]:
    """
    Set up a new synalinks project if not already inside one.

    Returns:
        (dict): The project configuration.
    """
    if is_inside_synalinks_project():
        config = get_synalinks_project_config()
    else:
        click.echo("Command executed outside a synalinks project.")
        create_new_project = (
            inquirer.confirm(
                "new_project",
                message="Do you want to create a new project",
                default=False,
            ),
        )
        if create_new_project:
            config = base_setup_config()
            config = models_setup_config(config)
            secrets = secrets_setup_config(config)
            setup_project(config, secrets)
        else:
            click.echo("Aborting")
            exit(0)
    return config

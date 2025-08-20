#!/usr/bin/env python3
r"""Script to update projects from a configuration file.

This script reads a config file containing project IDs, task template slugs,
and variables, then ensures each project is updated with the correct task
template version and configurable variables.

Example usage:
    python -m bitfount.runners.update_projects_from_config \\
    task_templates/project-config-production-public.yaml --username myuser \\
    --password mypass
"""

from datetime import datetime, timedelta, timezone
from enum import Enum
import json
from pathlib import Path
import sys
from typing import Any, Optional, cast

from fire import Fire
import yaml

from bitfount.externals.general.authentication import ExternallyManagedJWT
from bitfount.hub.api import BitfountHub
from bitfount.hub.helper import _create_bitfounthub, get_hub_url
from bitfount.runners.upload_task_templates import (
    _get_user_token,
    _update_and_upload_task_templates,
)

# These are the paths to the config files of task templates. They are used to find the
# local task template file from the slug of the task template.
TASK_TEMPLATES_CONFIG_PATHS: list[str] = [
    "task_templates/config-production-hidden.yaml",
    "task_templates/config-production-public.yaml",
]

# What type to use for the new variables. Defaults to "fixed". The other option is
# "default".
TASK_VARIABLE_MODE = "fixed"


class ProcessResult(Enum):
    """Enum representing the result of processing a project."""

    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class ProjectConfig:
    """Class to represent a project configuration."""

    def __init__(self, project_id: str, config_data: dict[str, Any]):
        self.project_id = project_id
        task_slug_full = config_data["task-slug"]

        # Parse the owner and slug from the format "owner/slug"
        if "/" not in task_slug_full:
            raise ValueError(
                f"Task slug must be in format 'owner/slug', got: {task_slug_full}"
            )

        self.task_owner, self.task_slug = task_slug_full.split("/", 1)
        self.project_owner = config_data["project-owner"]
        self.variables = config_data.get("variables", {})


def load_config(config_file: str) -> list[ProjectConfig]:
    """Load and parse the project configuration file.

    Args:
        config_file: Path to the YAML configuration file.

    Returns:
        List of ProjectConfig objects.
    """
    with open(config_file, "r") as f:
        config_data = yaml.safe_load(f)

    projects = []
    for project_entry in config_data.get("project_ids", []):
        for project_id, project_config in project_entry.items():
            projects.append(ProjectConfig(project_id, project_config))

    return projects


def get_project_info(
    project_id: str, hub: BitfountHub, hub_url: str
) -> Optional[dict[str, Any]]:
    """Get current project information from the hub.

    Args:
        project_id: The project ID to retrieve.
        hub: The hub connection object.
        hub_url: The hub URL.

    Returns:
        Project information dictionary or None if not found.
    """
    project_url: str = f"{hub_url}/api/projects/{project_id}"

    try:
        response = hub.session.get(url=project_url)
        if response.status_code == 200:
            return cast(dict[str, Any], response.json())
        elif response.status_code == 404:
            print(f"❌ Project not found: {project_id}")
            return None
        elif response.status_code == 403:
            print(f"❌ Access denied to project: {project_id}")
            return None
        else:
            print(f"❌ Failed to get project {project_id}: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting project {project_id}: {e}")
        return None


def get_task_template_info(
    owner_or_id: str, slug: Optional[str], hub: BitfountHub, hub_url: str
) -> Optional[dict[str, Any]]:
    """Get task template information from the hub by owner/slug or by ID.

    Args:
        owner_or_id: Either the task template owner (if slug provided) or template ID.
        slug: The task template slug (if getting by owner/slug), None if getting by ID.
        hub: The hub connection object.
        hub_url: The hub URL.

    Returns:
        Task template information dictionary or None if not found.
    """
    if slug:
        # Get by owner/slug
        template_url: str = f"{hub_url}/api/task-templates/{owner_or_id}/{slug}"
        identifier = f"{owner_or_id}/{slug}"
    else:
        # Get by ID
        template_url = f"{hub_url}/api/task-templates/{owner_or_id}"
        identifier = f"ID {owner_or_id}"

    try:
        response = hub.session.get(url=template_url)
        if response.status_code == 200:
            return cast(dict[str, Any], response.json())
        elif response.status_code == 404:
            print(f"❌ Task template not found: {identifier}")
            return None
        else:
            print(
                f"❌ Failed to get task template {identifier}: {response.status_code}"
            )
            return None
    except Exception as e:
        print(f"❌ Error getting task template {identifier}: {e}")
        return None


def get_project_task_definitions(
    project_id: str, hub: BitfountHub, hub_url: str
) -> Optional[dict[str, Any]]:
    """Get task definitions for a project from the hub.

    Args:
        project_id: The project ID.
        hub: The hub connection object.
        hub_url: The hub URL.

    Returns:
        Task definitions response dictionary or None if not found.
    """
    definitions_url: str = f"{hub_url}/api/projects/{project_id}/task-definitions"

    try:
        response = hub.session.get(url=definitions_url)
        if response.status_code == 200:
            return cast(dict[str, Any], response.json())
        elif response.status_code == 404:
            print(f"❌ Task definitions not found for project: {project_id}")
            return None
        elif response.status_code == 403:
            print(f"❌ Access denied to task definitions for project: {project_id}")
            return None
        else:
            print(
                f"❌ Failed to get task definitions for project {project_id}: "
                f"{response.status_code}"
            )
            return None
    except Exception as e:
        print(f"❌ Error getting task definitions for project {project_id}: {e}")
        return None


def print_template_differences(
    local_template: dict[str, Any], hub_template: dict[str, Any], prefix: str = ""
) -> None:
    """Print the differences between local and hub templates.

    Args:
        local_template: The local template dictionary.
        hub_template: The hub template dictionary.
        prefix: Prefix for nested keys (used in recursion).
    """
    all_keys = set(local_template.keys()) | set(hub_template.keys())

    for key in sorted(all_keys):
        current_prefix = f"{prefix}.{key}" if prefix else key

        if key not in local_template:
            print(f"  📍 Key missing in local: {current_prefix}")
        elif key not in hub_template:
            print(f"  📍 Key missing in hub: {current_prefix}")
        else:
            local_value = local_template[key]
            hub_value = hub_template[key]

            if isinstance(local_value, dict) and isinstance(hub_value, dict):
                # Recursively compare nested dictionaries
                if local_value != hub_value:
                    print_template_differences(local_value, hub_value, current_prefix)
            elif local_value != hub_value:
                print(f"  📍 Different value for {current_prefix}:")
                print(f"    Local:  {local_value}")
                print(f"    Hub:    {hub_value}")


def sort_dict_recursively(obj: Any) -> Any:
    """Recursively sort dictionaries by keys to ensure consistent ordering.

    Args:
        obj: The object to sort (can be dict, list, or any other type).

    Returns:
        The object with all nested dictionaries sorted by keys.
    """
    if isinstance(obj, dict):
        return {key: sort_dict_recursively(value) for key, value in sorted(obj.items())}
    elif isinstance(obj, list):
        return [sort_dict_recursively(item) for item in obj]
    else:
        return obj


def check_and_update_task_template(
    project_config: ProjectConfig,
    username: str,
    jwt: ExternallyManagedJWT,
    hub: BitfountHub,
    hub_url: str,
) -> Optional[str]:
    """Check if task template needs updating and update if necessary.

    Args:
        project_config: The project configuration.
        username: The authenticated username.
        jwt: The JWT token.
        hub: The hub connection object.
        hub_url: The hub URL.

    Returns:
        The task template ID to use, None if failed, or "SKIP_PROJECT" if project should
        be skipped.
    """
    # Use the task owner and slug directly from the config
    task_owner = project_config.task_owner
    task_slug = project_config.task_slug

    print(f"📋 Using task template '{task_slug}' owned by '{task_owner}'")

    # Get full task template info to validate it exists
    template_info: Optional[dict[str, Any]] = get_task_template_info(
        task_owner, task_slug, hub, hub_url
    )

    if not template_info:
        print(f"❌ Cannot find task template '{task_owner}/{task_slug}'")
        return None

    template_id = cast(Optional[str], template_info.get("id"))
    if not template_id:
        print(f"❌ Task template '{task_owner}/{task_slug}' has no ID")
        return None

    # Parse the task templates config to find the template file path
    local_template_path: Optional[str] = None

    for config_path in TASK_TEMPLATES_CONFIG_PATHS:
        try:
            with open(config_path, "r") as f:
                task_templates_config: dict[str, Any] = yaml.safe_load(f)

            # Look for the matching task template by slug
            if "task-templates" in task_templates_config:
                for template_config in task_templates_config["task-templates"]:
                    if template_config.get("slug") == task_slug:
                        local_template_path = template_config.get("template")
                        print(f"📋 Found task template config in: {config_path}")
                        break

            if local_template_path:
                break

        except FileNotFoundError:
            print(f"⚠️  Config file not found: {config_path}")
            continue
        except Exception as e:
            print(f"⚠️  Error parsing config file {config_path}: {e}")
            continue

    if not local_template_path:
        print(
            f"⚠️  Task template slug '{task_slug}' not found in any config files: {TASK_TEMPLATES_CONFIG_PATHS}"  # noqa: E501
        )
        print("ℹ️  Using hub version")
        return template_id

    if not Path(local_template_path).exists():
        print(f"⚠️  Local template file not found: {local_template_path}")
        print("ℹ️  Using hub version")
        return template_id

    # Found local template file and it exists
    print(f"📄 Found local template file: {local_template_path}")

    # Load local template
    with open(local_template_path, "r") as f:
        local_template: dict[str, Any] = yaml.safe_load(f)

    # Compare with hub template
    hub_template: dict[str, Any] = template_info.get("template", {})

    # Sort both templates recursively to avoid false positives due to key ordering
    sorted_local_template = sort_dict_recursively(local_template)
    sorted_hub_template = sort_dict_recursively(hub_template)

    if sorted_local_template != sorted_hub_template:
        # Check if the authenticated user owns the task template
        if username != task_owner:
            print(
                f"⚠️  Task template '{task_owner}/{task_slug}' is not "
                f"up to date and is owned by '{task_owner}', not "
                f"authenticated user '{username}'. Skipping entire project."
            )
            print_template_differences(sorted_local_template, sorted_hub_template)
            return "SKIP_PROJECT"

        print("🔄 Local template differs from hub template, uploading new version...")
        print_template_differences(sorted_local_template, sorted_hub_template)

        # Create a minimal config for the upload function
        upload_config: dict[str, list[dict[str, Any]]] = {
            "task-templates": [
                {
                    "slug": task_slug,
                    "title": template_info.get("title", task_slug),
                    "type": template_info.get("type", "text-classification"),
                    "description": template_info.get("description", ""),
                    "template": local_template_path,
                    "tags": template_info.get("tags", []),
                }
            ]
        }

        try:
            _update_and_upload_task_templates(
                upload_config,
                task_owner,  # Use the task owner from config
                {},  # No model versions to update
                jwt=jwt,
            )
            print("✅ Successfully uploaded new version of task template")

            # Get the updated template info to get the new version
            updated_template_info = get_task_template_info(
                task_owner, task_slug, hub, hub_url
            )
            if updated_template_info:
                template_id = updated_template_info.get("id")

        except Exception as e:
            print(f"❌ Failed to upload task template: {e}")
            return None
    else:
        print("✅ Local template matches hub template, no upload needed")

    return template_id


def format_template_variables(variables: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Format variables into the expected template variables format.

    Args:
        variables: Dictionary of variable names to values.

    Returns:
        Formatted template variables dictionary.
    """
    formatted = {}
    for var_name, var_value in variables.items():
        formatted[var_name] = {"value": var_value, "mode": TASK_VARIABLE_MODE}
    return formatted


def update_project(
    project_config: ProjectConfig,
    template_id: str,
    current_project: dict[str, Any],
    hub: BitfountHub,
    hub_url: str,
) -> bool:
    """Update a project with new task template and variables.

    Args:
        project_config: The project configuration.
        template_id: The task template ID to use.
        current_project: Current project information.
        hub: The hub connection object.
        hub_url: The hub URL.

    Returns:
        True if update was successful, False otherwise.
    """
    project_url: str = f"{hub_url}/api/projects/{project_config.project_id}"

    # Check what needs to be updated
    needs_template_update: bool = current_project.get("taskTemplateId") != template_id

    # Format the desired variables
    desired_variables: dict[str, dict[str, Any]] = format_template_variables(
        project_config.variables
    )
    current_variables: dict[str, Any] = current_project.get("templateVariables", {})
    needs_variables_update: bool = current_variables != desired_variables

    if not needs_template_update and not needs_variables_update:
        print(f"✅ Project {project_config.project_id} is already up to date")
        return True

    # Build update payload
    payload: dict[str, Any] = {}

    if needs_template_update:
        payload["taskTemplateId"] = template_id
        print(f"🔄 Updating task template ID to: {template_id}")

    if needs_variables_update:
        payload["templateVariables"] = desired_variables
        print(
            f"🔄 Updating template variables: {json.dumps(desired_variables, indent=2)}"
        )

    try:
        response = hub.session.patch(url=project_url, json=payload)

        if response.status_code == 200:
            print(f"✅ Successfully updated project {project_config.project_id}")
            return True
        else:
            print(
                f"❌ Failed to update project {project_config.project_id}: {response.status_code}"  # noqa: E501
            )
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error updating project {project_config.project_id}: {e}")
        return False


def process_project(
    project_config: ProjectConfig,
    username: str,
    jwt: ExternallyManagedJWT,
    hub: BitfountHub,
    hub_url: str,
) -> ProcessResult:
    """Process a single project configuration.

    Args:
        project_config: The project configuration to process.
        username: The authenticated username.
        jwt: The JWT token.
        hub: The hub connection object.
        hub_url: The hub URL.

    Returns:
        ProcessResult enum value.
    """
    print(f"\n🔄 Processing project: {project_config.project_id}")
    print(f"   Task template: {project_config.task_owner}/{project_config.task_slug}")
    print(f"   Variables: {project_config.variables}")

    # Get current project info
    current_project: Optional[dict[str, Any]] = get_project_info(
        project_config.project_id, hub, hub_url
    )
    if current_project and current_project.get("status") != "PUBLISHED":
        print(
            f"⚠️ Skipping project {project_config.project_id} because it is not published"  # noqa: E501
        )
        return ProcessResult.SKIPPED

    if current_project is None:
        print(f"❌ Failed to get project info for {project_config.project_id}")
        return ProcessResult.FAILED

    # Check and update task template if needed
    template_id: Optional[str] = check_and_update_task_template(
        project_config, username, jwt, hub, hub_url
    )
    if template_id == "SKIP_PROJECT":
        return ProcessResult.SKIPPED
    if not template_id:
        return ProcessResult.FAILED

    # Update the project
    if update_project(project_config, template_id, current_project, hub, hub_url):
        return ProcessResult.SUCCESS
    else:
        return ProcessResult.FAILED


def main(
    config_file: str,
    username: str,
    password: str,
) -> None:
    """Main function to update projects from configuration file.

    Args:
        config_file: Path to the YAML configuration file.
        username: The username for authentication.
        password: The password for authentication.
    """
    if not config_file or not username or not password:
        print("❌ config_file, username, and password are all required!")
        sys.exit(1)

    # Load configuration
    try:
        projects: list[ProjectConfig] = load_config(config_file)
        if not projects:
            print("❌ No projects found in configuration file!")
            sys.exit(1)
        print(f"📋 Loaded {len(projects)} projects from configuration")
    except Exception as e:
        print(f"❌ Failed to load configuration file: {e}")
        sys.exit(1)

    # Get JWT for authentication
    try:
        print(f"🔐 Authenticating as: {username}")
        access_token: str
        expires_in: int
        access_token, expires_in = _get_user_token(username, password)
        jwt: ExternallyManagedJWT = ExternallyManagedJWT(
            jwt=access_token,
            expires=datetime.now(timezone.utc) + timedelta(seconds=expires_in),
            # Refreshing not necessary as this is not a long-running script
            get_token=lambda: None,  # type: ignore[arg-type, return-value]
        )
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        sys.exit(1)

    # Create hub connection
    hub_url = get_hub_url()
    hub = _create_bitfounthub(username=username, url=hub_url, secrets=jwt)

    # Process each project
    success_count: int = 0
    failure_count: int = 0
    skipped_count: int = 0

    for project_config in projects:
        try:
            # Check if the authenticated user owns the project
            if username != project_config.project_owner:
                print(
                    f"\n⚠️  Skipping project {project_config.project_id} because authenticated user '{username}' "  # noqa: E501
                    f"does not own this project (owned by '{project_config.project_owner}')"  # noqa: E501
                )  # noqa: E501
                skipped_count += 1
                continue

            result: ProcessResult = process_project(
                project_config, username, jwt, hub, hub_url
            )
            if result == ProcessResult.SUCCESS:
                success_count += 1
            elif result == ProcessResult.SKIPPED:
                skipped_count += 1
            else:  # ProcessResult.FAILED
                failure_count += 1
        except Exception as e:
            print(
                f"❌ Unexpected error processing project {project_config.project_id}: {e}"  # noqa: E501
            )
            failure_count += 1

    # Summary
    print("\n📊 Summary:")
    print(f"   ✅ Successfully processed: {success_count}")
    print(f"   ⚠️  Skipped (ownership): {skipped_count}")
    print(f"   ❌ Failed: {failure_count}")

    if failure_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    Fire(main)

import os
import subprocess
import yaml
from pathlib import Path
import shutil
import functools

print = functools.partial(print, flush=True)
print(f"Current working directory: {os.getcwd()}")

# Configuration Files and Secrets
config_file = "config.yaml"
with open(config_file, "r") as file:
    config = yaml.safe_load(file)
if not config.get("EXCLUDED_FILES"):
    config["EXCLUDED_FILES"] = []


def print_step_complete():
    print("STEP_COMPLETE", flush=True)


# Step 1: Install Dependencies
def install_dependencies():
    dependencies = [
        "cryptography",
        "pyyaml",
        "azure-storage-blob",
        "auth0-python",
        "python-dateutil",
        "sseclient",
        "jupyter",
        "nbconvert",
        "pipreqs",
    ]

    # only download from PyPi if using production environment
    env = config.get("BEEKEEPER_ENVIRONMENT")
    if config.get("BEEKEEPER_ENVIRONMENT") in ["dev", "tst", "stg"]:
        if env == "tst":
            env = "testing"
        if env == "stg":
            env = "staging"

        wheel_url = f"https://stusebkstoragesdk.blob.core.windows.net/escrowaisdk/dist/{env}/escrowaici-0.1.5-py3-none-any.whl"
        wheel_file = "escrowaici-0.1.5-py3-none-any.whl"
        wheel = True
    else:
        dependencies.append("EscrowAICI")
        wheel = False

    try:
        print("Installing dependencies...")
        subprocess.run(
            ["pip", "install", "--upgrade", "pip"] + dependencies,
            check=True,
            stderr=subprocess.STDOUT,
        )

        if wheel:
            # Download the wheel file using curl
            print(f"Downloading wheel file from {wheel_url}...")
            subprocess.run(
                ["curl", "-O", wheel_url], check=True, stderr=subprocess.STDOUT
            )

            # Install the wheel file
            print(f"Installing wheel file: {wheel_file}...")
            subprocess.run(
                ["pip", "install", wheel_file], check=True, stderr=subprocess.STDOUT
            )

            os.remove(wheel_file)

        print_step_complete()

    except subprocess.CalledProcessError as e:
        raise Exception(f"Error installing dependencies or wheel file: {e}")


# Step 2: Convert Jupyter Notebooks in Root Directory to Python Scripts
def convert_notebooks_to_scripts():
    converted_scripts = []
    root_directory = Path(".")

    for notebook in root_directory.rglob("*.ipynb"):
        if str(notebook)[0] == "." or notebook.name in config.get("EXCLUDED_FILES"):
            continue
        script_name = notebook.with_suffix(".py")  # Target .py script
        print(f"Converting {notebook} to {script_name}...")

        try:
            # Convert notebook to Python script
            subprocess.run(
                ["jupyter", "nbconvert", "--to", "script", str(notebook)], check=True
            )
            converted_scripts.append(script_name)
            # If erroneously turned into .txt, convert into .py
            if notebook.with_suffix(".txt").exists():
                os.rename(notebook.with_suffix(".txt"), notebook.with_suffix(".py"))
        except subprocess.CalledProcessError as e:
            print(f"Error converting {notebook}: {e}")
            continue

    print("All notebooks converted.")
    print_step_complete()
    return converted_scripts


# Step 3: Generate requirements.txt
def generate_requirements(temp_folder="temp_py_files"):
    # Step 3.0: Verify that we want to generate requirements.txt
    if (
        Path("./requirements.txt").exists()
        and config.get("GENERATE_REQUIREMENTS", True) == False
    ):
        with open(Path("./requirements.txt"), "a") as f:
            f.write("\nipython\nnbconvert")
        print_step_complete()
        return

    temp_folder = Path(temp_folder)

    # Step 3.1: Create temporary folder and copy scripts there
    if temp_folder.exists():
        shutil.rmtree(temp_folder)  # Clean up if folder exists
    temp_folder.mkdir(parents=True, exist_ok=True)

    print(f"Copying scripts to temporary folder: {temp_folder}")
    for script in Path(".").rglob("*.py"):
        try:
            script.read_text(encoding="utf-8")
        except UnicodeDecodeError as e:
            print(f"File {file} failed UTF-8 decode: {e}")
            continue

        destination = temp_folder / script.name
        if (
            script.resolve() != destination.resolve()
        ):  # Check if source and destination are different
            shutil.copy(script, destination)

    # Step 3.2: Run pipreqs to generate requirements.txt
    print("Running pipreqs to generate requirements.txt...")
    subprocess.run(["pipreqs", str(temp_folder), "--force"], check=True)

    # Step 3.3: Move requirements.txt to root
    shutil.move(temp_folder / "requirements.txt", "./requirements.txt")

    # Step 3.4: Add ipython manually to requirements.txt
    requirements_path = Path("./requirements.txt")
    with open(requirements_path, "r") as f:
        requirements = f.read()

    with open(requirements_path, "w") as f:
        f.write(requirements)
        if "ipython" not in requirements:
            f.write("\nipython\n")

        # Add nbconvert if missing
        if "nbconvert" not in requirements:
            f.write("\nnbconvert\n")

    print("requirements.txt updated with ipython.")

    print("requirements.txt generated.")
    shutil.rmtree(temp_folder)
    print_step_complete()


# Step 4: Generate run.sh Script
def generate_run_script():
    # Step 4.0: Verify that we want to generate run.sh
    if Path("./run.sh").exists() and config.get("GENERATE_RUN_SCRIPT", True) == False:
        print_step_complete()
        return

    print("Loading entrypoint from config.yaml...")
    entrypoint = config.get("ENTRYPOINT", "run.py")

    run_script = "run.sh"
    print("Generating run.sh script...")
    with open(run_script, "w") as f:
        f.write("#!/bin/sh\n\n")
        f.write(f"ipython {entrypoint}\n")
    os.chmod(run_script, 0o755)  # Make it executable
    print("run.sh script generated and made executable.")
    print_step_complete()


# Step 5: Generate Dockerfile
def generate_dockerfile():
    # Step 5.0: Verify that we want to generate Dockerfile
    if (
        Path("./Dockerfile").exists()
        and config.get("GENERATE_DOCKERFILE", True) == False
    ):
        print_step_complete()
        return

    dockerfile_content = """FROM python:3.12-slim as bkstart

WORKDIR /app

RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt  .

RUN pip install -U pip setuptools uv && uv pip install -r requirements.txt --python `which python`

### BEEKEEPER START LOGIC ENDS HERE ###

############################################################################################

### YOUR DOCKERFILE STEPS BEGIN BELOW
FROM python:3.12-slim

WORKDIR /app

COPY --from=bkstart /opt/venv /opt/venv

COPY . .

ENV PATH="/opt/venv/bin:$PATH"

RUN echo $ENV

# Make the run.sh script executable
RUN chmod +x run.sh

# set the start command
ENTRYPOINT ["./run.sh"]
"""
    with open("Dockerfile", "w") as f:
        f.write(dockerfile_content)
    print("Dockerfile generated.")
    print_step_complete()


# Step 6: Add 'ipython' Import to Entrypoint File
def add_ipython_to_entrypoint():
    print("Ensuring 'ipython' is imported in the entrypoint file...")
    entrypoint = config.get("ENTRYPOINT", "run.py")

    # Check if the entrypoint file exists
    entrypoint_path = Path(entrypoint)
    if not entrypoint_path.exists():
        print(f"Entrypoint file '{entrypoint}' not found. Please verify the config.")
        exit(1)

    # Add 'import ipython' if not already present
    with open(entrypoint_path, "r") as f:
        lines = f.readlines()

    if not any("import IPython" in line for line in lines):
        print(f"'ipython' not found in {entrypoint}. Adding it now...")
        with open(entrypoint_path, "w") as f:
            f.write("import IPython\n")  # Add the import at the top
            f.writelines(lines)
    else:
        print(f"'ipython' is already imported in {entrypoint}.")

    print(f"'ipython' import ensured in {entrypoint}.")


# Step 7: Load Secrets and Configurations
def load_config_and_secrets():
    try:
        print("Loading project and organization IDs from config.yaml...")
        print("Setting additional environment variables and loading secrets...")
        os.environ["BEEKEEPER_PROJECT_ID"] = config.get("BEEKEEPER_PROJECT_ID")
        os.environ["BEEKEEPER_ORGANIZATION_ID"] = config.get(
            "BEEKEEPER_ORGANIZATION_ID"
        )
        email_address = config.get("BEEKEEPER_USERNAME")
        os.environ["BEEKEEPER_ENVIRONMENT"] = config.get(
            "BEEKEEPER_ENVIRONMENT", "prod"
        )
        algo_type = config.get("ALGORITHM_TYPE", "validation")
        algo_name = config.get("ALGORITHM_NAME", "Jupyter Algorithm")
        algo_description = config.get("ALGORITHM_DESCRIPTION", "null")
        version_description = config.get("VERSION_DESCRIPTION", "null")

        if not config.get("BEEKEEPER_PROJECT_ID") or not config.get(
            "BEEKEEPER_ORGANIZATION_ID"
        ):
            raise ValueError(
                "Missing BEEKEEPER_PROJECT_ID or BEEKEEPER_ORGANIZATION_ID in config.yaml."
            )
        print(
            f"Found user {email_address} from organization {config.get('BEEKEEPER_ORGANIZATION_ID')} on project {config.get('BEEKEEPER_PROJECT_ID')}."
        )

        # Extract secrets from environment
        secret_key_b64 = os.environ.get("CONTENT_ENCRYPTION_KEY")
        project_private_key_b64 = os.environ.get("PROJECT_PRIVATE_KEY")

        # Check for required environment variables
        if not secret_key_b64:
            raise ValueError("Missing CONTENT_ENCRYPTION_KEY environment variable")
        if not project_private_key_b64:
            raise ValueError("Missing PROJECT_PRIVATE_KEY environment variable")

        print("Configuration and secrets successfully loaded.")
        print_step_complete()

        # Return combined configuration and secrets
        return {
            "BEEKEEPER_USERNAME": email_address,
            "ALGORITHM_TYPE": algo_type,
            "ALGORITHM_NAME": algo_name,
            "ALGORITHM_DESCRIPTION": algo_description,
            "VERSION_DESCRIPTION": version_description,
        }

    except Exception as e:
        print(f"Error loading configuration or secrets: {e}")
        raise (e)


# Step 8: Encrypt Files and Upload
def encrypt_and_upload(secrets):
    repo_name = "algocode"
    folder_path = f"temp/{repo_name}"
    os.makedirs(folder_path, exist_ok=True)

    print("Preparing files for upload...")
    command = (
        [
            "rsync",
            "-av",
            "--exclude",
            ".git",
            "--exclude",
            "temp",
            "--exclude",
            ".ipynb_checkpoints",
            "--exclude",
            ".virtual_documents",
            "--exclude",
            "*.ipynb",
        ]
        + [f"--exclude={item}" for item in config.get("EXCLUDED_FILES")]
        + [".", folder_path]
    )
    subprocess.run(command, check=True)

    print("Encrypting and uploading files...")
    subprocess.run(
        [
            "escrowai",
            folder_path,
            "--algorithm_type",
            secrets["ALGORITHM_TYPE"],
            "--algorithm_name",
            secrets["ALGORITHM_NAME"],
            "--algorithm_description",
            secrets["ALGORITHM_DESCRIPTION"],
            "--version_description",
            secrets["VERSION_DESCRIPTION"],
            "--username",
            secrets["BEEKEEPER_USERNAME"],
        ],
        check=True,
    )
    print("Encryption and upload complete.")
    print_step_complete()


# Step 9: Clean up
def cleanup(converted_scripts):
    print("Cleaning up temporary files...")
    subprocess.run(["rm", "-rf", "temp/"], check=True)
    for i in converted_scripts:
        os.remove(i)
    print("Clean up complete.")


# Main Execution
if __name__ == "__main__":
    try:
        converted_scripts = []
        install_dependencies()
        converted_scripts = convert_notebooks_to_scripts()
        generate_requirements()
        generate_run_script()
        generate_dockerfile()
        add_ipython_to_entrypoint()
        secrets = load_config_and_secrets()
        encrypt_and_upload(secrets)
        cleanup(converted_scripts)
    except Exception as e:
        cleanup(converted_scripts)
        raise (e)

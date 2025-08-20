import os
import sys
import argparse
import requests
import subprocess
from pathlib import Path
from typing import Dict

# Network configuration mapping
NETWORK_CONFIGS = {
    "testnet": {
        "openapi_url": "https://api.etherealtest.net/openapi.json",
        "output_dir": "ethereal/models/testnet",
        "output_file": "rest.py",
    },
    "devnet": {
        "openapi_url": "https://api.etherealdev.net/openapi.json",
        "output_dir": "ethereal/models/devnet",
        "output_file": "rest.py",
    },
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate Pydantic types from OpenAPI spec"
    )
    parser.add_argument(
        "--network",
        type=str,
        choices=list(NETWORK_CONFIGS.keys()),
        default="testnet",
        help="Network to generate types for (default: testnet)",
    )
    parser.add_argument(
        "--url", type=str, help="Custom OpenAPI spec URL (overrides network default)"
    )
    return parser.parse_args()


def get_config(args) -> Dict[str, str]:
    """Get configuration based on arguments"""
    config = NETWORK_CONFIGS[args.network].copy()

    if args.url:
        config["openapi_url"] = args.url

    # Generate network-specific file names
    config["output_dir"] = f"ethereal/models/{args.network}"
    config["output_file"] = "rest.py"

    return config


def generate_types(network: str, config: Dict[str, str]):
    """Generate types for a specific network"""
    print(f"Generating types for {network}...")
    print(f"Fetching OpenAPI spec from: {config['openapi_url']}")

    # Request the spec
    try:
        response = requests.get(config["openapi_url"])
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching OpenAPI spec: {e}")
        sys.exit(1)

    # Create output directory if it doesn't exist
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write the spec to a temporary file
    temp_spec_file = f"openapi_{network}.json"
    with open(temp_spec_file, "w") as f:
        f.write(response.text)

    # Construct output path
    output_path = output_dir / config["output_file"]

    # Run datamodel-codegen
    result = subprocess.run(
        [
            "uv",
            "run",
            "datamodel-codegen",
            "--input",
            temp_spec_file,
            "--output",
            str(output_path),
            "--input-file-type",
            "openapi",
            "--openapi-scopes",
            "paths",
            "schemas",
            "parameters",
            "--output-model-type",
            "pydantic_v2.BaseModel",
            "--snake-case-field",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"Error generating types: {result.stderr}")
        os.remove(temp_spec_file)
        sys.exit(1)
    else:
        print(f"Generated types successfully at: {output_path}")

    # Replace all instances of '0', or "0", with Decimal("0"),
    with open(output_path, "r") as f:
        content = f.read()
    content = content.replace("'0',", 'Decimal("0"),')
    content = content.replace('"0",', 'Decimal("0"),')
    with open(output_path, "w") as f:
        f.write(content)

    # Remove the temporary openapi.json file
    os.remove(temp_spec_file)


def main():
    args = parse_args()
    config = get_config(args)
    generate_types(args.network, config)


if __name__ == "__main__":
    main()

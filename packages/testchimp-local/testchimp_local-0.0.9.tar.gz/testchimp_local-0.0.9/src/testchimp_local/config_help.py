def file_not_found_help(config_file: str) -> str:
    return f"\n[ERROR] Config file not found: {config_file}\nPlease provide a valid path to your exploration config JSON file.\nRefer https://github.com/awarelabshq/testchimp-sdk/blob/main/localagent/README.md for configuration examples.\n"

def json_parse_error_help(config_file: str, error: Exception) -> str:
    return f"\n[ERROR] Failed to parse JSON in config file: {config_file}\nDetails: {error}\n\n- Ensure your file is valid JSON (no trailing commas, matching brackets, etc).\n- You can validate your JSON using online tools like https://jsonlint.com/\n- Refer https://github.com/awarelabshq/testchimp-sdk/blob/main/localagent/README.md for a valid config example.\n"

def config_validation_error_help(config_file: str, error: Exception) -> str:
    return f"\n[ERROR] Config file structure is invalid or missing required fields: {config_file}\nDetails: {error}\n\n- Make sure your config matches the required schema.\n- Refer: https://github.com/awarelabshq/testchimp-sdk/blob/main/localagent/README.md for guidance.\n"

def generic_config_error_help(config_file: str, error: Exception) -> str:
    return f"\n[ERROR] Unexpected error while loading config file: {config_file}\nDetails: {error}\n\n- Please check your file and try again.\n- If the problem persists, consult the documentation at https://github.com/awarelabshq/testchimp-sdk/blob/main/localagent/README.md or reach out to contact@testchimp.io for support.\n" 
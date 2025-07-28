import requests
import opengpt_constants
import opengpt_utils

def check_for_updates() -> None:
    try:
        latest_release_response: requests.Response = requests.get(f"https://api.github.com/repos/{opengpt_constants.REPOSITORY_OWNER}/{opengpt_constants.REPOSITORY_NAME}/releases/latest")
        if latest_release_response.status_code == 200:
            print(latest_release_response.json())
    except requests.exceptions.ConnectionError:
        pass

def get_server_status(port: int) -> bool:
    server_health_response: requests.Response = requests.get(f"http://localhost:{port}/health")
    if server_health_response.status_code == 200:
        opengpt_utils.new_print("Server is online", opengpt_constants.PRINT_COLORS["success"])
        return True
    return False
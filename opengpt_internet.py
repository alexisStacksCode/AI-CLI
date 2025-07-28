import requests
import opengpt_constants
import opengpt_utils

def get_server_status(port: int) -> bool:
    server_health_response: requests.Response = requests.get(f"http://localhost:{port}/health")
    if server_health_response.status_code == 200:
        opengpt_utils.new_print("Server is online", opengpt_constants.PRINT_COLORS["success"])
        return True
    return False
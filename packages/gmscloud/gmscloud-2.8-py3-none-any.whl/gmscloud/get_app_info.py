import re

def get_app_info():
    """Mengembalikan informasi dasar aplikasi termasuk versi dari setup.py."""
    try:
        with open("./../setup.py", "r") as file:
            setup_content = file.read()
        version_match = re.search(r"version=['\"]([^'\"]+)['\"]", setup_content)
        if version_match:
            version = version_match.group(1)
        else:
            version = "Unknown"
    except FileNotFoundError:
        version = "File setup.py tidak ditemukan"
    except Exception as e:
        version = f"Error: {str(e)}"
    
    return f"GmsCloud Print App - {version}"

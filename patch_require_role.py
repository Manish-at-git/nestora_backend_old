import os

PATH = "server.py"

def patch():
    with open(PATH, "r") as f:
        content = f.read()

    # Replace require_role("Super admin") with require_role(["Super admin"])
    content = content.replace('require_role("Super admin")', 'require_role(["Super admin"])')

    with open(PATH, "w") as f:
        f.write(content)

    print("Patched server.py successfully")

if __name__ == "__main__":
    patch()

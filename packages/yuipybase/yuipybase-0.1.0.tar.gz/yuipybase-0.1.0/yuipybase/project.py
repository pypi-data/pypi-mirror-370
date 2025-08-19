import os

def create_project_structure(base_dir="my_project"):
    structure = ["src", "tests", "docs"]
    os.makedirs(base_dir, exist_ok=True)
    for folder in structure:
        os.makedirs(os.path.join(base_dir, folder), exist_ok=True)
    # READMEと.gitignoreも作成
    open(os.path.join(base_dir, "README.md"), "w").close()
    with open(os.path.join(base_dir, ".gitignore"), "w") as f:
        f.write("__pycache__/\n*.pyc\n")
    print(f"Created project structure in {base_dir}")

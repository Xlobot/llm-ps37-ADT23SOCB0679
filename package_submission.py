"""
Automated packaging script for Roll No 37 (Omkar Gaikwad) submission.
Creates the exact required folder layout:
Your individual folder/
├── Report.pdf
├── Code.zip
├── github_link.txt
└── screenshots/
"""

import os
import shutil
import zipfile

def package():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sub_folder_name = "llm-ps37-ADT23SOCB0679"
    sub_dir = os.path.join(base_dir, "submission_package", sub_folder_name)
    
    # Clean previous
    if os.path.exists(sub_dir):
        shutil.rmtree(sub_dir)
    os.makedirs(sub_dir, exist_ok=True)
    
    # 1. Create Code.zip (excluding .env, venv, cache, and submission_package)
    code_zip_path = os.path.join(sub_dir, "Code.zip")
    exclude_dirs = {'.git', 'venv', 'env', '__pycache__', 'submission_package', '.idea', '.vscode'}
    exclude_files = {'.env', 'Code.zip'}
    
    with zipfile.ZipFile(code_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(base_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for file in files:
                if file in exclude_files or file.endswith('.pyc'):
                    continue
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, base_dir)
                if rel_path.startswith("submission_package"):
                    continue
                zipf.write(full_path, rel_path)
    print(f"Created Code.zip: {code_zip_path}")
    
    # 2. Copy Report.pdf
    src_report = os.path.join(base_dir, "Report.pdf")
    if os.path.exists(src_report):
        shutil.copy2(src_report, os.path.join(sub_dir, "Report.pdf"))
        print("Copied Report.pdf")
        
    # 3. Copy github_link.txt
    src_github = os.path.join(base_dir, "github_link.txt")
    if os.path.exists(src_github):
        shutil.copy2(src_github, os.path.join(sub_dir, "github_link.txt"))
        print("Copied github_link.txt")
        
    # 4. Copy screenshots/
    src_screens = os.path.join(base_dir, "screenshots")
    dst_screens = os.path.join(sub_dir, "screenshots")
    if os.path.exists(src_screens):
        shutil.copytree(src_screens, dst_screens)
        print("Copied screenshots/")

    # Also keep a copy of Code.zip in the root for convenience
    shutil.copy2(code_zip_path, os.path.join(base_dir, "Code.zip"))

    print("\nSubmission Package Ready at:")
    print(sub_dir)
    print("\nContents:")
    for item in os.listdir(sub_dir):
        print(f" - {item}")

if __name__ == "__main__":
    package()

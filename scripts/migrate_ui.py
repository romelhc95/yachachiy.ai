import os
import re

def search_and_replace(directory):
    for root, dirs, files in os.walk(directory):
        if 'node_modules' in dirs:
            dirs.remove('node_modules')
        if '.next' in dirs:
            dirs.remove('.next')
        if '.git' in dirs:
            dirs.remove('.git')
            
        for file in files:
            if file.endswith(('.tsx', '.ts', '.js', '.jsx', '.md', '.json', '.css', '.html', '.py', '.sql', '.txt')):
                if file == 'migrate_ui.py': continue
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    new_content = content.replace('Amauta', 'Yachachiy')
                    new_content = new_content.replace('amauta', 'yachachiy')
                    new_content = new_content.replace('AMAUTA', 'YACHACHIY')
                    
                    if new_content != content:
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"Updated: {path}")
                except Exception as e:
                    print(f"Error processing {path}: {e}")

if __name__ == "__main__":
    root_dir = r"C:\xampp\htdocs\yachachiy_ai"
    search_and_replace(root_dir)
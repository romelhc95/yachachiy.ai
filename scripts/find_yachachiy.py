import os

def find_amauta(directory):
    matches = []
    for root, dirs, files in os.walk(directory):
        if 'node_modules' in dirs:
            dirs.remove('node_modules')
        if '.next' in dirs:
            dirs.remove('.next')
        for file in files:
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'amauta' in content.lower():
                        matches.append(path)
            except:
                pass
    return matches

if __name__ == "__main__":
    web_dir = r"C:\xampp\htdocs\yachachiy_ai\web"
    matches = find_amauta(web_dir)
    for m in matches:
        print(m)

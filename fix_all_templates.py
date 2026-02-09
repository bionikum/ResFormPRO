import os
import re

def fix_navbar_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Ищем navbar и заменяем стиль
    pattern = r'(<nav class="navbar navbar-expand-lg navbar-light"[^>]*)(>)'
    
    def replace_navbar(match):
        before = match.group(1)
        after = match.group(2)
        # Если уже есть стиль, заменяем его
        if 'style=' in before:
            before = re.sub(r'style="[^"]*"', 'style="background-color: #ffffff; border-bottom: 3px solid #4CAF50;"', before)
        else:
            before = before + ' style="background-color: #ffffff; border-bottom: 3px solid #4CAF50;"'
        return before + after
    
    new_content = re.sub(pattern, replace_navbar, content)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

# Обходим все HTML файлы кроме login.html и register.html
templates_dir = 'app/templates'
fixed_count = 0

for root, dirs, files in os.walk(templates_dir):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            # Пропускаем login и register
            if 'login.html' in filepath or 'register.html' in filepath:
                continue
            
            if fix_navbar_in_file(filepath):
                print(f"Исправлен: {filepath}")
                fixed_count += 1

print(f"\nВсего исправлено файлов: {fixed_count}")

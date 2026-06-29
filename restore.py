import re
import os

target_dir = r'c:\Users\DELL\Documents\PROYECTO FINAL\reservas\templates\reservas'
os.makedirs(target_dir, exist_ok=True)

with open(r'c:\Users\DELL\Documents\PROYECTO FINAL\implementacion html.MD', 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern: ## Paso X: Crear `filename` ... ```html ... ```
pattern = re.compile(r'## Paso \d+: Crear `([^`]+)`.*?```(?:html|python|django|)\n(.*?)```', re.DOTALL | re.IGNORECASE)
matches = pattern.finditer(content)

count = 0
for match in matches:
    filename = match.group(1).strip()
    code = match.group(2).strip()
    
    if filename.endswith('.html'):
        if 'partials' in filename or '/' in filename:
            name = filename.split('/')[-1]
            if 'partials' in filename:
                out_dir = os.path.join(target_dir, 'partials')
                os.makedirs(out_dir, exist_ok=True)
                out_path = os.path.join(out_dir, name)
            else:
                out_path = os.path.join(target_dir, name)
        else:
            out_path = os.path.join(target_dir, filename)
            
        with open(out_path, 'w', encoding='utf-8') as out_f:
            out_f.write(code + '\n')
            
        print(f'Restored {filename} to {out_path}')
        count += 1

print(f'Total templates restored: {count}')

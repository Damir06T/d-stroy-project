import os

def print_structure(startpath):
    # Папки, которые мы СКРЫВАЕМ (чтобы не засорять чат)
    exclude_dirs = {
        'node_modules', '.git', 'dist', 'build', 
        '.vscode', '.idea', '__pycache__', 'venv', 'env', 'prisma/migrations'
    }
    
    # Файлы, которые мы СКРЫВАЕМ
    exclude_files = {
        'package-lock.json', 'yarn.lock', '.DS_Store', 
        'check_structure.py'
    }

    for root, dirs, files in os.walk(startpath):
        # Фильтруем папки на лету
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * level
        folder_name = os.path.basename(root)
        
        # Красиво печатаем имя папки
        if folder_name:
            print(f'{indent}📂 {folder_name}/')
        else:
            print(f'📂 [Корень проекта]/')
        
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            # Скрываем исключенные файлы и тяжелые базы данных/логи
            if f not in exclude_files and not f.endswith('.sqlite') and not f.endswith('.log'):
                print(f'{subindent}📄 {f}')

if __name__ == "__main__":
    print("Структура проекта:\n" + "="*30)
    print_structure('.')
    print("="*30)
    input("\nВыдели всё выше, скопируй, и нажми Enter для выхода...")
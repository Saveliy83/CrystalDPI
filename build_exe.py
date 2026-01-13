"""
Простой сборщик EXE для CrystalDPI
"""

import sys
import os
import subprocess
import shutil
import tempfile

def check_dependencies():
    """Проверяет и устанавливает зависимости"""
    print("Проверка зависимостей...")
    
    try:
        import PyQt5
        print("✓ PyQt5 установлен")
    except ImportError:
        print("Установка PyQt5...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt5"])
    
    try:
        import PyInstaller
        print("✓ PyInstaller установлен")
    except ImportError:
        print("Установка PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def create_spec_file():
    """Создает spec файл для сборки"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        # .bat файлы
        ('general (ALT).bat', '.'),
        ('general (ALT2).bat', '.'),
        ('general (ALT3).bat', '.'),
        ('general (ALT4).bat', '.'),
        ('general (ALT5).bat', '.'),
        ('general (ALT6).bat', '.'),
        ('general (ALT7).bat', '.'),
        ('general (ALT8).bat', '.'),
        ('general (ALT9).bat', '.'),
        ('general (ALT10).bat', '.'),
        ('general (ALT11).bat', '.'),
        # Папки
        ('lists', 'lists'),
        ('bin', 'bin')
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='CrystalDPI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    with open("CrystalDPI.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)
    
    print("✓ Создан spec файл")

def rename_bat_files():
    """Временно переименовывает .bat файлы без пробелов"""
    original_files = [
        "general (ALT).bat", "general (ALT2).bat", "general (ALT3).bat",
        "general (ALT4).bat", "general (ALT5).bat", "general (ALT6).bat",
        "general (ALT7).bat", "general (ALT8).bat", "general (ALT9).bat",
        "general (ALT10).bat", "general (ALT11).bat"
    ]
    
    renamed_files = [
        "general_ALT.bat", "general_ALT2.bat", "general_ALT3.bat",
        "general_ALT4.bat", "general_ALT5.bat", "general_ALT6.bat",
        "general_ALT7.bat", "general_ALT8.bat", "general_ALT9.bat",
        "general_ALT10.bat", "general_ALT11.bat"
    ]
    
    # Создаем копии с новыми именами
    for original, renamed in zip(original_files, renamed_files):
        if os.path.exists(original):
            shutil.copy2(original, renamed)
            print(f"✓ Создана копия: {original} -> {renamed}")
    
    return renamed_files

def modify_app_for_build():
    """Модифицирует app.py для работы с переименованными файлами"""
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Заменяем имена файлов в словаре
    old_dict = """        self.bat_files = {
            "general (ALT)": "general (ALT).bat",
            "general (ALT2)": "general (ALT2).bat",
            "general (ALT3)": "general (ALT3).bat",
            "general (ALT4)": "general (ALT4).bat",
            "general (ALT5)": "general (ALT5).bat",
            "general (ALT6)": "general (ALT6).bat",
            "general (ALT7)": "general (ALT7).bat",
            "general (ALT8)": "general (ALT8).bat",
            "general (ALT9)": "general (ALT9).bat",
            "general (ALT10)": "general (ALT10).bat",
            "general (ALT11)": "general (ALT11).bat"
        }"""
    
    new_dict = """        self.bat_files = {
            "general (ALT)": "general_ALT.bat",
            "general (ALT2)": "general_ALT2.bat",
            "general (ALT3)": "general_ALT3.bat",
            "general (ALT4)": "general_ALT4.bat",
            "general (ALT5)": "general_ALT5.bat",
            "general (ALT6)": "general_ALT6.bat",
            "general (ALT7)": "general_ALT7.bat",
            "general (ALT8)": "general_ALT8.bat",
            "general (ALT9)": "general_ALT9.bat",
            "general (ALT10)": "general_ALT10.bat",
            "general (ALT11)": "general_ALT11.bat"
        }"""
    
    content = content.replace(old_dict, new_dict)
    
    with open("app_build.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("✓ Создан app_build.py с исправленными путями")

def build_exe():
    """Собирает EXE файл"""
    print("\nЗапуск сборки EXE...")
    
    # Команда для PyInstaller
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=CrystalDPI",
        "--clean",
        "--noconfirm",
        "app_build.py"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("\n✓ Сборка успешно завершена!")
        
        # Проверяем наличие EXE файла
        exe_path = os.path.join("dist", "CrystalDPI.exe")
        if os.path.exists(exe_path):
            size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
            print(f"\nEXE файл создан: {os.path.abspath(exe_path)}")
            print(f"Размер файла: {size:.2f} MB")
            
            # Копируем EXE в текущую папку
            shutil.copy2(exe_path, "CrystalDPI.exe")
            print("✓ EXE файл скопирован в текущую папку")
            
            # Создаем README
            create_readme()
        else:
            print("✗ EXE файл не найден!")
            
    except subprocess.CalledProcessError as e:
        print(f"✗ Ошибка при сборке: {e}")
    except Exception as e:
        print(f"✗ Неожиданная ошибка: {e}")

def create_readme():
    """Создает файл README"""
    readme = """CrystalDPI - инструкция по установке

1. Скопируйте все файлы в одну папку:
   - CrystalDPI.exe
   - Все .bat файлы (11 штук)
   - Папки bin и lists (будут созданы автоматически)

2. Запустите CrystalDPI.exe

3. При первом запуске:
   - Будут созданы папки bin и lists (если их нет)
   - В lists будут созданы файлы list-general.txt и list-exclude.txt

4. Использование:
   - Вкладка "Подключение": выбор и запуск конфигураций
   - Вкладка "Основной список": редактирование списка доменов
   - Вкладка "Исключения": редактирование списка исключений

Примечание: .bat файлы должны находиться в той же папке, что и EXE файл.
"""
    
    with open("README.txt", "w", encoding="utf-8") as f:
        f.write(readme)
    
    print("✓ Создан файл README.txt")

def cleanup():
    """Очистка временных файлов"""
    files_to_remove = [
        "CrystalDPI.spec",
        "app_build.py",
        "general_ALT.bat", "general_ALT2.bat", "general_ALT3.bat",
        "general_ALT4.bat", "general_ALT5.bat", "general_ALT6.bat",
        "general_ALT7.bat", "general_ALT8.bat", "general_ALT9.bat",
        "general_ALT10.bat", "general_ALT11.bat"
    ]
    
    folders_to_remove = ["build"]
    
    print("\nОчистка временных файлов...")
    
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
            print(f"✓ Удален: {file}")
    
    for folder in folders_to_remove:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"✓ Удалена папка: {folder}")

def main():
    print("=" * 60)
    print("Сборщик EXE для CrystalDPI")
    print("=" * 60)
    
    try:
        # Шаг 1: Проверка зависимостей
        check_dependencies()
        
        # Шаг 2: Создание временных копий .bat файлов
        rename_bat_files()
        
        # Шаг 3: Модификация app.py
        modify_app_for_build()
        
        # Шаг 4: Создание spec файла
        create_spec_file()
        
        # Шаг 5: Сборка EXE
        build_exe()
        
        # Шаг 6: Очистка
        cleanup()
        
        print("\n" + "=" * 60)
        print("Сборка успешно завершена!")
        print("=" * 60)
        
        print("\nГотовые файлы:")
        print("1. dist/CrystalDPI.exe - основной исполняемый файл")
        print("2. CrystalDPI.exe - копия в текущей папке")
        print("3. README.txt - инструкция по установке")
        
        input("\nНажмите Enter для выхода...")
        
    except Exception as e:
        print(f"\n✗ Ошибка: {e}")
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()
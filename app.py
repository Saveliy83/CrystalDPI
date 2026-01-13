import sys
import os
import subprocess
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QFrame, QMessageBox,
                             QComboBox, QTabWidget, QTextEdit, QGroupBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor, QBrush, QFont, QPen

class ModernButton(QPushButton):
    """Круглая кнопка с современными анимациями"""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(150, 150)
        self.setCursor(Qt.PointingHandCursor)
        
        font = QFont("Segoe UI", 12, QFont.Medium)
        self.setFont(font)
        
        self.normal_color = QColor("#2196F3")
        self.hover_color = QColor("#1976D2")
        self.pressed_color = QColor("#0D47A1")
        self.success_color = QColor("#4CAF50")
        self.disconnect_color = QColor("#F44336")
        self.current_color = self.normal_color
        
        self.is_connected = False
        self.is_hovered = False
        self.is_pressed = False
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        painter.setBrush(QBrush(self.current_color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(10, 10, 130, 130)
        
        painter.setPen(Qt.white)
        painter.setFont(self.font())
        
        if self.is_connected:
            font = QFont("Arial", 36, QFont.Bold)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignCenter, "✕")
        else:
            painter.drawText(self.rect(), Qt.AlignCenter, self.text())
        
        if self.is_hovered or self.is_pressed:
            painter.setBrush(QBrush(QColor(255, 255, 255, 30 if self.is_hovered else 50)))
            painter.drawEllipse(10, 10, 130, 130)
    
    def enterEvent(self, event):
        self.is_hovered = True
        if self.is_connected:
            self.current_color = self.disconnect_color
        else:
            self.current_color = self.hover_color
        self.update()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        self.is_hovered = False
        if self.is_connected:
            self.current_color = self.success_color
        else:
            self.current_color = self.normal_color
        self.update()
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_pressed = True
            if self.is_connected:
                self.current_color = self.disconnect_color
            else:
                self.current_color = self.pressed_color
            self.update()
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_pressed = False
            if self.is_connected:
                self.current_color = self.disconnect_color if self.is_hovered else self.success_color
            else:
                self.current_color = self.hover_color if self.is_hovered else self.normal_color
            self.update()
        super().mouseReleaseEvent(event)
    
    def set_connected(self, connected):
        self.is_connected = connected
        if connected:
            self.current_color = self.success_color
            self.setText("ОТКЛЮЧИТЬ")
        else:
            self.current_color = self.normal_color
            self.setText("ПОДКЛЮЧИТЬ")
        self.update()


class StatusIndicator(QWidget):
    """Индикатор статуса с анимацией"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(20, 20)
        self.status = "disconnected"
        
        self.rotation_angle = 0
        self.rotation_timer = QTimer()
        self.rotation_timer.timeout.connect(self.update_rotation)
        
    def update_rotation(self):
        self.rotation_angle = (self.rotation_angle + 30) % 360
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if self.status == "connected":
            painter.setBrush(QBrush(QColor("#4CAF50")))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(0, 0, 20, 20)
            
            painter.setPen(QPen(Qt.white, 2))
            painter.drawLine(5, 10, 9, 14)
            painter.drawLine(9, 14, 15, 6)
        
        elif self.status == "connecting":
            painter.setBrush(QBrush(QColor("#FF9800")))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(0, 0, 20, 20)
            
            painter.setPen(QPen(Qt.white, 2))
            painter.save()
            painter.translate(10, 10)
            painter.rotate(self.rotation_angle)
            painter.drawArc(-6, -6, 12, 12, 45 * 16, 270 * 16)
            painter.restore()
        
        else:
            painter.setBrush(QBrush(QColor("#F44336")))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(0, 0, 20, 20)
            
            painter.setPen(QPen(Qt.white, 2))
            painter.drawLine(5, 5, 15, 15)
            painter.drawLine(15, 5, 5, 15)
    
    def set_status(self, status):
        self.status = status
        if status == "connecting":
            self.rotation_timer.start(50)
        else:
            self.rotation_timer.stop()
        self.update()


class ListEditorTab(QWidget):
    """Вкладка для редактирования списка доменов"""
    
    def __init__(self, file_path, title, description="", parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.title = title
        self.description = description
        self.setup_ui()
        self.load_file()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Заголовок
        title_label = QLabel(self.title)
        title_label.setObjectName("editorTitle")
        title_label.setAlignment(Qt.AlignCenter)
        
        # Описание (если есть)
        if self.description:
            description_label = QLabel(self.description)
            description_label.setWordWrap(True)
            description_label.setObjectName("editorDescription")
            description_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(description_label)
        
        # Группа для добавления доменов
        add_group = QGroupBox("Добавить домены")
        add_group.setObjectName("addGroup")
        add_layout = QVBoxLayout(add_group)
        add_layout.setSpacing(8)
        
        # Текстовое поле для ввода новых доменов
        self.domain_input = QTextEdit()
        self.domain_input.setObjectName("domainInput")
        self.domain_input.setPlaceholderText("example.com\nsub.example.com")
        self.domain_input.setMaximumHeight(70)
        
        # Кнопки добавления
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Добавить")
        self.add_button.setObjectName("addButton")
        self.add_button.clicked.connect(self.add_domains)
        self.add_button.setFixedWidth(120)
        
        self.clear_input_button = QPushButton("Очистить")
        self.clear_input_button.setObjectName("clearInputButton")
        self.clear_input_button.clicked.connect(self.clear_input)
        self.clear_input_button.setFixedWidth(120)
        
        button_layout.addStretch()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.clear_input_button)
        button_layout.addStretch()
        
        add_layout.addWidget(self.domain_input)
        add_layout.addLayout(button_layout)
        
        # Группа для просмотра и редактирования
        view_group = QGroupBox("Текущий список")
        view_group.setObjectName("viewGroup")
        view_layout = QVBoxLayout(view_group)
        view_layout.setSpacing(8)
        
        # Текстовое поле для просмотра текущего списка
        self.domain_view = QTextEdit()
        self.domain_view.setObjectName("domainView")
        self.domain_view.setMinimumHeight(300)
        
        # Кнопки управления списком
        list_button_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.setObjectName("refreshButton")
        self.refresh_button.clicked.connect(self.load_file)
        self.refresh_button.setFixedWidth(100)
        
        self.clear_list_button = QPushButton("Очистить")
        self.clear_list_button.setObjectName("clearListButton")
        self.clear_list_button.clicked.connect(self.clear_list)
        self.clear_list_button.setFixedWidth(100)
        
        self.save_button = QPushButton("Сохранить")
        self.save_button.setObjectName("saveButton")
        self.save_button.clicked.connect(self.save_file)
        self.save_button.setFixedWidth(100)
        
        list_button_layout.addStretch()
        list_button_layout.addWidget(self.refresh_button)
        list_button_layout.addWidget(self.clear_list_button)
        list_button_layout.addWidget(self.save_button)
        list_button_layout.addStretch()
        
        view_layout.addWidget(self.domain_view)
        view_layout.addLayout(list_button_layout)
        
        # Добавление виджетов в основной layout
        layout.addWidget(title_label)
        if self.description:
            layout.addWidget(description_label)
        layout.addWidget(add_group)
        layout.addWidget(view_group)
        layout.addStretch()
    
    def load_file(self):
        """Загружает содержимое файла"""
        try:
            # Получаем директорию из пути
            directory = os.path.dirname(self.file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.domain_view.setText(content)
            else:
                # Создаем пустой файл
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    pass
                self.domain_view.setText("")
                
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить файл:\n{str(e)}")
    
    def add_domains(self):
        """Добавляет новые домены в список"""
        input_text = self.domain_input.toPlainText().strip()
        if not input_text:
            QMessageBox.warning(self, "Предупреждение", "Введите домены для добавления.")
            return
        
        new_domains = [d.strip() for d in input_text.split('\n') if d.strip()]
        
        if not new_domains:
            return
        
        existing_domains = []
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r', encoding='utf-8') as f:
                existing_domains = [d.strip() for d in f.read().split('\n') if d.strip()]
        
        added_count = 0
        duplicate_count = 0
        
        for domain in new_domains:
            if not self.is_valid_domain(domain):
                QMessageBox.warning(self, "Предупреждение", f"Неверный формат: {domain}")
                continue
                
            if domain not in existing_domains:
                existing_domains.append(domain)
                added_count += 1
            else:
                duplicate_count += 1
        
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(existing_domains))
            
            self.load_file()
            self.domain_input.clear()
            
            msg = f"Добавлено: {added_count}"
            if duplicate_count > 0:
                msg += f"\nДубликатов: {duplicate_count}"
            
            QMessageBox.information(self, "Успех", msg)
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить:\n{str(e)}")
    
    def is_valid_domain(self, domain):
        """Проверяет, является ли строка валидным доменом"""
        if not domain or not domain.strip():
            return False
        
        domain = domain.strip()
        
        # Допускаем IP-адреса
        if domain.replace('.', '').isdigit():
            # Это может быть IP адрес
            parts = domain.split('.')
            if len(parts) == 4 and all(part.isdigit() for part in parts):
                return True
        
        if '.' not in domain:
            return False
        
        if ' ' in domain or '\t' in domain:
            return False
        
        allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_')
        return all(c in allowed_chars for c in domain)
    
    def clear_input(self):
        """Очищает поле ввода"""
        self.domain_input.clear()
    
    def clear_list(self):
        """Очищает весь список"""
        reply = QMessageBox.question(
            self, "Подтверждение",
            "Очистить весь список?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    pass
                self.load_file()
                QMessageBox.information(self, "Успех", "Список очищен.")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка:\n{str(e)}")
    
    def save_file(self):
        """Сохраняет изменения в файле"""
        current_content = self.domain_view.toPlainText()
        
        domains = [d.strip() for d in current_content.split('\n') if d.strip()]
        invalid_domains = []
        
        for domain in domains:
            if not self.is_valid_domain(domain):
                invalid_domains.append(domain)
        
        if invalid_domains:
            reply = QMessageBox.warning(
                self, "Неверные домены",
                f"Неверные домены:\n\n" +
                "\n".join(invalid_domains) +
                "\n\nПродолжить без них?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                domains = [d for d in domains if self.is_valid_domain(d)]
                current_content = '\n'.join(domains)
            else:
                return
        
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(current_content)
            
            QMessageBox.information(self, "Успех", f"Сохранено.\nДоменов: {len(domains)}")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения:\n{str(e)}")


class ModernWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.bat_files = {
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
        }
        
        self.current_bat_file = list(self.bat_files.values())[0]
        self.process = None
        self.is_connected = False
        
        self.setup_ui()
        self.setup_styles()
        self.check_bat_files_existence()
        self.create_directories()
    
    def setup_ui(self):
        self.setWindowTitle("CrystalDPI")
        self.setFixedSize(900, 750)
        
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        # Вкладка подключения
        self.connection_tab = QWidget()
        self.setup_connection_tab()
        self.tab_widget.addTab(self.connection_tab, "Подключение")
        
        # Вкладка основного списка
        self.general_list_tab = ListEditorTab(
            "lists/list-general.txt",
            "Основной список доменов",
            "Домены для стандартной фильтрации (каждый с новой строки)"
        )
        self.tab_widget.addTab(self.general_list_tab, "Основной список")
        
        # Вкладка списка исключений
        self.exclude_list_tab = ListEditorTab(
            "lists/list-exclude.txt",
            "Список исключений",
            "Домены которые нужно исключить из фильтрации (каждый с новой строки)"
        )
        self.tab_widget.addTab(self.exclude_list_tab, "Исключения")
    
    def setup_connection_tab(self):
        """Настройка вкладки подключения"""
        layout = QVBoxLayout(self.connection_tab)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        title_label = QLabel("Подключение к системе")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("title")
        
        subtitle_label = QLabel("Выберите конфигурацию и установите соединение")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setObjectName("subtitle")
        
        # Выбор конфигурации
        config_layout = QHBoxLayout()
        config_label = QLabel("Конфигурация:")
        config_label.setObjectName("configLabel")
        
        self.config_combo = QComboBox()
        self.config_combo.setObjectName("configCombo")
        
        for display_name, filename in self.bat_files.items():
            self.config_combo.addItem(display_name, filename)
        
        self.config_combo.currentIndexChanged.connect(self.on_config_changed)
        
        config_layout.addStretch()
        config_layout.addWidget(config_label)
        config_layout.addSpacing(8)
        config_layout.addWidget(self.config_combo)
        config_layout.addStretch()
        
        # Кнопка подключения
        self.connect_button = ModernButton("ПОДКЛЮЧИТЬ")
        self.connect_button.clicked.connect(self.toggle_connection)
        
        # Статус
        self.status_label = QLabel("Ожидание подключения...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setObjectName("status")
        
        # Индикатор статуса
        self.status_indicator = StatusIndicator()
        
        # Layout для индикатора
        status_layout = QHBoxLayout()
        status_layout.addStretch()
        status_layout.addWidget(self.status_indicator)
        status_layout.addSpacing(8)
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        # Информационная панель
        info_frame = QFrame()
        info_frame.setObjectName("infoFrame")
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(15, 15, 15, 15)
        info_layout.setSpacing(8)
        
        info_title = QLabel("Информация")
        info_title.setObjectName("infoTitle")
        
        self.info_text = QLabel(
            f"Выбран файл: {self.current_bat_file}\n"
            "Нажмите кнопку для подключения"
        )
        self.info_text.setWordWrap(True)
        self.info_text.setObjectName("infoText")
        
        info_layout.addWidget(info_title)
        info_layout.addWidget(self.info_text)
        
        # Добавление виджетов
        layout.addStretch()
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addLayout(config_layout)
        layout.addStretch()
        layout.addWidget(self.connect_button, 0, Qt.AlignCenter)
        layout.addSpacing(15)
        layout.addLayout(status_layout)
        layout.addStretch()
        layout.addWidget(info_frame)
        layout.addStretch()
    
    def setup_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
            }
            
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
            
            QTabBar::tab {
                background: rgba(255, 255, 255, 0.1);
                color: white;
                padding: 8px 12px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-family: 'Segoe UI';
                font-size: 11px;
                min-width: 70px;
            }
            
            QTabBar::tab:selected {
                background: rgba(255, 255, 255, 0.2);
                font-weight: bold;
            }
            
            QTabBar::tab:hover {
                background: rgba(255, 255, 255, 0.15);
            }
            
            #title {
                font-family: 'Segoe UI';
                font-size: 24px;
                font-weight: bold;
                color: white;
                padding: 5px;
            }
            
            #subtitle {
                font-family: 'Segoe UI';
                font-size: 13px;
                color: rgba(255, 255, 255, 0.9);
                padding: 3px;
            }
            
            #configLabel {
                font-family: 'Segoe UI';
                font-size: 14px;
                font-weight: medium;
                color: white;
            }
            
            #configCombo {
                font-family: 'Segoe UI';
                font-size: 13px;
                padding: 6px 12px;
                border-radius: 6px;
                background-color: white;
                border: 1px solid rgba(0, 0, 0, 0.3);
                color: #333;
                min-width: 180px;
            }
            
            #configCombo::drop-down {
                border: none;
            }
            
            #configCombo QAbstractItemView {
                background-color: white;
                color: #333;
                border-radius: 6px;
                border: 1px solid rgba(0, 0, 0, 0.1);
                font-size: 12px;
            }
            
            #status {
                font-family: 'Segoe UI';
                font-size: 14px;
                font-weight: medium;
                color: white;
                padding: 3px;
            }
            
            #infoFrame {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            
            #infoTitle {
                font-family: 'Segoe UI';
                font-size: 14px;
                font-weight: bold;
                color: white;
            }
            
            #infoText {
                font-family: 'Segoe UI';
                font-size: 12px;
                color: rgba(255, 255, 255, 0.9);
                line-height: 1.4;
            }
            
            /* Стили для редактора списков */
            #editorTitle {
                font-family: 'Segoe UI';
                font-size: 18px;
                font-weight: bold;
                color: white;
                padding: 3px;
            }
            
            #editorDescription {
                font-family: 'Segoe UI';
                font-size: 11px;
                color: rgba(255, 255, 255, 0.8);
                padding: 3px;
            }
            
            QGroupBox {
                font-family: 'Segoe UI';
                font-size: 13px;
                font-weight: bold;
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            
            #domainInput, #domainView {
                font-family: 'Consolas', 'Monospace';
                font-size: 11px;
                padding: 6px;
                border-radius: 5px;
                background-color: rgba(255, 255, 255, 0.95);
                border: 1px solid rgba(0, 0, 0, 0.2);
                color: #333;
            }
            
            #domainInput:focus, #domainView:focus {
                border: 1px solid #2196F3;
            }
            
            QPushButton {
                font-family: 'Segoe UI';
                font-size: 12px;
                padding: 6px 12px;
                border-radius: 5px;
                border: none;
                min-height: 25px;
            }
            
            #addButton {
                background-color: #4CAF50;
                color: white;
            }
            
            #addButton:hover {
                background-color: #45a049;
            }
            
            #clearInputButton {
                background-color: #FF9800;
                color: white;
            }
            
            #clearInputButton:hover {
                background-color: #F57C00;
            }
            
            #refreshButton {
                background-color: #2196F3;
                color: white;
            }
            
            #refreshButton:hover {
                background-color: #1976D2;
            }
            
            #clearListButton {
                background-color: #F44336;
                color: white;
            }
            
            #clearListButton:hover {
                background-color: #D32F2F;
            }
            
            #saveButton {
                background-color: #673AB7;
                color: white;
            }
            
            #saveButton:hover {
                background-color: #5E35B1;
            }
        """)
    
    def create_directories(self):
        """Создает необходимые директории"""
        directories = ['bin', 'lists']
        for dir_name in directories:
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
                print(f"Создана директория: {dir_name}")
    
    def check_bat_files_existence(self):
        """Проверяет существование всех .bat файлов"""
        print("Проверка существования .bat файлов...")
        missing_files = []
        for display_name, filename in self.bat_files.items():
            if os.path.exists(filename):
                print(f"✓ Файл найден: {filename}")
            else:
                print(f"✗ Файл отсутствует: {filename}")
                missing_files.append((display_name, filename))
        
        if missing_files:
            msg = "Не найдены файлы:\n\n"
            for display_name, filename in missing_files:
                msg += f"• {display_name} ({filename})\n"
            msg += "\nПроверьте наличие файлов."
            
            QMessageBox.warning(self, "Файлы не найдены", msg)
    
    def on_config_changed(self, index):
        """Обработчик изменения выбранной конфигурации"""
        self.current_bat_file = self.config_combo.currentData()
        self.info_text.setText(
            f"Выбран файл: {self.current_bat_file}\n"
            "Нажмите кнопку для подключения"
        )
        print(f"Выбрана конфигурация: {self.config_combo.currentText()}, файл: {self.current_bat_file}")
    
    def run_bat_file(self):
        """Запускает выбранный .bat файл"""
        try:
            if not os.path.exists(self.current_bat_file):
                QMessageBox.critical(self, "Ошибка", 
                    f"Файл {self.current_bat_file} не найден!")
                raise FileNotFoundError(f"Файл {self.current_bat_file} не найден")
            
            bat_path = os.path.abspath(self.current_bat_file)
            bat_dir = os.path.dirname(bat_path)
            
            print(f"Запуск файла: {bat_path}")
            print(f"Рабочая директория: {bat_dir}")
            
            command = f'cmd /c "{bat_path}"'
            
            self.process = subprocess.Popen(
                command,
                shell=True,
                cwd=bat_dir,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            
            print(f"Конфигурация {self.config_combo.currentText()} запущена (PID: {self.process.pid})")
            
        except Exception as e:
            print(f"Ошибка при запуске скрипта: {e}")
            QMessageBox.warning(self, "Ошибка", 
                f"Не удалось запустить скрипт:\n{str(e)}")
            raise
    
    def kill_winws_process(self):
        """Завершает все процессы winws.exe"""
        try:
            result = subprocess.run(
                'tasklist /FI "IMAGENAME eq winws.exe"',
                shell=True,
                capture_output=True,
                text=True,
                encoding='cp866'
            )
            
            if "winws.exe" in result.stdout:
                print("Обнаружен процесс winws.exe. Завершаем...")
                
                subprocess.run(
                    'taskkill /F /IM winws.exe',
                    shell=True,
                    capture_output=True,
                    text=True
                )
                
                time.sleep(1)
                
                result_check = subprocess.run(
                    'tasklist /FI "IMAGENAME eq winws.exe"',
                    shell=True,
                    capture_output=True,
                    text=True,
                    encoding='cp866'
                )
                
                if "winws.exe" not in result_check.stdout:
                    print("Процесс winws.exe успешно завершен.")
                    return True
                else:
                    print("Не удалось завершить процесс winws.exe.")
                    return False
            else:
                print("Процесс winws.exe не найден.")
                return True
                
        except Exception as e:
            print(f"Ошибка при завершении процесса winws.exe: {e}")
            return False
    
    def stop_bat_file(self):
        """Останавливает запущенный .bat файл и все связанные процессы"""
        stopped_successfully = True
        
        if not self.kill_winws_process():
            stopped_successfully = False
        
        if self.process:
            try:
                try:
                    subprocess.run(f'taskkill /F /T /PID {self.process.pid}', 
                                  shell=True, check=True, capture_output=True)
                    print(f"Процесс bat-файла завершен (PID: {self.process.pid})")
                except subprocess.CalledProcessError as e:
                    print(f"Taskkill вернул ошибку для bat-файла: {e}")
                    try:
                        self.process.terminate()
                        print(f"Попытка завершить процесс bat-файла через terminate (PID: {self.process.pid})")
                    except:
                        print(f"Не удалось завершить процесс bat-файла (PID: {self.process.pid})")
                        stopped_successfully = False
                
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    try:
                        self.process.kill()
                        self.process.wait()
                        print(f"Процесс bat-файла принудительно завершен (PID: {self.process.pid})")
                    except:
                        print(f"Не удалось принудительно завершить процесс bat-файла (PID: {self.process.pid})")
                        stopped_successfully = False
                
                self.process = None
                
            except Exception as e:
                print(f"Ошибка при остановке процесса bat-файла: {e}")
                stopped_successfully = False
        
        try:
            subprocess.run('taskkill /F /IM cmd.exe', 
                          shell=True, capture_output=True)
            print("Завершены все процессы cmd.exe")
        except:
            pass
        
        return stopped_successfully
    
    def toggle_connection(self):
        if not self.is_connected:
            self.connect()
        else:
            self.disconnect()
    
    def connect(self):
        if not self.is_connected:
            self.status_indicator.set_status("connecting")
            self.status_label.setText(f"Подключение: {self.config_combo.currentText()}...")
            self.connect_button.setEnabled(False)
            self.config_combo.setEnabled(False)
            
            QTimer.singleShot(1500, self.complete_connection)
    
    def complete_connection(self):
        try:
            self.run_bat_file()
            self.is_connected = True
            self.connect_button.set_connected(True)
            self.status_indicator.set_status("connected")
            self.status_label.setText(f"Подключено: {self.config_combo.currentText()}")
            self.connect_button.setEnabled(True)
            self.show_success_message()
        except Exception as e:
            self.is_connected = False
            self.connect_button.set_connected(False)
            self.status_indicator.set_status("disconnected")
            self.status_label.setText("Ожидание подключения...")
            self.connect_button.setEnabled(True)
            self.config_combo.setEnabled(True)
    
    def disconnect(self):
        if self.is_connected:
            reply = QMessageBox.question(
                self, 'Отключение',
                f'Отключиться от "{self.config_combo.currentText()}"?\n'
                f'Будут завершены все связанные процессы.',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.status_indicator.set_status("connecting")
                self.status_label.setText("Выполняется отключение...")
                self.connect_button.setEnabled(False)
                
                stopped = self.stop_bat_file()
                
                QTimer.singleShot(1000, lambda: self.complete_disconnection(stopped))
    
    def complete_disconnection(self, stopped):
        self.is_connected = False
        
        self.connect_button.set_connected(False)
        self.status_indicator.set_status("disconnected")
        self.status_label.setText("Ожидание подключения...")
        self.connect_button.setEnabled(True)
        self.config_combo.setEnabled(True)
        
        if stopped:
            self.show_disconnect_message()
        else:
            QMessageBox.warning(self, "Внимание", 
                "Не удалось полностью остановить процесс.\n"
                "Проверьте диспетчер задач.")
    
    def show_success_message(self):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Подключение установлено")
        msg_box.setText(f"✓ Соединение установлено!\nКонфигурация: {self.config_combo.currentText()}")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStandardButtons(QMessageBox.Ok)
        
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: white;
                font-family: 'Segoe UI';
                border-radius: 8px;
                font-size: 12px;
            }
            QMessageBox QLabel {
                font-size: 12px;
                color: #333;
                padding: 8px;
            }
            QMessageBox QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 6px 15px;
                border-radius: 4px;
                font-size: 12px;
                min-width: 70px;
            }
            QMessageBox QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        msg_box.exec_()
    
    def show_disconnect_message(self):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Отключение выполнено")
        msg_box.setText(
            f"✓ Соединение разорвано!\n"
            f"Конфигурация: {self.config_combo.currentText()}"
        )
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStandardButtons(QMessageBox.Ok)
        
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: white;
                font-family: 'Segoe UI';
                border-radius: 8px;
                font-size: 12px;
            }
            QMessageBox QLabel {
                font-size: 12px;
                color: #333;
                padding: 8px;
            }
            QMessageBox QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 6px 15px;
                border-radius: 4px;
                font-size: 12px;
                min-width: 70px;
            }
            QMessageBox QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        msg_box.exec_()
    
    def closeEvent(self, event):
        if self.is_connected:
            reply = QMessageBox.question(
                self, 'Подтверждение',
                f'Закрыть приложение?\n'
                f'Конфигурация "{self.config_combo.currentText()}" будет отключена.',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.stop_bat_file()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = ModernWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
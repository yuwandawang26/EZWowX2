from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea, QWidget
from PySide6.QtCore import Qt


class SkillNameEditor(QDialog):
    """技能名称编辑器对话框"""

    def __init__(self, skill_manager, parent=None):
        super().__init__(parent)
        self.skill_manager = skill_manager
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("编辑技能名称")
        self.setFixedSize(300, 400)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)

        layout = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        self.edits = {}
        for color_key, data in self.skill_manager.get_all_skills().items():
            item_layout = QHBoxLayout()

            color_label = QLabel(color_key)
            color_label.setFixedWidth(80)
            color_label.setStyleSheet("color: rgb(150, 150, 150); font-family: Consolas; font-size: 9pt;")
            item_layout.addWidget(color_label)

            name_edit = QLineEdit(data['name'])
            name_edit.setMaxLength(8)
            name_edit.setFixedHeight(22)
            name_edit.setStyleSheet("""
                background-color: rgb(50, 50, 60);
                color: rgb(210, 210, 220);
                border: 1px solid rgb(60, 60, 70);
                border-radius: 4px;
                padding: 2px 4px;
            """)
            item_layout.addWidget(name_edit)

            self.edits[color_key] = name_edit
            scroll_layout.addLayout(item_layout)

        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        btn_layout = QHBoxLayout()

        reset_btn = QPushButton("重置")
        reset_btn.clicked.connect(self._on_reset)
        btn_layout.addWidget(reset_btn)

        btn_layout.addStretch()

        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def _on_reset(self):
        self.skill_manager.reset_all()
        for color_key, edit in self.edits.items():
            edit.setText(self.skill_manager.get_name(color_key))

    def _on_save(self):
        for color_key, edit in self.edits.items():
            new_name = edit.text().strip()
            if new_name:
                self.skill_manager.set_name(color_key, new_name)
        self.accept()
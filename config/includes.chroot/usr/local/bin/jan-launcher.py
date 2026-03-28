#!/usr/bin/env python3
# ============================================
#   JAN OS - 앱 검색기 (jan-launcher)
#   칼리 리눅스 스타일 전체화면 런처
#   단축키: Super 키 또는 직접 실행
# ============================================

import sys
import os
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QLabel, QGridLayout, QScrollArea,
    QFrame, QPushButton
)
from PyQt6.QtCore import Qt, QSize, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QFont, QKeyEvent, QPixmap, QColor

STYLE = """
/* 전체 배경 */
QWidget#launcher {
    background-color: rgba(5, 0, 15, 230);
}

/* 검색창 */
QLineEdit#search {
    background-color: rgba(20, 0, 40, 180);
    color: #ffffff;
    border: 2px solid #440088;
    border-radius: 8px;
    padding: 12px 20px;
    font-size: 20px;
    font-family: 'Nanum Gothic', sans-serif;
}
QLineEdit#search:focus {
    border: 2px solid #9933ff;
    background-color: rgba(30, 0, 60, 200);
}

/* 앱 버튼 */
QPushButton#app_btn {
    background-color: rgba(20, 0, 40, 150);
    color: #dddddd;
    border: 1px solid rgba(100, 0, 180, 80);
    border-radius: 8px;
    padding: 12px;
    font-size: 11px;
    font-family: 'Nanum Gothic', sans-serif;
    text-align: center;
}
QPushButton#app_btn:hover {
    background-color: rgba(80, 0, 150, 200);
    border: 1px solid #9933ff;
    color: #ffffff;
}
QPushButton#app_btn:pressed {
    background-color: rgba(120, 0, 200, 255);
}

/* 카테고리 라벨 */
QLabel#category {
    color: #7700cc;
    font-size: 11px;
    font-family: 'Nanum Gothic', sans-serif;
    padding: 4px 0px;
    letter-spacing: 2px;
}

/* 제목 */
QLabel#title {
    color: #9933ff;
    font-size: 14px;
    font-family: 'Nanum Gothic', sans-serif;
    padding: 8px 0px;
    letter-spacing: 1px;
}

/* 스크롤 */
QScrollArea {
    border: none;
    background-color: transparent;
}
QScrollBar:vertical {
    background-color: transparent;
    width: 6px;
}
QScrollBar::handle:vertical {
    background-color: #440088;
    border-radius: 3px;
}
"""

# 기본 앱 목록
DEFAULT_APPS = [
    # 이름, 실행 명령어, 카테고리, 이모지
    ("파일 탐색기", "jan-files", "시스템", "📁"),
    ("메모장", "jan-notepad", "도구", "📝"),
    ("터미널", "konsole", "시스템", "💻"),
    ("루트 터미널", "kdesu konsole", "시스템", "🔐"),
    ("Firefox", "firefox", "인터넷", "🌐"),
    ("케인 방송", "kane-stream", "인터넷", "📺"),
    ("텍스트 편집기", "kate", "도구", "✏️"),
    ("설정", "systemsettings", "시스템", "⚙️"),
    ("파일 관리자", "dolphin", "시스템", "🗂️"),
    ("스크린샷", "spectacle", "도구", "📷"),
    ("계산기", "kcalc", "도구", "🔢"),
    ("작업 관리자", "ksysguard", "시스템", "📊"),
    ("Wireshark", "wireshark", "보안", "🔍"),
    ("nmap", "konsole -e nmap", "보안", "🛡️"),
    ("Wine", "wine", "도구", "🍷"),
    ("VLC", "vlc", "미디어", "🎬"),
]

def get_installed_apps():
    """시스템에서 .desktop 파일 스캔"""
    apps = []
    desktop_dirs = [
        "/usr/share/applications",
        "/usr/local/share/applications",
        os.path.expanduser("~/.local/share/applications")
    ]
    for d in desktop_dirs:
        if not os.path.isdir(d):
            continue
        for f in os.listdir(d):
            if not f.endswith(".desktop"):
                continue
            path = os.path.join(d, f)
            try:
                name, exec_cmd, icon = "", "", ""
                with open(path, 'r', encoding='utf-8', errors='replace') as fp:
                    for line in fp:
                        if line.startswith("Name=") and not name:
                            name = line.strip().split("=", 1)[1]
                        elif line.startswith("Exec=") and not exec_cmd:
                            exec_cmd = line.strip().split("=", 1)[1]
                            exec_cmd = exec_cmd.replace("%u", "").replace("%U", "")
                            exec_cmd = exec_cmd.replace("%f", "").replace("%F", "").strip()
                        elif line.startswith("Icon=") and not icon:
                            icon = line.strip().split("=", 1)[1]
                if name and exec_cmd:
                    apps.append((name, exec_cmd, "설치된 앱", "📦"))
            except:
                pass
    return apps

class AppButton(QPushButton):
    def __init__(self, name, exec_cmd, emoji="📦", parent=None):
        super().__init__(parent)
        self.setObjectName("app_btn")
        self.exec_cmd = exec_cmd
        self.setFixedSize(110, 100)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 8, 4, 8)
        layout.setSpacing(4)

        emoji_label = QLabel(emoji)
        emoji_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        emoji_label.setStyleSheet("font-size: 28px; background: transparent; border: none;")

        name_label = QLabel(name)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setWordWrap(True)
        name_label.setStyleSheet("font-size: 11px; color: #dddddd; background: transparent; border: none;")

        layout.addWidget(emoji_label)
        layout.addWidget(name_label)

        self.clicked.connect(self.launch_app)

    def launch_app(self):
        try:
            subprocess.Popen(self.exec_cmd, shell=True,
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"실행 오류: {e}")
        QApplication.instance().activeWindow().hide()


class JanLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("launcher")
        self.setWindowTitle("JAN OS 런처")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        self.setStyleSheet(STYLE)
        self.all_apps = DEFAULT_APPS.copy()
        self.setup_ui()
        QTimer.singleShot(500, self.load_system_apps)

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(80, 60, 80, 60)
        main_layout.setSpacing(20)

        # 상단 제목
        title = QLabel("JAN OS")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #9933ff; font-size: 18px; letter-spacing: 4px;")
        main_layout.addWidget(title)

        # 검색창
        self.search = QLineEdit()
        self.search.setObjectName("search")
        self.search.setPlaceholderText("🔍  앱 검색...")
        self.search.textChanged.connect(self.filter_apps)
        self.search.setMaximumWidth(600)
        search_layout = QHBoxLayout()
        search_layout.addStretch()
        search_layout.addWidget(self.search)
        search_layout.addStretch()
        main_layout.addLayout(search_layout)

        # 앱 그리드 스크롤
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background: transparent;")
        self.grid = QGridLayout(self.scroll_content)
        self.grid.setSpacing(12)
        self.grid.setContentsMargins(20, 20, 20, 20)
        self.scroll.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll)

        # ESC 안내
        esc_label = QLabel("ESC  닫기")
        esc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        esc_label.setStyleSheet("color: #440066; font-size: 11px;")
        main_layout.addWidget(esc_label)

        self.render_apps(self.all_apps)
        self.search.setFocus()

    def load_system_apps(self):
        system_apps = get_installed_apps()
        existing_cmds = {a[1] for a in self.all_apps}
        for app in system_apps:
            if app[1] not in existing_cmds:
                self.all_apps.append(app)

    def render_apps(self, apps):
        # 기존 위젯 제거
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        cols = max(1, (self.width() - 160) // 125)
        for i, (name, cmd, category, emoji) in enumerate(apps):
            btn = AppButton(name, cmd, emoji)
            self.grid.addWidget(btn, i // cols, i % cols)

    def filter_apps(self, text):
        if not text:
            filtered = self.all_apps
        else:
            text_lower = text.lower()
            filtered = [a for a in self.all_apps
                       if text_lower in a[0].lower() or text_lower in a[2].lower()]
        self.render_apps(filtered)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
        elif event.key() == Qt.Key.Key_Return:
            text = self.search.text().lower()
            matches = [a for a in self.all_apps if text in a[0].lower()]
            if matches:
                try:
                    subprocess.Popen(matches[0][1], shell=True,
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)
                except:
                    pass
                self.hide()
        else:
            self.search.setFocus()

    def showEvent(self, event):
        self.search.clear()
        self.render_apps(self.all_apps)
        self.search.setFocus()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("JAN OS 런처")
    launcher = JanLauncher()
    launcher.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
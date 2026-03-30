#!/usr/bin/env python3
# ============================================
#   Mtefox Browser - JAN OS 전용 브라우저
#   PyQt5 → PyQt6 업그레이드
#   이미지 버튼 → 텍스트 버튼으로 대체
#   UI 개선 및 탭 기능 추가
# ============================================

import os
import sys
from PyQt6.QtCore import Qt, QUrl, QSize, QObject, QEvent, QPoint
from PyQt6.QtGui import QIcon, QKeyEvent, QMouseEvent, QShortcut, QKeySequence, QPainter, QColor, QFont
from PyQt6.QtWidgets import (
    QWidget, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QSizePolicy, QApplication, QTabWidget, QTabBar, QLabel,
    QMainWindow, QStatusBar, QProgressBar, QMenu, QToolButton, QStyle
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage


class CustomTabBar(QTabBar):
    """탭 닫기 버튼을 흰색 X 텍스트로 직접 그리는 커스텀 탭바"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDrawBase(False)

    def tabSizeHint(self, index):
        size = super().tabSizeHint(index)
        return QSize(max(size.width(), 150), size.height())

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        for i in range(self.count()):
            rect = self.tabRect(i)
            # 흰색 X 그리기 (오른쪽 끝에)
            close_rect_x = rect.right() - 20
            close_rect_y = rect.center().y() - 7
            painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            painter.setPen(QColor("#ffffff"))
            painter.drawText(close_rect_x, close_rect_y, 14, 14,
                           Qt.AlignmentFlag.AlignCenter, "X")
        painter.end()

    def mousePressEvent(self, event):
        for i in range(self.count()):
            rect = self.tabRect(i)
            close_rect_x = rect.right() - 20
            close_rect_y = rect.center().y() - 7
            from PyQt6.QtCore import QRect
            close_rect = QRect(close_rect_x, close_rect_y, 14, 14)
            if close_rect.contains(event.pos()):
                self.tabCloseRequested.emit(i)
                return
        super().mousePressEvent(event)

# ── 홈페이지 설정 ─────────────────────────
HOME_URL = "https://moongtang.netlify.app"

STYLE = """
QMainWindow, QWidget {
    background-color: #0d0d0d;
    color: #e0e0e0;
    font-family: 'Nanum Gothic', sans-serif;
    font-size: 13px;
}

/* 탭바 */
QTabWidget::pane {
    border: none;
    background-color: #0d0d0d;
}
QTabBar {
    background-color: #111118;
}
QTabBar::tab {
    background-color: #1a0028;
    color: #aaaaaa;
    border: none;
    padding: 8px 16px;
    min-width: 120px;
    max-width: 200px;
    border-right: 1px solid #0d0d0d;
}
QTabBar::tab:selected {
    background-color: #0d0d0d;
    color: #cc88ff;
    border-top: 2px solid #9933ff;
}
QTabBar::tab:hover:!selected {
    background-color: #220033;
    color: #dddddd;
}
QTabBar::close-button {
    color: #ffffff;
    subcontrol-position: right;
}
QTabBar::close-button:hover {
    background-color: #aa0000;
    border-radius: 2px;
}

/* 툴바 */
QWidget#toolbar {
    background-color: #111118;
    border-bottom: 1px solid #1a0028;
    padding: 4px;
}

/* 버튼들 */
QPushButton {
    background-color: transparent;
    color: #cc88ff;
    border: none;
    padding: 5px 10px;
    border-radius: 4px;
    font-size: 14px;
    min-width: 32px;
}
QPushButton:hover {
    background-color: #2a0a3a;
    color: #ffffff;
}
QPushButton:pressed {
    background-color: #4400aa;
}
QPushButton:disabled {
    color: #333355;
}

/* 주소창 */
QLineEdit#urlbar {
    background-color: #1a0028;
    color: #ffffff;
    border: 1px solid #330055;
    border-radius: 16px;
    padding: 6px 14px;
    font-size: 13px;
    selection-background-color: #6600aa;
}
QLineEdit#urlbar:focus {
    border: 1px solid #9933ff;
    background-color: #1e0030;
}

/* 진행바 */
QProgressBar {
    background-color: transparent;
    border: none;
    height: 2px;
}
QProgressBar::chunk {
    background-color: #9933ff;
    border-radius: 1px;
}

/* 상태바 */
QStatusBar {
    background-color: #0a0a0f;
    color: #555555;
    font-size: 11px;
    border-top: 1px solid #1a0028;
}

/* 탭 추가 버튼 */
QPushButton#new_tab_btn {
    background-color: transparent;
    color: #9933ff;
    border: none;
    font-size: 18px;
    padding: 4px 10px;
    border-radius: 4px;
    min-width: 30px;
}
QPushButton#new_tab_btn:hover {
    background-color: #2a0a3a;
}

/* 스크롤바 */
QScrollBar:vertical {
    background-color: #111118;
    width: 8px;
}
QScrollBar::handle:vertical {
    background-color: #4400aa;
    border-radius: 4px;
    min-height: 20px;
}
"""


class BrowserTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 진행바
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(2)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        # 웹뷰
        self.webview = QWebEngineView()
        profile = QWebEngineProfile.defaultProfile()
        profile.setHttpUserAgent(
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Mtefox/1.0"
        )
        layout.addWidget(self.webview)

        # 이벤트 연결
        self.webview.loadStarted.connect(self.on_load_started)
        self.webview.loadProgress.connect(self.on_load_progress)
        self.webview.loadFinished.connect(self.on_load_finished)

    def load(self, url: str):
        if not url.startswith("http://") and not url.startswith("https://"):
            if "." in url and " " not in url:
                url = "https://" + url
            else:
                url = f"https://www.google.com/search?q={url}"
        self.webview.load(QUrl(url))

    def on_load_started(self):
        self.progress_bar.show()
        self.progress_bar.setValue(0)

    def on_load_progress(self, progress):
        self.progress_bar.setValue(progress)

    def on_load_finished(self, ok):
        self.progress_bar.hide()
        self.progress_bar.setValue(0)


class MtefoxBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mtefox")
        self.setWindowIcon(QIcon("/usr/share/jan-os/Mtefox.png"))
        self.setGeometry(100, 100, 1280, 800)
        self.setStyleSheet(STYLE)
        self.setup_ui()
        self.setup_shortcuts()
        self.new_tab(HOME_URL)

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── 툴바 ────────────────────────────
        toolbar = QWidget()
        toolbar.setObjectName("toolbar")
        toolbar.setFixedHeight(48)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(8, 4, 8, 4)
        toolbar_layout.setSpacing(4)

        # 뒤로/앞으로/새로고침/홈
        self.btn_back = QPushButton("◀")
        self.btn_back.setToolTip("뒤로 (Alt+←)")
        self.btn_back.clicked.connect(self.go_back)

        self.btn_forward = QPushButton("▶")
        self.btn_forward.setToolTip("앞으로 (Alt+→)")
        self.btn_forward.clicked.connect(self.go_forward)

        self.btn_refresh = QPushButton("↺")
        self.btn_refresh.setToolTip("새로고침 (F5)")
        self.btn_refresh.setStyleSheet("font-size: 16px;")
        self.btn_refresh.clicked.connect(self.refresh_page)

        self.btn_home = QPushButton("⌂")
        self.btn_home.setToolTip("홈 (Alt+Home)")
        self.btn_home.setStyleSheet("font-size: 16px;")
        self.btn_home.clicked.connect(self.go_home)

        # 주소창
        self.url_bar = QLineEdit()
        self.url_bar.setObjectName("urlbar")
        self.url_bar.setPlaceholderText("주소 입력 또는 검색...")
        self.url_bar.returnPressed.connect(self.navigate)

        # 확대/축소 버튼
        self.btn_zoom_in = QPushButton("🔍+")
        self.btn_zoom_in.setToolTip("확대 (Ctrl++)")
        self.btn_zoom_in.setStyleSheet("font-size: 13px;")
        self.btn_zoom_in.clicked.connect(lambda: self.zoom(0.1))

        self.btn_zoom_out = QPushButton("🔍-")
        self.btn_zoom_out.setToolTip("축소 (Ctrl+-)")
        self.btn_zoom_out.setStyleSheet("font-size: 13px;")
        self.btn_zoom_out.clicked.connect(lambda: self.zoom(-0.1))

        # 북마크/메뉴 버튼
        self.btn_bookmark = QPushButton("☆")
        self.btn_bookmark.setToolTip("북마크 추가")
        self.btn_bookmark.setStyleSheet("font-size: 16px;")
        self.btn_bookmark.clicked.connect(self.toggle_bookmark)

        self.btn_menu = QPushButton("≡")
        self.btn_menu.setToolTip("메뉴")
        self.btn_menu.setStyleSheet("font-size: 18px;")
        self.btn_menu.clicked.connect(self.show_menu)

        toolbar_layout.addWidget(self.btn_back)
        toolbar_layout.addWidget(self.btn_forward)
        toolbar_layout.addWidget(self.btn_refresh)
        toolbar_layout.addWidget(self.btn_home)
        toolbar_layout.addWidget(self.url_bar, 1)
        toolbar_layout.addWidget(self.btn_zoom_in)
        toolbar_layout.addWidget(self.btn_zoom_out)
        toolbar_layout.addWidget(self.btn_bookmark)
        toolbar_layout.addWidget(self.btn_menu)

        main_layout.addWidget(toolbar)

        # ── 탭 위젯 ─────────────────────────
        self.tabs = QTabWidget()
        self.tabs.setTabBar(CustomTabBar())
        self.tabs.setTabsClosable(False)  # 기본 닫기버튼 끄고 커스텀으로 처리
        self.tabs.setMovable(True)
        self.tabs.tabBar().tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.on_tab_changed)

        # 새 탭 버튼
        new_tab_btn = QPushButton("+")
        new_tab_btn.setObjectName("new_tab_btn")
        new_tab_btn.setToolTip("새 탭 (Ctrl+T)")
        new_tab_btn.clicked.connect(lambda: self.new_tab(HOME_URL))
        self.tabs.setCornerWidget(new_tab_btn, Qt.Corner.TopRightCorner)

        main_layout.addWidget(self.tabs)

        # 상태바
        self.status = QStatusBar()
        self.setStatusBar(self.status)

    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+T"), self).activated.connect(
            lambda: self.new_tab(HOME_URL))
        QShortcut(QKeySequence("Ctrl+W"), self).activated.connect(
            lambda: self.close_tab(self.tabs.currentIndex()))
        QShortcut(QKeySequence("F5"), self).activated.connect(self.refresh_page)
        QShortcut(QKeySequence("Ctrl+R"), self).activated.connect(self.refresh_page)
        QShortcut(QKeySequence("Alt+Left"), self).activated.connect(self.go_back)
        QShortcut(QKeySequence("Alt+Right"), self).activated.connect(self.go_forward)
        QShortcut(QKeySequence("Alt+Home"), self).activated.connect(self.go_home)
        QShortcut(QKeySequence("Ctrl+L"), self).activated.connect(
            lambda: self.url_bar.selectAll() or self.url_bar.setFocus())
        QShortcut(QKeySequence("Escape"), self).activated.connect(self.stop_loading)
        QShortcut(QKeySequence("Ctrl+Tab"), self).activated.connect(self.next_tab)
        QShortcut(QKeySequence("Ctrl+Shift+Tab"), self).activated.connect(self.prev_tab)
        QShortcut(QKeySequence("Ctrl+="), self).activated.connect(lambda: self.zoom(0.1))
        QShortcut(QKeySequence("Ctrl++"), self).activated.connect(lambda: self.zoom(0.1))
        QShortcut(QKeySequence("Ctrl+-"), self).activated.connect(lambda: self.zoom(-0.1))

    def current_tab(self) -> BrowserTab:
        return self.tabs.currentWidget()

    def new_tab(self, url=HOME_URL):
        tab = BrowserTab()
        tab.webview.titleChanged.connect(
            lambda title, t=tab: self.update_tab_title(t, title))
        tab.webview.urlChanged.connect(self.update_url_bar)
        tab.webview.loadStarted.connect(
            lambda: self.btn_refresh.setText("✕"))
        tab.webview.loadFinished.connect(
            lambda: self.btn_refresh.setText("↺"))
        tab.webview.page().linkHovered.connect(self.status.showMessage)

        idx = self.tabs.addTab(tab, "새 탭")
        self.tabs.setCurrentIndex(idx)
        tab.load(url)

    def update_tab_title(self, tab, title):
        idx = self.tabs.indexOf(tab)
        if idx >= 0:
            short_title = title[:20] + "..." if len(title) > 20 else title
            self.tabs.setTabText(idx, short_title or "새 탭")
            if self.tabs.currentWidget() == tab:
                self.setWindowTitle(f"{title} - Mtefox")

    def update_url_bar(self, url: QUrl):
        if self.tabs.currentWidget():
            self.url_bar.setText(url.toString())
            self.url_bar.setCursorPosition(0)

    def on_tab_changed(self, idx):
        tab = self.tabs.widget(idx)
        if tab:
            self.url_bar.setText(tab.webview.url().toString())
            title = tab.webview.title()
            self.setWindowTitle(f"{title} - Mtefox" if title else "Mtefox")

    def close_tab(self, idx):
        if self.tabs.count() <= 1:
            self.close()
            return
        widget = self.tabs.widget(idx)
        self.tabs.removeTab(idx)
        if widget:
            widget.deleteLater()

    def navigate(self):
        tab = self.current_tab()
        if tab:
            tab.load(self.url_bar.text())

    def go_back(self):
        tab = self.current_tab()
        if tab:
            tab.webview.back()

    def go_forward(self):
        tab = self.current_tab()
        if tab:
            tab.webview.forward()

    def refresh_page(self):
        tab = self.current_tab()
        if tab:
            if tab.webview.page().isLoading() if hasattr(tab.webview.page(), 'isLoading') else False:
                tab.webview.stop()
            else:
                tab.webview.reload()

    def stop_loading(self):
        tab = self.current_tab()
        if tab:
            tab.webview.stop()

    def go_home(self):
        tab = self.current_tab()
        if tab:
            tab.load(HOME_URL)

    def toggle_bookmark(self):
        tab = self.current_tab()
        if tab:
            url = tab.webview.url().toString()
            self.status.showMessage(f"북마크 추가됨: {url}", 2000)
            self.btn_bookmark.setText("★")

    def show_menu(self):
        menu = QMenu(self)
        menu.addAction("새 탭", lambda: self.new_tab(HOME_URL))
        menu.addSeparator()
        menu.addAction("페이지 소스 보기", self.view_source)
        menu.addSeparator()
        menu.addAction("확대 🔍+", lambda: self.zoom(0.1))
        menu.addAction("축소 🔍-", lambda: self.zoom(-0.1))
        menu.addSeparator()
        menu.addAction("종료", self.close)
        menu.exec(self.btn_menu.mapToGlobal(
            self.btn_menu.rect().bottomLeft()))

    def view_source(self):
        tab = self.current_tab()
        if tab:
            url = "view-source:" + tab.webview.url().toString()
            self.new_tab(url)

    def zoom(self, delta):
        tab = self.current_tab()
        if tab:
            factor = tab.webview.zoomFactor() + delta
            tab.webview.setZoomFactor(max(0.3, min(factor, 3.0)))

    def set_zoom(self, factor):
        tab = self.current_tab()
        if tab:
            tab.webview.setZoomFactor(factor)

    def next_tab(self):
        idx = (self.tabs.currentIndex() + 1) % self.tabs.count()
        self.tabs.setCurrentIndex(idx)

    def prev_tab(self):
        idx = (self.tabs.currentIndex() - 1) % self.tabs.count()
        self.tabs.setCurrentIndex(idx)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_F5:
            self.refresh_page()
        elif event.key() == Qt.Key.Key_Escape:
            self.stop_loading()
        super().keyPressEvent(event)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Mtefox")
    app.setStyle("Fusion")
    window = MtefoxBrowser()
    # 인자로 URL 받으면 그 URL로 시작
    if len(sys.argv) > 1:
        window.new_tab(sys.argv[1])
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

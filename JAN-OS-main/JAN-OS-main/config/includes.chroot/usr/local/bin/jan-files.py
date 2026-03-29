#!/usr/bin/env python3
# ============================================
#   JAN OS - 파일 탐색기 (jan-files)
#   디자인: 보라색 + 검은색 기반
#   레이아웃: 왼쪽 사이드바 + 오른쪽 파일목록
# ============================================

import sys
import os
import shutil
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QTreeView, QListView, QFileSystemModel, QSplitter, QToolBar,
    QStatusBar, QLabel, QLineEdit, QMenu, QMessageBox, QInputDialog,
    QAbstractItemView, QFrame
)
from PyQt6.QtCore import Qt, QDir, QModelIndex, QSize
from PyQt6.QtGui import QIcon, QAction, QFont, QColor, QPalette

STYLE = """
QMainWindow, QWidget {
    background-color: #0d0d0d;
    color: #e0e0e0;
    font-family: 'Nanum Gothic', 'Malgun Gothic', sans-serif;
    font-size: 13px;
}

/* 사이드바 */
QTreeView {
    background-color: #111118;
    color: #cccccc;
    border: none;
    border-right: 1px solid #2a0a3a;
    padding: 4px;
    outline: none;
}
QTreeView::item:hover {
    background-color: #2a0a3a;
    color: #cc88ff;
}
QTreeView::item:selected {
    background-color: #6600aa;
    color: #ffffff;
    border-radius: 4px;
}

/* 파일 목록 */
QListView {
    background-color: #0d0d0d;
    color: #e0e0e0;
    border: none;
    padding: 8px;
    outline: none;
}
QListView::item {
    padding: 6px;
    border-radius: 4px;
    margin: 2px;
}
QListView::item:hover {
    background-color: #1e0030;
    color: #cc88ff;
}
QListView::item:selected {
    background-color: #6600aa;
    color: #ffffff;
}

/* 툴바 */
QToolBar {
    background-color: #111118;
    border-bottom: 1px solid #2a0a3a;
    padding: 4px;
    spacing: 4px;
}
QToolBar QToolButton {
    background-color: transparent;
    color: #cc88ff;
    border: none;
    padding: 6px 12px;
    border-radius: 4px;
    font-size: 13px;
}
QToolBar QToolButton:hover {
    background-color: #2a0a3a;
}
QToolBar QToolButton:pressed {
    background-color: #6600aa;
}

/* 경로 입력창 */
QLineEdit {
    background-color: #1a0028;
    color: #cc88ff;
    border: 1px solid #4400aa;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 13px;
}
QLineEdit:focus {
    border: 1px solid #9933ff;
}

/* 상태바 */
QStatusBar {
    background-color: #0a0a0f;
    color: #888888;
    border-top: 1px solid #1a0028;
}

/* 스크롤바 */
QScrollBar:vertical {
    background-color: #111118;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background-color: #4400aa;
    border-radius: 4px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover {
    background-color: #6600cc;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* 우클릭 메뉴 */
QMenu {
    background-color: #1a0028;
    color: #e0e0e0;
    border: 1px solid #4400aa;
    border-radius: 4px;
    padding: 4px;
}
QMenu::item {
    padding: 6px 20px;
    border-radius: 3px;
}
QMenu::item:selected {
    background-color: #6600aa;
    color: #ffffff;
}
QMenu::separator {
    height: 1px;
    background-color: #2a0a3a;
    margin: 4px 0px;
}

/* 헤더 */
QHeaderView::section {
    background-color: #111118;
    color: #9933ff;
    border: none;
    border-bottom: 1px solid #2a0a3a;
    padding: 4px 8px;
}

/* 스플리터 */
QSplitter::handle {
    background-color: #2a0a3a;
    width: 2px;
}
"""

class JanFileExplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JAN OS 파일 탐색기")
        self.setGeometry(100, 100, 1100, 700)
        self.setStyleSheet(STYLE)
        self.current_path = os.path.expanduser("~")
        self.setup_ui()

    def setup_ui(self):
        # 툴바
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)

        btn_back = QAction("◀ 뒤로", self)
        btn_back.triggered.connect(self.go_back)
        toolbar.addAction(btn_back)

        btn_up = QAction("▲ 위로", self)
        btn_up.triggered.connect(self.go_up)
        toolbar.addAction(btn_up)

        btn_home = QAction("⌂ 홈", self)
        btn_home.triggered.connect(self.go_home)
        toolbar.addAction(btn_home)

        toolbar.addSeparator()

        self.path_bar = QLineEdit(self.current_path)
        self.path_bar.returnPressed.connect(self.navigate_to_path)
        toolbar.addWidget(self.path_bar)

        toolbar.addSeparator()

        btn_new_folder = QAction("+ 폴더", self)
        btn_new_folder.triggered.connect(self.create_folder)
        toolbar.addAction(btn_new_folder)

        # 메인 레이아웃
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 사이드바 (트리뷰)
        self.sidebar_model = QFileSystemModel()
        self.sidebar_model.setRootPath("/")
        self.sidebar_model.setFilter(QDir.Filter.AllDirs | QDir.Filter.NoDotAndDotDot)

        self.sidebar = QTreeView()
        self.sidebar.setModel(self.sidebar_model)
        self.sidebar.setRootIndex(self.sidebar_model.index("/"))
        self.sidebar.setColumnHidden(1, True)
        self.sidebar.setColumnHidden(2, True)
        self.sidebar.setColumnHidden(3, True)
        self.sidebar.setHeaderHidden(True)
        self.sidebar.setMinimumWidth(200)
        self.sidebar.setMaximumWidth(280)
        self.sidebar.clicked.connect(self.sidebar_clicked)
        self.sidebar.setExpandsOnDoubleClick(True)

        # 파일 목록
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(self.current_path)
        self.file_model.setFilter(QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot)

        self.file_list = QListView()
        self.file_list.setModel(self.file_model)
        self.file_list.setRootIndex(self.file_model.index(self.current_path))
        self.file_list.setViewMode(QListView.ViewMode.IconMode)
        self.file_list.setIconSize(QSize(48, 48))
        self.file_list.setGridSize(QSize(90, 80))
        self.file_list.setResizeMode(QListView.ResizeMode.Adjust)
        self.file_list.setSpacing(8)
        self.file_list.doubleClicked.connect(self.file_double_clicked)
        self.file_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.show_context_menu)
        self.file_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        splitter.addWidget(self.sidebar)
        splitter.addWidget(self.file_list)
        splitter.setSizes([220, 880])

        layout.addWidget(splitter)

        # 상태바
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.update_status()

    def navigate(self, path):
        if os.path.isdir(path):
            self.current_path = path
            self.file_list.setRootIndex(self.file_model.index(path))
            self.path_bar.setText(path)
            self.update_status()

    def navigate_to_path(self):
        self.navigate(self.path_bar.text())

    def go_back(self):
        self.navigate(os.path.dirname(self.current_path))

    def go_up(self):
        self.navigate(os.path.dirname(self.current_path))

    def go_home(self):
        self.navigate(os.path.expanduser("~"))

    def sidebar_clicked(self, index):
        path = self.sidebar_model.filePath(index)
        self.navigate(path)

    def file_double_clicked(self, index):
        path = self.file_model.filePath(index)
        if os.path.isdir(path):
            self.navigate(path)
        else:
            os.system(f'xdg-open "{path}" &')

    def show_context_menu(self, pos):
        menu = QMenu(self)
        index = self.file_list.indexAt(pos)

        if index.isValid():
            path = self.file_model.filePath(index)
            open_action = QAction("열기", self)
            open_action.triggered.connect(lambda: os.system(f'xdg-open "{path}" &'))
            menu.addAction(open_action)
            menu.addSeparator()
            rename_action = QAction("이름 바꾸기", self)
            rename_action.triggered.connect(lambda: self.rename_file(path))
            menu.addAction(rename_action)
            delete_action = QAction("삭제", self)
            delete_action.triggered.connect(lambda: self.delete_file(path))
            menu.addAction(delete_action)
        else:
            new_folder = QAction("새 폴더", self)
            new_folder.triggered.connect(self.create_folder)
            menu.addAction(new_folder)
            refresh = QAction("새로고침", self)
            refresh.triggered.connect(lambda: self.navigate(self.current_path))
            menu.addAction(refresh)

        menu.exec(self.file_list.mapToGlobal(pos))

    def create_folder(self):
        name, ok = QInputDialog.getText(self, "새 폴더", "폴더 이름:")
        if ok and name:
            new_path = os.path.join(self.current_path, name)
            os.makedirs(new_path, exist_ok=True)

    def rename_file(self, path):
        old_name = os.path.basename(path)
        new_name, ok = QInputDialog.getText(self, "이름 바꾸기", "새 이름:", text=old_name)
        if ok and new_name:
            new_path = os.path.join(os.path.dirname(path), new_name)
            os.rename(path, new_path)

    def delete_file(self, path):
        reply = QMessageBox.question(self, "삭제 확인",
            f"'{os.path.basename(path)}' 을(를) 삭제할까요?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)

    def update_status(self):
        try:
            items = os.listdir(self.current_path)
            self.status.showMessage(f"  {len(items)}개 항목  |  {self.current_path}")
        except:
            self.status.showMessage(self.current_path)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("JAN OS 파일 탐색기")
    window = JanFileExplorer()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
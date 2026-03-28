#!/usr/bin/env python3
# ============================================
#   JAN OS - 메모장 (jan-notepad)
#   디자인: 검은색 기반
#   기능: 파일/편집/보기 메뉴바
# ============================================

import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QFileDialog,
    QMessageBox, QStatusBar, QLabel, QFontDialog,
    QInputDialog
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QFont, QKeySequence, QColor, QTextCharFormat

STYLE = """
QMainWindow, QWidget {
    background-color: #0a0a0a;
    color: #e0e0e0;
    font-family: 'Nanum Gothic Coding', 'D2Coding', monospace;
}

/* 메뉴바 */
QMenuBar {
    background-color: #111111;
    color: #cccccc;
    border-bottom: 1px solid #222222;
    padding: 2px;
}
QMenuBar::item {
    padding: 4px 12px;
    border-radius: 3px;
}
QMenuBar::item:selected {
    background-color: #222222;
    color: #ffffff;
}
QMenuBar::item:pressed {
    background-color: #333333;
}

/* 드롭다운 메뉴 */
QMenu {
    background-color: #1a1a1a;
    color: #e0e0e0;
    border: 1px solid #333333;
    border-radius: 4px;
    padding: 4px;
}
QMenu::item {
    padding: 6px 24px 6px 16px;
    border-radius: 3px;
}
QMenu::item:selected {
    background-color: #333333;
    color: #ffffff;
}
QMenu::separator {
    height: 1px;
    background-color: #2a2a2a;
    margin: 4px 0px;
}

/* 텍스트 편집창 */
QTextEdit {
    background-color: #0d0d0d;
    color: #e8e8e8;
    border: none;
    padding: 16px;
    font-size: 14px;
    line-height: 1.6;
    selection-background-color: #333399;
    selection-color: #ffffff;
}

/* 상태바 */
QStatusBar {
    background-color: #0a0a0a;
    color: #555555;
    border-top: 1px solid #1a1a1a;
    font-size: 11px;
}
QStatusBar QLabel {
    color: #555555;
    padding: 0px 8px;
}

/* 스크롤바 */
QScrollBar:vertical {
    background-color: #111111;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background-color: #333333;
    border-radius: 4px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover {
    background-color: #444444;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""

class JanNotepad(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JAN OS 메모장")
        self.setGeometry(150, 150, 900, 650)
        self.setStyleSheet(STYLE)
        self.current_file = None
        self.is_modified = False
        self.setup_ui()

    def setup_ui(self):
        # 텍스트 편집창
        self.editor = QTextEdit()
        self.editor.setFont(QFont("D2Coding", 13))
        self.editor.textChanged.connect(self.on_text_changed)
        self.setCentralWidget(self.editor)

        # 메뉴바
        menubar = self.menuBar()

        # 파일 메뉴
        file_menu = menubar.addMenu("파일")

        new_action = QAction("새 파일", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("열기...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        save_action = QAction("저장", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        saveas_action = QAction("다른 이름으로 저장...", self)
        saveas_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        saveas_action.triggered.connect(self.save_file_as)
        file_menu.addAction(saveas_action)

        file_menu.addSeparator()

        exit_action = QAction("종료", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 편집 메뉴
        edit_menu = menubar.addMenu("편집")

        undo_action = QAction("실행 취소", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self.editor.undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("다시 실행", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self.editor.redo)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        cut_action = QAction("잘라내기", self)
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.triggered.connect(self.editor.cut)
        edit_menu.addAction(cut_action)

        copy_action = QAction("복사", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(self.editor.copy)
        edit_menu.addAction(copy_action)

        paste_action = QAction("붙여넣기", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self.editor.paste)
        edit_menu.addAction(paste_action)

        edit_menu.addSeparator()

        select_all_action = QAction("전체 선택", self)
        select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)
        select_all_action.triggered.connect(self.editor.selectAll)
        edit_menu.addAction(select_all_action)

        find_action = QAction("찾기...", self)
        find_action.setShortcut(QKeySequence.StandardKey.Find)
        find_action.triggered.connect(self.find_text)
        edit_menu.addAction(find_action)

        # 보기 메뉴
        view_menu = menubar.addMenu("보기")

        font_action = QAction("글꼴 변경...", self)
        font_action.triggered.connect(self.change_font)
        view_menu.addAction(font_action)

        view_menu.addSeparator()

        zoom_in_action = QAction("크게", self)
        zoom_in_action.setShortcut(QKeySequence("Ctrl+="))
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)

        zoom_out_action = QAction("작게", self)
        zoom_out_action.setShortcut(QKeySequence("Ctrl+-"))
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)

        wordwrap_action = QAction("줄 바꿈", self)
        wordwrap_action.setCheckable(True)
        wordwrap_action.setChecked(True)
        wordwrap_action.triggered.connect(self.toggle_wordwrap)
        view_menu.addAction(wordwrap_action)

        # 상태바
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.lbl_pos = QLabel("줄 1, 열 1")
        self.lbl_count = QLabel("0자")
        self.lbl_file = QLabel("새 파일")
        self.status.addWidget(self.lbl_file)
        self.status.addPermanentWidget(self.lbl_count)
        self.status.addPermanentWidget(self.lbl_pos)

        self.editor.cursorPositionChanged.connect(self.update_status)

    def on_text_changed(self):
        self.is_modified = True
        self.update_title()
        self.update_status()

    def update_title(self):
        name = os.path.basename(self.current_file) if self.current_file else "새 파일"
        modified = " *" if self.is_modified else ""
        self.setWindowTitle(f"JAN OS 메모장 - {name}{modified}")

    def update_status(self):
        cursor = self.editor.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        count = len(self.editor.toPlainText())
        self.lbl_pos.setText(f"줄 {line}, 열 {col}")
        self.lbl_count.setText(f"{count}자")

    def new_file(self):
        if self.is_modified:
            if not self.ask_save():
                return
        self.editor.clear()
        self.current_file = None
        self.is_modified = False
        self.lbl_file.setText("새 파일")
        self.update_title()

    def open_file(self):
        if self.is_modified:
            if not self.ask_save():
                return
        path, _ = QFileDialog.getOpenFileName(self, "파일 열기", "",
            "텍스트 파일 (*.txt *.md *.py *.sh *.cfg *.conf);;모든 파일 (*)")
        if path:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                self.editor.setPlainText(f.read())
            self.current_file = path
            self.is_modified = False
            self.lbl_file.setText(os.path.basename(path))
            self.update_title()

    def save_file(self):
        if self.current_file:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
            self.is_modified = False
            self.update_title()
        else:
            self.save_file_as()

    def save_file_as(self):
        path, _ = QFileDialog.getSaveFileName(self, "다른 이름으로 저장", "",
            "텍스트 파일 (*.txt);;모든 파일 (*)")
        if path:
            self.current_file = path
            self.save_file()
            self.lbl_file.setText(os.path.basename(path))

    def ask_save(self):
        reply = QMessageBox.question(self, "저장",
            "변경사항을 저장할까요?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No |
            QMessageBox.StandardButton.Cancel)
        if reply == QMessageBox.StandardButton.Yes:
            self.save_file()
            return True
        elif reply == QMessageBox.StandardButton.No:
            return True
        return False

    def find_text(self):
        text, ok = QInputDialog.getText(self, "찾기", "찾을 내용:")
        if ok and text:
            cursor = self.editor.document().find(text)
            if cursor.isNull():
                QMessageBox.information(self, "찾기", f"'{text}'를 찾을 수 없습니다.")
            else:
                self.editor.setTextCursor(cursor)

    def change_font(self):
        font, ok = QFontDialog.getFont(self.editor.font(), self)
        if ok:
            self.editor.setFont(font)

    def zoom_in(self):
        self.editor.zoomIn(2)

    def zoom_out(self):
        self.editor.zoomOut(2)

    def toggle_wordwrap(self, checked):
        if checked:
            self.editor.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        else:
            self.editor.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

    def closeEvent(self, event):
        if self.is_modified:
            if self.ask_save():
                event.accept()
            else:
                event.ignore()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("JAN OS 메모장")
    window = JanNotepad()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
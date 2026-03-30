#!/bin/bash
# ============================================
#   JAN OS 앱 설치 스크립트
# ============================================

echo "[JAN OS] 앱 설치 시작좀하고..."

# PyQt6 설치
pip3 install PyQt6 --break-system-packages 2>/dev/null || \
    apt-get install -y python3-pyqt6

# 앱 파일 복사
cp jan-files.py /usr/local/bin/jan-files
cp jan-notepad.py /usr/local/bin/jan-notepad
cp jan-launcher.py /usr/local/bin/jan-launcher
chmod +x /usr/local/bin/jan-files
chmod +x /usr/local/bin/jan-notepad
chmod +x /usr/local/bin/jan-launcher

# .desktop 등록 (앱 메뉴에 표시)
cat > /usr/share/applications/jan-files.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=파일 탐색기
Name[en]=File Explorer
Comment=JAN OS 파일 탐색기
Exec=python3 /usr/local/bin/jan-files
Icon=system-file-manager
Terminal=false
Categories=System;FileManager;
EOF

cat > /usr/share/applications/jan-notepad.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=메모장
Name[en]=Notepad
Comment=JAN OS 메모장
Exec=python3 /usr/local/bin/jan-notepad
Icon=accessories-text-editor
Terminal=false
Categories=Utility;TextEditor;
EOF

cat > /usr/share/applications/jan-launcher.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=앱 검색기
Name[en]=App Launcher
Comment=JAN OS 앱 런처
Exec=python3 /usr/local/bin/jan-launcher
Icon=system-search
Terminal=false
Categories=System;
EOF

echo "[JAN OS] 앱 설치 완료!"
echo ""
echo "실행 방법:"
echo "  파일 탐색기: python3 jan-files.py"
echo "  메모장:      python3 jan-notepad.py"
echo "  앱 검색기:   python3 jan-launcher.py"

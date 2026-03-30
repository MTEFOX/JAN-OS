#!/bin/bash
# ============================================
#   JAN OS - Build Script
#   Debian 기반 커스텀 OS 빌드 스크립트
#   베이스: Debian 12 (Bookworm)
#   GUI: KDE Plasma
# ============================================

set -e

echo "============================================"
echo "   JAN OS 빌드좀하고..."
echo "============================================"

# live-build 설치 확인
if ! command -v lb &> /dev/null; then
    echo "[*] live-build 설치좀하고..."
    sudo apt-get update
    sudo apt-get install -y live-build
fi

# 이전 빌드 정리
echo "[*] 이전 빌드 정리좀하고..."
sudo lb clean --purge 2>/dev/null || true

# live-build 기본 설정
echo "[*] live-build 설정좀하고..."
lb config \
    --distribution bookworm \
    --architectures amd64 \
    --binary-images iso-hybrid \
    --debian-installer live \
    --bootappend-live "boot=live components locales=ko_KR.UTF-8,en_US.UTF-8 keyboard-layouts=kr,us" \
    --iso-application "JAN OS" \
    --iso-publisher "JAN OS Project" \
    --iso-volume "JANOS" \
    --memtest none \
    --win32-loader false

echo "[*] 빌드 설정 완료"
echo ""
echo "[*] ISO 빌드 시작좀하고(4시쯤)... (시간이 걸릴 수 있음)..."
sudo lb build

echo ""
echo "============================================"
echo "   빌드 완료!"
echo "   ISO 파일: live-image-amd64.hybrid.iso"
echo "============================================"

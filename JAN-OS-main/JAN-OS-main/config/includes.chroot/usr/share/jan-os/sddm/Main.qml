// ============================================
//   JAN OS - SDDM 로그인화면 테마 (Main.qml)
//   색상: 어두운 보라 + 검정
// ============================================

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import SddmComponents 2.0

Rectangle {
    id: root
    width: Screen.width
    height: Screen.height
    color: "#0a0010"

    // 배경 그라디언트
    Rectangle {
        anchors.fill: parent
        gradient: Gradient {
            GradientStop { position: 0.0; color: "#0a0010" }
            GradientStop { position: 0.5; color: "#0d0018" }
            GradientStop { position: 1.0; color: "#050008" }
        }
    }

    // 배경 장식 원
    Rectangle {
        width: 600; height: 600
        radius: 300
        x: -150; y: -150
        color: "transparent"
        border.color: "#1a0030"
        border.width: 1
        opacity: 0.5
    }
    Rectangle {
        width: 400; height: 400
        radius: 200
        x: root.width - 250; y: root.height - 250
        color: "transparent"
        border.color: "#1a0030"
        border.width: 1
        opacity: 0.5
    }

    // 중앙 로그인 박스
    Rectangle {
        id: loginBox
        width: 420
        height: 520
        anchors.centerIn: parent
        color: "#0d0018"
        radius: 16
        border.color: "#2a0050"
        border.width: 1

        // 상단 보라 라인
        Rectangle {
            width: parent.width
            height: 3
            radius: 2
            anchors.top: parent.top
            gradient: Gradient {
                orientation: Gradient.Horizontal
                GradientStop { position: 0.0; color: "transparent" }
                GradientStop { position: 0.5; color: "#9933ff" }
                GradientStop { position: 1.0; color: "transparent" }
            }
        }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 40
            spacing: 20

            // 로고
            Image {
                Layout.alignment: Qt.AlignHCenter
                source: "/usr/share/jan-os/logo.png"
                width: 100
                height: 100
                fillMode: Image.PreserveAspectFit

                // 로고 없을 때 텍스트로 대체
                visible: status === Image.Ready
            }
            Text {
                Layout.alignment: Qt.AlignHCenter
                text: "JAN"
                color: "#9933ff"
                font.pixelSize: 48
                font.bold: true
                font.letterSpacing: 8
                visible: logoImage.status !== Image.Ready
            }

            // OS 이름
            Text {
                Layout.alignment: Qt.AlignHCenter
                text: "JAN OS"
                color: "#9933ff"
                font.pixelSize: 22
                font.letterSpacing: 4
            }

            Text {
                Layout.alignment: Qt.AlignHCenter
                text: "Debian Based Custom OS"
                color: "#440066"
                font.pixelSize: 11
            }

            // 구분선
            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: "#1a0030"
            }

            // 유저 선택
            ComboBox {
                id: userCombo
                Layout.fillWidth: true
                model: userModel
                currentIndex: userModel.lastIndex
                height: 44

                contentItem: Text {
                    text: userCombo.displayText
                    color: "#cccccc"
                    font.pixelSize: 13
                    verticalAlignment: Text.AlignVCenter
                    leftPadding: 12
                }

                background: Rectangle {
                    color: "#160025"
                    radius: 8
                    border.color: "#330055"
                    border.width: 1
                }
            }

            // 비밀번호 입력
            TextField {
                id: passwordField
                Layout.fillWidth: true
                height: 44
                placeholderText: "비밀번호"
                echoMode: TextInput.Password
                color: "#ffffff"
                font.pixelSize: 13

                background: Rectangle {
                    color: "#160025"
                    radius: 8
                    border.color: passwordField.activeFocus ? "#9933ff" : "#330055"
                    border.width: 1

                    Behavior on border.color {
                        ColorAnimation { duration: 200 }
                    }
                }

                leftPadding: 12

                Keys.onReturnPressed: loginButton.clicked()
            }

            // 로그인 버튼
            Button {
                id: loginButton
                Layout.fillWidth: true
                height: 44
                text: "로그인"

                contentItem: Text {
                    text: loginButton.text
                    color: "#ffffff"
                    font.pixelSize: 14
                    font.letterSpacing: 2
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }

                background: Rectangle {
                    color: loginButton.pressed ? "#7700cc" :
                           loginButton.hovered ? "#5500aa" : "#4400aa"
                    radius: 8

                    Behavior on color {
                        ColorAnimation { duration: 150 }
                    }
                }

                onClicked: {
                    sddm.login(userCombo.currentText, passwordField.text, sessionCombo.currentIndex)
                }
            }

            // 세션 선택
            ComboBox {
                id: sessionCombo
                Layout.fillWidth: true
                model: sessionModel
                currentIndex: sessionModel.lastIndex
                height: 36

                contentItem: Text {
                    text: sessionCombo.displayText
                    color: "#666666"
                    font.pixelSize: 11
                    verticalAlignment: Text.AlignVCenter
                    leftPadding: 12
                }

                background: Rectangle {
                    color: "transparent"
                    radius: 8
                    border.color: "#1a0030"
                    border.width: 1
                }
            }
        }
    }

    // 하단 시스템 버튼
    Row {
        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottomMargin: 30
        spacing: 20

        Button {
            text: "재시작"
            width: 80; height: 32
            contentItem: Text {
                text: parent.text
                color: "#555555"
                font.pixelSize: 11
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
            background: Rectangle {
                color: parent.hovered ? "#1a0028" : "transparent"
                radius: 6
                border.color: "#220033"
                border.width: 1
            }
            onClicked: sddm.reboot()
        }

        Button {
            text: "종료"
            width: 80; height: 32
            contentItem: Text {
                text: parent.text
                color: "#555555"
                font.pixelSize: 11
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
            background: Rectangle {
                color: parent.hovered ? "#1a0028" : "transparent"
                radius: 6
                border.color: "#220033"
                border.width: 1
            }
            onClicked: sddm.powerOff()
        }
    }

    // 시계
    Text {
        anchors.top: parent.top
        anchors.right: parent.right
        anchors.margins: 30
        text: Qt.formatDateTime(new Date(), "hh:mm")
        color: "#330055"
        font.pixelSize: 14

        Timer {
            interval: 1000
            running: true
            repeat: true
            onTriggered: parent.text = Qt.formatDateTime(new Date(), "hh:mm")
        }
    }

    // 오류 메시지
    Connections {
        target: sddm
        function onLoginFailed() {
            passwordField.clear()
            passwordField.placeholderText = "비밀번호가 틀렸습니다"
        }
    }
}

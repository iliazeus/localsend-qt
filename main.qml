import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQ
// import QtQuick.Controls
import org.kde.plasma.components
import QtQuick.Window

import lol.iliazeus.localsend as LS

QQ.ApplicationWindow {
    LS.Peer {
        id: lsPeer
    }

    title: "localsend-qt: " + lsPeer.info.alias
    visible: true

    ColumnLayout {
        anchors.fill: parent

        Label {
            text: lsPeer.info.alias
            font.pixelSize: 24
            Layout.alignment: Qt.AlignHCenter
        }

        Label {
            text: "Peers:"
        }

        Frame {
            Layout.fillWidth: true
            Layout.fillHeight: true

            // title: "Peers"

            ListView {
                anchors.fill: parent

                currentIndex: -1

                model: lsPeer.remotePeers
                delegate: ItemDelegate {
                    required property int index
                    required property LS.PeerInfo info
                    required property url url

                    width: parent.width
                    text: info.alias + " (" + url + ")"

                    highlighted: ListView.isCurrentItem
                    // onClicked: parent.currentIndex = index
                }
            }
        }
    }
}

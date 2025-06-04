import sys
import cv2
import numpy as np
import time
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QApplication, QLabel, QWidget, QVBoxLayout, QHBoxLayout
)

from logic.detection import detect_dimensions
from sensor.height_sensor import start_sensor_thread
from logic import camera_module

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AVØA Rotation Table Dashboard")
        self.setGeometry(50, 50, 1920, 1080)
        self.setStyleSheet("background-color: #2f2f2f; color: white; font-family: Arial; font-size: 18px;")
        self.running = True
        self.last_detected_time = 0

        # Labels
        self.image_label = QLabel()
        self.image_label.setFixedSize(960, 720)
        self.image_label.setStyleSheet("border: 2px solid #555; background-color: black;")

        self.lbh_label = QLabel("L × B × H: - × - × - mm")
        self.match_label = QLabel("Match: -")
        self.debug_label = QLabel("Debug: systeem start...")
        self.time_label = QLabel("Laatste detectie: -")

        for lbl in [self.lbh_label, self.match_label, self.debug_label, self.time_label]:
            lbl.setMinimumHeight(40)
            lbl.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            lbl.setStyleSheet("padding: 10px; background-color: #444; color: white;")

        # Layouts
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.lbh_label)
        left_layout.addWidget(self.match_label)
        left_layout.addWidget(self.debug_label)
        left_layout.addWidget(self.time_label)
        left_layout.addStretch()

        cam_box = QVBoxLayout()
        cam_box.addWidget(QLabel("<b>LIVE CAM FEED</b>"))
        cam_box.addWidget(self.image_label)
        cam_box.addStretch()

        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout, 3)
        main_layout.addLayout(cam_box, 5)

        self.setLayout(main_layout)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            print("⛔ ESC gedrukt — applicatie sluiten")
            self.running = False
            QApplication.quit()

    def update_frame(self, frame):
        length, width, height, matched_id, match_ok, log, frame_with_overlay = detect_dimensions(frame)

        # tijd bijhouden
        if matched_id:
            self.last_detected_time = time.time()
        since = time.time() - self.last_detected_time
        sinds_str = f"{since:.1f}s geleden" if self.last_detected_time > 0 else "-"

        # beeld verwerken
        img_rgb = cv2.cvtColor(frame_with_overlay, cv2.COLOR_BGR2RGB)
        h, w, ch = img_rgb.shape
        bytes_per_line = ch * w
        qt_image = QImage(img_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image).scaled(
            self.image_label.width(), self.image_label.height(), Qt.KeepAspectRatio
        )
        self.image_label.setPixmap(pixmap)

        # labels bijwerken
        self.lbh_label.setText(f"L × B × H: {length:.1f} × {width:.1f} × {height:.1f} mm")
        self.lbh_label.setStyleSheet("padding: 10px; background-color: #339933;" if match_ok else "padding: 10px; background-color: #cc3333;")

        if matched_id:
            self.match_label.setText(f"Match: {matched_id}")
            self.match_label.setStyleSheet("padding: 10px; background-color: #339933;")
        else:
            self.match_label.setText("Match: geen")
            self.match_label.setStyleSheet("padding: 10px; background-color: #cc3333;")

        self.debug_label.setText(f"Debug: {log}")
        self.time_label.setText(f"Laatst gemeten: {sinds_str}")

def main():
    app = QApplication(sys.argv)
    dashboard = Dashboard()
    start_sensor_thread()

    def frame_callback(img):
        if dashboard.running:
            dashboard.update_frame(img)
        return img

    QTimer.singleShot(100, lambda: camera_module.start_stream(callback=frame_callback, is_running=lambda: dashboard.running))
    dashboard.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

import sys
import threading
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

from dashboard import Dashboard
from logic import camera_module
from sensor.height_sensor import start_sensor_thread

def main():
    app = QApplication(sys.argv)
    dashboard = Dashboard()
    start_sensor_thread()

    def frame_callback(frame):
        if dashboard.running:
            dashboard.update_frame(frame)
        return frame

    # Start stream in aparte thread om UI niet te blokkeren
    threading.Thread(
        target=lambda: camera_module.start_stream(
            callback=frame_callback,
            is_running=lambda: dashboard.running
        ),
        daemon=True
    ).start()

    dashboard.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

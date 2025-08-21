
import os
import tempfile
import subprocess
import cv2

class ProcShell:
    def __init__(self):
        self.base_tmp = os.path.join(tempfile.gettempdir(), "proc_shell")
        os.makedirs(self.base_tmp, exist_ok=True)

    def run_command(self, cmd):
        pid_tmp = os.path.join(self.base_tmp, str(os.getpid()))
        os.makedirs(pid_tmp, exist_ok=True)
        env = os.environ.copy()
        env["TMPDIR"] = pid_tmp
        try:
            result = subprocess.run(cmd, shell=True, env=env, capture_output=True, text=True)
        finally:
            # Clean up temp folder after command
            for f in os.listdir(pid_tmp):
                os.remove(os.path.join(pid_tmp, f))
            os.rmdir(pid_tmp)
        return result.stdout, result.stderr

    def stream_webcam(self, device=0):
        cap = cv2.VideoCapture(device)
        if not cap.isOpened():
            raise RuntimeError("Cannot open webcam")
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            cv2.imshow('Webcam', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()

import sounddevice as sd
import numpy as np
import threading
import logging
import queue
import json
import os
from vosk import Model, KaldiRecognizer
from djitellopy import Tello
from dotenv import load_dotenv
import time
import keyboard  # pip install keyboard
import cv2
from gesture_utils import detect_gesture

class RobartistController:
    def __init__(self, model_path):
        self.samplerate = 16000
        self.channels = 1
        self.device_id = 0
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, self.samplerate)
        self.audio_queue = queue.Queue()
        self.drone = Tello()
        self.connected = False
        logging.basicConfig(level=logging.INFO, filename='robartist.log', format='%(asctime)s - %(levelname)s - %(message)s')
        self.kill = False

    def connect_drone(self, address):
        try:
            self.drone.connect(address)
            self.connected = True
            logging.info("Connected to Tello drone.")
        except Exception as e:
            logging.error(f"Failed to connect to Tello drone: {e}")
            raise

    def _set_tello(self):
        try:
            self.drone.connect()
            battery_level = self.drone.get_battery()
            print(f"Tello battery level: {battery_level}%")
            self.connected = True
            self.drone.streamon()
            self.frame_reader = self.drone.get_frame_read()
            time.sleep(2)  # <== Add this to allow stream to initialize
            logging.info("Tello connected and video stream started.")
        except Exception as e:
            logging.error(f"Error in _set_tello: {e}")

    def _set_microphone(self):
        devices = sd.query_devices()
        print("Available microphones:")
        for idx, device in enumerate(devices):
            print(f"ID: {idx}, Name: {device['name']}, Samplerate: {device['default_samplerate']}")
        while True:
            try:
                device_id = int(input("Enter the ID of the microphone to use: "))
                sd.check_input_settings(device=device_id, samplerate=self.samplerate)
                self.device_id = device_id
                break
            except Exception as e:
                print(f"Invalid device ID or unsupported sample rate: {e}")

    def _handle_command(self, command: str):
        command = command.lower().strip()
        logging.info(f"Voice command received: {command}")
        print(f"[Voice Command] {command}")
        try:
            if "take" in command:
                self.drone.takeoff()
                self.drone.hover()
            elif "land" in command:
                self.drone.land()
            elif "forward" in command:
                self.drone.move_forward(30)
            elif "backward" in command:
                self.drone.move_back(30)
            elif "left" in command:
                self.drone.move_left(30)
            elif "right" in command:
                self.drone.move_right(30)
            elif "stop" in command or "hover" in command:
                self.drone.send_rc_control(0, 0, 0, 0)
            elif "picture" in command:
                frame = self.drone.get_frame_read().frame
                import cv2
                cv2.imwrite("customer_photo.jpg", frame)
                print("Picture taken.")
            elif "bazinga" in command:
                self.drone.rotate_counter_clockwise(45)
            elif "banana" in command:
                self.gesture_show_off()
                # self.gesture_test()
            else:
                print(f"Unrecognized command: {command}")
        except Exception as e:
            logging.error(f"Failed to execute command '{command}': {e}")

    def record_and_process(self):
        print("Recording for 5 seconds...")
        audio_data = sd.rec(int(5 * self.samplerate), samplerate=self.samplerate, channels=self.channels, dtype='int16', device=self.device_id)
        sd.wait()

        # Convert numpy array to bytes
        audio_bytes = audio_data.tobytes()

        # Feed to recognizer
        if self.recognizer.AcceptWaveform(audio_bytes):
            result = json.loads(self.recognizer.Result())
            text = result.get("text", "")
            if text:
                self._handle_command(text)
        else:
            partial = json.loads(self.recognizer.PartialResult())
            print(f"Could not recognize: {partial.get('partial', '')}")

    def listen_for_key(self):
        print("Press 'v' to talk...")
        while True:
            if keyboard.read_key() == 'v':
                self.record_and_process()

    def run(self):
        self._set_microphone()
        self._set_tello()
        threading.Thread(target=self.listen_for_key, daemon=True).start()
        try:
            while True:
                time.sleep(1)  # Keep main thread alive
        except KeyboardInterrupt:
            print("Exiting...")
    
    def gesture_test(self):
        for i in range(10):
            print(i)
            time.sleep(1)
    
    def gesture_show_off(self):
        last_gesture = None
        last_command_time = 0
        cooldown = 2  # seconds

        print("Starting gesture control mode. Press 'q' in window or Ctrl+C to exit.")

        while True:
            try:
                frame = self.frame_reader.frame
                if frame is None:
                    print("Warning: Empty frame received.")
                    time.sleep(0.1)
                    continue

                gesture = detect_gesture(frame)
                print("Gesture:", gesture)

                current_time = time.time()
                if gesture == "thumb_up":
                    print("Gesture: thumb_up → Exit gesture mode")
                    break
                if gesture != last_gesture and (current_time - last_command_time > cooldown):
                    if gesture == "open_palm":
                        self.drone.takeoff()
                        print("Gesture: open_palm → Takeoff")
                    elif gesture == "fist":
                        self.drone.move_down(30)
                    elif gesture == "victory":
                        self.drone.rotate_clockwise(45)
                    elif gesture == "index_up":
                        self.drone.move_up(30)

                    last_command_time = current_time
                    last_gesture = gesture

                cv2.putText(frame, f"Gesture: {gesture}", (30, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

                cv2.imshow("Gesture Control", frame)
                key = cv2.waitKey(10) & 0xFF
                if key == ord('q') or key == 27:
                    print("Exiting gesture control.")
                    break

                time.sleep(0.03)

            except KeyboardInterrupt:
                print("Gesture control interrupted by user.")
                break
            except Exception as e:
                print(f"[Gesture Loop Error] {e}")
                logging.error(f"Error inside gesture control loop: {e}")
                time.sleep(0.5)

        self.drone.streamoff()
        cv2.destroyAllWindows()


# Entry point
if __name__ == "__main__":
    load_dotenv()
    vosk_model_path = os.getenv("VOSK_MODEL_PATH", "vosk-model-small-en-us-0.15")
    robartist = RobartistController(vosk_model_path)
    robartist.run()
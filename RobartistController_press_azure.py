import sounddevice as sd
import numpy as np
import threading
import logging
import queue
import os
import time
import keyboard
import cv2
from djitellopy import Tello
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk
from gesture_utils import detect_gesture

class RobartistController:
    def __init__(self, speech_key, service_region):
        self.samplerate = 16000
        self.channels = 1
        self.device_id = 0
        self.speech_key = speech_key
        self.service_region = service_region
        self.audio_queue = queue.Queue()
        self.drone = Tello()
        self.connected = False
        logging.basicConfig(level=logging.INFO, filename='robartist.log',
                            format='%(asctime)s - %(levelname)s - %(message)s')
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
            self.connected = True
            self.drone.streamon()
            self.frame_reader = self.drone.get_frame_read()
            time.sleep(2)
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
            if "hello" in command:
                self.drone.takeoff()
            elif "land" in command:
                self.drone.land()
            elif "forward" in command:
                self.drone.move_forward(30)
                # self.drone.send_rc_control(0, 0, 0, 0)
            elif "backward" in command:
                self.drone.move_back(30)
                # self.drone.send_rc_control(0, 0, 0, 0)
            elif "left" in command:
                self.drone.move_left(30)
                # self.drone.send_rc_control(0, 0, 0, 0)
            elif "right" in command:
                self.drone.move_right(30)
                # self.drone.send_rc_control(0, 0, 0, 0)
            # elif "stop" in command or "hover" in command:
                # self.drone.send_rc_control(0, 0, 0, 0)
            elif "picture" in command:
                frame = self.drone.get_frame_read().frame
                cv2.imwrite("customer_photo.jpg", frame)
                print("Picture taken.")
            elif "bazinga" in command:
                self.drone.rotate_counter_clockwise(45)
            elif "banana" in command:
                self.gesture_show_off()
            else:
                print(f"Unrecognized command: {command}")
        except Exception as e:
            logging.error(f"Failed to execute command '{command}': {e}")

    def record_and_process(self):
        try:
            print("Please speak clearly into the microphone after the beep.")
            time.sleep(0.5)
            print('\a')  # Beep
            audio = sd.rec(int(4 * self.samplerate), samplerate=self.samplerate,
                           channels=self.channels, dtype='int16', device=self.device_id)
            sd.wait()
            print("Recording complete.")

            # Convert to bytes
            audio_bytes = audio.tobytes()

            # Azure Speech recognition setup
            speech_config = speechsdk.SpeechConfig(subscription=self.speech_key, region=self.service_region)
            stream = speechsdk.audio.PushAudioInputStream()
            audio_config = speechsdk.audio.AudioConfig(stream=stream)
            recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

            stream.write(audio_bytes)
            stream.close()

            print("Recognizing...")
            result = recognizer.recognize_once()

            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                print(f"Recognized: {result.text}")
                self._handle_command(result.text)
            elif result.reason == speechsdk.ResultReason.NoMatch:
                print("No speech could be recognized.")
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation = result.cancellation_details
                print(f"Speech recognition canceled: {cancellation.reason}")
                if cancellation.reason == speechsdk.CancellationReason.Error:
                    print(f"Error details: {cancellation.error_details}")
        except Exception as e:
            print(f"[Azure Recognition Error] {e}")
            logging.error(f"Speech recognition failed: {e}")

    def listen_for_key(self):
        print("Press 'v' to talk... Press 'k' to exit program.")
        while True:
            key = keyboard.read_key()
            if key == 'v':
                self.record_and_process()
            elif key == 'k':
                print("Kill signal received. Exiting...")
                os._exit(0)  # Force exit entire program

    def run(self):
        self._set_microphone()
        # self._set_tello()
        threading.Thread(target=self.listen_for_key, daemon=True).start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Exiting...")

    def gesture_test(self):
        for i in range(10):
            print(i)
            time.sleep(1)

    def gesture_show_off(self):
        self.kill = False  # Reset the flag at the start
        last_gesture = None
        last_command_time = 0
        cooldown = 2

        print("Starting gesture control mode. Press 'v' to exit or 'q' in window.")

        while not self.kill:  # <--- Modify here
            try:
                frame = self.frame_reader.frame
                if frame is None:
                    time.sleep(0.1)
                    continue

                gesture = detect_gesture(frame)
                print("Gesture:", gesture)

                current_time = time.time()
                if gesture == "thumb_up":
                    print("Thumb up gesture detected. Exiting gesture mode.")
                    break
                if gesture != last_gesture and (current_time - last_command_time > cooldown):
                    if gesture == "open_palm":
                        self.drone.takeoff()
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
                if cv2.waitKey(10) & 0xFF in [ord('q'), 27]:
                    print("Key 'q' or ESC pressed. Exiting gesture mode.")
                    break

                time.sleep(0.03)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"[Gesture Loop Error] {e}")
                logging.error(f"Error inside gesture control loop: {e}")
                time.sleep(0.5)

        self.drone.streamoff()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    load_dotenv()
    speech_key = os.getenv("AZURE_SPEECH_KEY")
    service_region = os.getenv("AZURE_REGION", "eastus2")
    robartist = RobartistController(speech_key, service_region)
    robartist.run()
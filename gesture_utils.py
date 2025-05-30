# gesture_utils.py
import cv2
import mediapipe as mp
import math
mp_hands = mp.solutions.hands
hands_detector = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

def detect_gesture(frame):
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands_detector.process(image_rgb)

    if results.multi_hand_landmarks:
        hand = results.multi_hand_landmarks[0]
        landmarks = hand.landmark

        # ===== 0. Fist 检测 =====
        def distance(p1, p2):
            return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

        def is_fist(landmarks):
            tip_ids = [4, 8, 12, 16, 20]
            tips = [landmarks[i] for i in tip_ids]
            total_dist = 0
            count = 0
            for i in range(len(tips)):
                for j in range(i+1, len(tips)):
                    total_dist += distance(tips[i], tips[j])
                    count += 1
            avg_dist = total_dist / count
            return avg_dist < 0.2

        if is_fist(landmarks):
            return "fist"

        # ===== Thumb Up 👍 =====
        thumb_tip_y = landmarks[4].y
        thumb_ip_y = landmarks[3].y
        thumb_up = thumb_tip_y < thumb_ip_y

        other_folded = True
        for tip_id, pip_id in zip([8, 12, 16, 20], [6, 10, 14, 18]):
            if landmarks[tip_id].y < landmarks[pip_id].y:
                other_folded = False
                break

        if thumb_up and other_folded:
            return "thumb_up"

        # ===== 1. Index Up ☝️ =====
        index_tip_y = landmarks[8].y
        index_pip_y = landmarks[6].y
        index_straight = index_tip_y < index_pip_y

        other_folded = True
        for tip_id, pip_id in zip([12, 16, 20], [10, 14, 18]):
            if landmarks[tip_id].y < landmarks[pip_id].y:
                other_folded = False
                break

        if index_straight and other_folded:
            return "index_up"

        # ===== 2. Victory ✌️ =====
        fingers = []
        for tip_id, pip_id in zip([8, 12, 16, 20], [6, 10, 14, 18]):
            fingers.append(landmarks[tip_id].y < landmarks[pip_id].y)

        if fingers[0] and fingers[1] and not any(fingers[2:]):
            return "victory"

        # ===== 3. Open Palm 🖐️ =====
        if all(fingers):
            return "open_palm"

        return "unknown"

    return "no_hand"
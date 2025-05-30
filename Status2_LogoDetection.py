import torch
import cv2

class LogoDetector:
    def __init__(self, model_path='best.pt', img_size = 640, device = 'cpu'):
        self.model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path)
        self.model_path = model_path
        self.img_size = img_size
        self.device = device
        self.model.conf = 0.5
        self.model.iou = 0.45
        self.img_size = img_size
        self.frame = None
        self.pred = None

    def get_frame(self, frame):
        self.frame = frame
        results = self.model(frame)
        self.pred = results.xyxy[0]
    
    def detect(self,frame):
        self.frame = frame
        results = self.model(frame)
        self.pred = results.xyxy[0]

    def is_target_found(self):
        has_text = False
        has_icon = False
        if self.pred is None:
            return False
        for *xyxy, conf, cls in self.pred:
            if int(cls) == 0:
                has_text = True
            elif int(cls) == 1:
                has_icon = True
        return has_text and has_icon

    def get_offset(self, frame_shape):
        width = frame_shape[1]
        for *xyxy, conf, cls in self.pred:
            if int(cls) == 1:  # 找 icon 类
                x1, _, x2, _ = xyxy
                center_x = (x1 + x2) / 2
                return (center_x - width / 2) / (width / 2)
        return None

    def is_centered(self, frame_shape, threshold=0.3):
        offset = self.get_offset(frame_shape)
        if offset is None:
            return False
        offset = float(offset.item()) if hasattr(offset, 'item') else float(offset)
        return abs(offset) < threshold

    def is_close_enough(self, frame_shape, size_threshold=0.02):
        h, w = frame_shape[:2]
        frame_area = h * w
        for *xyxy, conf, cls in self.pred:
            if int(cls) == 1:
                # Convert all xyxy to float safely
                x1, y1, x2, y2 = [float(x.item()) if hasattr(x, 'item') else float(x) for x in xyxy]
                box_area = (x2 - x1) * (y2 - y1)
                ratio = box_area / frame_area
                print(f"📏 icon area ratio: {ratio:.4f}")
                return ratio > size_threshold
        return False


    def draw_boxes(self, frame):
        if self.pred is None:
            return frame
        for *xyxy, conf, cls in self.pred:
            x1, y1, x2, y2 = map(int, xyxy)
            label = f"{int(cls)} ({conf:.2f})"
            color = (0, 255, 0) if int(cls) == 0 else (255, 0, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        return frame

    def get_detected_classes(self):
        classes = set()
        if self.pred is None:
            return []
        for *_, cls in self.pred:
            classes.add(int(cls))
        return list(classes)
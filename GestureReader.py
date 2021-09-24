import numpy as np
import mediapipe as mp
from model import KeyPointClassifier
import pandas as pd
import cv2 as cv
import copy
from utils import CvFpsCalc
from data_collection import calc_bounding_rect
from data_collection import calc_landmark_list
from data_collection import pre_process_landmark
from data_collection import draw_bounding_rect
from data_collection import draw_landmarks
from data_collection import draw_info_text
from data_collection import draw_info
from collections import deque
from scipy import stats

class GestureReader():

    def __init__(self, use_static_image_mode = False, 
                 min_detection_confidence = 0.7,
                 min_tracking_confidence = 0.5) -> None:
        mp_hands = mp.solutions.hands
        self.hands = mp_hands.Hands(
            static_image_mode=use_static_image_mode,
            max_num_hands=1,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        self.kp_classifier = KeyPointClassifier( model_path = ('./model/keypoin'
            't_classifier/keypoint_classifier.tflite'))

        gesture_labels = pd.read_csv( ('./model/keypoint_classifier/keypoint_cl'
            'assifier_label.csv'), header=None)
        gesture_labels = gesture_labels.values.tolist()
        self.labels = [label[0] for label in gesture_labels]
        self.identified_ids = deque(maxlen=10)
        self.cvFpsCalc = CvFpsCalc(buffer_len=10)

    def detect_gesture(self, image, draw_debug_info=True):
        image = cv.flip(image, 1)  # Mirror display
        debug_image = copy.deepcopy(image)
        image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = self.hands.process(image)
        image.flags.writeable = True
        mode = 0    
        use_brect = True
        fps = self.cvFpsCalc.get()
        if results.multi_hand_landmarks is not None:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks,
                                                  results.multi_handedness):
                # Bounding box calculation
                brect = calc_bounding_rect(debug_image, hand_landmarks)
                # Landmark calculation
                landmark_list = calc_landmark_list(debug_image, hand_landmarks)

                # Conversion to relative coordinates / normalized coordinates
                pre_processed_landmark_list = pre_process_landmark(
                    landmark_list)                

                # Hand sign classification
                hand_sign_id = self.kp_classifier(pre_processed_landmark_list)
                self.identified_ids.append(hand_sign_id)
                # Drawing part
                debug_image = draw_bounding_rect(use_brect, debug_image, brect)
                debug_image = draw_landmarks(debug_image, landmark_list)
                if len(self.identified_ids) == self.identified_ids.maxlen:
                    predicted_id = stats.mode(self.identified_ids)[0][0]                    
                    # print(f"Action: {action}")
                    debug_image = draw_info_text(
                        debug_image,
                        brect,
                        handedness,
                        self.labels[predicted_id],
                        "",
                    )
                    detected_gesture = self.labels[predicted_id]
                else:
                    detected_gesture = None
        else:
            self.identified_ids.clear()
            detected_gesture = None
        debug_image = draw_info(debug_image, fps, mode, 0)
        return detected_gesture, debug_image
from GestureReader import GestureReader
from SimpleStateMachine import SimpleStateMachine
import cv2 as cv

def main():
    sm = SimpleStateMachine()
    gr = GestureReader()

    # Opencv configs:
    cap_device = 0
    cap_width = 960
    cap_height = 540
    cap = cv.VideoCapture(cap_device)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, cap_width)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, cap_height)

    sm.start()
    while True:
        key = cv.waitKey(10)
        if key == 27:  # ESC
            break

        # Camera capture
        ret, image = cap.read()
        if not ret:
            break

        detected_gesture, debug_image = gr.detect_gesture(image)
        if(detected_gesture != None):
            if detected_gesture == "One":
                sm.perform_action("perform action 1")
            elif detected_gesture == "Two":
                sm.perform_action("perform action 2")
            elif detected_gesture == "Open":
                sm.perform_action("stop")

        cv.imshow('Hand Gesture Recognition', debug_image)
    sm.stop()
    cap.release()
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()
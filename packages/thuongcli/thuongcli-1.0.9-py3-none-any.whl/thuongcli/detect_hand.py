import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,       # False để xử lý video/live-stream
    max_num_hands=2,               # Số tay tối đa phát hiện
    min_detection_confidence=0.5,  # Ngưỡng tin cậy khi phát hiện
    min_tracking_confidence=0.5    # Ngưỡng tin cậy khi theo dõi
)

cap = cv2.VideoCapture(0)  # 0 là camera mặc định
while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Không thể đọc video")
        break
    # Đảo ngược hình ảnh theo chiều ngang để hiển thị đúng hướng
    image = cv2.flip(image, 1)

    # Chuyển đổi màu sắc từ BGR sang RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)

    # Vẽ các landmark của tay nếu có
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                image,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0,255,0), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(0,0,255), thickness=2)
            )

            # Lấy tọa độ các landmark
            h, w, _ = image.shape
            for id, lm in enumerate(hand_landmarks.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.putText(image, str(id), (cx+10, cy+10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255), 1)

    # Hiển thị kết quả
    cv2.imshow('Hand Tracking', image)

    if cv2.waitKey(5) & 0xFF == 27:  # Nhấn 'Esc' để thoát
        break

# Giải phóng tài nguyên
cap.release()
cv2.destroyAllWindows()
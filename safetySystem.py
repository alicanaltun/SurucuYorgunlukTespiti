import cv2
import mediapipe as mp
import math
import numpy as np
import time
from collections import deque
import pygame

# Pygame ses sistemi başlatma
pygame.mixer.init()
# Uyarı sesini yükle
warning_sound = pygame.mixer.Sound("warning.wav")  # Uyarı ses dosyasının yolu

# EAR hesaplamak için fonksiyon
def calculate_EAR(eye_landmarks, landmarks):
    p2_p6 = math.dist(
        (landmarks[eye_landmarks[1]].x, landmarks[eye_landmarks[1]].y),
        (landmarks[eye_landmarks[5]].x, landmarks[eye_landmarks[5]].y)
    )
    p3_p5 = math.dist(
        (landmarks[eye_landmarks[2]].x, landmarks[eye_landmarks[2]].y),
        (landmarks[eye_landmarks[4]].x, landmarks[eye_landmarks[4]].y)
    )
    p1_p4 = math.dist(
        (landmarks[eye_landmarks[0]].x, landmarks[eye_landmarks[0]].y),
        (landmarks[eye_landmarks[3]].x, landmarks[eye_landmarks[3]].y)
    )
    
    EAR = (p2_p6 + p3_p5) / (2.0 * p1_p4)
    return EAR

# 3D kafa pozisyonu hesaplamak için fonksiyon
def calculate_head_pose_3d(landmarks):
    # Referans noktaları
    nose_tip = landmarks[1]      # Burun ucu
    left_eye = landmarks[33]     # Sol göz
    right_eye = landmarks[263]   # Sağ göz
    chin = landmarks[152]        # Çene
    
    # Yatay açı (sağa-sola)
    dx = right_eye.x - left_eye.x
    dy = right_eye.y - left_eye.y
    horizontal_angle = math.degrees(math.atan2(dy, dx))
    
    # Dikey açı (öne-arkaya)
    # Burun ucu ile çene arasındaki z farkını kullan
    dz = nose_tip.z - chin.z
    vertical_angle = math.degrees(math.atan2(dz, 1))  # 1 birim referans mesafe
    
    # Açıları normalize et
    if horizontal_angle > 90:
        horizontal_angle = horizontal_angle - 180
    elif horizontal_angle < -90:
        horizontal_angle = horizontal_angle + 180
        
    return horizontal_angle, vertical_angle

# Esneme tespiti için fonksiyon
def calculate_yawn(landmarks):
    # Ağız köşeleri ve üst/alt dudak noktaları
    upper_lip = landmarks[13]  # Üst dudak
    lower_lip = landmarks[14]  # Alt dudak
    left_mouth = landmarks[61]  # Sol ağız köşesi
    right_mouth = landmarks[291]  # Sağ ağız köşesi
    
    # Ağız açıklığını hesapla
    mouth_height = math.dist(
        (upper_lip.x, upper_lip.y),
        (lower_lip.x, lower_lip.y)
    )
    mouth_width = math.dist(
        (left_mouth.x, left_mouth.y),
        (right_mouth.x, right_mouth.y)
    )
    
    # Ağız açıklık oranı
    yawn_ratio = mouth_height / mouth_width
    return yawn_ratio

# Font ayarları
FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 1
FONT_THICKNESS = 3
FONT_COLOR = (0, 0, 255)  # Kırmızı
NORMAL_COLOR = (0, 255, 0)  # Yeşil
INFO_COLOR = (255, 255, 255)  # Beyaz

# MediaPipe FaceMesh başlat
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)


# Kamera başlat
cap = cv2.VideoCapture(0)  # Video dosyasını aç

# Sol ve sağ göz için landmark indeksleri
LEFT_EYE = [33, 159, 158, 133, 153, 145]
RIGHT_EYE = [362, 385, 386, 263, 373, 380]

# Eşik değerler
EAR_THRESHOLD = 0.28  # Göz kapalı eşiği
HEAD_HORIZONTAL_THRESHOLD = 40  # Yatay kafa eğikliği eşiği (derece)
HEAD_VERTICAL_THRESHOLD = 10    # Dikey kafa eğikliği eşiği (derece)
YAWN_THRESHOLD = 0.30  # Esneme eşiği
CLOSED_FRAMES = 0
HEAD_TILT_FRAMES = 0  # Kafa eğikliği için frame sayacı
BASE_FRAME_LIMIT = 48  # Temel frame limiti
MIN_FRAME_LIMIT = 30    # Minimum frame limiti
HEAD_TILT_FRAME_LIMIT = 60  # Kafa eğikliği için frame limiti

# Esneme takibi için değişkenler
yawn_times = deque(maxlen=30)  # Son 5 dakika için esneme zamanlarını tut (30 FPS varsayımıyla)
current_frame_limit = BASE_FRAME_LIMIT
is_yaawning = False  # Esneme durumunu takip etmek için
last_yawn_time = 0   # Son esneme zamanı
YAWN_COOLDOWN = 2.0  # İki esneme arası minimum süre (saniye)

# Ses uyarısı için değişkenler
last_warning_time = 0
WARNING_COOLDOWN = 1.0  # İki uyarı arası minimum süre (saniye)
is_warning_active = False  # Uyarının aktif olup olmadığını takip etmek için
previous_warning_state = False  # Önceki uyarı durumunu takip etmek için
warning_sound_length = 2.0  # Ses dosyasının süresi (saniye)
is_sound_playing = False  # Sesin çalıp çalmadığını takip etmek için

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # BGR -> RGB çevir
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    rgb_frame.flags.writeable = False
    results = face_mesh.process(rgb_frame)
    rgb_frame.flags.writeable = True

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            landmarks = face_landmarks.landmark
            
            # Sol ve sağ göz için EAR hesapla
            left_ear = calculate_EAR(LEFT_EYE, landmarks)
            right_ear = calculate_EAR(RIGHT_EYE, landmarks)
            
            # Esneme kontrolü
            yawn_ratio = calculate_yawn(landmarks)
            current_time = time.time()
            
            # Esneme durumunu kontrol et
            if yawn_ratio > YAWN_THRESHOLD and not is_yaawning and (current_time - last_yawn_time) > YAWN_COOLDOWN:
                is_yaawning = True
                last_yawn_time = current_time
                yawn_times.append(current_time)
            elif yawn_ratio <= YAWN_THRESHOLD:
                is_yaawning = False
            
            # Son 5 dakikadaki esneme sayısına göre frame limitini ayarla
            recent_yawns = sum(1 for t in yawn_times if current_time - t <= 300)  # 300 saniye = 5 dakika
            
            # Esneme sayısına göre frame limitini ayarla
            if recent_yawns >= 3:  # 5 dakikada 3 veya daha fazla esneme
                current_frame_limit = MIN_FRAME_LIMIT
            else:
                current_frame_limit = BASE_FRAME_LIMIT
            
            # 3D kafa pozisyonunu hesapla
            horizontal_angle, vertical_angle = calculate_head_pose_3d(landmarks)

            # Yüzdeki tüm kontrol noktalarını çiz
            for landmark in landmarks:
                x = int(landmark.x * frame.shape[1])
                y = int(landmark.y * frame.shape[0])
                cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)

            # Göz kapalı mı kontrol et
            if left_ear < EAR_THRESHOLD or right_ear < EAR_THRESHOLD:
                CLOSED_FRAMES += 1
            else:
                CLOSED_FRAMES = 0
                
            # Kafa pozisyonu uyarıları
            if abs(horizontal_angle) > HEAD_HORIZONTAL_THRESHOLD or abs(vertical_angle) > HEAD_VERTICAL_THRESHOLD:
                HEAD_TILT_FRAMES += 1
            else:
                HEAD_TILT_FRAMES = 0

            # Uyarı mesajlarını hazırla
            warning_messages = []
            current_warning_state = False  # Mevcut uyarı durumunu takip et
            
            # Göz kapalılığı uyarısı
            if CLOSED_FRAMES > current_frame_limit:
                warning_messages.append("UYARI: Yorgunluk Algilandi!")
                current_warning_state = True
            
            # Kafa pozisyonu uyarıları
            if HEAD_TILT_FRAMES > HEAD_TILT_FRAME_LIMIT:
                if abs(horizontal_angle) > HEAD_HORIZONTAL_THRESHOLD:
                    direction = "SAGA" if horizontal_angle > 0 else "SOLA"
                    warning_messages.append(f"UYARI: Kafa {direction} Egik ({int(abs(horizontal_angle))} derece)")
                    current_warning_state = True
                
                if abs(vertical_angle) > HEAD_VERTICAL_THRESHOLD:
                    direction = "ARKAYA" if vertical_angle > 0 else "ONE"
                    warning_messages.append(f"UYARI: Kafa {direction} Egik ({int(abs(vertical_angle))} derece)")
                    current_warning_state = True
            
            # Uyarı durumu değiştiğinde veya belirli bir süre geçtiğinde ses çal
            if current_warning_state:
                # Eğer ses çalmıyorsa veya ses dosyasının süresi dolmuşsa, yeniden başlat
                if not pygame.mixer.get_busy():  # Ses çalmıyorsa kontrol et
                    warning_sound.play()  # Ses dosyasını çal
                    last_warning_time = current_time  # Zaman damgasını güncelle
                    is_sound_playing = True  # Sesin oynadığını işaretle
            else:
                # Eğer uyarılar tamamen sona erdiyse, sesi durdur
                if pygame.mixer.get_busy():  # Ses çalıyorsa durdur
                    warning_sound.stop()
                    is_sound_playing = False  # Ses oynatma durumunu sıfırla            
            
            # Önceki uyarı durumunu güncelle
            previous_warning_state = current_warning_state
            
            # Uyarı mesajlarını ekrana yazdır
            if warning_messages:
                for i, message in enumerate(warning_messages):
                    cv2.putText(frame, message, (50, 100 + i*40), FONT, FONT_SCALE, FONT_COLOR, FONT_THICKNESS)
            else:
                cv2.putText(frame, "Durum: Normal", (50, 100), FONT, FONT_SCALE, NORMAL_COLOR, FONT_THICKNESS)
            
            # Bilgi mesajlarını ekrana yazdır
            cv2.putText(frame, f"Yatay Aci: {int(horizontal_angle)} derece", (50, 200), FONT, FONT_SCALE, INFO_COLOR, 2)
            cv2.putText(frame, f"Dikey Aci: {int(vertical_angle)} derece", (50, 250), FONT, FONT_SCALE, INFO_COLOR, 2)
            cv2.putText(frame, f"Son 5 dk esneme: {recent_yawns}", (50, 300), FONT, FONT_SCALE, INFO_COLOR, 2)
            cv2.putText(frame, f"Frame limit: {current_frame_limit}", (50, 350), FONT, FONT_SCALE, INFO_COLOR, 2)
            cv2.putText(frame, f"Esneme orani: {yawn_ratio:.2f}", (50, 400), FONT, FONT_SCALE, INFO_COLOR, 2)

    # Ekranda göster
    cv2.imshow("Yorgunluk Tespiti", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# Program sonunda pygame'i kapat
pygame.mixer.quit()


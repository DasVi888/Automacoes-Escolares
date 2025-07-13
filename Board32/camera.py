# camera.py - Versão Adaptativa para Luzes Fracas e Fortes

import cv2
import numpy as np
from PySide6.QtGui import QGuiApplication
from collections import deque
import math


class AdaptiveStableTracker:
    def __init__(self):
        # Histórico de posições para análise de movimento
        self.position_history = deque(maxlen=25)
        self.velocity_history = deque(maxlen=10)
        self.brightness_history = deque(maxlen=10)
        
        # Estado atual do rastreamento
        self.current_position = None
        self.predicted_position = None
        self.is_moving = False
        self.movement_confidence = 0.0
        self.light_intensity = 0.0
        
        # Filtros adaptativos
        self.kalman_filter = self._init_kalman_filter()
        
        # Parâmetros adaptativos baseados na intensidade da luz
        self.adaptive_params = {
            'weak_light': {
                'movement_threshold': 2.0,
                'noise_threshold': 2.0,  
                'confidence_decay': 0.90,
                'min_confidence': 0.3,  
                'stable_frames_threshold': 5,
                'proximity_tolerance': 25.0,
                'blend_factor': 0.15
            },
            'strong_light': {
                'movement_threshold': 20.0,
                'noise_threshold': 8.0,
                'confidence_decay': 0.75,
                'min_confidence': 0.5,
                'stable_frames_threshold': 12,
                'proximity_tolerance': 15.0,
                'blend_factor': 0.05
            }
        }
        
        # Parâmetros atuais (serão ajustados dinamicamente)
        self.current_params = self.adaptive_params['weak_light'].copy()
        
        # Contador de frames estáveis
        self.stable_frames = 0
        
        # Variáveis do IR.py integradas
        self.prevX = 0
        self.prevY = 0
        self.movement_locked = False
        self.lock_counter = 0
        
        # Detecção de saturação e ruído
        self.saturation_detector = SaturationDetector()
        self.noise_filter = NoiseFilter()
        
        # Histórico para validação de movimento real
        self.position_buffer = deque(maxlen=8)
        self.detection_quality_history = deque(maxlen=5)
        
        # Controle de proximidade para luzes fortes
        self.proximity_validator = ProximityValidator()
        
    def _init_kalman_filter(self):
        """Inicializa filtro de Kalman adaptativo"""
        kf = cv2.KalmanFilter(4, 2)
        
        kf.transitionMatrix = np.array([
            [1, 0, 1, 0],
            [0, 1, 0, 1],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)
        
        kf.measurementMatrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0]
        ], dtype=np.float32)
        
        # Ruído adaptativo (será ajustado dinamicamente)
        kf.processNoiseCov = np.eye(4, dtype=np.float32) * 0.01
        kf.measurementNoiseCov = np.eye(2, dtype=np.float32) * 0.1
        kf.errorCovPost = np.eye(4, dtype=np.float32) * 100
        
        return kf
    
    def _classify_light_intensity(self, detected_position, frame_brightness):
        """Classifica a intensidade da luz e ajusta parâmetros"""
        if detected_position is None:
            return 'unknown'
        
        # Adiciona ao histórico
        self.brightness_history.append(frame_brightness)
        
        # Calcula média da intensidade
        avg_brightness = sum(self.brightness_history) / len(self.brightness_history)
        
        # Classifica baseado na intensidade
        if avg_brightness > 180:
            light_type = 'strong_light'
        elif avg_brightness > 100:
            light_type = 'medium_light'
        else:
            light_type = 'weak_light'
        
        # Ajusta parâmetros dinamicamente
        if light_type == 'strong_light':
            self.current_params = self.adaptive_params['strong_light'].copy()
        elif light_type == 'medium_light':
            # Interpolação entre weak e strong
            weak = self.adaptive_params['weak_light']
            strong = self.adaptive_params['strong_light']
            blend = 0.5
            
            self.current_params = {
                key: weak[key] * (1 - blend) + strong[key] * blend
                for key in weak.keys()
            }
        else:
            self.current_params = self.adaptive_params['weak_light'].copy()
        
        return light_type
    
    def _calculate_detection_quality(self, detected_position, contour_data):
        """Calcula qualidade da detecção"""
        if not contour_data:
            return 0.0
        
        # Métricas de qualidade
        area = contour_data.get('area', 0)
        circularity = contour_data.get('circularity', 0)
        brightness = contour_data.get('brightness', 0)
        
        # Score composto
        quality = (area * 0.3 + circularity * 0.4 + brightness * 0.3) / 255.0
        
        self.detection_quality_history.append(quality)
        return quality
    
    def _validate_position_proximity(self, detected_position):
        """Valida se a posição detectada está próxima o suficiente da anterior"""
        if self.current_position is None:
            return True
        
        distance = math.sqrt(
            (detected_position[0] - self.current_position[0])**2 + 
            (detected_position[1] - self.current_position[1])**2
        )
        
        return distance <= self.current_params['proximity_tolerance']
    
    def _apply_adaptive_filtering(self, detected_position, light_type):
        """Aplica filtragem adaptativa baseada no tipo de luz"""
        if detected_position is None:
            return None
        
        # Para luzes fracas: mais permissivo, menos filtragem
        if light_type == 'weak_light':
            return self._filter_weak_light(self.current_position, detected_position)
        
        # Para luzes fortes: mais restritivo, mais filtragem
        elif light_type == 'strong_light':
            return self._filter_strong_light(detected_position)
        
        # Para luzes médias: filtragem balanceada
        else:
            return self._filter_medium_light(detected_position)
    
    def _filter_weak_light(self, prev, new):
        dx = new[0] - prev[0]
        dy = new[1] - prev[1]
        dist = math.hypot(dx, dy)

        # 🔒 Não atualiza se o deslocamento for muito pequeno (ruído)
        if dist < self.current_params['noise_threshold']:
            return None  # sinal de que nada deve ser feito

        # Caso contrário, faz blend suave (mas só se for acima do ruído)
        blend = self.current_params['blend_factor']
        filtered = (
            int(prev[0] * (1 - blend) + new[0] * blend),
            int(prev[1] * (1 - blend) + new[1] * blend)
        )
        return filtered
    
    def _filter_strong_light(self, detected_position):
        """Filtragem especializada para luzes fortes"""
        # Validação de proximidade rigorosa
        if not self._validate_position_proximity(detected_position):
            # Posição muito distante - provavelmente ruído/saturação
            if self.current_position:
                return self.current_position
            return None
        
        # Filtragem anti-jitter para luzes fortes
        if self.current_position:
            distance = math.sqrt(
                (detected_position[0] - self.current_position[0])**2 + 
                (detected_position[1] - self.current_position[1])**2
            )
            
            if distance < self.current_params['noise_threshold']:
                # Zona morta expandida para luzes fortes
                return self.current_position
        
        return detected_position
    
    def _filter_medium_light(self, detected_position):
        """Filtragem balanceada para luzes médias"""
        if self.current_position:
            distance = math.sqrt(
                (detected_position[0] - self.current_position[0])**2 + 
                (detected_position[1] - self.current_position[1])**2
            )
            
            if distance < self.current_params['noise_threshold']:
                # Transição moderada
                blend = 0.15
                return (
                    int(self.current_position[0] * (1 - blend) + detected_position[0] * blend),
                    int(self.current_position[1] * (1 - blend) + detected_position[1] * blend)
                )
        
        return detected_position
    
    def update(self, detected_position, frame_brightness=128, contour_data=None):
        light_type = self._classify_light_intensity(detected_position, frame_brightness)

        if detected_position is None:
            self.prevX = 0
            self.prevY = 0
            self.movement_locked = False
            self.lock_counter = 0

            if self.current_position and self.stable_frames > self.current_params['stable_frames_threshold']:
                return self.current_position
            else:
                self.current_position = None
                return None

        detection_quality = self._calculate_detection_quality(detected_position, contour_data)

        if self.current_position is None or (self.prevX == 0 and self.prevY == 0):
            self.current_position = detected_position
            self.prevX = detected_position[0]
            self.prevY = detected_position[1]
            self.kalman_filter.statePre = np.array([*detected_position, 0, 0], dtype=np.float32)
            self.kalman_filter.statePost = np.array([*detected_position, 0, 0], dtype=np.float32)
            self.position_history.append(detected_position)
            self.position_buffer.append(detected_position)
            self.stable_frames = 0
            return detected_position

        filtered_position = self._apply_adaptive_filtering(detected_position, light_type)
        if filtered_position is None:
            self.stable_frames += 1
            return self.current_position

        distance_from_prev = math.hypot(filtered_position[0] - self.prevX, filtered_position[1] - self.prevY)
        self.position_buffer.append(filtered_position)

        if distance_from_prev < self.current_params['noise_threshold']:
            self.stable_frames += 1
            self.lock_counter += 1

            if self.lock_counter > self.current_params['stable_frames_threshold']:
                self.movement_locked = True

            if self.movement_locked:
                return self.current_position

            # Transição mínima mesmo sem lock (rígida)
            return self.current_position

        self.movement_locked = False
        self.lock_counter = 0
        self.position_history.append(filtered_position)

        velocity = self._calculate_adaptive_velocity()
        self.velocity_history.append(velocity)

        if velocity > self.current_params['movement_threshold'] and detection_quality > 0.3:
            self.movement_confidence = min(1.0, self.movement_confidence + 0.3)
            self.is_moving = True
        else:
            self.movement_confidence *= self.current_params['confidence_decay']
            if self.movement_confidence < self.current_params['min_confidence']:
                self.is_moving = False

        self._adjust_kalman_for_light_type(light_type)

        prediction = self.kalman_filter.predict()
        measurement = np.array(filtered_position, dtype=np.float32)
        corrected = self.kalman_filter.correct(measurement)
        kalman_pos = (int(corrected[0]), int(corrected[1]))

        final_position = self._make_final_decision(filtered_position, kalman_pos, light_type)

        self.prevX = final_position[0]
        self.prevY = final_position[1]
        self.current_position = final_position

        return final_position
    
    def _calculate_adaptive_velocity(self):
        """Calcula velocidade adaptativa baseada no histórico"""
        if len(self.position_history) < 2:
            return 0.0
        
        recent_positions = list(self.position_history)[-5:]
        total_distance = 0.0
        
        for i in range(1, len(recent_positions)):
            dx = recent_positions[i][0] - recent_positions[i-1][0]
            dy = recent_positions[i][1] - recent_positions[i-1][1]
            total_distance += math.sqrt(dx*dx + dy*dy)
        
        return total_distance / len(recent_positions)
    
    def _adjust_kalman_for_light_type(self, light_type):
        """Ajusta parâmetros do Kalman baseado no tipo de luz"""
        if light_type == 'weak_light':
            # Mais permissivo para luzes fracas
            self.kalman_filter.processNoiseCov = np.eye(4, dtype=np.float32) * 0.02
            self.kalman_filter.measurementNoiseCov = np.eye(2, dtype=np.float32) * 0.15
        elif light_type == 'strong_light':
            # Mais restritivo para luzes fortes
            self.kalman_filter.processNoiseCov = np.eye(4, dtype=np.float32) * 0.005
            self.kalman_filter.measurementNoiseCov = np.eye(2, dtype=np.float32) * 0.02
        else:
            # Balanceado para luzes médias
            self.kalman_filter.processNoiseCov = np.eye(4, dtype=np.float32) * 0.01
            self.kalman_filter.measurementNoiseCov = np.eye(2, dtype=np.float32) * 0.08
    
    def _make_final_decision(self, filtered_position, kalman_pos, light_type):
        if self.is_moving and self.movement_confidence > 0.6:
            distance_to_kalman = math.hypot(
                kalman_pos[0] - filtered_position[0],
                kalman_pos[1] - filtered_position[1]
            )
            kalman_threshold = 20 if light_type == 'weak_light' else 10

            if distance_to_kalman < kalman_threshold:
                self.stable_frames = 0
                return kalman_pos
            else:
                blend = 0.3 if light_type == 'weak_light' else 0.15
                final_x = int(self.current_position[0] * (1 - blend) + filtered_position[0] * blend)
                final_y = int(self.current_position[1] * (1 - blend) + filtered_position[1] * blend)
                self.stable_frames = 0
                return (final_x, final_y)
        else:
            # 🔒 Movimento não confiável: mantenha posição atual fixa
            distance_to_current = math.hypot(
                filtered_position[0] - self.current_position[0],
                filtered_position[1] - self.current_position[1]
            )

            if distance_to_current < self.current_params['noise_threshold'] * 2:
                self.stable_frames += 1
                return self.current_position
            else:
                # Mesmo que salte, não mexa se não estiver confiante
                return self.current_position

class SaturationDetector:
    """Detecta saturação na imagem"""
    def __init__(self):
        self.saturation_threshold = 250
    
    def is_saturated(self, roi):
        """Verifica se a região está saturada"""
        if roi is None:
            return False
        
        # Conta pixels saturados
        saturated_pixels = np.sum(roi > self.saturation_threshold)
        total_pixels = roi.shape[0] * roi.shape[1]
        
        return (saturated_pixels / total_pixels) > 0.5

class NoiseFilter:
    """Filtra ruído baseado em padrões"""
    def __init__(self):
        self.noise_patterns = deque(maxlen=10)
    
    def is_noise(self, position, previous_positions):
        """Determina se a posição é ruído"""
        if len(previous_positions) < 3:
            return False
        
        # Análise de padrão de movimento
        distances = []
        for i in range(1, len(previous_positions)):
            dx = previous_positions[i][0] - previous_positions[i-1][0]
            dy = previous_positions[i][1] - previous_positions[i-1][1]
            distances.append(math.sqrt(dx*dx + dy*dy))
        
        # Se movimento é muito irregular, pode ser ruído
        if len(distances) > 2:
            variance = np.var(distances)
            return variance > 100
        
        return False

class ProximityValidator:
    """Valida posições baseada em proximidade"""
    def __init__(self):
        self.max_jump_distance = 50
    
    def validate(self, new_position, reference_position):
        """Valida se posição está próxima o suficiente"""
        if reference_position is None:
            return True
        
        distance = math.sqrt(
            (new_position[0] - reference_position[0])**2 + 
            (new_position[1] - reference_position[1])**2
        )
        
        return distance <= self.max_jump_distance

def start_camera(click_queue, calibration_file='calibration.txt'):
    # Obtem tamanho da tela
    screen_size = QGuiApplication.primaryScreen().size()
    width, height = screen_size.width(), screen_size.height()

    # Lê pontos do arquivo de calibração
    pts = np.loadtxt(calibration_file).reshape(4, 2).astype(np.float32)
    dst = np.array([[0, 0], [width, 0], [width, height], [0, height]], dtype=np.float32)
    M = cv2.getPerspectiveTransform(pts, dst)

    # Inicia captura da câmera
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    # Faixas para luzes fracas (vermelho claro, rosa, magenta)
    weak_light_params = {
        'lower_ir1': np.array([160, 50, 80]),   # vermelho magenta
        'upper_ir1': np.array([179, 255, 255]),
        'lower_ir2': np.array([0, 50, 80]),     # vermelho claro
        'upper_ir2': np.array([10, 255, 255]),
        'min_brightness': 60,                   # exige brilho moderado
        'min_contour_area': 8,
        'min_radius': 2
    }

    # Faixas para luzes fortes (vermelho claro, rosa, magenta)
    strong_light_params = {
        'lower_ir1': np.array([160, 70, 100]),
        'upper_ir1': np.array([179, 255, 255]),
        'lower_ir2': np.array([0, 70, 100]),
        'upper_ir2': np.array([10, 255, 255]),
        'min_brightness': 100,                 # exige brilho mais intenso
            
        'min_radius': 4
    }

    
    # Inicializa o rastreador adaptativo
    tracker = AdaptiveStableTracker()
    
    # Variáveis de controle
    drawing = False
    marker_radius = 15
    
    # Detector de intensidade de luz
    light_intensity_history = deque(maxlen=10)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Aplica transformação de perspectiva
        warped = cv2.warpPerspective(frame, M, (width, height))
        
        # Converte para diferentes espaços de cor
        hsv = cv2.cvtColor(warped, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        
        # Calcula intensidade média da imagem
        avg_intensity = np.mean(gray)
        light_intensity_history.append(avg_intensity)
        
        # Determina se é luz fraca ou forte
        if len(light_intensity_history) >= 3:
            recent_avg = sum(list(light_intensity_history)[-3:]) / 3
            if recent_avg > 120:
                current_params = strong_light_params
                light_type = 'strong'
            else:
                current_params = weak_light_params
                light_type = 'weak'
        else:
            current_params = weak_light_params
            light_type = 'weak'
        
        # Cria máscaras adaptativas
        mask1 = cv2.inRange(hsv, current_params['lower_ir1'], current_params['upper_ir1'])
        mask2 = cv2.inRange(hsv, current_params['lower_ir2'], current_params['upper_ir2'])
        
        # Detecção por brilho adaptativa
        _, bright_mask = cv2.threshold(gray, current_params['min_brightness'], 255, cv2.THRESH_BINARY)
        
        # Combina máscaras
        mask = cv2.bitwise_or(mask1, mask2)
        mask = cv2.bitwise_or(mask, bright_mask)
        
        # Processamento morfológico adaptativo
        if light_type == 'weak':
            # Menos agressivo para luzes fracas
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        else:
            # Mais agressivo para luzes fortes
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4))
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)
        
        mask = cv2.medianBlur(mask, 3)
        
        # Encontra contornos
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Detecta posição adaptativa
        detected_position = None
        contour_data = None
        
        if contours:
            valid_contours = []
            
            for c in contours:
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                area = cv2.contourArea(c)
                
                if radius > current_params['min_radius'] and area > current_params['min_contour_area']:
                    # Calcula métricas de qualidade
                    perimeter = cv2.arcLength(c, True)
                    if perimeter > 0:
                        circularity = 4 * np.pi * area / (perimeter * perimeter)
                        
                        # Calcula brilho médio na região
                        mask_roi = np.zeros(gray.shape, dtype=np.uint8)
                        cv2.fillPoly(mask_roi, [c], 255)
                        mean_brightness = cv2.mean(gray, mask=mask_roi)[0]
                        
                        # Score adaptativo
                        if light_type == 'weak':
                            score = area * 0.4 + circularity * 0.3 + mean_brightness * 0.3
                        else:
                            score = area * 0.3 + circularity * 0.5 + mean_brightness * 0.2
                        
                        valid_contours.append({
                            'score': score,
                            'position': (int(x), int(y)),
                            'area': area,
                            'circularity': circularity,
                            'brightness': mean_brightness
                        })
            
            if valid_contours:
                # Seleciona melhor contorno
                best_contour = max(valid_contours, key=lambda x: x['score'])
                detected_position = best_contour['position']
                contour_data = best_contour
        
        # Atualiza o rastreador adaptativo
        stable_position = tracker.update(detected_position, avg_intensity, contour_data)
        
        # Lógica de eventos de desenho
        if stable_position:
            if not drawing:
                drawing = True
                click_queue.put(('start', stable_position))
            else:
                click_queue.put(('move', stable_position))
            
            # Desenha marcador adaptativo
            marker_color = (0, 255, 0) if light_type == 'weak' else (0, 200, 255)
            cv2.circle(warped, stable_position, marker_radius, marker_color, 2)
            cv2.circle(warped, stable_position, 3, marker_color, -1)
            # Desenha posição detectada original (para debug)
            if detected_position and detected_position != stable_position:
                cv2.circle(warped, detected_position, 3, (0, 0, 255), 1)
                cv2.line(warped, detected_position, stable_position, (255, 0, 0), 1)
            
            # Indicadores de status
            status_color = (0, 255, 255) if tracker.is_moving else (255, 255, 0)
            cv2.putText(warped, f"Conf: {tracker.movement_confidence:.2f}", 
                       (stable_position[0] + 20, stable_position[1] - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, status_color, 1)
            
            cv2.putText(warped, f"Light: {light_type}", 
                       (stable_position[0] + 20, stable_position[1] - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            
            if tracker.movement_locked:
                cv2.putText(warped, "LOCKED", 
                           (stable_position[0] + 20, stable_position[1] + 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
        else:
            if drawing:
                drawing = False
                click_queue.put(('end', None))
        
        # Desenha posição detectada original (para debug)
        if detected_position and detected_position != stable_position:
            cv2.circle(warped, detected_position, 3, (0, 0, 255), 1)
            status_color = (0, 255, 255) if tracker.is_moving else (255, 255, 0)
            cv2.putText(warped, f"Conf: {tracker.movement_confidence:.2f}", 
                    (stable_position[0] + 20, stable_position[1] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, status_color, 1)

            cv2.putText(warped, f"Light: {light_type}", 
                    (stable_position[0] + 20, stable_position[1] - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

            if tracker.movement_locked:
                cv2.putText(warped, "LOCKED", 
                        (stable_position[0] + 20, stable_position[1] + 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
            cv2.line(warped, detected_position, stable_position, (255, 0, 0), 1)
        
        # Informações de debug no canto superior
        debug_info = [
            f"Light Type: {light_type}",
            f"Avg Intensity: {avg_intensity:.1f}",
            f"Tracking Confidence: {tracker.movement_confidence:.2f}",
            f"Stable Frames: {tracker.stable_frames}"
        ]
        
        for i, info in enumerate(debug_info):
            cv2.putText(warped, info, (10, 25 + i * 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        conf_color = int((1 - tracker.movement_confidence) * 255)
        heat_overlay = warped.copy()
        heat_overlay[:] = (0, 0, conf_color)
        warped = cv2.addWeighted(warped, 1.0, heat_overlay, 0.1, 0)
        
        debug_info = [
            f"Light Type: {light_type}",
            f"Avg Intensity: {avg_intensity:.1f}",
            f"Tracking Confidence: {tracker.movement_confidence:.2f}",
            f"Stable Frames: {tracker.stable_frames}"
        ]

        for i, info in enumerate(debug_info):
            cv2.putText(warped, info, (10, 25 + i * 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        
        cv2.imshow('CameraROI', warped)
        
        # Opcional: mostra máscara para debug
        if cv2.waitKey(1) & 0xFF == ord('m'):
            cv2.imshow('Detection Mask', mask)
        
        if cv2.waitKey(1) & 0xFF == 27:  # ESC
            break
    
    

    cap.release()
    cv2.destroyAllWindows()
    click_queue.put(('end_camera', None))
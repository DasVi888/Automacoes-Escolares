import cv2
import numpy as np
import os
import tkinter as tk  # Usado para detectar a resolução da tela

# Detecta resolução da tela usando tkinter
root = tk.Tk()
root.withdraw()  # Oculta a janela
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Usa a resolução detectada
width, height = screen_width, screen_height
calibration_file = 'calibration.txt'

# Função para criar calibração padrão
def default_calibration():
    return np.array([[width//4, height//4],           # Top-left
                     [3*width//4, height//4],          # Top-right
                     [3*width//4, 3*height//4],        # Bottom-right
                     [width//4, 3*height//4]])         # Bottom-left

# Verifica se arquivo existe e tenta carregar
if os.path.exists(calibration_file):
    try:
        pts = np.loadtxt(calibration_file).reshape(4, 2).astype(int)
        print("Calibração carregada do arquivo!")
    except:
        print("Erro ao carregar calibração. Iniciando nova calibração...")
        pts = default_calibration()
else:
    print("Arquivo de calibração não encontrado. Iniciando nova calibração...")
    pts = default_calibration()

# Variáveis de controle
selected_edge = -1
edge_thickness = 10
dragging = False

def draw_calibration(img):
    for i in range(4):
        cv2.line(img, tuple(pts[i]), tuple(pts[(i+1)%4]), (0, 255, 0), 2)

    colors = [(255, 0, 0), (0, 255, 255), (255, 0, 255), (0, 165, 255)]
    for i in range(4):
        cv2.line(img, tuple(pts[i]), tuple(pts[(i+1)%4]), colors[i], edge_thickness)

    for i, pt in enumerate(pts):
        cv2.circle(img, tuple(pt), 10, (0, 0, 255), -1)
        cv2.putText(img, str(i+1), (pt[0]-10, pt[1]+5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    return img

def is_near_edge(point, edge_idx):
    pt1 = pts[edge_idx]
    pt2 = pts[(edge_idx + 1) % 4]
    line_length = np.linalg.norm(pt2 - pt1)
    if line_length == 0:
        return False
    t = max(0, min(1, np.dot(point - pt1, pt2 - pt1) / (line_length**2)))
    projection = pt1 + t * (pt2 - pt1)
    distance = np.linalg.norm(point - projection)
    return distance < edge_thickness + 5

def mouse_callback(event, x, y, flags, param):
    global pts, selected_edge, dragging
    mouse_pos = np.array([x, y])

    if event == cv2.EVENT_LBUTTONDOWN:
        dragging = True
        for i in range(4):
            if is_near_edge(mouse_pos, i):
                selected_edge = i
                break

    elif event == cv2.EVENT_MOUSEMOVE and dragging and selected_edge != -1:
        pt1_idx = selected_edge
        pt2_idx = (selected_edge + 1) % 4
        vec = pts[pt2_idx] - pts[pt1_idx]

        if abs(vec[0]) > abs(vec[1]):  # Horizontal
            new_y = mouse_pos[1]
            if selected_edge == 0:  # Top
                if new_y < pts[2][1] - 20:
                    pts[pt1_idx][1] = new_y
                    pts[pt2_idx][1] = new_y
            elif selected_edge == 2:  # Bottom
                if new_y > pts[0][1] + 20:
                    pts[pt1_idx][1] = new_y
                    pts[pt2_idx][1] = new_y
        else:  # Vertical
            new_x = mouse_pos[0]
            if selected_edge == 3:  # Left
                if new_x < pts[1][0] - 20:
                    pts[pt1_idx][0] = new_x
                    pts[pt2_idx][0] = new_x
            elif selected_edge == 1:  # Right
                if new_x > pts[0][0] + 20:
                    pts[pt1_idx][0] = new_x
                    pts[pt2_idx][0] = new_x

    elif event == cv2.EVENT_LBUTTONUP:
        dragging = False
        selected_edge = -1

cv2.namedWindow("Calibracao da Camera", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Calibracao da Camera", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
cv2.setMouseCallback("Calibracao da Camera", mouse_callback)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

print("Instrucoes:")
print("- Arraste as BARRAS COLORIDAS para ajustar a area de interesse")
print("- A barra AZUL ajusta o topo")
print("- A barra CIANO ajusta a direita")
print("- A barra MAGENTA ajusta a base")
print("- A barra LARANJA ajusta a esquerda")
print("- Pressione 'C' para confirmar e salvar a calibracao")
print("- Pressione 'R' para resetar")
print("- Pressione ESC para sair")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (width, height))
    display_frame = frame.copy()
    display_frame = draw_calibration(display_frame)

    cv2.imshow("Calibracao da Camera", display_frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('c'):
        np.savetxt(calibration_file, pts, fmt='%d')
        print(f"Calibração salva em {calibration_file}")
        print("Pontos calibrados:")
        print(pts)
        break
    elif key == ord('r'):
        pts = default_calibration()
        print("Calibração resetada!")
    elif key == 27:
        break

cap.release()
cv2.destroyAllWindows()

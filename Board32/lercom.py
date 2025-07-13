import os

LANGUAGE_FILE = "language.txt"
DEFAULT_LANG = "en"

translations = {
    "en": {
        "enter_com": "Enter the COM number (USB port of the PC): ",
        "success": "COM port {port} saved successfully!"
    },
    "pt": {
        "enter_com": "Informe o número da sua COM (porta USB do PC): ",
        "success": "Porta COM {port} salva com sucesso!"
    },
    "es": {
        "enter_com": "Ingrese el número de COM (puerto USB de la PC): ",
        "success": "¡Puerto COM {port} guardado correctamente!"
    }
}

# Carregar idioma salvo
lang = DEFAULT_LANG
if os.path.exists(LANGUAGE_FILE):
    with open(LANGUAGE_FILE, "r", encoding="utf-8") as f:
        lang_candidate = f.read().strip().lower()
        if lang_candidate in translations:
            lang = lang_candidate

t = translations[lang]

# Solicitar COM e salvar
porta = input(t["enter_com"])
door = "COM" + porta

with open("porta_com.txt", "w", encoding="utf-8") as arquivo:
    arquivo.write(door)

print(t["success"].format(port=porta))

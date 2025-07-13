import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import google.generativeai as genai
import logging
import requests
import speech_recognition as sr
import re
import io
import wave
import audioop
from threading import Lock
from time import time, sleep
import sys
import tempfile
import subprocess

# Configuração da API do Gemini - usando variáveis de ambiente
#API_KEY = os.getenv("GEMINI_API_KEY", "")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")
chat = model.start_chat(history=[])

# Credenciais do Twilio - usando variáveis de ambiente
#TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
#TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")

# Controle de taxa: 15 requisições por minuto
lock = Lock()
timestamps = []

def throttle():
    """Garante no máximo 15 requisições em qualquer janela de 60 segundos."""
    with lock:
        agora = time()
        while timestamps and agora - timestamps[0] > 60:
            timestamps.pop(0)
        if len(timestamps) >= 15:
            time_to_wait = 60 - (agora - timestamps[0])
            sleep(time_to_wait)
            agora = time()
            while timestamps and agora - timestamps[0] > 60:
                timestamps.pop(0)
        timestamps.append(agora)

# Mensagens de erro
MENSAGEM_ERRO_TEXTO = (
    "Não entendi sua pergunta, você pode ter se expressado mal ou eu não tenho essas informações "
    "salvas em meu banco de dados. Pode reformular? (Caso não seja um erro, entre em contato com a "
    "SERAC pelo email: serac.mariadagraca@cefet-rj.br)"
)
MENSAGEM_ERRO_AUDIO = "Não entendi seu audio, poderia mandar de novo ou falar via texto?"
MENSAGEM_NAO_CONHECIMENTO = "Não tenho ainda essa informação, favor falar com a SERAC (email: serac.mariadagraca@cefet-rj.br)"
MENSAGEM_ERRO_SISTEMA = "Mil perdões! O sistema enfrentou uma falha. Caso continue, favor falar com a SERAC (email: serac.mariadagraca@cefet-rj.br)"
MENSAGEM_ERRO_TRANSCRICAO = "Mil perdões! O sistema de reconhecimento de audio enfrentou uma falha. Caso continue, favor falar com a SERAC (email: serac.mariadagraca@cefet-rj.br)"


# Banco de dados completo
COLEGIO_INFO = {
    "nome da escola": "CEFET-RJ Uned Maria da Graça",
    "nome": "CEFETBOT",
    "Para qual Feira você foi criado":"Fui criado para disputar na EXPOTEC (Exposição do Ensino Técnico) de 2025.",
    "Quem sou eu": "Eu sou um BOT de atendimento da escola",
    "criadores": (
        "Fui criado pelos alunos Davi Corvello, Pedro Lukas e Pedro Oliveira, alunos do terceiro ano de automação industrial de 2025. "
        "Fui supervisionado pelos professores Leandro Samyn (orientador) e Arcano (coorientador)"
    ),
    "fundacao": "2010",
    "Uso de uniforme/calça jeans": "Obrigatório",
    "Cor do uniforme": "Azul e Branco",
    "tipo": "Pública",
    "estágio": "Obrigatório para obter o diploma",
    "formação": "Apenas se é possível obter o diploma se formando tanto no técnico quanto no ensino médio OBRIGATORIAMENTE EM AMBOS",
    "endereço": "Rua Miguel Ângelo, 96 - Maria da Graça, Rio de Janeiro - RJ, 20785-220",
    "nacionalidade": "Escola Brasileira",
    "email da Seção de Articulação Pedagógica (SERAC)": "serac.mariadagraca@cefet-rj.br",
    "site": "https://www.cefet-rj.br/index.php/campus-maria-da-graca",
    "diretor": "Prof. Saulo",
    "niveis": ["Ensino Médio Técnico", "Ensino Técnico subsequente", "Bacharelado"],
    "horarios": [
        "Majoritariamente Matutinos (com contraturno à tarde): Produção Cultural e Automação Industrial (Ensino Médio Técnico)",
        "Majoritariamente Vespertinos (com contraturno de manhã): Segurança do Trabalho e Manutenção Automotiva (Ensino Médio Técnico)",
        "Noturnos: Bacharelado em Sistemas de Informação e Cursos Técnicos Subsequentes em Segurança do Trabalho e Sistemas de Energias Renováveis"
    ],
    "diferenciais": [
        "Laboratórios equipados de ciências, informática e robótica",
        "Biblioteca",
        "Quadra poliesportiva coberta",
        "Ensino de Línguas",
        "Programa de iniciação científica"
    ],
    "calendario": "Procure a escola para mais informações",
    "valores": "A escola não cobra mensalidade e fornece material didático gratuitamente, uniformes são pagos",
    "atividades_extracurriculares": [
        "Esportes", "Programas de extensão", "Clube de Física",
        "Extensão em música", "Xadrez", "Ensino de Línguas"
    ],
    "infraestrutura": [
        "Laboratórios equipados de ciências, informática e robótica",
        "Biblioteca",
        "Quadra poliesportiva coberta",
        "Ensino de Línguas",
        "Programa de iniciação científica"
    ],
    "Cursos": [
        "Ensino Médio Técnico: Automação Industrial, Manutenção Automotiva, Produção Cultural e Segurança do Trabalho",
        "Cursos Técnicos Subsequentes: Segurança do Trabalho e Sistemas de Energias Renováveis",
        "Bacharelado: Sistemas de Informação"
    ]
}

REGRAS = """
1. Seja DIRETO e OBJETIVO em todas as respostas
2. Responda APENAS o que foi perguntado, não adicione informações extras
3. Use SOMENTE as informações fornecidas acima
4. Se não entender a pergunta ou ela não for sobre a escola, responda EXATAMENTE: "Não entendi sua pergunta, você pode ter se expressado mal ou eu não tenho essas informações salvas em meu banco de dados. Pode reformular? (Caso não seja um erro, entre em contato com a SERAC pelo email: serac.mariadagraca@cefet-rj.br)"
5. Caso a pergunta for sobre algo relacionado à escola mas não souber a resposta, responda EXATAMENTE: "Não tenho ainda essa informação, favor falar com a SERAC (email: serac.mariadagraca@cefet-rj.br)"
6. NUNCA dê respostas incompletas ou vagas
7. Respostas devem caber em mensagens de WhatsApp (máx. 1600 caracteres)
8. Responda sempre em português
9. Jamais inicie com "bom dia" ou similares se o usuário não cumprimentar primeiro
10. Se o usuário cumprimentar, cumprimente da mesma forma e depois pergunte: "Em que posso ajudá-lo?"
11. Mensagens sem sentido (só símbolos, caracteres) devem receber a mensagem de erro
12. NUNCA responda apenas com frases como "mensagem de erro" ou "mensagem de não conhecimento" - sempre use as mensagens completas especificadas
13. Responda o usuário com base no idioma que ele falou contigo, se ele falou em português, responda em português, se foi em inglês, responda em inglês, e por aí vai com todos os idiomas possíveis.
14. Todos os serviços que a escola oferece, traduza-os para cada idioma, exemplo: "Ensino Médio", caso for em inglês, vira - "High School" - e por aí vai. PORÉM, NUNCA TRADUZA O NOME DE INSTITUIÇÕES/LUGARES - MARIA DA GRAÇA CONTINUA SENDO MARIA DA GRAÇA E SERAC E CEFET CONTINUAM IGUAIS.
"""

PROMPT_BASE = f"""
Você é um atendente virtual do {COLEGIO_INFO['nome']}. Responda como um assistente de atendimento.
Siga as instruções abaixo SEMPRE, sem exceção:

INFORMAÇÕES:
{COLEGIO_INFO}

REGRAS:
{REGRAS}

Agora, responda à seguinte pergunta do usuário:
"""

# Funções utilitárias
def mensagem_invalida(texto):
    if not texto or not texto.strip(): return True
    txt = texto.strip()
    if re.fullmatch(r'[^a-zA-ZÀ-ÿ0-9]+', txt): return True
    if len(txt) <= 1 and not re.search(r'[a-zA-ZÀ-ÿ]', txt): return True
    return False

def interpretar_e_responder(pergunta):
    throttle()
    
    # 1. Detecta o idioma (nova funcionalidade)
    idioma = detectar_idioma(pergunta)
    logging.info(f"🌐 Idioma detectado: {idioma}")
    
    # 2. Prepara o prompt com instrução de idioma
    prompt = PROMPT_BASE + f"\n\nIDIOMA DA RESPOSTA: {idioma}\nPERGUNTA: {pergunta}"
    
    try:
        resposta = chat.send_message(prompt)
        texto = resposta.text.strip()
        
        # 3. Mantém as verificações originais de mensagens inadequadas
        if texto.lower() in ["mensagem de erro", "mensagem de não conhecimento"]:
            texto = MENSAGEM_ERRO_TEXTO if "mensagem de erro" in texto.lower() else MENSAGEM_NAO_CONHECIMENTO
        
        # 4. Limita tamanho e faz log (como antes)
        resposta_final = texto[:1597] + "..." if len(texto) > 1600 else texto
        logging.info(f"💬 RESPOSTA ENVIADA: '{resposta_final}'")
        
        return resposta_final
        
    except Exception as e:
        logging.error(f"Erro ao processar resposta do Gemini: {e}")
        logging.info(f"💬 RESPOSTA ENVIADA (ERRO): '{MENSAGEM_ERRO_SISTEMA}'")
        return MENSAGEM_ERRO_SISTEMA
    
    
def convert_ogg_to_wav_ffmpeg(ogg_data):
    """
    Converte dados OGG para WAV usando FFmpeg.
    """
    try:
        # Criar arquivo temporário para entrada
        with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as input_file:
            input_file.write(ogg_data)
            input_path = input_file.name
        
        # Criar arquivo temporário para saída
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as output_file:
            output_path = output_file.name
        
        # Executar FFmpeg
        cmd = [
            'ffmpeg', '-i', input_path, 
            '-acodec', 'pcm_s16le', 
            '-ac', '1', 
            '-ar', '16000', 
            '-y', output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            # Ler arquivo convertido
            with open(output_path, 'rb') as f:
                wav_data = f.read()
            logging.info("Conversão OGG->WAV bem-sucedida com FFmpeg")
            return wav_data
        else:
            logging.error(f"Erro no FFmpeg: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        logging.error("Timeout na conversão FFmpeg")
        return None
    except Exception as e:
        logging.error(f"Erro na conversão FFmpeg: {e}")
        return None
    finally:
        # Limpar arquivos temporários
        try:
            os.unlink(input_path)
            os.unlink(output_path)
        except:
            pass
        
def detectar_idioma(texto):
    """Detecta o idioma do texto usando Gemini"""
    try:
        prompt = f"Identifique o idioma deste texto (responda APENAS com sigla: 'pt', 'en', 'es', 'fr', 'ar', etc.):\n{texto}"
        resposta = model.generate_content(prompt)
        return resposta.text.strip().lower()
    except:
        return "pt"  # padrão: português se falhar

def convert_ogg_to_wav_pure_python(ogg_data):
    """
    Converte dados OGG para WAV usando apenas Python puro.
    """
    try:
        # Tentar detectar se é um arquivo WAV disfarçado
        if ogg_data.startswith(b'RIFF') and b'WAVE' in ogg_data[:20]:
            logging.info("Arquivo já está em formato WAV")
            return ogg_data
        
        # Para arquivos OGG, tentar extrair usando técnicas básicas
        if ogg_data.startswith(b'OggS'):
            logging.info("Detectado arquivo OGG - tentando conversão básica")
            # Implementação muito básica - pode não funcionar com todos os OGG
            return None
        
        logging.warning("Formato de áudio não reconhecido")
        return None
        
    except Exception as e:
        logging.error(f"Erro na conversão básica: {e}")
        return None

def process_audio_with_wave(audio_data):
    """
    Processa áudio usando apenas a biblioteca wave do Python.
    """
    try:
        audio_file = io.BytesIO(audio_data)
        
        with wave.open(audio_file, 'rb') as wav_file:
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            frame_rate = wav_file.getframerate()
            frames = wav_file.readframes(wav_file.getnframes())
            
            logging.info(f"Áudio WAV - Canais: {channels}, Sample Width: {sample_width}, Frame Rate: {frame_rate}")
            
            # Converter para mono se necessário
            if channels == 2:
                frames = audioop.tomono(frames, sample_width, 1, 1)
                channels = 1
            
            # Converter para 16kHz se necessário
            if frame_rate != 16000:
                frames = audioop.ratecv(frames, sample_width, channels, frame_rate, 16000, None)[0]
                frame_rate = 16000
            
            # Criar novo arquivo WAV em memória
            output = io.BytesIO()
            with wave.open(output, 'wb') as out_wav:
                out_wav.setnchannels(channels)
                out_wav.setsampwidth(sample_width)
                out_wav.setframerate(frame_rate)
                out_wav.writeframes(frames)
            
            return output.getvalue()
            
    except wave.Error as e:
        logging.error(f"Erro ao processar WAV: {e}")
        return None
    except Exception as e:
        logging.error(f"Erro inesperado no processamento: {e}")
        return None

def transcrever_audio(media_url):
    """
    Requer binário 'ffmpeg' ou 'ffmpeg.exe' na mesma pasta.
    """
    try:
        logging.info(f"Iniciando transcrição com FFmpeg: {media_url}")

        # Caminho local para ffmpeg
        FFMPEG_EXEC = "ffmpeg.exe" if os.name == "nt" else "./ffmpeg"

        # Baixar o áudio
        response = requests.get(
            media_url,
            headers={'User-Agent': 'Mozilla/5.0'},
            auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
            timeout=30
        )
        response.raise_for_status()

        if not response.content:
            logging.warning("⚠️ Áudio vazio.")
            return None

        # Salvar .ogg temporário
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as ogg_file:
            ogg_file.write(response.content)
            ogg_path = ogg_file.name

        # Criar .wav temporário
        wav_path = ogg_path.replace(".ogg", ".wav")

        # Converter com FFmpeg local
        cmd = [
            FFMPEG_EXEC,
            '-y', '-i', ogg_path,
            '-ar', '16000', '-ac', '1',
            '-acodec', 'pcm_s16le',
            wav_path
        ]
        result = subprocess.run(cmd, capture_output=True)

        if result.returncode != 0:
            logging.error(f"❌ FFmpeg falhou: {result.stderr.decode(errors='ignore')}")
            return None

        # Transcrever com speech_recognition
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = recognizer.record(source)

        for lang in ["pt-BR", "pt-PT", "en-US"]:
            try:
                texto = recognizer.recognize_google(audio_data, language=lang).strip()
                if not texto or mensagem_invalida(texto):
                    logging.warning(f"🟡 Áudio transcrito ({lang}) mas vazio ou inválido: '{texto}'")
                    return "AUDIO_INVÁLIDO"  # código especial
                logging.info(f"✅ Transcrição OK ({lang}): {texto}")
                return texto
            except sr.UnknownValueError:
                logging.warning(f"🤷 Não entendeu em {lang}")
            except sr.RequestError as e:
                logging.error(f"Erro Google STT ({lang}): {e}")


        return "FALHA_TECNICA"

    except Exception as e:
        logging.error(f"💥 Erro na transcrição: {e}")
        return None
    finally:
        try:
            os.unlink(ogg_path)
            os.unlink(wav_path)
        except:
            pass
            

# Inicializa Flask
app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        msg_body = request.values.get("Body", "").strip()
        num_media = int(request.values.get("NumMedia", 0))

        logging.info(f"🔄 Webhook chamado - Body: '{msg_body}', NumMedia: {num_media}")

        if num_media > 0:
            media_url = request.values.get("MediaUrl0")
            content_type = request.values.get("MediaContentType0", "")

            logging.info(f"🎵 Mídia recebida - URL: {media_url}, Tipo: {content_type}")

            if content_type.startswith("audio"):
                transcricao = transcrever_audio(media_url)

                if transcricao == "AUDIO_INVÁLIDO":
                    resposta_final = MENSAGEM_ERRO_AUDIO
                    logging.warning("🟡 Áudio transcrito mas sem conteúdo útil.")
                    logging.info(f"💬 RESPOSTA ENVIADA (AUDIO INVÁLIDO): '{resposta_final}'")

                elif transcricao:
                    resposta_final = interpretar_e_responder(transcricao)
                    logging.info(f"✅ Transcrição bem-sucedida: '{transcricao}'")

                    if resposta_final == MENSAGEM_ERRO_TEXTO:
                        resposta_final = MENSAGEM_ERRO_AUDIO
                        logging.info("💬 RESPOSTA ENVIADA (AUDIO FORA DO ESCOPO): " + resposta_final)

                else:
                    resposta_final = MENSAGEM_ERRO_TRANSCRICAO
                    logging.warning("❌ Falha técnica na transcrição do áudio")
                    logging.info(f"💬 RESPOSTA ENVIADA (FALHA TRANSCRIÇÃO): '{resposta_final}'")

            else:
                resposta_final = "Desculpe, só consigo entender áudios de voz ou mensagens de texto."
                logging.info(f"💬 RESPOSTA ENVIADA (TIPO MÍDIA): '{resposta_final}'")

        elif mensagem_invalida(msg_body):
            resposta_final = MENSAGEM_ERRO_TEXTO
            logging.info("❌ Mensagem de texto inválida")
            logging.info(f"💬 RESPOSTA ENVIADA (TEXTO INVÁLIDO): '{resposta_final}'")

        else:
            resposta_final = interpretar_e_responder(msg_body)
            logging.info(f"📝 Mensagem de texto processada: '{msg_body}'")

        # Enviar resposta pelo WhatsApp e imprimir no terminal
        resp = MessagingResponse()
        resp.message(resposta_final)
        print(f"📤 RESPOSTA AO USUÁRIO: {resposta_final}")
        return str(resp), 200, {'Content-Type': 'text/xml; charset=utf-8'}

    except Exception as e:
        logging.error(f"💥 ERRO CRÍTICO no webhook: {e}")
        resp = MessagingResponse()
        resp.message(MENSAGEM_ERRO_SISTEMA)
        logging.info(f"💬 RESPOSTA ENVIADA (ERRO CRÍTICO): '{MENSAGEM_ERRO_SISTEMA}'")
        return str(resp), 500, {'Content-Type': 'text/xml; charset=utf-8'}


if __name__ == "__main__":
    logging.info("🚀 Bot iniciado!")
    
    app.run(host="0.0.0.0", port=5000, debug=True)
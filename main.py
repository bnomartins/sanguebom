from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
from google import genai

from google.genai import types

import threading
import os

# Configuração da API
# Certifique-se de definir a variável de ambiente 
# com sua chave de API do Google GenAI
# (crie um arquivo chamado .env com uma constante chamada GENAI_API_KEY = "sua_chave_aqui")
GENAI_API_KEY = os.getenv("GENAI_API_KEY")

class ChatGenAI(BoxLayout):
    chat_history = StringProperty("")

    # Configuração da API
    client = genai.Client(api_key=GENAI_API_KEY)

    # Cria um modelo de chat com o modelo Gemini Pro

    chat_config = types.GenerateContentConfig(
        system_instruction="""Você é um assistente que utiliza frases famosas de filmes e desenhos de herois, 
            responda a pergunta do usuário sobre aptidão para doação de sangue e medula óssea e convide-o para clicar em começar ou 
            faça pergunta de sim ou não (uma de cada vez) e avalie inicialmente se a pessoa pode doar sangue e ou médula, 
            se sim, informe o texto 'gerando o certificado' e nas próximas linhas insira um certificado simples de aptidão para salvar vidas e sua estatística de doador (não esqueça de colocar que é necessário a avaliação de um profissional). 
            tudo isso sem usar markdown
            """,
    )
    model = "models/gemini-2.0-flash"

    chat = client.chats.create(model=model, config=chat_config)

    def send_message(self):
        user_input = self.ids.user_input.text.strip()
        if not user_input:
            return

        self.chat_history += f"\nVocê: {user_input}\n"
        self.ids.user_input.text = ""

        threading.Thread(target=self.ask_genai, args=(user_input,), daemon=True).start()

    def ask_genai(self, prompt):
        try:
            
            resposta = self.chat.send_message(prompt)
            reply = resposta.text
            
            # se reply contiver a palavra gerando o certificado, então gerar o pdf
            if "gerando o certificado".upper() in reply.upper():
                self.chat_history += "\nTambém foi gerado um PDF para que você se lembre deste ato de heroísmo....\n"
                # Chama a função de geração de PDF
                threading.Thread(target=self.gerar_pdf, args=(), daemon=True).start()
                self.chat_history += f"\nGemini: {reply}\n"
            else:
                # Caso contrário, apenas exibe a resposta
                self.chat_history += f"\nGemini: {reply}\n"
            
            print(f"Resposta: {reply}")
            
        except Exception as e:
            self.chat_history += f"\n[Erro]: {str(e)}\n"

    def on_action_button(self, action):
        self.chat_history += f"\nVocê: {action}\n"
        self.ask_genai(action)

        # Aqui você pode chamar a função de geração de PDF
    def gerar_pdf(self):

        from fpdf import FPDF

        # # Cria o objeto PDF
        # pdf = FPDF()
        # pdf.add_page()

        # # Define a fonte
        # pdf.set_font("Arial", size=12)

        # # Adiciona um texto
        # pdf.cell(200, 10, txt="Olá, este é um PDF simples gerado com Python!", ln=True, align='C')

        # # Salva o PDF
        # pdf.output("pdf_simples.pdf")
        
        
        
        from fpdf import FPDF

        # Criação do PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Título
        pdf.set_font("Arial", "B", 14)
        pdf.multi_cell(0, 10, "CERTIFICADO DE APTIDÃO INICIAL PARA SALVAR VIDAS", align='C')

        # Título
        pdf.set_font("Arial", "B", 14)
        pdf.multi_cell(0, 10, "(AVALIAÇÃO INICIAL)", align='C')

        pdf.ln(10)  # Espaço vertical

        # Texto inicial
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, "Parabéns! Pelas suas respostas, você tem o perfil inicial para ser um doador de sangue e medula óssea.")

        pdf.ln(5)

        # Estatísticas
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "ESTATÍSTICAS DO DOADOR (INICIAL):", ln=True)

        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, "- Potencial de salvar até 4 vidas com uma doação de sangue.")
        pdf.multi_cell(0, 10, "- Chance de ser a esperança de cura para alguém que precisa de um transplante de medula óssea.")

        pdf.ln(5)

        # Aviso importante
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "IMPORTANTE:", ln=True)

        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, "Este certificado é apenas uma avaliação inicial. É fundamental passar por uma avaliação médica completa para confirmar sua aptidão e garantir a segurança tanto sua quanto do receptor. Procure um hemocentro ou um profissional de saúde para realizar os exames necessários.")

        pdf.ln(5)

        # Frase final
        pdf.set_font("Arial", "I", 12)
        pdf.multi_cell(0, 10, 'Lembre-se, "ninguém pode fazer tudo, mas todos podem fazer alguma coisa."')

        pdf.ln(5)

        # Chamada final reforçada
        pdf.set_font("Arial", "B", 12)
        pdf.multi_cell(0, 10, "Dirija-se ao posto de coleta de sangue mais próximo. Com apenas uma doação, você pode ajudar até 4 pessoas a continuarem vivendo. Faça a diferença hoje mesmo!")

        # Salvar o arquivo
        pdf.output("certificado_aptidao.pdf")

        
        
        
        # gerar_pdf(texto)
        self.chat_history += "\nPDF gerado com sucesso!\n"

class ChatApp(App):
    def build(self):
        return ChatGenAI()

if __name__ == '__main__':
    ChatApp().run()

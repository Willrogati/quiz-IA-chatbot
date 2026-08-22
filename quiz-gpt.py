import os
from http import client
from rich.console import Console
from rich.prompt import Prompt
from google import genai
import json
from google.genai import types
from pydantic import BaseModel
from dotenv import load_dotenv


class Pergunta(BaseModel):
    enunciado: str
    opcoes: list[str]
    certa: str


console = Console()

load_dotenv()

client = genai.Client()


def esperar_enter():
    console.input(
        prompt="\nPressione [bold green]Enter[/bold green] para continuar...",
        password=True
    )


def gerar_pergunta(topico):

    system_instruction = f"""
        Você é um especilista muito experiente com conhecimentos em diferentes assuntos e conceitos e práticos sobre o {topico}.
        Você está trabalhando em um processo de contratação e seu trabalho agora é escrever perguntas para uma entrevista           .
        Cada pergunta deve ter quatro opções de resposta, sendo apenas uma correta. A pergunta deve ser clara e objetiva,   
        e as opções de resposta devem ser plausíveis, mas apenas uma deve ser a correta. A pergunta deve ser escrita em português.
        Escreva essas perguntas em formato JSON, com a seguinte estrutura:
        {{
            "enunciado": "Pergunta", 
            "opcoes": ["Opção 1", "Opção 2", "Opção 3", "Opção 4"], 
            "certa": "Opção Correta"
        }}
        """
    resposta = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=f"Gere uma pergunta sobre o {topico}",
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=Pergunta,
        ),
    )

    return json.loads(resposta.text)


def gerar_quiz():
    pontos = 0
    continuar = ""

    topico = Prompt.ask("Escolha um tópico para o quiz")

    while continuar.lower() != "n":
        with console.status("[bold green]Gerando pergunta...", spinner="dots"):
            pergunta = gerar_pergunta(topico)

        opcoes = pergunta["opcoes"]

        console.clear()
        console.print(f"\n{pergunta['enunciado']}", style="bold yellow")

        for i, opcao in enumerate(opcoes, start=1):
            console.print(f"{i}. {opcao}")

        resposta_indice = int(
            Prompt.ask(
                prompt="Opção",
                choices=[str(i) for i in range(1, len(pergunta["opcoes"]) + 1)]
            )
        ) - 1

        resposta = opcoes[resposta_indice]
        resposta_certa = pergunta["certa"]

        console.clear()

        if resposta == resposta_certa:
            pontos += 1
            console.print(
                f"[green] Você acertou! Agora você tem {pontos} pontos.")
        else:
            console.print(
                f"[red] Você errou! Você continua com {pontos} pontos.")
            console.print(
                f"A resposta certa é: [bold green]{resposta_certa}[/bold green].")
        continuar = Prompt.ask(
            prompt="Deseja continuar?",
            choices=["S", "n"]
        )

    console.print(topico, style="bold blue")


def main():
    console.clear()
    titulo = "[bold purple]Quiz Com IA[bold purple]"
    console.print(f"Bem vindo ao {titulo}", style="bold green")

    gerar_quiz()


main()

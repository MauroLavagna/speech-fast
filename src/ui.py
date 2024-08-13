from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich import box

console = Console()
conversation_history = []

layout = Layout()
layout.split(
    Layout(name="header", size=3),
    Layout(name="main", ratio=1),
    Layout(name="footer", size=3)
)

layout["header"].update(Panel(
    "Asistente de Voz AI",
    border_style="bold magenta",
    box=box.DOUBLE
))

layout["footer"].update(Panel(
    "Presiona 'C' para iniciar/detener la grabación, 'V' para detener la reproducción de audio",
    border_style="bold cyan",
    box=box.DOUBLE
))

conversation_panel = Panel(
    Text("Inicia la conversación...", style="italic"),
    title="Conversación",
    border_style="bold blue",
    box=box.ROUNDED,
    expand=True
)

layout["main"].update(conversation_panel)

def update_conversation(transcription, response):
    global conversation_history
    user_message = Text(f"Mauro: {transcription}\n", style="bold green")
    ai_message = Text(f"AI: {response}\n", style="bold blue")
    conversation_history.append(user_message)
    conversation_history.append(Text("\n"))
    conversation_history.append(ai_message)

    conversation_text = Text()
    for message in conversation_history:
        conversation_text.append(message)

    conversation_panel = Panel(
        conversation_text,
        title="Conversación",
        border_style="cyan",
        box=box.ROUNDED,
        expand=True,
        padding=(1, 1)
    )
    layout["main"].update(conversation_panel)

    console.clear()
    console.print(layout)

def initialize_ui():
    console.clear()
    console.print(layout)
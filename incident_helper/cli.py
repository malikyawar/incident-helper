import typer
from incident_helper.context import IncidentContext
from incident_helper.agents import LLMEngine

app = typer.Typer()
ctx = IncidentContext()
llm = LLMEngine()

@app.command()
def start():
    typer.echo("👋 Hi! Describe your incident.")
    user_input = input("> ")
    ctx.set("alert", user_input)

    while True:
        prompt = f"""
You are an SRE assistant. Based on this context:

Alert: {ctx.get('alert')}
Context: {ctx.data}

Ask a relevant next question to help debug this issue.
Say 'exit' to stop.
"""
        reply = llm.ask(prompt)
        typer.echo(f"🤖 {reply}")
        user_input = input("> ")

        if user_input.lower() in ["exit", "quit"]:
            typer.echo("👋 Ending session.")
            break

        ctx.set(f"step_{len(ctx.data)}", user_input)

if __name__ == "__main__":
    app()

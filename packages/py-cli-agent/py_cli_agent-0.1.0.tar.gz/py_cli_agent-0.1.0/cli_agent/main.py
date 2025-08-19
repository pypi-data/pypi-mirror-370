from dotenv import load_dotenv
import os

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("API key not found. Set GEMINI_API_KEY environment variable.")


from openai import OpenAI
import json
from rich.console import Console
from rich.panel import Panel

from cli_agent.tools import Tools

console = Console()

availableTools = {
    # file operations
    "createFile": Tools.createFile,
    "readFile": Tools.readFile,
    "writeFile": Tools.writeFile,
    "deleteFile": Tools.deleteFile,
    # folder operations
    "createFolder": Tools.createFolder,
    "deleteFolder": Tools.deleteFolder,
    # general utilities
    "executeCommand": Tools.executeCommand,
    "getCurrentDirectory": Tools.getCurrentDirectory,
    "changeDirectory": Tools.changeDirectory,
}

SYSTEM_PROMPT = """
You are a highly skilled web developer specializing in HTML, CSS, and JavaScript. You write clean, modern, and maintainable code. You follow best practices, semantic HTML, responsive design, and modular CSS/JS. You have to to reponse on the bases of user input. You have to provide response in structured JSON.
You response in 4 steps: START (input), THINK, TOOL, OBSERVE and OUTPUT. You are allowed to use tools from availableTools when needed

INSTRUCTIONS:
1. Always respond in a structured format JSON*
4. Use the THINK step to analyze user input, use this step when you need to analyze the user input and plan your response and you can use it N times.
5. Use the TOOL step to call available tools when needed or want to use them.
6. OBSERVE step will be provided to you by the tool execution results.
7. Use the OUTPUT step to provide final responses and before give output check that every thing is correct.

availableTools:
- createFile(filePath: str, content: str): Creates a new file with the specified content.
- readFile(filePath: str): Reads the content of a file.
- writeFile(filePath: str, content: str): Writes content to a file.
- deleteFile(filePath: str): Deletes a file.
- createFolder(folderPath: str): Creates a new folder.
- deleteFolder(folderPath: str): Deletes a folder.
- executeCommand(command: str): Executes a command in the user shell.
- getCurrentDirectory(): Returns the current working directory.
- changeDirectory(directory: str): Changes the current working directory.

The structure you have to reponse is like below:  
{"step": "THINK" | "TOOL" | "OUTPUT", "input": string}

When responding, you will **only provide one step at a time**.  
- Wait for user confirmation to continue to the next step.
- use THINK step when you need to analyze the user input and plan your response.
- wait for OBSERVE step when you use tools from availableTools.

TOOL CALL SYNTAX:
{ "step": "TOOL", "tool": "executeCommand", "input": "echo test.txt" }


Example:  
USER: create a new file called test.txt  

EXAMPLE:
INPUT: {"step": "START", "input": "create a new file called test.txt"}
ASSISTANCE: {"step": "THINK", "input": "I can use tool from available tools to create the file."}
ASSISTANCE: {"step": "TOOL", "tool": "executeCommand", "input": "touch test.txt"}
ASSISTANCE: {"step": "OBSERVE", "input": "tool executed successfully."}
ASSISTANCE: {"step": "OUTPUT", "input": "The file test.txt has been created."}

INPUT: {"step": "START", "input": "Hi there!"}
ASSISTANCE: {"step": "OUTPUT", "input": "Hello! How can I assist you today?"}

INPUT: {"step": "START", "input": "create a new folder called test"}
ASSISTANCE: {"step": "THINK", "input": "I can use tool from available tools to create the folder."}
ASSISTANCE: {"step": "TOOL", "tool": "createFolder", "input": "test"}
ASSISTANCE: {"step": "OBSERVE", "input": "tool executed successfully."}
ASSISTANCE: {"step": "OUTPUT", "input": "The folder test has been created."}

INPUT: {"step": "START", "input": "create a new file called test.txt in the test folder"}
ASSISTANCE: {"step": "THINK", "input": "I can use tool from available tools to create the file."}
ASSISTANCE: {"step": "THINK", "input": "I have to use two tools: createFolder and createFile from availableTools."}
ASSISTANCE: {"step": "TOOL", "tool": "createFolder", "input": "test"}
ASSISTANCE: {"step": "OBSERVE", "input": "tool executed successfully."}
ASSISTANCE: {"step": "TOOL", "tool": "createFile", "input": {"filePath": "test/test.txt", "content": ""}}
ASSISTANCE: {"step": "OBSERVE", "input": "tool executed successfully."}
ASSISTANCE: {"step": "OUTPUT", "input": "The file test.txt has been created in the test folder."}
"""

messages = [{"role": "system", "content": SYSTEM_PROMPT}]


def ask():
    client = OpenAI(
        api_key=gemini_api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )

    while True:
        response = client.chat.completions.create(
            model="gemini-1.5-flash",
            messages=messages,
            response_format={"type": "json_object"},
        )

        reply = response.choices[0].message.content
        parsed_reply = json.loads(reply)
        messages.append({"role": "assistant", "content": reply})

        step = parsed_reply.get("step")
        content = parsed_reply.get("input")

        console.rule(f"[bold magenta]Step: {step}[/bold magenta]")

        if step == "START":
            console.print(Panel("👋 Welcome to the CLI Agent!", style="green"))
            continue

        elif step == "THINK":
            console.print(f"[yellow]🧠 Thinking: {content}[/yellow]")
            continue

        elif step == "TOOL":
            tool_name = parsed_reply.get("tool")
            tool = availableTools.get(tool_name)
            if tool:
                try:
                    # 🔑 Normalize tool call based on content type
                    if isinstance(content, dict):
                        tool(**content)  # spread dict -> kwargs
                    elif isinstance(content, (list, tuple)):
                        tool(*content)  # spread list/tuple -> args
                    else:
                        tool(content)  # single value

                    messages.append(
                        {
                            "role": "assistant",
                            "content": json.dumps(
                                {"step": "OBSERVE", "content": content}
                            ),
                        }
                    )
                    console.print(
                        f"[blue]🔧 Tool used: {tool_name} with input: {content}[/blue]"
                    )
                except Exception as e:
                    console.print(f"[red]⚠️ Error running tool {tool_name}: {e}[/red]")
            else:
                console.print(f"[red]⚠️ Unknown tool: {tool_name}[/red]")
            continue

        elif step == "OUTPUT":
            console.print(Panel(f"✅ Output: {content}", style="bold green"))
            break


def main():
    while True:
        userInput = console.input("[bold yellow]>> [/bold yellow]")
        if userInput == "exit":
            console.print("[bold red]Exiting the CLI Agent...[/bold red]")
            break
        messages.append(
            {
                "role": "user",
                "content": json.dumps({"step": "START", "input": userInput}),
            }
        )

        ask()


if __name__ == "__main__":
    main()

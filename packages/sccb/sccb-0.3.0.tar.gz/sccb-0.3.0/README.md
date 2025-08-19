📋 SCCB – Shortcut Clipboard + Command Binder


SCCB is a customizable CLI tool that lets you save and run command shortcuts and clipboard snippets.
It’s like a mix of a snippet manager and a Git alias system, but fully configurable via a JSON file.

I built this project to save time in my daily workflow — instead of typing long Git commands or reusing the same text snippets, I can now run them instantly with sccb.


---

✨ Features

- 🔖 Snippets → Save reusable text and copy it to your clipboard with one command.
- ⚡ Commands → Save shell command macros and run them instantly.
- 📝 Variable substitution → Use placeholders like {msg} or {name} and fill them at runtime.
- 🛠 Defaults → Define default values for variables in your config.
- 📂 Config file → All shortcuts are stored in ~/.sccb.json (easy to edit, share, or sync).
- 🎨 Pretty output → Uses Rich for nice tables.
- 🖥 Shell integration → Optionally push commands into your shell buffer (zsh).
- 🧹 Simple management → Add, remove, list, and edit shortcuts easily.

---

📦 Installation

From PyPI (recommended)

	pip install sccb

From source

	git clone https://github.com/yourusername/sccb.git
	cd sccb
	pip install -e .


---

🚀 Usage

Add a Command

	sccb add gitall:"git add . && git commit -m '{msg}' && git push"


- 
{msg} is a variable placeholder.



- 
You can pass it at runtime:



	sccb gitall msg:"Initial commit" !


→ Runs git add . && git commit -m 'Initial commit' && git push



- 
Or define a default in ~/.sccb.json:



	"gitall": {
	  "type": "command",
	  "value": "git add . && git commit -m '{msg}' && git push",
	  "defaults": { "msg": "quick commit" }
	}


Then just run:



	sccb gitall !




---

Add a Snippet

	sccb add@ greet:"Hello {name}!"


- 
Copy with a variable:



	sccb greet name:"Alice"


→ Copies Hello Alice! to clipboard.



- 
With a default in config:



	"greet": {
	  "type": "snippet",
	  "value": "Hello {name}!",
	  "defaults": { "name": "friend" }
	}



	sccb greet


→ Copies Hello friend! to clipboard.




---

List Shortcuts

	sccb ls

Shows all saved commands and snippets in pretty tables.


---

Remove a Shortcut

	sccb rm gitall


---

Edit Config

	sccb edit

Opens ~/.sccb.json in your default editor ($EDITOR or nano).


---

Help

	sccb help

Shows a quick guide to all commands.


---

⚙️ Shell Integration (Optional)


You can install shell integration to push commands into your shell buffer (zsh only for now):


	sccb install_shell
	source ~/.zshrc

Then you can type:


	sccb gitall

and the command will appear in your terminal buffer, ready to run.


---

🛠 How I Built It

- Language: Python
- CLI Framework: Typer
- Clipboard: Pyperclip
- Pretty Output: Rich
- Config: JSON file stored at ~/.sccb.json
- Packaging: pyproject.toml + published to PyPI
This project started as a way to save time typing repetitive Git commands and reusing text snippets. Over time, I added:


- Variable substitution ({msg}, {name})
- Defaults in config
- Shell integration for buffer mode
- A polished CLI with ls, rm, edit, and help

---

📌 Example Config (~/.sccb.json)

	{
	  "commands": {
	    "gitall": {
	      "type": "command",
	      "value": "git add . && git commit -m '{msg}' && git push",
	      "defaults": { "msg": "quick commit" }
	    }
	  },
	  "snippets": {
	    "greet": {
	      "type": "snippet",
	      "value": "Hello {name}!",
	      "defaults": { "name": "friend" }
	    }
	  }
	}

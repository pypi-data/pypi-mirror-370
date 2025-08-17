![Brixterm Logo](img/logo.png)

## About

**BrixTerm** is a simple terminal app that integrates GPT to assist with everyday development tasks.
> Powered by **LLMBrix** framework: https://github.com/matejkvassay/LLMBrix

---

## Features

- Automatically suggests fixes for failed Unix commands
- Generates Python code and copies it directly to your clipboard
- Built-in chatbot accessible inside the terminal

> **Note:** This tool is **not fully agentic** — developers maintain control by using pre-defined commands.

---

## Available Commands

### 1. TERMINAL (default)

Type any terminal command.
If it fails, the AI will suggest a corrected version.

---

### 2. INTERACTIVE SHELL

Use `!<command>` to run an interactive shell command.
Without the `!`, interactive commands timeout after 10 seconds.
**Example:** `!htop`

---

### 3. CODE GEN

Use `c <your request>` to generate Python code.
The generated code is automatically copied to your clipboard.

---

### 4. CODE GEN + CLIPBOARD

Use `ccc <your request>` to generate Python code.
The content of your clipboard is automatically passed to the code generator prompt.
The generated code is copied back to your clipboard.

---

### 5. CHAT ANSWER

Use `a <your request>` to chat with GPT.

---

### 6. CHAT ANSWER + CLIPBOARD

Use `aaa <your request>` to chat with GPT.
The content of your clipboard is automatically passed to the AI chatbot prompt.

---

### 7. EXIT

Use `q` to exit the application.

---

> Note: All GPT powered commands also maintain chat history and remember your previous requests.
___

## Usage guide

### Install

```bash
pip install brix-term
```

### Configure

#### Public OpenAI API configuration

```bash
# Configure OpenAI API access
export OPENAI_API_KEY='<TOKEN>'
```

#### (alternative) Azure OpenAI API configuration

```bash
# (ALTERNATIVELY) API access for Azure AI is also supported
export AZURE_OPENAI_API_KEY='<TOKEN>'
export AZURE_OPENAI_API_VERSION='<VERSION>'
export AZURE_OPENAI_ENDPOINT='<ENDPOINT>'
export AZURE_DEPLOYMENT='<DEPLOYMENT>'
```

#### BrixTerm settings

```bash
# (optional) GPT model to be used, default is `gpt-5-mini`
export BRIXTERM_MODEL='gpt-5-mini'

# (optional) Optimize colors for light mode (dark is default, light support is limited, not recommended)
export BRIXTERM_COLOR_MODE='light'
```

### Run

```bash
brixterm
```

### Run options

> **Note:** env vars have priority over run arguments

> **Note:** `--light_mode` is enabled in minimal way however dark terminal and dark mode is recommended for better
> visibility.

```bash
brixterm --help
usage: brixterm [-h] [--dev] [--light_mode] [--model MODEL] [--azure]

BrixTerm AI Terminal

options:
  -h, --help     show this help message and exit
  --dev          (optional) Run in development mode with Arize Phoenix tracing enabled.
  --light_mode   (optional) Optimize looks for light mode terminal (dark is default).
  --model MODEL  (optional) Specify GPT model. (default='gpt-4o-mini')
  --azure        (optional) Default to Azure. Use to enforce Azure OpenAI API in case both public and Azure OpenAI env vars are set.

```

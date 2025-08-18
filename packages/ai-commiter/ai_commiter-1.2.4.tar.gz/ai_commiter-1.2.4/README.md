# AI-Commiter

**`grit`** = **G**it **R**eview **I**ntelligence **T**ool

[![PyPI version](https://badge.fury.io/py/ai-commiter.svg)](https://badge.fury.io/py/ai-commiter)

AI-powered Git commit message generator with multi-language support. Analyzes file changes and generates clear, structured commit messages using OpenAI API.

인공지능을 활용한 다국어 지원 Git 커밋 메시지 생성기입니다. 파일 변경 내역을 분석하고 OpenAI API를 통해 명확하고 구조화된 커밋 메시지를 생성합니다.

## ✨ Key Features

- **🌍 Multi-language Support**: Generate commit messages in Korean, English, Japanese, Chinese (Simplified/Traditional)
- **🤖 Intelligent Analysis**: Analyzes Git diff to create specific, structured commit messages
- **📝 Conventional Commits**: Uses standardized format with structured body using bullet points
- **📁 File Categorization**: Categorizes multiple file changes and provides summary information
- **⚙️ Custom Prompts**: Support for user-defined prompt templates
- **⚡ Simple CLI**: Use `grit` command for quick and convenient access
- **🧠 Multiple AI Models**: Choose from various OpenAI GPT models with automatic complexity-based selection
- **📋 Structured Output**: Body messages formatted with bullet points for better readability

## 📦 Installation

### Option 1: Homebrew (macOS Recommended)

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python and pipx
brew install python pipx
pipx ensurepath && source ~/.zshrc

# Install AI-Commiter
pipx install ai-commiter
```

### Option 2: pipx (Cross-platform)

```bash
# Install pipx
pip3 install pipx  # macOS/Linux
pipx ensurepath

# Apply environment variables
source ~/.zshrc     # macOS (zsh)
source ~/.bashrc    # Linux (bash)

# Install AI-Commiter
pipx install ai-commiter
```

### Option 3: pip3 (Direct installation)

```bash
# macOS/Linux
pip3 install ai-commiter

# Windows
pip install ai-commiter
```

## 🔑 API Key Setup

AI-Commiter supports two environment variables for OpenAI API key:

1. `AI_COMMITER_API_KEY` - Dedicated for AI-Commiter (recommended)
2. `OPENAI_API_KEY` - Standard OpenAI environment variable

### Permanent Setup (Recommended)

```bash
# macOS (zsh)
echo 'export AI_COMMITER_API_KEY=your-api-key-here' >> ~/.zshrc
source ~/.zshrc

# Linux (bash)
echo 'export AI_COMMITER_API_KEY=your-api-key-here' >> ~/.bashrc
source ~/.bashrc

# Windows
setx AI_COMMITER_API_KEY "your-api-key-here"
# Restart terminal after running the command
```

### Temporary Setup

```bash
# macOS/Linux
export AI_COMMITER_API_KEY=your-api-key-here

# Windows
set AI_COMMITER_API_KEY=your-api-key-here
```

## 🔄 Upgrade

```bash
# pipx
pipx upgrade ai-commiter

# pip3 (macOS/Linux)
pip3 install --upgrade ai-commiter

# pip (Windows)
pip install --upgrade ai-commiter

# Check version
grit --version  # 또는 grit -v
```

## 🚀 Quick Start

```bash
# Generate commit message (preview)
grit commit

# Generate and commit automatically
grit commit --commit

# Use Korean language
grit commit --lang ko --commit

# Use GPT-5-mini (recommended)
grit commit --model gpt-5-mini --commit

# Auto-split complex changes into multiple commits
grit commit --commit --split
```

## 📝 Usage Examples

```bash
# Basic usage
grit commit                         # Preview commit message
grit commit --commit                # Generate and commit
grit commit --repo /path/to/repo    # Specify repository path

# Language options
grit commit --lang ko               # Korean
grit commit --lang en               # English (default)
grit commit --lang ja               # Japanese
grit commit --lang zh-CN            # Chinese Simplified
grit commit --lang zh-TW            # Chinese Traditional

# Model selection
grit commit --model gpt-5-mini      # Recommended (default)
grit commit --model gpt-4o          # Alternative option
grit commit --model gpt-4           # Legacy option
grit commit --model gpt-3.5-turbo   # For simple changes
grit commit --model gpt-4o-mini     # ⚠️ May include markdown formatting in output

# Advanced options
grit commit --all                   # Include unstaged changes
grit commit --prompt custom.txt     # Use custom prompt template
grit commit --split                 # Auto-split complex changes
grit commit --exclude package.json  # Exclude specific files from analysis
grit commit -e file1.txt -e file2.py # Exclude multiple files

# Combined examples
grit commit --lang ko --model gpt-5-mini --commit  # Using recommended GPT-5-mini
grit commit --all --lang en --split --exclude package-lock.json
```

## ⚙️ Configuration Management

You can save frequently used options as default settings using Git-style configuration:

```bash
# List all settings
grit config --list
grit config -l

# Get specific setting
grit config core.lang
grit config core.model

# Set configuration (key value format)
grit config core.lang ko
grit config core.model gpt-4
grit config core.commit true
grit config core.split false
grit config core.prompt /path/to/custom-prompt.txt

# Remove setting
grit config --unset core.lang
grit config --unset core.model

# Global config (applies to all repositories)
grit config --global core.lang en
grit config --global core.model gpt-4
grit config --global --list

# Local repository config (default behavior, overrides global)
grit config --local --list
grit config --local core.lang ko
```

### Available Configuration Sections

#### Core Section (`[core]`)
| Key | Valid Values | Description |
|-----|-------------|-------------|
| `core.lang` | `ko`, `ko-KR`, `en`, `en-US`, `en-GB`, `ja`, `ja-JP`, `zh`, `zh-CN`, `zh-TW` | Default commit message language |
| `core.model` | `gpt-5-mini` (recommended), `gpt-4o`, `gpt-4`, `gpt-3.5-turbo`, `gpt-4o-mini` | Default AI model (⚠️ gpt-4o-mini may include markdown formatting) |
| `core.commit` | `true`, `false` | Automatically commit after generating message |
| `core.split` | `true`, `false` | Automatically split complex changes |
| `core.prompt` | File path | Path to custom prompt template |

Configuration is stored in INI format:

**Global config** (`~/.grit/config`):
```ini
[core]
lang = en
model = gpt-5-mini  # Recommended default
commit = false
```

**Local config** (`./grit/config`):
```ini
[core]
lang = ko
commit = true
split = false
prompt = /path/to/custom-prompt.txt
```

로컬 설정이 글로벌 설정보다 우선순위를 가집니다.

## 🌍 Supported Languages

| Language | Code | Example |
|----------|------|--------|
| Korean | `ko`, `ko-KR` | `grit commit --lang ko` |
| English | `en`, `en-US`, `en-GB` | `grit commit --lang en` |
| Japanese | `ja`, `ja-JP` | `grit commit --lang ja` |
| Chinese (Simplified) | `zh`, `zh-CN` | `grit commit --lang zh-CN` |
| Chinese (Traditional) | `zh-TW` | `grit commit --lang zh-TW` |

> **Note**: Commit titles are always in English (imperative mood) following Conventional Commits standard. Only the detailed descriptions are localized.

## 📋 Output Example

```
🧠 Complexity analysis: Simple changes (score: 0)
   • 1 files (+0), 39 diff lines (+0)
   → Selected gpt-3.5-turbo model
🤖 AI is generating commit message...

📝 Generated commit message:
--------------------------------------------------
docs: Update commit prompt template

- 커밋 프롬프트 템플릿 업데이트
- 커밋 메시지 템플릿 내용 수정 및 명확하게 작성 요청
--------------------------------------------------
```

## ⚙️ Custom Prompt Templates

Create custom prompt template files to adjust AI-generated commit message style:

```bash
# Use custom template
grit --prompt my_template.txt
```

**Template variables:**
- `{diff}` - Git diff content
- `{language_instruction}` - Language-specific instructions
- Categorization variables for file types

**Example template:**
```
You are an expert Git commit message generator. Create a commit message following Conventional Commits format.

## Requirements:
- Type: feat, fix, docs, style, refactor, test, chore, perf, ci, build
- Title: English imperative mood (max 50 chars)
- Body: Bullet points with specific changes

## Code Changes:
{diff}

## Language:
{language_instruction}
```

## 📋 Requirements

- Python 3.7+
- Git
- OpenAI API Key

## 🔧 Troubleshooting

### GPT-4o-mini 모델 사용 시 출력 형식 문제

**문제**: GPT-4o-mini 모델 사용 시 커밋 메시지에 코드 블록 마크다운(```` ``` ````)이 포함되어 출력될 수 있습니다.

**해결 방법**:
```bash
# GPT-5-mini 사용 (권장)
grit commit --model gpt-5-mini

# 또는 기본 모델을 GPT-5-mini로 변경
grit config core.model gpt-5-mini

# 대안: GPT-4o, GPT-4 또는 GPT-3.5-turbo 사용
grit commit --model gpt-4o
grit commit --model gpt-4
grit commit --model gpt-3.5-turbo
```

**참고**: 이는 GPT-4o-mini 모델의 특성으로, 향후 업데이트에서 개선될 예정입니다.

## 📄 License

MIT License


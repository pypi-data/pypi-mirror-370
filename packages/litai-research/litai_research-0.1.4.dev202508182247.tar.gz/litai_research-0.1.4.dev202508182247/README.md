# LitAI

**Turn weeks of literature review into hours.** LitAI lets you have research conversations with your entire paper collection - ask questions across multiple papers and get cited, contextual answers. Whether finding your research direction or unblocking active experiments, LitAI synthesizes literature to accelerate discovery.

## Table of Contents

- [Background](#background)
  - [The Problem](#the-problem)
  - [The LitAI Difference: Synthesis](#the-litai-difference-synthesis)
  - [Who Benefits](#who-benefits)
- [Installation](#installation)
  - [Quick Install](#quick-install-if-you-know-what-youre-doing)
  - [Prerequisites](#prerequisites)
  - [API Key Setup](#api-key-setup)
  - [Package Installation](#package-installation)
  - [Updates](#updates)
- [Usage](#usage)
  - [1. Launch LitAI](#1-launch-litai)
  - [2. Set Up Your Research Profile](#2-set-up-your-research-profile-recommended)
  - [3. How LitAI Works](#3-how-litai-works)
  - [4. Example Workflows](#4-example-workflows)
- [Data Storage](#data-storage)
  - [Database Management](#database-management)
- [FAQ](#faq)
  - [Why do paper searches sometimes fail?](#why-do-paper-searches-sometimes-fail)
- [Support](#support)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
  - [Installing the development version](#installing-the-development-version)
- [Authors and Acknowledgments](#authors-and-acknowledgments)
- [License](#license)

## Background

### The Problem
Literature reviews take weeks. You read dozens of papers, lose track of insights, and struggle to synthesize findings across documents. Existing tools help you find or store papers - but not understand them together.

### The LitAI Difference: Synthesis
LitAI is the only tool that lets you have research conversations with your entire paper collection:

1. **Discovery**: Search millions of papers using natural language
2. **Collection**: Save papers locally with automatic ArXiv PDF downloads  
3. **Context Building**: Add your notes, select which papers and sections to analyze
4. **Synthesis**: Ask questions across multiple papers and get cited, contextual answers

This synthesis capability transforms how you work:
- **Finding Your Research Question**: Explore a field systematically, discover gaps, understand contradictions
- **Active Research Support**: Get immediate answers to operational questions that arise during experiments, debugging, or analysis

Unlike AI writing tools, LitAI helps you *discover* your research direction through literature understanding, not by choosing for you.

### Who Benefits
- **Graduate Students**: Navigate unfamiliar literature to find and refine research questions
- **Active Researchers**: Unblock experiments with immediate synthesis of relevant methods
- **Engineers**: Find academic solutions to technical problems in production
- **Research Teams**: Build shared understanding across collaborative projects

## Installation

### Quick Install (if you know what you're doing)
```bash
uv tool install litai-research && export OPENAI_API_KEY=sk-... && litai
```

### Prerequisites
- Python 3.11 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

> [!WARNING]
> Currently, papers can only be downloaded from ArXiv. Support for importing your own PDFs is coming soon via `/import`.

### API Key Setup
Get your API key from [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

**Permanent setup (recommended):**

macOS: 
```bash
echo 'export OPENAI_API_KEY="sk-..."' >> ~/.zshrc && source ~/.zshrc
```

Linux: 
```bash
echo 'export OPENAI_API_KEY="sk-..."' >> ~/.bashrc && source ~/.bashrc
```

**Current session only:**
```bash
export OPENAI_API_KEY=sk-...
```

### Package Installation

First [install uv](https://docs.astral.sh/uv/getting-started/installation/), then:

```bash
# Using uv (recommended)
uv tool install litai-research

# Alternative: using pipx
pipx install litai-research
```

> [!TIP]
> If `litai` command not found, restart your terminal.

### Updates
```bash
# Get latest stable updates
uv tool upgrade litai-research

# Alternative: using pipx
pipx upgrade litai-research
```

## Usage

### 1. Launch LitAI
```bash
litai
```

### 2. Set Up Your Research Profile (Recommended)
Tell LitAI about your research focus for better responses:

```bash
/prompt
```

This opens an editor where you can describe your background, interests, and preferences. LitAI includes this in every conversation to tailor its responses.

### 3. How LitAI Works

**The Workflow:**
1. **Find**: Search for papers → "find papers on transformers" or `/find transformers`
2. **Save**: Add to collection → "add papers 1-3" or `/add 1-3`  
3. **Organize**: Add notes/tags → "add a note" or `/note`
4. **Analyze**: Build context → "add paper to context" or `/cadd <paper>`
5. **Synthesize**: Ask questions → "what methods do they use?" or `/synthesize`

> [!IMPORTANT]
> Only papers in your context are analyzed. Collection stores everything; context is your active analysis set.

> [!NOTE]
> LitAI understands natural language - just chat with it. Want more control? Use `/commands` instead. Mix both freely.

**Commands**: For a complete list of commands, use `/help` in LitAI. For detailed information about any specific command, use `<command> --help` (e.g., `/add --help`).

**AI Models**: LitAI uses two models for optimal performance:
- **Large model (GPT-5)**: Used for `/synthesis` queries
- **Small model (GPT-5-nano)**: Used for search, extraction, and simple operations

These can be customized in settings, but we recommend the defaults for best results.

### 4. Example Workflows

**Exploring a new field:**
```
→ Find recent papers on vision transformers
→ Add the top 5 papers to my collection
→ Add ViT and DINO papers to context with abstracts
→ What are the main architectural innovations?
```

**Debugging your implementation:**
```
→ Find papers about transformer memory efficiency
→ Add papers 1-3 about flash attention
→ Add them to context with full text
→ How do they handle the quadratic complexity problem?
```

**Finding research gaps:**
```
→ Search for graph neural network survey papers
→ Save all the recent surveys
→ Add top 3 surveys to context
→ What problems do they identify as unsolved?
```

## Data Storage

LitAI stores all data locally in `~/.litai/`:
- `litai.db` - SQLite database with paper metadata and extractions
- `pdfs/` - Downloaded PDF files  
- `logs/litai.log` - Application logs for debugging
- `config.json` - User configuration
- `user_prompt.txt` - Personal research profile

### Database Management

The LitAI database (`~/.litai/db/litai.db`) is a standard SQLite database that you can explore and manage with any SQLite-compatible tool. We recommend [Beekeeper Studio](https://www.beekeeperstudio.io/) for its user-friendly interface, but you can use any database tool you prefer.

**To open the database in Beekeeper Studio:**

1. Download and install [Beekeeper Studio](https://www.beekeeperstudio.io/)
2. Open Beekeeper Studio and click "New Connection"
3. Select "SQLite" as the database type
4. Click "Browse" and navigate to: `~/.litai/db/litai.db`
   - **macOS tip**: Hidden files (starting with `.`) may not be visible in Finder by default. Press `Command + Shift + .` to show hidden files
5. Click "Connect"

You can now browse tables, run queries, and explore your research data directly.

## FAQ

### Why do paper searches sometimes fail?

Semantic Scholar's public API can experience high load, leading to search failures. If you encounter frequent issues:
- Wait a few minutes and try again
- Consider requesting a free API key for higher rate limits: [Semantic Scholar API Key Form](https://www.semanticscholar.org/product/api#api-key-form)

## Support

- Email issues to [harmonsbhasin@gmail.com](mailto:harmonsbhasin@gmail.com)
- Logs for debugging: `~/.litai/logs/litai.log`

## Roadmap

**Coming soon:** Support for importing your own PDFs via `/import`.

## Contributing

We welcome contributions! Guidelines coming soon.

### Installing the development version

```bash
# Using uv (recommended)
uv tool install --prerelease=allow litai-research

# Using pipx
pipx install --prerelease litai-research
```

## Authors and Acknowledgments

- Created by [Harmon Bhasin](https://www.harm0n.com/) and [Alex Wilf](https://abwilf.github.io/)
- Powered by [Semantic Scholar API](https://www.semanticscholar.org/product/api) and [OpenAI API](https://openai.com/api/)

## License

This project is open source and available under the [MIT License](LICENSE).

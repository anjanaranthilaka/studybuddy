# StudyBuddy AI - Local LLM Study Assistant Using Ollama

StudyBuddy AI is an autonomous, privacy-preserving study assistant that runs entirely on local hardware using **Ollama and Python**. It uses a multi-turn **ReAct (Reasoning + Acting) agent loop** to search local study notes, generate multiple-choice quizzes, evaluate answers, track student performance, and create personalized revision schedules.

The system is designed to demonstrate practical **AI agent architecture, local LLM inference, tool calling, persistent memory, database management, and defensive software engineering**.

---

## Key Features

- **100% Local AI Inference**  
  Runs the `qwen2.5:3b` language model locally through Ollama. No cloud API is required.

- **Privacy-Preserving**  
  Study notes, quiz results, and learning history remain on the local machine.

- **AI Agent with Tool Calling**  
  Uses Ollama's native tool-calling capabilities to dynamically select and execute tools.

- **ReAct Agent Loop**  
  The agent can reason about a request, call tools, observe their results, and continue until it can provide a final answer.

- **Persistent Memory**  
  SQLite stores quizzes, answer keys, quiz attempts, learning progress, and study plans.

- **Quiz Generation and Evaluation**  
  Generates structured multiple-choice quizzes and automatically evaluates submitted answers.

- **Learning Progress Tracking**  
  Calculates historical performance and identifies weak topics requiring additional revision.

- **Personalized Study Plans**  
  Creates multi-day revision schedules based on topics, available study time, and number of days.

- **Dual Interface**  
  Includes both a command-line interface and a Streamlit web application.

- **Real-Time Tool Tracing**  
  The Streamlit interface displays the tools being called and their results.

- **Defensive Engineering**  
  Uses explicit tool dispatch, input validation, parameterized SQL queries, and a maximum agent-round limit.

---

## System Architecture

```text
                    ┌───────────────────────┐
                    │     Student / User    │
                    └───────────┬───────────┘
                                │
                    ┌───────────▼───────────┐
                    │   CLI / Streamlit UI  │
                    └───────────┬───────────┘
                                │
                    ┌───────────▼───────────┐
                    │    StudyBuddy Agent   │
                    │      agent.py         │
                    └───────────┬───────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ▼                 ▼                 ▼
      ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
      │    Ollama    │  │ Tool Layer   │  │  SQLite DB   │
      │ qwen2.5:3b   │  │ 6 Tools      │  │  Persistence  │
      └──────────────┘  └──────────────┘  └──────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ▼             ▼             ▼
          Note Search     Quiz Engine   Study Planner
```

---

## How It Works

A typical request follows this process:

```text
User Request
     │
     ▼
StudyBuddy Agent
     │
     ▼
Ollama LLM
     │
     ├── Needs information?
     │       │
     │       ▼
     │   Call a tool
     │       │
     │       ▼
     │   Tool executes
     │       │
     │       ▼
     │   Result returned
     │       │
     │       └──────────────┐
     │                      ▼
     └──────────────► Ollama processes result
                            │
                            ▼
                     Final Response
```

The agent supports up to **8 reasoning/tool-execution rounds** for a single request.

---

## Project Structure

```text
studybuddy/
│
├── app.py
├── main.py
├── config.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── agents/
│   ├── __init__.py
│   ├── agent.py
│   └── prompts.py
│
├── tools/
│   ├── __init__.py
│   ├── notes_tools.py
│   ├── quiz_tools.py
│   ├── progress_tools.py
│   └── study_plan_tools.py
│
├── database/
│   ├── __init__.py
│   └── db.py
│
├── data/
│   ├── sample_notes/
│   │   ├── python_functions.md
│   │   └── python_loops.md
│   └── studybuddy.db
│
├── logs/
│   └── agent.log
│
├── tests/
│   ├── __init__.py
│   ├── test_database.py
│   ├── test_tools.py
│   ├── test_agent.py
│   └── test_integration.py
│
├── docs/
│   ├── architecture.md
│   ├── contribution_table.md
│   └── viva_questions.md
│
└── report/
    └── report.md
```

---

## Tool Registry

StudyBuddy contains six tools that can be selected by the local LLM.

| Tool | Parameters | Description |
|---|---|---|
| `search_notes` | `query: str` | Searches local Markdown study notes. |
| `generate_quiz` | `topic: str, num_questions: int` | Generates and stores a multiple-choice quiz. |
| `evaluate_answers` | `quiz_id: str, answers: list[str]` | Evaluates submitted answers and records the attempt. |
| `get_learning_progress` | `topic: str \| None` | Calculates learning performance and identifies weak topics. |
| `create_study_plan` | `topics: list[str], available_minutes_per_day: int, days: int` | Creates a multi-day revision schedule. |
| `get_active_study_plan` | None | Retrieves the most recent active study plan. |

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application and agent implementation |
| Ollama | Local LLM runtime |
| Qwen 2.5 3B | Local language model |
| SQLite | Persistent data storage |
| Streamlit | Web interface |
| Pytest | Automated testing |
| Markdown | Local study notes and documentation |

---

## Prerequisites

Before installing StudyBuddy, make sure you have:

- Python **3.10 or newer**
- Ollama
- `qwen2.5:3b` model
- Git (if cloning from GitHub)

Ollama can be downloaded from:

https://ollama.com

---

## Installation

### 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd studybuddy
```

If you already have the project folder, simply open a terminal inside the project directory.

---

### 2. Create a Virtual Environment

#### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

#### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 4. Install the Ollama Model

Make sure Ollama is installed and running.

Then download the model:

```bash
ollama pull qwen2.5:3b
```

You can verify that the model is available with:

```bash
ollama list
```

---

### 5. Initialize the Database

Run:

```bash
python -c "import database.db as db; db.init_db(); print('Database initialized.')"
```

The SQLite database will be created at:

```text
data/studybuddy.db
```

---

## Running the Application

### Command-Line Interface

Run:

```bash
python main.py
```

You can then interact with StudyBuddy directly from the terminal.

To clear the current conversation memory:

```text
reset
```

To exit:

```text
exit
```

or:

```text
quit
```

---

### Streamlit Web Application

Run:

```bash
streamlit run app.py
```

Streamlit will provide a local address similar to:

```text
http://localhost:8501
```

Open this address in your browser.

The web interface provides:

- Chat interaction
- Tool execution traces
- Quiz generation
- Quiz evaluation
- Learning progress
- Study plans
- Persistent application data

---

## Example Prompts

### 1. Search and Explain Notes

```text
Search my notes for functions and explain what the LEGB rule means.
```

StudyBuddy searches the local Markdown notes before generating its explanation.

---

### 2. Generate a Quiz

```text
Make a 3-question quiz on Python loops.
```

The agent generates the quiz and stores the answer key securely in SQLite.

You can then submit answers:

```text
Submit answers A, B, C for quiz <quiz_id>.
```

The system calculates the score and records the attempt.

---

### 3. Create a Study Plan

```text
I have 3 days before my exam with 60 minutes per day.
Search my notes and generate a revision plan for Python functions and loops.
```

The agent can search the notes and create a personalized revision schedule.

---

## Database

StudyBuddy uses SQLite for persistent storage.

The database is located at:

```text
data/studybuddy.db
```

The main stored information includes:

- Quiz questions
- Quiz answer keys
- Quiz attempts
- Scores
- Learning progress
- Study plans

Because the database is stored locally, the student's learning history does not need to be uploaded to an external service.

---

## Quiz Security

Quiz answer keys are separated from the public quiz questions.

When a quiz is generated:

```text
                    Quiz Generation
                          │
              ┌───────────┴───────────┐
              ▼                       ▼
       Public Questions          Answer Key
              │                       │
              ▼                       ▼
        Returned to UI          Stored in SQLite
```

The answer key is not included in the normal quiz response.

When the student submits answers, the system retrieves the stored key and performs the evaluation internally.

---

## Learning Progress

StudyBuddy tracks previous quiz attempts and calculates historical performance.

Topics with an average score below **70%** are identified as topics requiring additional revision.

Example:

```text
Python Functions     85%
Python Loops         62%
Python Variables     91%
```

The system would identify:

```text
Weak Topic:
Python Loops
```

This information can then be used when creating future study plans.

---

## Study Plan

The study planner distributes available study time using a simple 40/40/20 structure:

```text
40% → Reading / Reviewing Notes
40% → Active Coding Practice
20% → Quiz Review / Weak Areas
```

For example, with 60 minutes available:

```text
24 minutes → Notes
24 minutes → Coding Practice
12 minutes → Quiz / Review
```

The generated schedule is stored in SQLite so that it remains available after restarting the application.

---

## Agent Safety

The agent uses several defensive programming techniques.

### Explicit Tool Dispatcher

The system does not use:

```python
eval()
```

or:

```python
exec()
```

Instead, tools are registered explicitly in a dictionary.

Only approved tools can be executed by the agent.

---

### Input Validation

Tool parameters are validated before execution.

Examples include:

- Empty query validation
- Quiz question limits
- Valid quiz IDs
- Valid answer choices
- Study time boundaries
- Study plan day limits

---

### Parameterized SQL

Database operations use parameterized SQL queries.

For example:

```python
cursor.execute(
    "SELECT * FROM quizzes WHERE quiz_id = ?",
    (quiz_id,)
)
```

This prevents user-provided values from being interpreted as SQL commands.

---

### Agent Round Limit

The agent cannot continuously call tools forever.

A maximum of:

```text
8 reasoning/tool rounds
```

is allowed for a single request.

This prevents runaway agent execution.

---

## Testing

The project includes automated tests covering the database, individual tools, agent behavior, and live Ollama integration.

Run the complete test suite with:

```bash
python -m pytest tests/ -v
```

### Test Results

| Test File | Tests | Result |
|---|---:|---|
| `test_database.py` | 4 | ✅ Passed |
| `test_tools.py` | 7 | ✅ Passed |
| `test_agent.py` | 4 | ✅ Passed |
| `test_integration.py` | 1 | ✅ Passed |
| **Total** | **16** | **16/16 Passed** |

The integration test verifies communication with the locally running Ollama model.

---

## Testing Coverage

The test suite verifies:

- Database initialization
- SQLite foreign keys
- Quiz persistence
- Quiz evaluation
- Score calculation
- Note searching
- Input validation
- Study plan generation
- Tool dispatching
- Unknown tool handling
- Agent round limits
- Conversation memory reset
- Local Ollama integration

---

## Example Agent Flow

For a request such as:

```text
Search my notes for Python loops and make me a quiz.
```

The agent may perform the following sequence:

```text
1. Receive user request
        ↓
2. Ask Ollama what tool is needed
        ↓
3. Call search_notes
        ↓
4. Receive matching note content
        ↓
5. Send tool result back to Ollama
        ↓
6. Ollama decides to call generate_quiz
        ↓
7. Generate quiz
        ↓
8. Store quiz and answer key in SQLite
        ↓
9. Return quiz to student
```

This demonstrates the ReAct-style **reason → act → observe → continue** workflow.

---

## Known Limitations

### Context Size

Very large Markdown notes may exceed the model's available context window when too much content is returned during note searching.

### Local Hardware

Inference speed depends on the available CPU, GPU, RAM, and VRAM.

### Single-Host Inference

Because the LLM runs locally, simultaneous users may be limited by available hardware resources.

### Basic Retrieval

The current note search uses keyword-based retrieval rather than vector-based semantic search.

---

## Future Improvements

Possible future improvements include:

- Semantic vector search
- Local embedding models
- ChromaDB or FAISS integration
- Spaced repetition algorithms such as SM-2
- More advanced adaptive learning
- Multi-user authentication
- Improved quiz difficulty adjustment
- More detailed analytics dashboards
- Additional study material formats such as PDF and DOCX
- Mobile-friendly interface

---

## Privacy

StudyBuddy is designed around local-first operation.

Student:

- Study notes
- Quiz history
- Scores
- Study plans
- Learning progress

are stored locally.

No external cloud LLM API is required for normal operation.

---

## Documentation

Additional project documentation is available in the `docs/` directory:

```text
docs/
├── architecture.md
├── contribution_table.md
└── viva_questions.md
```

The academic project report is available at:

```text
report/report.md
```

---

## Project Status

```text
Development      ✅ Complete
Database         ✅ Complete
Agent            ✅ Complete
Tool Layer       ✅ Complete
CLI              ✅ Complete
Streamlit UI     ✅ Complete
Automated Tests  ✅ 16/16 Passed
Documentation    ✅ Complete
```

---

## References

1. Lewis, P. et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. Advances in Neural Information Processing Systems.

2. Yao, S. et al. (2023). *ReAct: Synergizing Reasoning and Acting in Language Models*. International Conference on Learning Representations (ICLR).

3. Ollama. *Ollama Python Library and Tool Calling Documentation*.  
   https://github.com/ollama/ollama-python

4. SQLite. *SQLite Documentation*.  
   https://www.sqlite.org/

---

## Authors

**StudyBuddy AI Project**

Developed as an academic project demonstrating:

- Artificial Intelligence Agents
- Local Large Language Models
- ReAct Architecture
- Tool Calling
- Database Persistence
- Software Testing
- Secure Software Engineering
- Human-AI Learning Assistance

---

## License

This project was developed for educational and academic purposes.
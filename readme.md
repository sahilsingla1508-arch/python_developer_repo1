# PyChronicle

PyChronicle is an AST-powered Time-Travel Debugger for Python that allows users to visualize program execution line by line. The project combines static code analysis using Python's AST module with runtime tracing (`sys.settrace`), SQLite event storage, and a Textual-based terminal UI to provide an interactive debugging experience.

---

# Mid Review Progress (Week 1 & Week 2)

## ✅ Core Features Implemented

- AST parsing for Python source files
- Variable detection with line number tracking
- Runtime tracing using `sys.settrace`
- Variable change detection during execution
- SQLite database integration for execution events
- End-to-end pipeline connecting AST → Tracer → Storage
- Terminal-based UI using Textual
- Code Viewer
- Variable Panel
- Timeline UI
- Sample scripts for testing
- Integration and edge-case tests
- README updates and project documentation

---

# Project Workflow

```
Python Script
      │
      ▼
 AST Parser
      │
      ▼
 Variable Detection
      │
      ▼
 Runtime Tracer (sys.settrace)
      │
      ▼
 SQLite Storage
      │
      ▼
 Textual User Interface
```

---

# Current Features

### AST Module

- Parse Python source files
- Traverse AST using `ast.NodeVisitor`
- Detect variable assignments
- Store line numbers and column offsets
- Handle edge cases

### Tracer Module

- Runtime execution tracing
- Capture executed lines
- Detect variable value changes
- Filter external library calls
- Generate execution events

### Storage Module

- SQLite event database
- Store execution history
- Retrieve timeline events
- Query variable history

### UI Module

- Code Viewer
- Variable Panel
- Timeline Slider
- Terminal-based interface using Textual

### Pipeline

- Complete integration between all modules
- AST → Tracer → Storage → UI

---

# Tech Stack

- Python 3
- Python AST
- sys.settrace
- SQLite
- Textual
- Rich
- Pytest

---

# Project Structure

```
PyChronicle/
│
├── app.py
├── main.py
├── pipeline.py
├── ast_parser.py
├── tracer.py
├── storage.py
├── code_viewer.py
├── variable_detector.py
├── variable_panel.py
├── timeline.py
├── styles.tcss
├── chronicle.db
├── tests/
├── sample_1.py
├── sample_2.py
└── README.md
```

---

# Running the Project

Create virtual environment

```bash
python -m venv .venv
```

Activate

```bash
# Windows
.venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run application

```bash
python main.py sample_1.py
```

or

```bash
python main.py sample_2.py
```

---

# Running Tests

```bash
pytest -v
```

---

# Mid Review Deliverables

- ✅ AST Module Working
- ✅ Variable Detection Working
- ✅ Runtime Tracing
- ✅ SQLite Integration
- ✅ Textual UI Skeleton
- ✅ Timeline Interface
- ✅ End-to-End Pipeline
- ✅ Integration Tests

---

# Future Enhancements

- Reverse execution support
- Advanced execution visualization
- Breakpoints
- Function call tracing
- Export execution timeline
- Performance optimization

---

# Authors

- Prateek Sharma
- Tejas
- Sahil
- Varad

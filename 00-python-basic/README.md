# Stage 0: Python Basics

## Goal

Learn enough Python to write small scripts, call APIs, process files, and build LLM applications later.

## Topics

1. Variables and data types
2. `print` and string formatting
3. Lists, tuples, and dictionaries
4. Conditions and loops
5. Functions
6. Files and JSON
7. Exceptions
8. Modules and packages
9. Classes
10. Virtual environments and pip

## Graduation Project

Build a command-line script that:

1. Reads a `.txt` or `.md` file.
2. Counts characters, words, and selected keywords.
3. Saves the result as JSON.
4. Commits the project with Git.

## Completed Lessons

- Lesson 01: Variables, data types, and print
- Lesson 02: File reading, text statistics, and JSON output
- Lesson 03: Command-line arguments and keyword statistics
- Lesson 04: Error handling and function splitting
- Lesson 05: Conda environment and pip
- Lesson 06: HTTP/API requests
- Lesson 07: Learning log analyzer project

## Stage 0 Skills

After this stage, I practiced:

- Reading and writing text files
- Working with JSON
- Writing functions
- Using command-line arguments
- Handling errors with `try/except`
- Creating conda environments
- Installing packages with `pip`
- Sending HTTP requests with `requests`
- Using Git and GitHub for learning records

## Final Project

The final project of this stage is a learning log analyzer.

Project file:

```text
00-python-basic/project/learning_log_analyzer.py
```
Run:
```bash
python 00-python-basic/project/learning_log_analyzer.py learning-log.md python agent json git api
```
Outputs:

```text
00-python-basic/project/learning_summary.json
00-python-basic/project/learning_summary.md
```
The project can:
Read learning-log.md
Count characters and lines
Count learning entries
Count selected keywords
Save a JSON summary
Save a Markdown summary
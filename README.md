# AI Engineer Assignment

Welcome to the AI Engineer Assignment repository. This project is designed to help you understand the fundamentals of AI engineering and involves various tasks and exercises.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Overview

This repository contains the assignments for the AI Engineer role. The assignments cover various aspects of AI and software engineering, including but not limited to:

- Code generation using OpenAI API
- Code improvement based on feedback
- Test case generation and validation
- Integration with FastAPI
- Frontend interaction using HTML and JavaScript

## Features

- Generate code snippets in various programming languages (Python, JavaScript, Ruby)
- Improve code snippets based on feedback
- Generate test cases for code snippets
- Run and validate test cases
- Integrated with FastAPI for backend API handling
- Simple frontend interface for interacting with the backend

## Requirements

To run this project, you need to have the following:

- Python 3.11 or higher
- FastAPI
- Uvicorn
- OpenAI API key
- Docker
- Git
- Web browser

## Installation

Follow these steps to set up the project on your local machine:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/gunjan5489/ai-engineer-assignment-main.git
   cd ai-engineer-assignment-main

2. **Set up environment variables**:
   Create a .env file in the root directory and add your OpenAI API key and other necessary configurations:
   ```bash
   # put your environment variables here
   # and rename this file to .env
   # any of 'gpt-4-turbo' model is recommended
   OPENAI_API_KEY=your-openai-api-key
   MODEL_NAME=gpt-3.5-turbo-16k
   TEMPERATURE=0.0
   MAX_TOKENS=1000

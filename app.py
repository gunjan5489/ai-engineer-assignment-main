# app.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
from typing import List, Optional
import os
import json
import re

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for code snippets
snippets = []

# OpenAI API key setup and other parameters
openai.api_key = os.getenv("OPENAI_API_KEY")
model_name = os.getenv("MODEL_NAME")
max_tokens = int(os.getenv("MAX_TOKENS"))
temperature = float(os.getenv("TEMPERATURE"))

# Pydantic models
class Snippet(BaseModel):
    id: int
    description: str
    language: str
    code: str


class GenerateRequest(BaseModel):
    description: str
    language: str


class ImproveRequest(BaseModel):
    code: str
    feedback: str
    language: str


class GenerateTestsRequest(BaseModel):
    code: str
    language: str


class RunTestsRequest(BaseModel):
    code: str
    tests: str
    language: str


class ImproveCodeBasedOnTestsRequest(BaseModel):
    code: str
    feedback: str
    language: str


def extract_code(response_text, language):
    """
    Extract the code block for the specified language from the response text.
    """
    code_block_identifiers = {
        "python": "```python",
        "ruby": "```ruby",
        "javascript": "```javascript",
    }

    code_block_identifier = code_block_identifiers.get(language.lower())
    if not code_block_identifier:
        return response_text.strip()

    pattern = fr"{code_block_identifier}(.*?```)"
    code_match = re.search(pattern, response_text, re.DOTALL)
    if code_match:
        return code_match.group(1).strip().strip("```").strip()
    else:
        return response_text.strip()


def generate_code(description, language):
    """
    Generate code for the given description and language using OpenAI's API.
    """
    response = openai.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": f"Generate a {language} code function for: {description}"},
        ],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    full_response = response.choices[0].message.content.strip()
    return extract_code(full_response, language)


def improve_code(code, feedback, language):
    """
    Improve the given code based on feedback using OpenAI's API.
    """
    response = openai.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": f"Improve the following {language} code based on feedback: {feedback}\n\n{code}"},
        ],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()


def generate_tests(code, language):
    """
    Generate test cases for the given code and language using OpenAI's API.
    """
    json_format = '[{"input":"some value","output": "as per function output"}]'
    response = openai.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": f"Generate a {json_format} for test cases, each with the fields: input and output. Ensure the JSON is properly formatted with double quotes around keys and string values for the following {language} code:\n\n{code}"},
        ],
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()


@app.post("/generate", response_model=Snippet)
def generate(data: GenerateRequest):
    """
    Generate a new code snippet based on the provided description and language.
    """
    code = generate_code(data.description, data.language)
    snippet = {"id": len(snippets) + 1, "description": data.description, "language": data.language, "code": code}
    snippets.append(snippet)
    return snippet


@app.post("/improve")
def improve(data: ImproveRequest):
    """
    Improve the generated code based on feedback.
    """
    improved_code = improve_code(data.code, data.feedback, data.language)
    return {"improved_code": improved_code}


@app.post("/improve_test")
def improve_test(data: ImproveRequest):
    """
    Improve test cases based on feedback.
    """
    json_format = '[{"input":"some value","output": "as per function output"}]'
    response = openai.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": f"Generate the {json_format} for test cases based on the {data.feedback}, "
                                          f"each with the fields: input and output. Ensure the JSON is properly formatted with double quotes around keys and "
                                          f"string values for the following {data.language} code:\n\n{data.code}"},
        ],
        max_tokens=max_tokens,
        temperature=0.7
    )
    improved_test = response.choices[0].message.content.strip()
    print(improved_test)
    return {"improved_test": improved_test}


@app.post("/generate_tests")
def generate_tests_route(data: GenerateTestsRequest):
    """
    Generate test cases for the given code and language.
    """
    tests = generate_tests(data.code, data.language)
    return {"tests": tests}


@app.post("/run_tests")
def run_tests(data: RunTestsRequest):
    """
    Run the provided tests on the given code.
    """
    if data.language.lower() != "python":
        return {"result": "Code execution failed", "error": "Test execution is only supported for Python"}

    code = data.code
    tests = data.tests

    global_vars = {}
    exec(code, global_vars)  # Execute the code and store the resulting global variables in global_vars

    function_name = None
    for name, obj in global_vars.items():
        if callable(obj):
            function_name = name
            break

    if function_name is None:
        raise ValueError("No function found in the provided code.")

    function_to_test = global_vars[function_name]  # Retrieve the function from global_vars

    try:
        test_cases = json.loads(tests)
        all_passed = True
        for i, test in enumerate(test_cases):
            input_value = int(test["input"])
            expected_output = test["output"]
            actual_output = function_to_test(input_value)

            if actual_output == str(expected_output):
                print(f"Test case {i + 1} passed.")
            else:
                print(f"Test case {i + 1} failed. Expected: {expected_output}, Got: {actual_output}")
                all_passed = False
                return {"result": "Code execution failed", "error": f"Test case {i + 1} failed"}

        if all_passed:
            print("All test cases passed.")
            return {"result": "Code Executed Successfully", "output": 0}

    except Exception as e:
        return {"result": "Code execution failed", "error": str(e)}


@app.post("/improve_code_based_on_tests")
def improve_code_based_on_tests(data: ImproveCodeBasedOnTestsRequest):
    """
    Improve the code based on the test results.
    """
    code = data.code
    test_result = data.feedback
    language = data.language
    improved_code = improve_code(code, test_result, language)
    return {"improved_code": improved_code}


@app.get("/snippets", response_model=List[Snippet])
def list_snippets():
    """
    List all the code snippets.
    """
    return snippets


@app.get("/snippets/{id}", response_model=Snippet)
def get_snippet(id: int):
    """
    Retrieve a specific code snippet by ID.
    """
    snippet = next((s for s in snippets if s["id"] == id), None)
    if snippet is None:
        raise HTTPException(status_code=404, detail="Snippet not found")
    return snippet


@app.delete("/snippets/{id}", status_code=204)
def delete_snippet(id: int):
    """
    Delete a specific code snippet by ID.
    """
    global snippets
    snippets = [s for s in snippets if s["id"] != id]
    return


@app.get("/", response_class=HTMLResponse)
async def read_index():
    """
    Serve the index HTML page.
    """
    with open("design.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

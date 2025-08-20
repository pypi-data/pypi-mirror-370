import pandas as pd
import ast
import os
from pathlib import Path
import openai
from tqdm import tqdm
import hashlib

from SharedData.Logger import Logger
from SharedData.Routines.WorkerLib import send_command
from SharedData.IO.ClientAPI import ClientAPI

# ------------- Chunking code (your version, already robust) -------------
def get_node_source_lines(node, source_lines):
    """
    Extracts the source code lines corresponding to a given AST node, including decorators if present.
    
    Parameters:
        node (ast.AST): The abstract syntax tree node to extract source lines from.
        source_lines (list of str): The list of source code lines from the original file.
    
    Returns:
        tuple: A tuple containing:
            - start_line (int): The starting line number of the node's source code (including decorators).
            - end_line (int): The ending line number of the node's source code.
            - code_snippet (str): The concatenated source code lines corresponding to the node.
    """
    if hasattr(node, 'decorator_list') and node.decorator_list:
        start_line = node.decorator_list[0].lineno
    else:
        start_line = node.lineno
    end_line = getattr(node, 'end_lineno', None)
    if end_line is None:
        end_line = max(getattr(n, "lineno", start_line) for n in ast.walk(node))
    code_snippet = '\n'.join(source_lines[start_line-1:end_line])
    return start_line, end_line, code_snippet

def has_numba_jit(node):
    """
    Check if a given AST node has a Numba JIT decorator.
    
    This function inspects the decorator list of the provided AST node to determine
    if any decorator corresponds to Numba's JIT compilation decorators. It looks for:
    - Decorators that are attributes of the 'numba' module (e.g., numba.jit)
    - Decorators that are calls to functions with names starting with 'jit'
    - Decorators that are names starting with 'jit'
    
    Parameters:
        node (ast.AST): The AST node to check for Numba JIT decorators.
    
    Returns:
        bool: True if the node has a Numba JIT decorator, False otherwise.
    """
    if hasattr(node, 'decorator_list'):
        for dec in node.decorator_list:
            if isinstance(dec, ast.Attribute) and getattr(dec.value, 'id', None) == 'numba':
                return True
            if isinstance(dec, ast.Call) and hasattr(dec.func, 'attr') and dec.func.attr.startswith('jit'):
                return True
            if isinstance(dec, ast.Name) and dec.id.startswith('jit'):
                return True
    return False

def chunk_node(node, source_lines, file_path, parent_stack=None):
    """
    Recursively traverses an AST node to yield dictionaries representing class and function definitions.
    
    Each yielded dictionary contains metadata about the node, including its type ('ClassDef', 'FunctionDef', or 'AsyncFunctionDef'),
    fully qualified name (including parent classes/functions), start and end line numbers, source code snippet, file path,
    whether the function is asynchronous, and whether it is decorated with Numba's JIT.
    
    Parameters:
        node (ast.AST): The current AST node to process.
        source_lines (list of str): The source code lines of the file being analyzed.
        file_path (str): The path to the source file.
        parent_stack (list of str, optional): A list of parent names to build the fully qualified name. Defaults to None.
    
    Yields:
        dict: A dictionary containing metadata and source code for each class or function definition found in the AST subtree.
    """
    parent_stack = parent_stack or []
    for child in ast.iter_child_nodes(node):
        if isinstance(child, ast.ClassDef):
            start, end, code = get_node_source_lines(child, source_lines)
            yield {
                'type': 'ClassDef',
                'name': '.'.join(parent_stack + [child.name]),
                'start_line': start,
                'end_line': end,
                'code': code,
                'file': file_path,
                'async': False,
                'numba_jit': False
            }
            yield from chunk_node(child, source_lines, file_path, parent_stack + [child.name])
        elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            start, end, code = get_node_source_lines(child, source_lines)
            is_async = isinstance(child, ast.AsyncFunctionDef)
            numba_jit = has_numba_jit(child)
            yield {
                'type': type(child).__name__,
                'name': '.'.join(parent_stack + [child.name]),
                'start_line': start,
                'end_line': end,
                'code': code,
                'file': file_path,
                'async': is_async,
                'numba_jit': numba_jit
            }
            yield from chunk_node(child, source_lines, file_path, parent_stack + [child.name])

def chunk_script_blocks(tree, source_lines, file_path):
    """
    '''
    Extracts and returns top-level script code blocks from the given AST and source lines.
    
    This function identifies all class and function definitions (including async functions) in the
    AST, marks their line ranges as covered, and then collects all lines outside these ranges as
    separate script blocks. Each script block corresponds to contiguous lines of code not part of
    any class or function definition.
    
    Parameters:
        tree (ast.AST): The abstract syntax tree of the Python source code.
        source_lines (List[str]): The source code lines as a list of strings.
        file_path (str): The path to the source file.
    
    Returns:
        List[dict]: A list of dictionaries, each representing a top-level script block with keys:
            - 'type': Always 'ScriptBlock'.
            - 'name': Always '<top-level>'.
            - 'start_line': The starting line number of the block (1-based).
            - 'end_line': The ending line number of the block (inclusive).
            - 'code': The source code of the block as a single string.
            - 'file': The file path provided.
            - 'async': Always False (script blocks are not async).
            - 'numba_jit': Always False (no JIT compilation
    """
    def_ranges = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            if hasattr(node, 'decorator_list') and node.decorator_list:
                start = node.decorator_list[0].lineno
            else:
                start = node.lineno
            end = getattr(node, 'end_lineno', None)
            if end is None:
                end = max(getattr(n, "lineno", start) for n in ast.walk(node))
            def_ranges.append((start, end))
    def_ranges.sort()
    N = len(source_lines)
    covered = [False] * N
    for start, end in def_ranges:
        for i in range(start-1, end):
            covered[i] = True
    chunks = []
    script_code = []
    script_start = None
    for i, (line, cov) in enumerate(zip(source_lines, covered)):
        if not cov:
            if script_start is None:
                script_start = i
            script_code.append(line)
        elif script_start is not None:
            if script_code and ''.join(script_code).strip():
                chunks.append({
                    'type': 'ScriptBlock',
                    'name': '<top-level>',
                    'start_line': script_start+1,
                    'end_line': i,
                    'code': '\n'.join(script_code),
                    'file': file_path,
                    'async': False,
                    'numba_jit': False
                })
            script_code = []
            script_start = None
    if script_start is not None and script_code and ''.join(script_code).strip():
        chunks.append({
            'type': 'ScriptBlock',
            'name': '<top-level>',
            'start_line': script_start+1,
            'end_line': N,
            'code': '\n'.join(script_code),
            'file': file_path,
            'async': False,
            'numba_jit': False
        })
    return chunks

def chunk_python_code(filepath):
    """
    Reads a Python source file, parses it into an AST, and extracts code chunks and script blocks.
    
    For each extracted chunk, it adds metadata including a unique SHA-256 hash based on file, type, and name,
    and the current normalized timestamp. Each chunk is then posted to a remote collection via ClientAPI.
    
    Parameters:
        filepath (str): The path to the Python source file to be processed.
    
    Returns:
        None
    """
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()
    source_lines = source.splitlines()
    tree = ast.parse(source)
    chunks = list(chunk_node(tree, source_lines, filepath))
    script_chunks = chunk_script_blocks(tree, source_lines, filepath)
    allchunks = chunks + script_chunks
    for chunk in allchunks:
        chunk['file'] = str(chunk['file'])
        hashstr = f"{chunk['file']}#{chunk['type']}#{chunk['name']}"
        chunk['hash'] = hashlib.sha256(hashstr.encode()).hexdigest()
        chunk['date'] = pd.Timestamp.now().normalize()                
        ClientAPI.post_collection('Text','D1','AutoDocstrings','SharedData',value=chunk)
    return 

# ------------- OpenAI docstring generation (yours, updated/new API) -------------
def generate_docstring(code, api_key, model="gpt-4.1-turbo"):
    """
    Generate a Python docstring for the given code using the OpenAI API.
    
    This function sends the provided Python code to the OpenAI language model specified by the `model` parameter,
    prompting it to create a suitable Python docstring. The response contains only the docstring formatted with
    triple double quotes, without any markdown code fences.
    
    Parameters:
        code (str): The Python code snippet for which to generate a docstring.
        api_key (str): The API key used to authenticate with the OpenAI service.
        model (str, optional): The OpenAI model to use for generating the docstring. Defaults to "gpt-4.1-turbo".
    
    Returns:
        str: The generated Python docstring as a string, formatted with triple double quotes.
    """
    client = openai.OpenAI(api_key=api_key)
    # prompt = f"Read the following python code and write a suitable Python docstring for it. Only return the Python docstring (use triple double-quotes).\n\nCODE:\n{code}\n"
    prompt = (
        "Read the following python code and write a suitable Python docstring for it. "
        "Return ONLY the Python docstring using triple double quotes, and DO NOT include "
        "markdown code fences (do not write ```python or ```)."
        f"\n\nCODE:\n{code}\n"
    )
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=256
    )
    return response.choices[0].message.content.strip()

def _add_docstrings_to_chunks(chunks, api_key, model="gpt-4.1-mini"):
    """
    '''
    Generates and adds docstrings to code chunks using an AI model, then posts each updated chunk to a remote collection.
    
    Parameters:
        chunks (list of dict): A list of code chunks, each represented as a dictionary containing at least 'code' and 'type' keys.
        api_key (str): API key used for authentication with the docstring generation service.
        model (str, optional): The AI model identifier to use for generating docstrings. Defaults to "gpt-4.1-mini".
    
    Returns:
        list of dict: The input list with each chunk updated to include a 'docstring' key containing the generated docstring or an error message.
    
    Behavior:
        - Iterates over each chunk in the input list.
        - If the chunk's 'code' is empty or whitespace, sets its 'docstring' to an empty string.
        - For chunks representing classes or functions ('ClassDef', 'FunctionDef', 'AsyncFunctionDef'), attempts to generate a docstring using the specified AI model.
        - Posts each successfully updated chunk to a remote collection via ClientAPI.
        - If docstring generation fails, sets the 'docstring' to an error message.
        - For other chunk types, sets 'docstring' to an
    """
    for chunk in tqdm(chunks):
        if not chunk['code'].strip():
            chunk['docstring'] = ""
            continue
        if chunk['type'] in {'ClassDef', 'FunctionDef', 'AsyncFunctionDef'}:
            try:                
                chunk['docstring'] = generate_docstring(chunk['code'], api_key=api_key, model=model)                
                chunk['mtime'] = pd.Timestamp.utcnow()
                ClientAPI.post_collection('Text','D1','AutoDocstrings','SharedData',
                                          value=chunk)
            except Exception as e:
                chunk['docstring'] = f"Error generating docstring: {e}"
        else:
            chunk['docstring'] = ""
    return chunks
import textwrap

def clean_docstring(docstring, indent=''):
    """
    Insert or replace docstrings in the source code file at the appropriate locations.
    
    Given a file path and a list of code chunks representing classes or functions with their associated docstrings,
    this function reads the source code, identifies the exact position immediately after each complete class or function
    signature (handling multi-line signatures, decorators, and indentation), and inserts or replaces the docstring accordingly.
    
    Parameters:
        filepath (str): The path to the Python source code file to be processed.
        chunks (list of dict): A list of dictionaries, each containing:
            - 'type' (str): The type of the code chunk ('FunctionDef', 'AsyncFunctionDef', or 'ClassDef').
            - 'start_line' (int): The line number where the chunk's definition starts.
            - 'docstring' (str): The docstring to insert for the chunk.
    
    Returns:
        list of str: The modified source code lines with docstrings inserted or replaced.
    """
    import textwrap
    doc = docstring.strip()
    # Remove any surrounding triple quotes (both kinds)
    if (doc.startswith('"""') and doc.endswith('"""')) or (doc.startswith("'''") and doc.endswith("'''")):
        doc = doc[3:-3].strip('\n')
    # Remove single/double quotes at ends
    elif (doc.startswith('"') and doc.endswith('"')) or (doc.startswith("'") and doc.endswith("'")):
        doc = doc[1:-1]
    doc = textwrap.dedent(doc).strip('\n')
    # Escaping internal triple quotes
    if '"""' in doc and "'''" not in doc:
        doc = doc.replace('"""', "'''")
        quote = '"""'
    elif "'''" in doc:
        doc = doc.replace("'''", '"""')
        quote = "'''"
    else:
        quote = '"""'
    block = [f'{indent}{quote}']
    for line in doc.splitlines():
        block.append(f'{indent}{line.rstrip()}')
    block.append(f'{indent}{quote}')
    return '\n'.join(block) + '\n'

# ------------- Reconstruct code with docstrings -------------
def _reconstruct_code_with_docstrings(filepath, chunks):
    """
    Insert/replace ONLY the docstring at the start of function/class body, respecting
    decorators, multi-line signatures, indentation, and not merging or leaking adjacent docstrings.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        code_lines = f.readlines()
    doc_chunks = [
        c for c in chunks
        if c['type'] in ("FunctionDef", "AsyncFunctionDef", "ClassDef") and c['docstring'].strip()
    ]
    doc_chunks.sort(key=lambda c: c['start_line'], reverse=True)

    for chunk in doc_chunks:
        lines = code_lines
        def_idx = chunk['start_line'] - 1
        # Move up for decorators (so we know exactly where signature starts, if needed)
        while def_idx > 0 and lines[def_idx-1].lstrip().startswith('@'):
            def_idx -= 1

        # Find last line of signature (could be multi-line)
        sig_idx = chunk['start_line'] - 1
        while not lines[sig_idx].rstrip().endswith(':'):
            sig_idx += 1
        insert_idx = sig_idx + 1

        # Figure indentation for injected docstring
        for i in range(insert_idx, len(lines)):
            s = lines[i].strip()
            if s and not s.startswith('#'):
                body_indent = lines[i][:len(lines[i]) - len(lines[i].lstrip())]
                break
        else:
            sig_indent = lines[sig_idx][:len(lines[sig_idx]) - len(lines[sig_idx].lstrip())]
            body_indent = sig_indent + '    '

        # Clean/wrap the docstring text
        docstring_block = clean_docstring(chunk['docstring'], body_indent)

        # Remove existing docstring, only if it's the FIRST statement in the body
        first_stmt_idx = None
        for idx in range(insert_idx, len(lines)):
            if lines[idx].strip() == '' or lines[idx].lstrip().startswith('#'):
                continue
            # Check for triple-quoted string (matching expected body indent)
            lstripped = lines[idx].lstrip()
            this_indent = lines[idx][:len(lines[idx]) - len(lstripped)]
            if (lstripped.startswith('"""') or lstripped.startswith("'''")) and this_indent == body_indent:
                # This is a docstring: remove it
                """
                Executes a git command in the specified directory and returns the result.
                
                Parameters:
                    cmd (list of str): The git command and its arguments to execute.
                    cwd (str, optional): The directory in which to run the command. If None, runs in the current directory.
                
                Returns:
                    The result of the command execution as returned by send_command.
                """
                dq = lstripped[:3]
                end_doc = idx
                # Look for end (handles one-liners, multi-liners)
                if lstripped.strip().endswith(dq) and len(lstripped.strip()) > 3:  # """something"""
                    end_doc = idx + 1
                else:
                    # Span lines until end quote
                    """
                    Create a new Git branch and switch to it. If the branch already exists, switch to the existing branch instead.
                    
                    Parameters:
                        branch (str): The name of the branch to create or switch to.
                        cwd (str, optional): The directory in which to run the Git commands. Defaults to None, which runs commands in the current directory.
                    
                    Behavior:
                        - Attempts to create and switch to a new branch named `branch`.
                        - If the branch already exists, switches to the existing branch.
                        - Prints the commands being run for transparency.
                    """
                    end_doc += 1
                    while end_doc < len(lines):
                        if lines[end_doc].strip().endswith(dq):
                            end_doc += 1
                            break
                        end_doc += 1
                lines[idx:end_doc] = docstring_block.splitlines(keepends=True)
                break
            else:
                # No docstring; insert before first real statement
                lines[idx:idx] = docstring_block.splitlines(keepends=True)
                break
        else:
            # No statement: just append to empty body (rare, pass, ...)
            """
            Stages all changes, commits them with the provided message, and pushes the commit to the specified branch on the remote repository.
            
            Parameters:
                branch (str): The name of the branch to push to.
                msg (str): The commit message.
                cwd (str, optional): The working directory where the git commands should be executed. Defaults to None.
            """
            lines[insert_idx:insert_idx] = docstring_block.splitlines(keepends=True)
        code_lines = lines
    return code_lines

# ------------- Git utilities ------------
def run_git(cmd, cwd=None):
    """
    Splits a Python file into smaller chunks using the `chunk_python_code` function and prints a confirmation message.
    
    Parameters:
    pyfile (str): The path to the Python file to be chunked.
    api_key (str): An API key (currently unused in the function).
    
    Returns:
    None
    """
    cmd_str = 'git ' + ' '.join(cmd)
    if cwd:
        cmd_str = f'cd {cwd} && {cmd_str}'
    print(f"Running: {cmd_str}")
    result = send_command(cmd_str)
    return result

def git_create_branch(branch, cwd=None):
    """
    Processes all Python files in the specified folder by applying the chunk_python_file function to each file.
    
    Parameters:
        folder (str or Path): The directory path to search for Python files recursively.
        api_key (str): The API key used for authentication in the chunk_python_file function.
        model (str, optional): The model identifier to be used (default is "gpt-4.1-mini").
    
    This function searches for all `.py` files within the given folder and its subdirectories,
    then processes each file using the chunk_python_file function, displaying a progress bar.
    """
    cmd_create = f"git checkout -b {branch}"
    if cwd:
        cmd_create = f"cd {cwd} && {cmd_create}"
    print(f"Running: {cmd_create}")
    result = send_command(cmd_create)
    if result is False or (isinstance(result, str) and 'already exists' in result):
        print(f"Branch {branch} already exists, switching to it instead.")
        cmd_switch = f"git checkout {branch}"
        if cwd:
            cmd_switch = f"cd {cwd} && {cmd_switch}"
        send_command(cmd_switch)

def git_commit_push(branch, msg, cwd=None):
    run_git(['add', '.'], cwd=cwd)
    run_git(['commit', '-m', msg], cwd=cwd)
    run_git(['push', '-u', 'origin', branch], cwd=cwd)

# ------------- Overall workflow -------------
def chunk_python_folder(folder):
    pyfiles = list(Path(folder).rglob('*.py'))
    for pyfile in tqdm(pyfiles):    
        chunks = chunk_python_code(pyfile)
        print(f"Chunked and saved {pyfile}")

def add_docstrings_to_chunks(api_key, model="gpt-4.1-mini"):
    chunks = ClientAPI.get_collection(
        'Text', 'D1', 'AutoDocstrings', 'SharedData',
        output_dataframe=False,
        query={
            '$or': [
                {'docstring': {'$exists': False}},
                {'docstring': None}
            ]
        }
    )                                      
    chunks = _add_docstrings_to_chunks(chunks, api_key, model)
    return chunks

def reconstruct_code_with_docstrings():
    chunks = ClientAPI.get_collection(
        'Text', 'D1', 'AutoDocstrings', 'SharedData',
        output_dataframe=False,
        query={            
            'docstring': {'$exists': True}
        },
        sort=[('file', 1), ('start_line', 1)]
    )
    files={}
    for chunk in chunks:
        if chunk['file'] not in files:
            files[chunk['file']] = []
        files[chunk['file']].append(chunk)

    for file in files:
        chunks = files[file]
        new_lines = _reconstruct_code_with_docstrings(file,chunks)
        with open(file, "w", encoding='utf-8') as f:
            f.writelines(new_lines)
            
      
if __name__ == "__main__":
          
    import os, sys
    from pathlib import Path
    from SharedData.Logger import Logger
    from SharedData.IO.AutoDocstrings import *
    Logger.connect(__file__)

    # Settings
    BRANCH = "auto/docstrings"
    COMMIT_MSG = "Add AI-generated docstrings"
    api_key = os.environ['OPENAI_API_KEY']
    repo_path = Path(os.environ.get('SOURCE_FOLDER', '.')) / 'SharedData/src' # must be a git repo
    py_source = repo_path / 'SharedData/SharedData.py'  # or set to whatever path to process

    # Git: create branch
    git_create_branch(BRANCH, cwd=repo_path)

    # Chunk, doc, and reconstruct all
    chunk_python_folder(repo_path)

    add_docstrings_to_chunks(api_key)

    reconstruct_code_with_docstrings()

    # Git: commit and push
    git_commit_push(BRANCH, COMMIT_MSG, cwd=repo_path)

    print(f"Done! Review and open a PR for branch {BRANCH}.")
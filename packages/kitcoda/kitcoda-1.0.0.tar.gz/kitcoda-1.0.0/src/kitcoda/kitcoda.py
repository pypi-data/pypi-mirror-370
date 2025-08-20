import os
import sys
import shlex
import io
import contextlib
import re


def evaluate_condition(cond_str, variables):
    """
    cond_str is like "bap x isn't like 3"
    Returns True or False.
    """
    words = tokenize(cond_str)
    # must start with bap
    if words[0] == "bap" and words[2] in ["is", "isn't", "isnt"] and words[3] == "like":
        left  = resolve_value(words[1], variables)
        right = resolve_value(words[4], variables)
        if words[2] == "is":
            return left == right
        else:
            return left != right
    else:
        print(f"[kitcoda error] invalid condition: {cond_str}")
        return False

def tokenize(line):
    """
    Custom tokenizer that splits like tokenize(),
    but handles nested quotes and escaped quotes.
    """
    pattern = r'''
        (                               # Start group
            "(?:\\.|[^"\\])*"           # Double-quoted string, support escapes
            | '(?:\\.|[^'\\])*'         # Single-quoted string, support escapes
            | [^\s"']+                  # Or bareword
        )
    '''
    return [tok.strip() for tok in re.findall(pattern, line, re.VERBOSE)]

def normalize_output(result):
    result = result.strip()
    if (result.startswith('"') and result.endswith('"')) or (result.startswith("'") and result.endswith("'")):
        return result[1:-1]
    return result



def extract_block(lines, start_index):
    block_lines = []
    i = start_index + 1
    while i < len(lines):
        line = lines[i].strip()
        if line == "}":
            break
        block_lines.append(line)
        i += 1
    return block_lines, i

def run_and_capture(line, variables, functions, repl_mode=False):
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        result = run_line(line, variables, functions, repl_mode=repl_mode, as_condition=True)
        if result is not None:
            print(result)
    captured = buffer.getvalue().strip()


    return normalize_output(captured)




def resolve_value(word, variables):
    val = None
    if word in variables:
        val = variables[word][0]
    elif (word.startswith('"') and word.endswith('"')) or (word.startswith("'") and word.endswith("'")):
        val = word[1:-1]
    else:
        val = word
    return val



def strip_comment(line):
    in_quote = False
    result = ""
    for i, char in enumerate(line):
        if char == '"' and (i == 0 or line[i - 1] != "\\"):
            in_quote = not in_quote
        if char == "#" and not in_quote:
            break
        result += char
    return result.strip()



def import_functions_only(path, functions):
    with open(path, "r") as f:
        lines = f.read().splitlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        try:
            line = strip_comment(line)
            words = tokenize(line)
        except ValueError as e:
            print(f"[kitcoda error] line {i+1}: {e}")
            i += 1
            continue

        if "{" in words:
            brace_index = words.index("{")
            funcname = words[1]
            params = words[2:brace_index]
            func_lines = []
            i += 1
            while i < len(lines):
                fline = lines[i].strip()
                if fline == "}":
                    break
                func_lines.append(fline)
                i += 1
            functions[funcname] = {
                "params": params,
                "lines": func_lines
            }
        else:
            pass

        i += 1


def run_line(line, variables, functions, repl_mode=False, as_condition=False):
    if line in ["{", "}", "bop {"]:
        return
    try:
        line = strip_comment(line)

        is_inline_block = "{" in line and line.strip().endswith("}")

        words = tokenize(line)
    except ValueError as e:
        print(f"[kitcoda error]: {e}")
        return

    if not line:
        return
    if not words:
        return
    
    cmd = words[0]
    if cmd == "meow":
        # print something
        printstr = words[1:]
        output = [resolve_value(w, variables) for w in printstr]
        print(" ".join(output), flush=True)

    elif cmd == "sit":
        # set a variable
        if len(words) >= 4 and words[2] == "is":
            varname = words[1]
            value_line = " ".join(words[3:])
            subwords = tokenize(value_line)

            if subwords[0] in ["add", "subtract", "multiply", "divide"]:
                result = run_line(value_line, variables, functions)
                variables[varname] = [result]
            elif subwords[0] == "pounce" or (subwords[0] == "bap" and value_line.endswith("}")):
                result = run_line(value_line, variables, functions)
                variables[varname] = [result if result is not None else ""]
            elif value_line in variables:
                variables[varname] = [variables[value_line][0]]
            else:
                variables[varname] = [resolve_value(value_line, variables)]

    elif cmd == "eat":
        # take input
        if len(words) >= 3 and words[2] == "is":
            varname = words[1]
            prompt = " ".join(words[3:]).strip()
            prompt = resolve_value(prompt, variables)
            value = input(prompt)
            variables[varname] = [value.strip()]

    elif cmd == "bap":
        # if statement
        if words[2] in ["is", "isn't", "isnt"] and words[3] == "like":
            val1 = resolve_value(words[1], variables)
            val2 = resolve_value(words[4], variables)

            baptruth = (val1 == val2) if words[2] == "is" else (val1 != val2)

            if is_inline_block:
                clean = strip_comment(line)
                if "} bop {" in clean:
                    before_else, after_else = clean.split("} bop {", 1)
                    true_block = before_else.split("{", 1)[1].strip()
                    false_block = after_else.rsplit("}", 1)[0].strip()
                else:
                    true_block = clean.split("{", 1)[1].rsplit("}", 1)[0].strip()
                    false_block = None

                if baptruth:
                    block = true_block
                else:
                    block = false_block


            if block:
                if as_condition:
                    result = run_and_capture(block, variables, functions, repl_mode=repl_mode)
                    result = normalize_output(result)
                    return result if result else ("true" if baptruth else "false")
                else:
                    for line in block.split(";"):
                        run_line(line.strip(), variables, functions)
                    return None
            else:
                return "true" if baptruth else "false"

    elif cmd == "pounce":
        # function call
        funcname = words[1]
        args = words[2:]
        if funcname in functions:
            funcdata = functions[funcname]
            params = funcdata["params"]
            lines = funcdata["lines"]

            local_vars = variables.copy()

            for i, param in enumerate(params):
                if i < len(args):
                    val = resolve_value(args[i], variables)
                    local_vars[param] = [val]


            for fline in lines:
                result = run_line(fline, local_vars, functions, repl_mode=True)
                if result is not None and fline.strip().startswith("toss"):
                    return result

    elif cmd == "sip":
        # import a file
        if len(words) >= 2:
            import_path = resolve_value(words[1], variables)
            if os.path.exists(import_path) and import_path.endswith(".kit"):
                import_functions_only(import_path, functions)
            else:
                print(f"[kitcoda error] could not sip file '{import_path}'")

    elif cmd in ["add", "subtract", "multiply", "divide"]:
        if len(words) >= 4 and words[2] == "with":
            num1_raw = resolve_value(words[1], variables)
            num2_raw = resolve_value(words[3], variables)

            # safeguard: default to 0 if missing/empty
            if num1_raw is None or str(num1_raw).strip() == "":
                num1_raw = 0
            if num2_raw is None or str(num2_raw).strip() == "":
                num2_raw = 0

            try:
                num1 = int(num1_raw)
                num2 = int(num2_raw)
            except ValueError:
                print(f"[kitcoda error] cannot convert to number: '{num1_raw}', '{num2_raw}'")
                return ""

            if cmd == "add":
                result = num1 + num2
            elif cmd == "subtract":
                result = num1 - num2
            elif cmd == "multiply":
                result = num1 * num2
            elif cmd == "divide":
                result = num1 / num2
            return str(result)

        
    elif cmd == "nap":
        # exit the program
        exit()

    elif cmd == "spin":
        # loops (while or if loops)
        block = []

        if words[1].isdigit():
            count = int(words[1])
            if "{" in line and line.strip().endswith("}"):
                inner = line[line.index("{")+1:line.rindex("}")].strip()
                block = [inner]
            else:
                while True:
                    block_line = input("... ").strip()
                    if block_line == "}":
                        break
                    block.append(block_line)
            for _ in range(count):
                for b in block:
                    run_line(b, variables, functions, repl_mode=repl_mode)

        elif words[1] == "while":
            match = re.search(r"while\s+(.*?)\s*\{", line)
            cond = match.group(1).strip() if match else None
            if cond is None:
                print("[kitcoda error] Invalid spin while syntax.")
                return

            while True:
                block_line = input("... ").strip()
                if block_line == "}":
                    break
                block.append(block_line)

            while evaluate_condition(cond, variables):
                for b in block:
                    run_line(b, variables, functions, repl_mode=repl_mode)

    elif cmd == "toss":
        # toss only works inside a function
        if len(words) > 1:
            value_str = " ".join(words[1:])
            result = resolve_value(value_str, variables)
            return result
        else:
            return ""


    else:
        print("Invalid command.")
    

def compile():
    i = 0
    variables = {}
    functions = {}
    lines = []
    while True:
        line = input(":3 ")
        lines.append(line)
        try:
            line = strip_comment(line)
            words = tokenize(line)
        except ValueError as e:
            print(f"[kitcoda error] line {i+1}: {e}")
            i += 1
            continue

        if not words:
            i += 1
            continue

        cmd = words[0].lower()

        if cmd == "purr":
            if "{" in words:
                brace_index = words.index("{")
                funcname = words[1]
                params = words[2:brace_index]
                func_lines = []
                while True:
                    fline = input("... ").strip()
                    if fline == "}":
                        break
                    func_lines.append(fline)
                functions[funcname] = {
                    "params": params,
                    "lines": func_lines
                }
        elif cmd == "bap":
            # if statements are bap, else statements are bop
            if "{" in line and line.strip().endswith("}"):
                result = run_line(line, variables, functions)
                if result is not None and result != "":
                    print(result)
                i += 1
                continue

            if words[2] in ["is", "isn't", "isnt"] and words[3] == "like" and words[5] == "{":
                val1 = resolve_value(words[1], variables)
                val2 = resolve_value(words[4], variables)
                baptruth = (val1 == val2) if words[2] == "is" else (val1 != val2)

                block_lines = []
                else_lines = []
                collecting_else = False

                while True:
                    block_line = input("... ").strip()
                    if block_line == "}":
                        next_line = input("... ").strip()
                        if next_line == "bop {":
                            collecting_else = True
                            continue
                        else:
                            break
                    elif block_line == "} bop {":
                        collecting_else = True
                        continue
                    elif collecting_else:
                        else_lines.append(block_line)
                    else:
                        block_lines.append(block_line)

                chosen_block = block_lines if baptruth else else_lines
                for bl in chosen_block:
                    result = run_line(bl, variables, functions)
                    if result is not None and result != "":
                        print(result)
            else:
                print(f"[kitcoda error] Invalid syntax: {line}")
        else:
            result = run_line(line, variables, functions, repl_mode=True)
            if result is not None and result != "":
                print(result)

        i += 1


def interpret(lines):
    i = 0
    variables = {}
    functions = {}



    while i < len(lines):
        line = lines[i]
        try:
            line = strip_comment(line)
            words = tokenize(line)
        except ValueError as e:
            print(f"[kitcoda error] line {i+1}: {e}")
            i += 1
            continue

        if not words:
            i += 1
            continue

        cmd = words[0]

        if cmd == "purr":
            # function definition
            if "{" in words:
                brace_index = words.index("{")
                funcname = words[1]
                params = words[2:brace_index]
                func_lines = []
                i += 1
                while i < len(lines):
                    fline = lines[i].strip()
                    if fline == "}":
                        break
                    func_lines.append(fline)
                    i += 1
                functions[funcname] = {
                    "params": params,
                    "lines": func_lines
                }


        elif cmd == "bap":
            if words[2] in ["is", "isn't", "isnt"] and words[3] == "like":
                val1 = resolve_value(words[1], variables)
                val2 = resolve_value(words[4], variables)
                baptruth = (val1 == val2) if words[2] == "is" else (val1 != val2)

                if "{" in line and line.strip().endswith("}"):
                    inner = line[line.index("{")+1:line.rindex("}")].strip()
                    if baptruth:
                        run_line(inner, variables, functions)
                else:
                    i += 1
                    block_lines = []
                    else_lines = []
                    collecting_else = False

                    while i < len(lines):
                        block_line = lines[i].strip()

                        if block_line == "}":
                            # check if next line starts an else block
                            if i + 1 < len(lines) and lines[i + 1].strip() == "bop {":
                                collecting_else = True
                                i += 2  # skip the "}" and the "bop {" only
                                continue
                            else:
                                break

                        if collecting_else:
                            else_lines.append(block_line)
                        else:
                            block_lines.append(block_line)

                        i += 1


                    chosen_block = block_lines if baptruth else else_lines

                    for bl in chosen_block:
                        run_line(bl, variables, functions)

                    continue
        elif cmd == "spin" and len(words) >= 2 and words[1] == "while":
            # spin while loop
            match = re.search(r"while\s+(.*?)\s*\{", line)
            cond = match.group(1).strip() if match else None
            if cond is None:
                print("[kitcoda error] Invalid spin while syntax.")
                i += 1
                continue

            block_lines = []
            i += 1
            while i < len(lines) and lines[i].strip() != "}":
                block_lines.append(lines[i].strip())
                i += 1
            i += 1

            while evaluate_condition(cond, variables):
                for bl in block_lines:
                    run_line(bl, variables, functions)
            continue

        elif cmd == "spin" and words[1].isdigit():
            count = int(words[1])
            block_lines = []
            if "{" in line and line.strip().endswith("}"):
                # inline form
                inner = line[line.index("{")+1:line.rindex("}")].strip()
                block_lines = [inner]
            else:
                i += 1
                while i < len(lines) and lines[i].strip() != "}":
                    block_lines.append(lines[i].strip())
                    i += 1
                i += 1  # skip the closing }
            for _ in range(count):
                for bl in block_lines:
                    run_line(bl, variables, functions)
            continue






        else:
            run_line(line, variables, functions, repl_mode=False)

        i += 1
        
def main():
    if len(sys.argv) > 1:
        file = sys.argv[1]
        if os.path.exists(file) and file.endswith(".kit"):
            dir = file
        else:
            print("Invalid directory.")
            exit()
    else:
        compile()

    with open(dir, "r") as d:
        filecontents = d.read()
    if not filecontents.strip():
        print("File is empty.")
        exit()

    lines = filecontents.splitlines()
    interpret(lines)

main()
from lark import Lark, Tree, Token
from lark.exceptions import UnexpectedInput, UnexpectedEOF
from pathlib import Path

import sys
import json

RUN_LOCAL = False

class StartError(Exception):
    pass

compilerPass = 0
buildingSymbolTable = True
found_return = False
returnType = None

imports = []  # the start modules that are to be imported in the final compile python file as python imports from /lib
types = ["number", "text", "null", "void"]  # all defined types
# all defined functions, including built-in constructors, user defined ones (are added during compilation), and modules
functions = {
    "null":         {"name": "_null", "return_type": "*", "args": []},
    "number":       {"name": "number", "return_type": "number", "args": ["*"]},
    "text":         {"name": "text", "return_type": "text", "args": ["*"]},
    "char":         {"name": "_char_at", "return_type": "text", "args": ["text", "number"]},
    "print":        {"name": "_print", "return_type": "null", "args": ["**"]},
    "print_raw":    {"name": "_print_raw", "return_type": "null", "args": ["**"]},
    "input_number": {"name": "_input_number", "return_type": "number", "args": []},
    "input_text":   {"name": "_input_text", "return_type": "text", "args": []},
    "len":          {"name": "_len", "return_type": "number", "args": ["*"]},
    "text_len":     {"name": "_text_len", "return_type": "number", "args": ["text"]},
    "random":       {"name": "_random", "return_type": "number", "args": ["number"]},
    "key":          {"name": "_key", "return_type": "number", "args": ["text"]},
    "sleep":        {"name": "_sleep", "return_type": "null", "args": ["number"]},
    "+":            {"name": "_add", "return_type": "number", "args": ["number", "number"]},
    "-":            {"name": "_sub", "return_type": "number", "args": ["number", "number"]},
    "++":           {"name": "_append", "return_type": "text", "args": ["text", "text"]},
    "*":            {"name": "_mul", "return_type": "number", "args": ["number", "number"]},
    "/":            {"name": "_div", "return_type": "number", "args": ["number", "number"]},
    "%":            {"name": "_mod", "return_type": "number", "args": ["number", "number"]},
    "^":            {"name": "_pow", "return_type": "number", "args": ["number", "number"]},
    "==":           {"name": "_eql_val", "return_type": "number", "args": ["*", "*"]},
    "===":          {"name": "_eql_ref", "return_type": "number", "args": ["*", "*"]},
    ">":            {"name": "_gt", "return_type": "number", "args": ["number", "number"]},
    "<":            {"name": "_lt", "return_type": "number", "args": ["number", "number"]},
    ">=":           {"name": "_gte", "return_type": "number", "args": ["number", "number"]},
    "<=":           {"name": "_lte", "return_type": "number", "args": ["number", "number"]},
    "&":            {"name": "_and", "return_type": "number", "args": ["number", "number"]},
    "|":            {"name": "_or", "return_type": "number", "args": ["number", "number"]},
    "!":            {"name": "_not", "return_type": "number", "args": ["number"]}
}

variables = {}  # a dict of defined variables and functions with their name as key and their type as value {name:type}
symbols = {}  # the symbol table, a dict of defined variables and functions with their name as key and their type as value {name:type}
types_to_check = {}  # filled with all variables that are defined of which the type is not known yet, type must be known after complete compilation.
functions_to_check = {}  # same for functions

event_code = ""  # used to build the "when" blocks
parsing_event = False
event_count = 0

def get(t, data):
    for c in t.children:
        if type(c) == Tree and c.data == data:
            return c
    return None

def val(t, data):
    o = get(t, data)
    if o is None:
        return None
    else:
        if data == "text":
            return o.children[0].value
        else:
            return o.children[0].value.lower()

def setter(s):
    return s.replace("_get(", "_set(", 1)

def is_int(s):
    try:
        i = int(s)
        return i >= 0
    except ValueError:
        return False

def symbol_type(line, symbol):
    # First check if the symbol is in the symbol table (function or var)
    if is_int(symbol):
        return "number"

    if symbol in symbols:
        return symbols[symbol]

    if "." not in symbol:  # the symbol is atomic and does not exist so return None
        return None

    parent_symbol = symbol.rsplit(".", 1)[0]
    child_symbol = symbol.rsplit(".", 1)[1]

    # Recursively retrieve the parent symbol type
    parent_type = symbol_type(line, parent_symbol)
    
    # if we found a parent symbol type, we need to reconstruct the symbol and then check if it perhaps now exists in the symbol table
    if parent_type is None:  
        return None
    else:
        symbol = parent_type + "." + child_symbol
        wildcard = parent_type + ".*"
        if symbol in symbols:
            return symbols[symbol]
        elif wildcard in symbols:  # only accept integers as index for indexable types
            return symbols[wildcard]
        else:
            return None

def to_symbol(t, state, indent, scope, namespace):
    result = ""
    if type(t) == Tree:
        if t.data == "variable":  # variable Tree, so its bracketed
            if val(t, "name") is not None:
                if scope != "expression":
                    name = val(t, "name")
                    result = namespace + name
                else:
                    result = "*"
            else:
                if get(t, "expression") is not None:  # dealing with indexable
                    key = to_symbol(get(t, "expression"), state, "", scope, namespace)
                else:
                    key = val(t, "attr")
                result = to_symbol(get(t, "variable"), state, "", scope, namespace) + "." + key

        elif t.data == "expression":  # just relay to the next Tree object
            result += to_symbol(t.children[0], state, indent, "expression", namespace)

        elif t.data == "argument":  # just relay to the next Tree object
            result += to_symbol(t.children[0], state, indent, scope, namespace)

        elif t.data == "right_hand" or t.data == "return_expression":  # just relay to the next Tree object
            result += to_symbol(t.children[0], state, indent, scope, namespace)

        elif t.data == "function_call":
            if scope == "expression":  # in an expression the function simple means "any"
                result = "*"
            else:  # outside an expression we need to return the variable symbol and function name
                function = val(t, "function") if val(t, "function") is not None else val(t, "operator")
                if get(t, "type") is not None:
                    result = val(t, "type") + "." + function
                else:
                    result = function

        elif t.data == "constant":  # just return the token value
            if scope == "expression":
                if get(t, "number") is not None:
                    result = val(t, "number")
                elif get(t, "text") is not None:
                    result = val(t, "text")[1:-1]
                elif get(t, "null") is not None:
                    result = "null"
            else:
                if get(t, "number") is not None:
                    result = "number"
                elif get(t, "text") is not None:
                    result = "text"
                elif get(t, "null") is not None:
                    result = "null"
    # it is a token, simply return the token value (for now return nothing, we deal with all tokens in the Tree parser)
    elif type(t) == Token:
        return ""

    return result

def parse_arguments(line, t, state, _, scope, namespace, function):
    result = []
    arg_count = 0
    for cmd in t.children:
        if type(cmd) == Tree and cmd.data == "argument":
            if arg_count >= len(functions[function]["args"]):
                raise StartError(f"ERROR in line {line}: Too many parameters in function call <{function}>, defined as <{functions[function]}>.")

            result.append(to_python(cmd, state, "", scope, namespace))
            if functions[function]["args"][0] != "**":  # only check types and nr of arguments for functions with types: exclude print functions and constructors (not known in advance)
                arg_symbol = to_symbol(cmd, state, "", scope, namespace)
                arg_type = symbol_type(line, arg_symbol)
                param_type = functions[function]["args"][arg_count]

                if (arg_type != param_type
                        and param_type != "*"
                        and arg_type != "*"
                        and not (param_type[1:] == arg_type and param_type[0] == "*")):
                    raise StartError(f"ERROR in line {line}: Type mismatch <{arg_type}> while <{param_type}> is expected, in function call <{function}> parameter <{arg_count}>.")

            if not (functions[function]["args"][0][0] == "*" and len(functions[function]["args"][0]) > 1):  # only count args if the function does not accept a dynamic nr of arguments
                arg_count += 1

    if (function not in types
            and arg_count < len(functions[function]["args"])
            and not (functions[function]["args"][0][0] == "*" and len(functions[function]["args"][0]) > 1)):
        raise StartError(f"ERROR in line {line}: Not enough parameters in function call <{function}>, defined as <{functions[function]}>.")

    return ', '.join(result)

def load_package(name):
    # Load package
    print(f"Importing functions from package: {name}")
    try:
        # import the .lib file which contains the start typing for the associated python file
        with open("lib/" + name + ".lib", "r") as file:
            package = file.read()

        imported_functions = json.loads(package)

        # add the lib to the defined functions
        functions.update(imported_functions)
        # update the symbol table
        for f in imported_functions:
            symbols[f] = imported_functions[f]["return_type"]

        # import the python file
        imports.append("import lib." + name + " as " + name)
    except Exception as _:
        raise StartError("ERROR loading imported package " + "lib/" + name + ".lib")
    return None

def to_python(t, state, indent, scope, namespace):
    global found_return
    global returnType
    global event_code
    global parsing_event
    global event_count

    result = ""
    if type(t) == Token:  # it is a token, simply return the token value (for now return nothing, we deal with all tokens in the Tree parser)
        return ""
    if type(t) != Tree:
        return ""

    line = t.meta.line
    if t.data == "import":
        if compilerPass == 0 and buildingSymbolTable:
            load_package(val(t, "package"))

    elif t.data == "type_declaration":
        if compilerPass != 0:
            return ""

        type_dec = val(t, "type")

        if buildingSymbolTable:
            if type_dec not in symbols:
                types.append(type_dec)  # define the type
                functions[type_dec] = {"name": type_dec, "return_type": type_dec, "args": []}  # define the constructor function with no args
                symbols[type_dec] = type_dec  # Add the constructor to the symbol table
            else:
                raise StartError(f"ERROR in line {line}: Symbol <{type_dec}> already defined when trying to define a type.")

        result = (f"\n\n{indent}class {type_dec}(start):"
                  f"\n{indent}\tdef __init__(self, *args):")
        if get(t, "indexable") is not None:  # if it is a indexable type def, parse the indexable notation and do all that here
            indexed = get(t, "indexable")

            if buildingSymbolTable:
                functions[type_dec]["args"].append("*" + val(indexed, "type"))
                variables[type_dec + ".*"] = val(indexed, "type")
                symbols[type_dec + ".*"] = val(indexed, "type")

            if val(indexed, "length") == "*":  # no length. so we need to configure this class as a "variable length" (set) type.
                variables[type_dec + ".**"] = val(indexed, "type")
                symbols[type_dec + ".**"] = val(indexed, "type")
                class_indent, inner_indent = indent + "\t\t", indent + "\t\t\t"
                result += (f"\n{class_indent}self.indexLength =- 1"
                           f"\n{class_indent}for i, arg in enumerate(args):"
                           f"\n{inner_indent}self.__dict__[str(i)] = arg")
            else:
                length = val(indexed, "length")
                class_indent, inner_indent = indent + "\t\t", indent + "\t\t\t"
                result += (f"\n{class_indent}self.indexLength = {length}"
                           f"\n{class_indent}for i in range(0, self.indexLength):"
                           f"\n{inner_indent}self.__dict__[str(i)] = args[i] if len(args) > i else start()")

        # continue with the rest of the type def, in case of indexable, only the functions if any as per the grammar, and parse the content of the code block using the current type"s scope
        arg_count = 0
        for cmd in t.children:
            if type(cmd) == Tree:
                if get(cmd, "variable_declaration") is not None:
                    result += to_python(cmd, str(arg_count), indent + "\t\t", "type", type_dec + ".")
                    arg_count += 1
                elif get(cmd, "function_declaration") is not None:
                    result += to_python(cmd, state, indent + "\t", "type", type_dec + ".")

    elif t.data == "function_declaration":
        if compilerPass == 0:
            function = namespace + val(t, "name")
            returnType = val(t, "type")
            if returnType is None:  # if the return type is not specified we assume the function does not return anything so its a void return type
                returnType = "void"

            found_return = False  # flag so we know if we found a return value or not later in teh oarse Tree (bit ugly, to use global flag for this)
            if buildingSymbolTable:
                if function not in symbols:
                    functions[function] = {"name": val(t, "name"), "return_type": returnType, "args": []}
                    symbols[function] = returnType
                else:
                    raise StartError(f"ERROR in line {line}: Symbol <{function}> already defined when trying to define a function.")

                if returnType not in types:  # If the type is not found yet, then make sure to check after the entire compilation that the type does exist
                    types_to_check[function] = (returnType, line)

            result = (f"\n\n{indent}def {val(t, 'name')}({'self, ' if scope != '' else ''}*args):"
                      f"\n{indent}\tlocal_vars = {{}}")
            arg_count = 0
            for cmd in t.children:
                if type(cmd) == Tree and (get(cmd, "argument_declaration") or get(cmd, "variable_declaration")):  # process the arguments and variables
                    result += to_python(cmd, str(arg_count), indent + "\t", "function", function + ".")  # set the scope to function
                    arg_count += 1
                elif not buildingSymbolTable:
                    result += to_python(cmd, returnType, indent + "\t", "function", function + ".")  # set the scope to function and pass the return type as state so that the return statement can check for the correct type

            if not found_return and not buildingSymbolTable:
                if returnType == "void":
                    raise StartError(f"ERROR in line {line}: Function <{function}> misses a return statement.")
                else:
                    raise StartError(f"ERROR in line {line}: Function <{function}> misses return statement and should return type <{returnType}>.")

    elif t.data == "return":
        return_expression = to_python(get(t, "return_expression"), state, indent, scope, namespace)
        if return_expression != "" and state != "void":  # This means we found a return expression and we need one so parse it and check types
            return_symbol = to_symbol(get(t, "return_expression"), state, "", scope, namespace)
            if symbol_type(line, return_symbol) != state:
                raise StartError(f"ERROR in line {line}: Type mismatch in function <{namespace[0:-1]}>, should return type <{returnType}> but instead returns <{symbol_type(line, return_symbol)}>.")
            else:
                result = f"\n{indent}return {return_expression}"
                found_return = True

        elif return_expression == "" and state != "void":  # This means we found no expression but we do need one, so raise an error
            raise StartError(f"ERROR in line {line}: Function <{namespace[0:-1]}>, should return type <{returnType}> but instead returns nothing.")
        elif return_expression != "" and state == "void":  # This means we found an expresswion but we dont need one, so raise an error
            raise StartError(f"ERROR in line {line}: Function <{namespace[0:-1]}> should not return a value as it is defined without a return type.")
        else:  # we found only a return and we need that
            result = f"\n{indent}return"
            found_return = True

    elif t.data == "instruction":
        result += to_python(t.children[0], state, indent, scope, namespace)

    elif t.data == "variable_declaration" or t.data == "argument_declaration":
        # ignore this the first pass in the global scope to process imports and type and function definitions only
        if compilerPass == 1 or (compilerPass == 0 and scope != ""):
            type_dec = val(t, "type")
            name = val(t, "name")
            variable = namespace + name
            if buildingSymbolTable or compilerPass == 1:
                if variable not in symbols:
                    variables[variable] = type_dec
                    symbols[variable] = type_dec
                else:
                    raise StartError(f"ERROR in line {line}: Symbol <{variable}> already defined when trying to define a variable.")

                if t.data == "argument_declaration":  # this is an argument, so add the type to the arg list of the function as passed through namespace
                    functions[namespace.rsplit(".", 1)[0]]["args"].append(type_dec)
                if t.data == "variable_declaration" and scope == "type":  # I am parsing type declaration variables, and each of these need to be added to the constructor as argument types
                    functions[namespace.rsplit(".", 1)[0]]["args"].append(type_dec)
                if type_dec not in types:  # If the type is not found yet, then make sure to check after the entire compilation that the type does exist
                    types_to_check[variable] = (type_dec, line)

            # If we are in the global scope (not a function of type constructor) OR this is a normal var def in a function just define it
            if scope == "" or (scope == "function" and t.data == "variable_declaration"):
                result = f"\n{indent}local_vars['{name}'] = start()"
            elif scope == "function":  # this is in a function, and not a var but an arg, so then we need to use the args to fill it.
                result = f"\n{indent}local_vars['{name}'] = args[{state}] if len(args) > {state} else start()"
            elif scope == "type":  # this is in a type constructor
                result = f"\n{indent}self.{name} = args[{state}] if len(args) > {state} else start()"

    elif t.data == "statement":  # pass it on with a newline for the next statememt
        if not buildingSymbolTable and (compilerPass == 1 or (compilerPass == 0 and scope != "")):  # ignore this the first pass in the global scope to process imports and type and function defs only
            result = f"\n{indent}StartError.lineNumber = {line}"
            if not parsing_event:
                result += "\n" + indent + "check_events()"

            result += "\n" + indent + to_python(t.children[0], state, indent, scope, namespace)

    elif t.data == "assignment":
        right_hand_side = to_python(get(t, "right_hand"), state, "", scope, namespace)
        left_hand_side = setter(to_python(get(t, "variable"), state, "", scope, namespace))
        if val(t, "assign_operator") == "=":
            result = f"{left_hand_side} = {right_hand_side}.clone()"
        elif val(t, "assign_operator") == "->":
            result = f"{left_hand_side} = {right_hand_side}"
        elif val(t, "assign_operator") == ":=":
            result = f"{right_hand_side}.copy({left_hand_side})"

        left_symbol = to_symbol(get(t, "variable"), state, "", scope, namespace)
        left_type = symbol_type(line, left_symbol)
        right_symbol = to_symbol(get(t, "right_hand"), state, "", scope, namespace)
        right_type = symbol_type(line, right_symbol)

        if left_type != right_type and right_type != "*":
            raise StartError(f"ERROR in line {line}: Type mismatch <{left_symbol}:{left_type}> with <{right_symbol}:{right_type}>.")

    elif t.data == "right_hand":
        result += to_python(t.children[0], state, indent, scope, namespace)

    elif t.data == "variable":  # variable Tree, so its bracketed
        symbol = to_symbol(t, state, "", scope, namespace)
        if symbol_type(line, symbol) is None:
            raise StartError(f"ERROR in line {line}: Variable <{symbol}> not defined.")

        if val(t, "name") is not None:
            name = val(t, "name")
            if namespace + name not in variables:  # the var does not exist in the current namespace, and class vars in class methods need an explicit ref to the instance in start
                raise StartError(f"ERROR in line {line}: Variable <{name}> not defined.")

            result = f"_get('{name}', local_vars, None)['{name}']"
        else:
            # add coping with . for attr referencing
            if get(t, "expression") is not None:  # dealing with indexable
                expression_symbol = to_symbol(get(t, "expression"), state, "", scope, namespace)
                # irritant
                stripped_symbol_type = symbol_type(line, symbol.replace("." + expression_symbol, ""))
                if symbol_type(line, expression_symbol) != "number" and (stripped_symbol_type + ".**") not in symbols:
                    raise StartError(f"ERROR in line {line}: An index can only be a number.")

                key = to_python(get(t, "expression"), state, "", scope, namespace)
            else:  # dealing with attribute
                key = f"text('{val(t, 'attr')}')"
            result = f"_get(to_key({key}), local_vars, {to_python(get(t, 'variable'), state, '', scope, namespace)})[to_key({key})]"

    elif t.data == "expression":  # just relay to the next Tree object
        result += to_python(t.children[0], state, indent, scope, namespace)

    elif t.data == "function_call":
        # get the function's name
        function = val(t, "function") if val(t, "function") is not None else val(t, "operator")

        symbol = to_symbol(t, state, "", scope, namespace)
        if symbol_type(line, symbol) is None:
            raise StartError(f"ERROR in line {line}: Function <{symbol}> not defined.")

        # check if the call is on a type method
        if get(t, "type") is not None:
            # parse the variable (which checks if it is defined)
            # now retreive the proper function name using the variable"s type (which must be defined because every variable needs a type)
            function = val(t, "type") + "." + function
            # add the function symbol name for checking
            functions_to_check[function] = line

            # continue parsing the arguments, assuming the function is defined or will be defined later if type was not found yet, using the "base" function name
            result = f"{function}(None, {parse_arguments(line, t, state, '', scope, namespace, function)})"
            # IMPORTANT THE NONE MUST BE THERE AS Start ASSUMES you pass the instance yourself but python assumes the first arg is the instance (self) if you call a class method iso instance method
        else:
            # it is not a type method, so it must be a global function, built-in or imported package library.
            if function in functions:  # we know the function, so use the function name (required for imported modules and built in operators etc)
                result = f"{functions[function]['name']}({parse_arguments(line, t, state, '', scope, namespace, function)})"
            else:
                # add the function symbol name for checking, and use the function as is as it must be defined in the code later
                functions_to_check[function] = line
                result = f"{function}({parse_arguments(line, t, state, '', scope, namespace, function)})"

    elif t.data == "constant":  # just return the token value
        if get(t, "number") is not None:
            result = f"number({val(t, 'number')})"
        elif get(t, "text") is not None:
            result = f"text({(val(t, 'text'))})"
        elif get(t, "null") is not None:
            result = "start()"

    elif t.data in ["if_block", "if_else_block", "while_block"]:
        condition = f"{to_python(get(t, 'expression'), state, '', scope, namespace)}"
        block = to_python(get(t, "block"), "while" if t.data == "while_block" else state, indent+"\t", scope, namespace)
        if t.data == "if_block":
            result = f"\n{indent}if {condition}: {block}\n"
        elif t.data == "if_else_block":
            else_block = to_python(get(t, "else_block"), state, indent + "\t", scope, namespace)
            result = (f"\n{indent}if {condition}: {block}"
                      f"\n{indent}else:{else_block}\n")
        elif t.data == "while_block":
            result = f"\n{indent}while {condition}: {block}\n"

    elif t.data == "when_block":  # reset the indentation because all of this code goes into the check_event() function
        if scope == "":
            parsing_event = True
            block = to_python(get(t, 'block'), state, '\t\t', scope, namespace)
            event_code += (f"\ndef event{event_count}():"
                           f"\n\tif {to_python(get(t, 'expression'), state, '', scope, namespace)}: {block}\n")
            parsing_event = False
            result = f"\n{indent}start_events[event{event_count}] = event{event_count}"
            event_count += 1
        else:
            raise StartError(f"ERROR in line {line}: when blocks can only be defined in global scope (events are global).")

    elif t.data == "break":
        if state == "while":
            result = "\n" + indent + "break"
        else:
            raise StartError(f"ERROR in line {line}: break outside a while loop.")
    elif t.data == "exit":
        result = "\n" + indent + "listener.stop()"
        result += "\n" + indent + "exit(0)"
    else:
        for cmd in t.children:
            result += to_python(cmd, state, indent, scope, namespace)
    return result

def compile_start(parse_tree):
    result = ""

    global compilerPass
    global buildingSymbolTable

    buildingSymbolTable = True
    compilerPass = 0

    print("Building symbol table")
    for inst in parse_tree.children:
        to_python(inst, state="", indent="", scope="", namespace="")
    compilerPass = 0

    print("Compiling types and functions")
    buildingSymbolTable = False
    for inst in parse_tree.children:
        result += to_python(inst, state="", indent="", scope="", namespace="")
    result += "\ntry:"

    print("Compiling main")
    compilerPass = 1
    for inst in parse_tree.children:
        result += to_python(inst, state="", indent="\t", scope="", namespace="")

    # add pass for an empty file
    if len(result.split("try:\n")) <= 1:
        result += "\n\tpass"
    result += "\nexcept Exception as e:\n\tprint('Start runtime error in line '+str(StartError.lineNumber)+': ',e)"
    return result + "\nfinally:\n\tlistener.stop()\n"

def compile_source(file_name):
    with open(file_name, "r") as file:
        # Read the entire contents of the file into a string
        source = file.readlines()
    # check if there are imports
    for line in source:
        if line.strip().startswith("include"):
            include_file = line.strip()[7:].strip() + ".start"
            print("Including file:" + include_file)
            # Add the include sourcefile to this source recursively
            source = compile_source(include_file) + source

    return source + ["\n"]  # make sure that every file at least ends with an enter

def main(file_name):
    try:
        try:
            with open(Path(__file__).parent / Path('start_grammar.ebnf'), 'r') as file:
                # Read the entire contents of the file into a string
                grammar = file.read()
            source = "".join(compile_source(file_name))
        except Exception as e:
            print(e)
            raise StartError(f"ERROR opening grammar <start_grammar.ebnf> or source file <{file_name}>")

        try:
            parser = Lark(grammar, propagate_positions=True)  # The parser matters for ambiguity and there are no guarentees
            parse_tree = parser.parse(source)
        except UnexpectedEOF as _:
            raise StartError("Syntax Error end missing in start-end block")
        except UnexpectedInput as e:
            # give a different error if an end is missing
            if "END" in str(e):
                raise StartError(f"Syntax Error end missing before line {e.line} in a start-end block\nor\nSyntax Error in line {e.line}: \n{e._context}")
            raise StartError(f"Syntax Error in line {e.line}: \n{e._context}")

        # populate the symbol table with the built-in functions as well
        for f in functions:
            symbols[f] = functions[f]["return_type"]

        target = (compile_start(parse_tree))

        for t, l in types_to_check.values():
            if t not in types:
                raise StartError(f"ERROR in line {l}: Type <{t}> not defined.")
        for f in functions_to_check:
            if f not in functions:
                raise StartError(f"ERROR in line {functions_to_check[f]}: Function <{f}> not defined.")

        if RUN_LOCAL:
            import_start = "from import_start import *"
        else:
            import_start = "from start_compiler.import_start import *"
        outfile = Path(file_name).stem  # Removes both path and extension    
        f = open(outfile + ".py", "w")

        # replace tabs with space to make the whitespace consistent
        f.write(("\n".join(imports) + "\n" + import_start + "\n" + event_code + "\n" + target).replace("\t", "    "))
        f.close()
    except StartError as e:
        print(e)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: compile.py <source.start>")
        sys.exit(1)

    main(sys.argv[1])

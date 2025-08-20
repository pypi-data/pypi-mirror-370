import random
import string
import time
from pynput import keyboard

# For local testing at absolute import
try:
    from .starttypes import *
except ImportError:
    from starttypes import *

local_vars = {}
start_events = {}
checkingEvents = False


def check_events():
    global checkingEvents
    if checkingEvents:
        return
    checkingEvents = True
    for e in start_events:
        start_events[e]()
    checkingEvents = False

def null_check(*args):
    for arg in args:
        if type(arg) == start:
            raise StartError("null pointer exception. You forgot to instantiate the object .")

def to_key(*args):
    result = ""
    for arg in args:
        result += arg.to_key()
    return result

def is_dynamic(scope):
    if getattr(scope, "indexLength", None) == -1:
        return True

def is_indexable(scope):
    if getattr(scope, "indexLength", None):
        return True

def _set(name, local, scope):
    return _do_get(name, local, scope, True)

def _get(name, local, scope):
    return _do_get(name, local, scope, False)

def _do_get(name, local, scope, setter=False):
    if type(scope) == start:  # we try to find a member of null instance (all initial assignments are start() objects).
        raise StartError("Start runtime error in line " + str(
            StartError.lineNumber) + ": null pointer exception. You forgot to instantiate the object.")

    # local is the local_vars passed from where get is called
    # we are NOT looking in a class instance <scope> so the variable should exist in local_vars (either global or in local_vars of a global function)
    if scope is None:
        if name in local:
            return local
        else:
            raise StartError("variable " + name + " is not defined.")
    else:  # we are in the scope of an instance
        attr = getattr(scope, name, None)
        if attr is None:
            if is_dynamic(scope) and setter == True:
                # not existing but scope is a set so dynamically create it, so it can be set/retrieved.
                setattr(scope, name, None)
                return scope.__dict__
            else:
                # it's not existing as part of the class or instance, and its not a set, so its a variable not found exception
                if is_dynamic(scope):
                    raise StartError("index " + name + " is not defined.")
                elif is_indexable(scope):
                    raise StartError("index out of bounds [" + name + "].")
                else:
                    # this should never happen due to compile time type and symbol checking!
                    raise StartError("attribute " + name + " is not defined.")
        else:
            # It is in the class or instance, se we return the dict here
            if name in scope.__dict__:  # found in instance
                return scope.__dict__
            elif name in type(scope).__dict__:
                return type(scope).__dict__
            else:
                # "this should never happen due to compile time type and symbol checking!"
                raise StartError(name + " is not defined in type:" + type(scope).__name__)

def _null():
    return start()

def _char_at(t, index):
    null_check(t, index)
    return text(t.value[int(index.value):int(index.value + 1)])

def _print_raw(*args):
    r = ""
    for obj in args:
        if (isinstance(obj, start)):
            r += obj.toStr()
    r = ''.join(ch for ch in r if ch in set(string.printable))
    print(r, end="", flush=True)

def _print(*args):
    r = []
    for obj in args:
        if (isinstance(obj, start)):
            r.append(obj.toStrStructured())
    r = ''.join(ch for ch in " ".join(r) if ch in set(string.printable))
    print(r, flush=True)

def _input_number():
    i = input()
    return number(i)

def _input_text():
    i = input()
    return text(i)

def _len(obj):
    null_check(obj)
    return number(len(vars(obj)) - 1) if is_indexable(obj) else number(len(vars(obj)))

def _text_len(t):
    null_check(t)
    return number(len(t.value))

def _random(n):
    null_check(n)
    return number(random.randint(min(0, int(n.value)), max(0, int(n.value))))

def _add(n1, n2):
    null_check(n1, n2)
    return number(n1.value + n2.value)

def _sub(n1, n2):
    null_check(n1, n2)
    return number(n1.value - n2.value)

def _mul(n1, n2):
    null_check(n1, n2)
    return number(n1.value * n2.value)

def _div(n1, n2):
    null_check(n1, n2)
    return number(n1.value / n2.value)

def _mod(n1, n2):
    null_check(n1, n2)
    return number(n1.value % n2.value)

def _pow(n1, n2):
    null_check(n1, n2)
    return number(n1.value ** n2.value)

def _eql_val(n1, n2):
    # null_check(n1,n2)
    return number(n2.toStr() == n1.toStr())

def _eql_ref(n1, n2):
    # null_check(n1,n2)
    return number(n2 is n1)

def _gt(n1, n2):
    null_check(n1, n2)
    return number(n1.value > n2.value)

def _lt(n1, n2):
    null_check(n1, n2)
    return number(n1.value < n2.value)

def _gte(n1, n2):
    null_check(n1, n2)
    return number(n1.value >= n2.value)

def _lte(n1, n2):
    null_check(n1, n2)
    return number(n1.value <= n2.value)

def _and(n1, n2):
    null_check(n1, n2)
    return number(bool(n2.value and n1.value))

def _or(n1, n2):
    null_check(n1, n2)
    return number(bool(n2.value or n1.value))

def _not(n1):
    null_check(n1)
    return number(not n1.value)

def _append(s1, s2):
    null_check(s1, s2)
    return text(s1.value + s2.value)

# key events for pressed keys
pressed_keys = set()

def add_key(key):
    if isinstance(key, keyboard.KeyCode):
        pressed_keys.add(key.char)
    # else:  # TODO: decide what design we want
        # pressed_keys.clear()

def remove_key(key):
    if isinstance(key, keyboard.KeyCode):
        pressed_keys.clear()

listener = keyboard.Listener(on_press=add_key, on_release=remove_key)
listener.daemon = True
listener.start()

def _key(k):
    null_check(k)
    return number(k.value in pressed_keys)

def _sleep(ms):
    null_check(ms)
    time.sleep(ms.value)

# dynamic is safer if the file changes but then IDE does not recognize the namespace.s
# __all__ = list(globals().keys())
__all__ = [
 "keyboard", "start", "number", "text", "StartError",
 "local_vars", "start_events", "checkingEvents", "pressed_keys", "listener",
 "add_key", "check_events", "null_check", "to_key",
 "is_dynamic", "is_indexable",
 "_set", "_get", "_do_get", "_null", "_char_at",
 "_print_raw", "_print", "_input_number", "_input_text",
 "_len", "_text_len", "_random", "_add", "_sub", "_mul",
 "_div", "_mod", "_pow", "_eql_val", "_eql_ref",
 "_gt", "_lt", "_gte", "_lte", "_and", "_or", "_not",
 "_append", "_key", "_sleep"
]

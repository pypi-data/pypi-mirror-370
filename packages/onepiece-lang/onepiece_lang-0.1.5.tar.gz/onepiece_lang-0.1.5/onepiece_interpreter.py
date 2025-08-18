import re
import sys
import click
from typing import List

class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value

class RuntimeError_(Exception):
    pass

def split_args(argstr: str) -> List[str]:
    parts = []
    cur = ''
    depth = 0
    in_str = False
    str_char = ''
    for ch in argstr:
        if in_str:
            cur += ch
            if ch == str_char:
                in_str = False
            continue
        if ch in ('"', "'"):
            in_str = True
            str_char = ch
            cur += ch
            continue
        if ch in '([{':
            depth += 1
            cur += ch
            continue
        if ch in ')]}':
            depth -= 1
            cur += ch
            continue
        if ch == ',' and depth == 0:
            parts.append(cur.strip())
            cur = ''
            continue
        cur += ch
    if cur.strip():
        parts.append(cur.strip())
    return parts

def eval_literal(expr: str):
    expr = expr.strip()
    if expr.startswith('"') and expr.endswith('"') or (expr.startswith("'") and expr.endswith("'")):
        return expr[1:-1]
    if expr.startswith('[') and expr.endswith(']'):
        inner = expr[1:-1].strip()
        if inner == "":
            return []
        parts = split_args(inner)
        return [eval_literal(p) for p in parts]
    if re.match(r'^-?\d+(\.\d+)?$', expr):
        return float(expr) if '.' in expr else int(expr)
    return expr

def call_builtin(obj, meth, args, env):
    if obj == 'Usopp' and meth == 'shoot':
        prefix = "-> "
        print(prefix, *args)
        return None
    if obj == 'Zoro' and meth == 'slice':
        if len(args) < 2:
            raise RuntimeError_("Zoro.slice needs at least (data, start, end?)")
        data = args[0]; start = args[1] if len(args) >= 2 else None; end = args[2] if len(args) >= 3 else None
        if not isinstance(data, (list, str)):
            raise RuntimeError_("Zoro.slice expects list or string")
        return data[start:end] if end is not None else data[start:]
    if obj == 'Luffy' and meth == 'stretch':
        if not args or isinstance(args[0], list):
            raise RuntimeError_("Luffy.stretch expects a single number")
        return int(args[0]) if args else 1
    if obj == 'Chopper' and meth == 'heal':
        if len(args) < 2:
            raise RuntimeError_("Chopper.heal needs (value, Type)")
        val, typename = args[0], args[1]
        if typename == 'Int': return int(val)
        if typename == 'Float': return float(val)
        if typename == 'String': return str(val)
        return val
    if obj == 'Franky' and meth == 'build':
        if not args: raise RuntimeError_("Franky.build requires at least a type name")
        type_name = args[0]
        props = {}
        for a in args[1:]:
            if isinstance(a, str) and '=' in a:
                k, v = a.split('=', 1); props[k.strip()] = v.strip().strip('"').strip("'")
        return {"type": type_name, "built_by": "Franky", "props": props}
    if obj == 'Robin' and meth == 'clone':
        if len(args) < 2:
            raise RuntimeError_("Robin.clone needs (value, n)")
        value, n = args[0], int(args[1]) if len(args) > 1 else 1
        return [value] * n
    if obj == 'Nami' and meth == 'navigate':
        if not args:
            raise RuntimeError_("Nami.navigate requires a condition")
        return bool(args[0])
    if obj == 'Jinbe' and meth == 'stream':
        src = args[0] if args else []
        if isinstance(src, str): return iter(src.split(','))
        if isinstance(src, list): return iter(src)
        return iter([])
    if obj == 'Sanji' and meth == 'cook':
        if len(args) < 2:
            raise RuntimeError_("Sanji.cook needs (dish_name, ingredients)")
        dish_name, ingredients = args[0], args[1]
        if not isinstance(ingredients, list):
            raise RuntimeError_("Sanji.cook expects ingredients as a list")
        return {"dish": dish_name, "ingredients": ingredients, "chef": "Sanji"}
    raise RuntimeError_(f"Unknown builtin or method: {obj}.{meth}")

class OnePieceInterpreter:
    def __init__(self):
        self.global_env = {'vars': {}, 'ships': {}, 'fns': {}}

    def eval_condition(self, expr: str, env):
        expr = expr.strip()
        for op in ['==', '!=', '<=', '>=', '<', '>']:
            if op in expr:
                left, right = [x.strip() for x in expr.split(op)]
                left_val = self.eval_expr(left, env)
                right_val = self.eval_expr(right, env)
                # Convert to numbers if possible
                try:
                    if isinstance(left_val, str) and re.match(r'^-?\d+(\.\d+)?$', left_val):
                        left_val = float(left_val) if '.' in left_val else int(left_val)
                    if isinstance(right_val, str) and re.match(r'^-?\d+(\.\d+)?$', right_val):
                        right_val = float(right_val) if '.' in right_val else int(right_val)
                except (ValueError, TypeError):
                    raise RuntimeError_(f"Invalid types for comparison: {left_val} {op} {right_val}")
                if isinstance(left_val, (int, float)) and isinstance(right_val, (int, float)):
                    if op == '==': return left_val == right_val
                    if op == '!=': return left_val != right_val
                    if op == '<': return left_val < right_val
                    if op == '<=': return left_val <= right_val
                    if op == '>': return left_val > right_val
                    if op == '>=': return left_val >= right_val
                raise RuntimeError_(f"Invalid types for comparison: {left_val} {op} {right_val}")
        return bool(self.eval_expr(expr, env))

    def run(self, script: str):
        lines = script.splitlines()
        processed = [(len(line) - len(line.lstrip(' ')), line.lstrip(' ')) for line in lines if line.strip() != '']
        idx = 0; ast = []
        while idx < len(processed):
            indent, text = processed[idx]
            node, idx = self.parse_block(processed, idx, indent)
            ast.append(node)
        for node in ast:
            self.exec_node(node, self.global_env)

    def parse_block(self, lines, start_idx, curr_indent):
        indent, text = lines[start_idx]
        assert indent == curr_indent
        if text.startswith('ship '):
            m = re.match(r'ship\s+([A-Za-z_][A-Za-z0-9_]*)\s*:', text)
            if not m: raise RuntimeError_("Invalid ship declaration")
            name = m.group(1); body = []; i = start_idx + 1
            while i < len(lines) and lines[i][0] > curr_indent:
                node, i = self.parse_block(lines, i, lines[i][0]); body.append(node)
            return (('ship', name, body), i)
        if text.startswith('fn '):
            m = re.match(r'fn\s+([A-Za-z_][A-Za-z0-9_]*)\s*\((.*?)\)\s*:', text)
            if not m: raise RuntimeError_("Invalid fn declaration")
            name = m.group(1); params = [p.strip() for p in m.group(2).split(',')] if m.group(2).strip() else []
            body = []; i = start_idx + 1
            while i < len(lines) and lines[i][0] > curr_indent:
                node, i = self.parse_block(lines, i, lines[i][0]); body.append(node)
            return (('fn', name, params, body), i)
        if text.startswith('let '):
            m = re.match(r'let\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)', text)
            if not m: raise RuntimeError_("Invalid let statement")
            var, expr = m.group(1), m.group(2).strip(); return (('let', var, expr), start_idx + 1)
        if text.startswith('return '):
            expr = text[len('return '):].strip(); return (('return', expr), start_idx + 1)
        if text.startswith('sail '):
            call = text[len('sail '):].strip(); return (('sail', call), start_idx + 1)
        if text.startswith('for '):
            m = re.match(r'for\s+([A-Za-z_][A-Za-z0-9_]*)\s+in\s+(.+)\s*:', text)
            if not m: raise RuntimeError_("Invalid for statement")
            var, expr = m.group(1), m.group(2).strip(); body = []; i = start_idx + 1
            while i < len(lines) and lines[i][0] > curr_indent:
                node, i = self.parse_block(lines, i, lines[i][0]); body.append(node)
            return (('for', var, expr, body), i)
        if text.startswith('while '):
            m = re.match(r'while\s+(.+)\s*:', text); cond = m.group(1).strip() if m else None
            if not m: raise RuntimeError_("Invalid while statement")
            body = []; i = start_idx + 1
            while i < len(lines) and lines[i][0] > curr_indent:
                node, i = self.parse_block(lines, i, lines[i][0]); body.append(node)
            return (('while', cond, body), i)
        m = re.match(r'([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)\s*\(\s*(.*?)\s*\)\s*:', text)
        if m:
            obj, meth, arg = m.groups(); body = []; i = start_idx + 1
            while i < len(lines) and lines[i][0] > curr_indent:
                node, i = self.parse_block(lines, i, lines[i][0]); body.append(node)
            else_body = []
            if obj == 'Nami' and i < len(lines) and lines[i][1].startswith('else:'):
                j = i + 1
                while j < len(lines) and lines[j][0] > curr_indent:
                    node, j = self.parse_block(lines, j, lines[j][0]); else_body.append(node)
                i = j
            return (('crew_block', obj, meth, arg, body, else_body), i)
        m = re.match(r'([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+)', text)
        if m:
            var, expr = m.group(1), m.group(2).strip()
            return (('assign', var, expr), start_idx + 1)
        return (('expr', text), start_idx + 1)

    def eval_expr(self, expr: str, env):
        expr = expr.strip()
        if expr.startswith('"') and expr.endswith('"') or (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]
        if expr.startswith('[') and expr.endswith(']'):
            inner = expr[1:-1].strip()
            if inner == "": return []
            parts = split_args(inner); return [self.eval_expr(p, env) for p in parts]
        if re.match(r'^-?\d+(\.\d+)?$', expr): 
            return float(expr) if '.' in expr else int(expr)
        if '+' in expr:
            parts = [p.strip() for p in expr.split('+')]
            vals = [self.eval_expr(p, env) for p in parts]
            # Try to convert strings to numbers if they look like numbers
            converted_vals = []
            all_numeric = True
            for v in vals:
                if isinstance(v, str) and re.match(r'^-?\d+(\.\d+)?$', v):
                    converted_vals.append(float(v) if '.' in v else int(v))
                else:
                    converted_vals.append(v)
                    all_numeric = False
            # If all values are numeric, perform addition
            if all_numeric and all(isinstance(v, (int, float)) for v in converted_vals):
                return sum(converted_vals)
            # Otherwise, concatenate as strings
            return ''.join(str(v) for v in vals)
        m = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)\s*\((.*)\)$', expr)
        if m:
            obj, meth, args = m.groups(); args = args.strip()
            arglist = split_args(args) if args else []
            avals = [self.eval_expr(a, env) for a in arglist]
            if obj in env.get('ships', {}) or obj in self.global_env['ships']:
                ship = self.global_env['ships'].get(obj)
                if ship:
                    fn = ship['fns'].get(meth)
                    if fn: return fn(*avals)
            return call_builtin(obj, meth, avals, env)
        m2 = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)\s*\((.*)\)$', expr)
        if m2:
            name, args = m2.groups(); args = args.strip()
            arglist = split_args(args) if args else []
            avals = [self.eval_expr(a, env) for a in arglist]
            fn = env.get('fns', {}).get(name) or self.global_env['fns'].get(name)
            if fn: return fn(*avals)
            raise RuntimeError_(f"Function {name} not found")
        if expr in env.get('vars', {}): return env['vars'][expr]
        if expr in self.global_env['vars']: return self.global_env['vars'][expr]
        if expr == 'True': return True
        if expr == 'False': return False
        if expr == 'None': return None
        return eval_literal(expr)

    def exec_node(self, node, env):
        typ = node[0]
        if typ == 'ship':
            _, name, body = node
            ship = {'fns': {}, 'vars': {}}
            for b in body:
                if b[0] == 'fn':
                    fnname, params, fnbody = b[1], b[2], b[3]
                    def make_fn(fnbody, params):
                        def fn_callable(*args):
                            local = {'vars': {}, 'ships': self.global_env['ships'], 'fns': {}}
                            for i, p in enumerate(params):
                                if p: local['vars'][p] = args[i] if i < len(args) else None
                            try:
                                for n in fnbody: self.exec_node(n, local)
                            except ReturnSignal as r: return r.value
                        return fn_callable
                    ship['fns'][fnname] = make_fn(fnbody, params)
                elif b[0] in ('let', 'assign'):
                    _, var, expr = b
                    val = self.eval_expr(expr, {'vars': ship.get('vars', {}), 'ships': self.global_env['ships']})
                    ship['vars'][var] = val
            self.global_env['ships'][name] = ship
            self.global_env['vars'][name] = name
            return None
        if typ == 'fn':
            _, name, params, body = node
            def make_fn_global(fnbody, params):
                def fn_callable(*args):
                    local = {'vars': {}, 'ships': self.global_env['ships'], 'fns': {}}
                    for i, p in enumerate(params):
                        if p: local['vars'][p] = args[i] if i < len(args) else None
                    try:
                        for n in fnbody: self.exec_node(n, local)
                    except ReturnSignal as r: return r.value
                    return None
                return fn_callable
            self.global_env['fns'][name] = make_fn_global(body, params)
            return None
        if typ == 'let':
            _, var, expr = node
            if var in env.get('vars', {}):
                raise RuntimeError_(f"Variable {var} already declared. Use assignment without 'let'.")
            val = self.eval_expr(expr, {'vars': env.get('vars', {}), 'ships': self.global_env['ships']})
            env.setdefault('vars', {})[var] = val
            return None
        if typ == 'assign':
            _, var, expr = node
            val = self.eval_expr(expr, {'vars': env.get('vars', {}), 'ships': self.global_env['ships']})
            env.setdefault('vars', {})[var] = val
            return None
        if typ == 'return':
            _, expr = node
            val = self.eval_expr(expr, env)
            raise ReturnSignal(val)
        if typ == 'sail':
            _, call = node
            m = re.match(r'([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)\s*\((.*)\)', call)
            if m:
                shipname, fnname, args = m.groups(); arglist = split_args(args) if args.strip() else []
                avals = [self.eval_expr(a, env) for a in arglist]
                ship = self.global_env['ships'].get(shipname)
                if not ship: raise RuntimeError_(f"Ship {shipname} not found")
                fn = ship['fns'].get(fnname)
                if not fn: raise RuntimeError_(f"Function {fnname} not found on ship {shipname}")
                return fn(*avals)
            else:
                m2 = re.match(r'([A-Za-z_][A-Za-z0-9_]*)\s*\((.*)\)', call)
                if m2:
                    name, args = m2.groups(); arglist = split_args(args) if args.strip() else []
                    avals = [self.eval_expr(a, env) for a in arglist]
                    fn = self.global_env['fns'].get(name)
                    if not fn: raise RuntimeError_(f"Function {name} not found")
                    return fn(*avals)
            return None
        if typ == 'for':
            _, var, expr, body = node
            iterable = self.eval_expr(expr, env)
            if not hasattr(iterable, '__iter__'):
                raise RuntimeError_(f"Cannot iterate over {expr}")
            local_env = {'vars': env.get('vars', {}).copy(), 'ships': self.global_env['ships'], 'fns': {}}
            for item in iterable:
                local_env['vars'][var] = item
                for b in body:
                    self.exec_node(b, local_env)
                env['vars'].update(local_env['vars'])
            return None
        if typ == 'while':
            _, cond, body = node
            local_env = {'vars': env.get('vars', {}).copy(), 'ships': self.global_env['ships'], 'fns': {}}
            while True:
                cond_val = self.eval_condition(cond, local_env)
                if not isinstance(cond_val, bool):
                    raise RuntimeError_(f"While condition must evaluate to boolean, got {cond_val}")
                if not cond_val:
                    break
                for b in body:
                    self.exec_node(b, local_env)
                env['vars'].update(local_env['vars'])
            return None
        if typ == 'crew_block':
            _, obj, meth, arg, body, else_body = node
            local_env = {'vars': env.get('vars', {}).copy(), 'ships': self.global_env['ships'], 'fns': {}}
            if obj == 'Luffy' and meth == 'stretch':
                args = split_args(arg) if arg.strip() else []
                avals = [self.eval_expr(a, env) for a in args]
                n = call_builtin('Luffy', 'stretch', avals, env)
                for _ in range(n):
                    for b in body:
                        self.exec_node(b, local_env)
                env['vars'].update(local_env['vars'])
                return None
            if obj == 'Robin' and meth == 'clone':
                args = split_args(arg) if arg.strip() else []
                avals = [self.eval_expr(a, env) for a in args]
                result = call_builtin('Robin', 'clone', avals, env)
                local_env['vars']['clones'] = result
                for b in body:
                    self.exec_node(b, local_env)
                env['vars'].update(local_env['vars'])
                return None
            if obj == 'Nami' and meth == 'navigate':
                args = split_args(arg) if arg.strip() else []
                cond = self.eval_condition(args[0], env) if args else False
                if not isinstance(cond, bool):
                    raise RuntimeError_(f"Nami.navigate condition must be boolean, got {cond}")
                if cond:
                    for b in body:
                        self.exec_node(b, local_env)
                else:
                    for b in else_body:
                        self.exec_node(b, local_env)
                env['vars'].update(local_env['vars'])
                return None
            return None
        if typ == 'expr':
            _, text = node
            m = re.match(r'([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)\s*\((.*)\)', text)
            if m:
                obj, meth, args = m.groups()
                arglist = split_args(args) if args.strip() else []
                avals = [self.eval_expr(a, env) for a in arglist]
                if obj in self.global_env['ships']:
                    ship = self.global_env['ships'][obj]
                    fn = ship['fns'].get(meth)
                    if fn: return fn(*avals)
                return call_builtin(obj, meth, avals, env)
            m2 = re.match(r'([A-Za-z_][A-Za-z0-9_]*)\s*\((.*)\)', text)
            if m2:
                name, args = m2.groups(); arglist = split_args(args) if args.strip() else []
                avals = [self.eval_expr(a, env) for a in arglist]
                fn = env.get('fns', {}).get(name) or self.global_env['fns'].get(name)
                if fn: return fn(*avals)
                raise RuntimeError_(f"Function {name} not found")
            return self.eval_expr(text, env)
        raise RuntimeError_("Unknown node type: " + str(typ))

def run_string(src: str):
    interp = OnePieceInterpreter()
    interp.run(src)

@click.command()
@click.argument("filename", type=click.Path(exists=True))
def main(filename):
    """Run a OnePiece source file."""
    with open(filename, "r") as f:
        code = f.read()
    run_string(code)

if __name__ == "__main__":
    import sys, pathlib
    if len(sys.argv) < 2:
        print("Usage: python onepiece_interpreter.py <file.op>")
        sys.exit(1)
    p = pathlib.Path(sys.argv[1])
    if not p.exists():
        print("File not found:", p); sys.exit(1)
    src = p.read_text(); run_string(src)
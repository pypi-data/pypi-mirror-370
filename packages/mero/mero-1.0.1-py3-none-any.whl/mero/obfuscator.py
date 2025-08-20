import ast
import types
import marshal
import struct
import zlib
import base64

class MeroObfuscator:
    def __init__(self):
        self.obfuscation_level = 5
        self.variable_map = {}
        self.function_map = {}
        self.string_pool = []
        self.control_flow_depth = 3
        
    def obfuscate_python_code(self, source_code):
        try:
            tree = ast.parse(source_code)
            
            for level in range(self.obfuscation_level):
                tree = self._apply_obfuscation_pass(tree, level)
                
            obfuscated_code = self._ast_to_code(tree)
            return self._add_runtime_protection(obfuscated_code)
        except Exception as e:
            raise RuntimeError(f"Obfuscation failed: {e}")
            
    def _apply_obfuscation_pass(self, tree, level):
        transformers = [
            self._obfuscate_names,
            self._obfuscate_strings,
            self._add_dummy_code,
            self._flatten_control_flow,
            self._encrypt_constants
        ]
        
        transformer = transformers[level % len(transformers)]
        return transformer(tree)
        
    def _obfuscate_names(self, tree):
        class NameObfuscator(ast.NodeTransformer):
            def __init__(self, obfuscator):
                self.obfuscator = obfuscator
                
            def visit_Name(self, node):
                if isinstance(node.ctx, (ast.Store, ast.Load)):
                    if node.id not in ['print', '__name__', '__main__']:
                        if node.id not in self.obfuscator.variable_map:
                            self.obfuscator.variable_map[node.id] = self.obfuscator._generate_obfuscated_name()
                        node.id = self.obfuscator.variable_map[node.id]
                return node
                
            def visit_FunctionDef(self, node):
                if node.name not in self.obfuscator.function_map:
                    self.obfuscator.function_map[node.name] = self.obfuscator._generate_obfuscated_name()
                node.name = self.obfuscator.function_map[node.name]
                return self.generic_visit(node)
                
        return NameObfuscator(self).visit(tree)
        
    def _obfuscate_strings(self, tree):
        class StringObfuscator(ast.NodeTransformer):
            def __init__(self, obfuscator):
                self.obfuscator = obfuscator
                
            def visit_Str(self, node):
                if len(node.s) > 1:
                    encoded = self.obfuscator._encode_string(node.s)
                    decode_call = ast.Call(
                        func=ast.Name(id='_decode_str', ctx=ast.Load()),
                        args=[ast.Str(s=encoded)],
                        keywords=[]
                    )
                    return decode_call
                return node
                
        return StringObfuscator(self).visit(tree)
        
    def _add_dummy_code(self, tree):
        class DummyCodeAdder(ast.NodeTransformer):
            def __init__(self, obfuscator):
                self.obfuscator = obfuscator
                
            def visit_FunctionDef(self, node):
                dummy_statements = self.obfuscator._generate_dummy_statements()
                node.body = dummy_statements + node.body
                return self.generic_visit(node)
                
        return DummyCodeAdder(self).visit(tree)
        
    def _flatten_control_flow(self, tree):
        class ControlFlowFlattener(ast.NodeTransformer):
            def __init__(self, obfuscator):
                self.obfuscator = obfuscator
                self.state_var = obfuscator._generate_obfuscated_name()
                
            def visit_If(self, node):
                if len(node.body) > 2:
                    flattened = self.obfuscator._create_state_machine(node, self.state_var)
                    return flattened
                return self.generic_visit(node)
                
        return ControlFlowFlattener(self).visit(tree)
        
    def _encrypt_constants(self, tree):
        class ConstantEncryptor(ast.NodeTransformer):
            def __init__(self, obfuscator):
                self.obfuscator = obfuscator
                
            def visit_Num(self, node):
                if isinstance(node.n, int) and node.n > 10:
                    encrypted = self.obfuscator._encrypt_number(node.n)
                    decrypt_call = ast.Call(
                        func=ast.Name(id='_decrypt_num', ctx=ast.Load()),
                        args=[ast.Num(n=encrypted)],
                        keywords=[]
                    )
                    return decrypt_call
                return node
                
        return ConstantEncryptor(self).visit(tree)
        
    def _generate_obfuscated_name(self):
        import random
        chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        length = random.randint(8, 16)
        name = ''.join(random.choice(chars) for _ in range(length))
        
        hash_val = hash(name) & 0xffffffff
        return f"_{name}_{hash_val:08x}"
        
    def _encode_string(self, s):
        encoded = base64.b64encode(s.encode('utf-8')).decode('ascii')
        key = len(s) % 256
        obfuscated = ''.join(chr((ord(c) + key) % 256) for c in encoded)
        return base64.b64encode(obfuscated.encode('latin-1')).decode('ascii')
        
    def _generate_dummy_statements(self):
        dummy_statements = []
        
        dummy_var1 = self._generate_obfuscated_name()
        dummy_var2 = self._generate_obfuscated_name()
        
        dummy_statements.append(
            ast.Assign(
                targets=[ast.Name(id=dummy_var1, ctx=ast.Store())],
                value=ast.BinOp(
                    left=ast.Num(n=42),
                    op=ast.Mult(),
                    right=ast.Num(n=13)
                )
            )
        )
        
        dummy_statements.append(
            ast.Assign(
                targets=[ast.Name(id=dummy_var2, ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Name(id='len', ctx=ast.Load()),
                    args=[ast.Str(s='dummy_string')],
                    keywords=[]
                )
            )
        )
        
        return dummy_statements
        
    def _create_state_machine(self, if_node, state_var):
        states = []
        current_state = 0
        
        state_assignments = []
        
        state_assignments.append(
            ast.Assign(
                targets=[ast.Name(id=state_var, ctx=ast.Store())],
                value=ast.Num(n=current_state)
            )
        )
        
        while_body = []
        if_conditions = []
        
        for i, stmt in enumerate(if_node.body):
            state_num = i + 1
            condition = ast.Compare(
                left=ast.Name(id=state_var, ctx=ast.Load()),
                ops=[ast.Eq()],
                comparators=[ast.Num(n=state_num)]
            )
            
            body = [
                stmt,
                ast.Assign(
                    targets=[ast.Name(id=state_var, ctx=ast.Store())],
                    value=ast.Num(n=state_num + 1)
                )
            ]
            
            if_conditions.append(ast.If(test=condition, body=body, orelse=[]))
            
        exit_condition = ast.Compare(
            left=ast.Name(id=state_var, ctx=ast.Load()),
            ops=[ast.Gt()],
            comparators=[ast.Num(n=len(if_node.body))]
        )
        
        break_stmt = ast.If(test=exit_condition, body=[ast.Break()], orelse=[])
        while_body = [break_stmt] + if_conditions
        
        while_loop = ast.While(
            test=ast.NameConstant(value=True),
            body=while_body,
            orelse=[]
        )
        
        return ast.Module(body=state_assignments + [while_loop])
        
    def _encrypt_number(self, number):
        key = 0x9e3779b9
        encrypted = number ^ key
        return encrypted
        
    def _ast_to_code(self, tree):
        try:
            import ast
            # Fix line numbers for all nodes
            for node in ast.walk(tree):
                if not hasattr(node, 'lineno'):
                    node.lineno = 1
                if not hasattr(node, 'col_offset'):
                    node.col_offset = 0
            ast.fix_missing_locations(tree)
            
            if hasattr(ast, 'unparse'):
                return ast.unparse(tree)
            else:
                compiled = compile(tree, '<obfuscated>', 'exec')
                return f"exec({repr(marshal.dumps(compiled))})"
        except Exception as e:
            # Return a simple obfuscated version
            return f"""
import base64, marshal
exec(marshal.loads(base64.b64decode(b'dummy_obfuscated_code')))
# Obfuscation error: {str(e)[:50]}
"""
            
    def _add_runtime_protection(self, code):
        protection_code = '''
import base64
import sys
import struct

def _decode_str(encoded):
    decoded = base64.b64decode(encoded.encode('ascii')).decode('latin-1')
    key = len(decoded) % 256
    return ''.join(chr((ord(c) - key) % 256) for c in decoded)

def _decrypt_num(encrypted):
    key = 0x9e3779b9
    return encrypted ^ key

def _runtime_check():
    if hasattr(sys, 'gettrace') and sys.gettrace() is not None:
        sys.exit(1)
    
    frame = sys._getframe()
    if frame.f_back and 'pdb' in str(frame.f_back.f_code):
        sys.exit(1)

_runtime_check()

'''
        return protection_code + code
        
    def create_packed_executable(self, source_code):
        obfuscated = self.obfuscate_python_code(source_code)
        compiled = compile(obfuscated, '<packed>', 'exec')
        marshaled = marshal.dumps(compiled)
        compressed = zlib.compress(marshaled, 9)
        encoded = base64.b64encode(compressed).decode('ascii')
        
        loader_template = '''
import base64
import zlib
import marshal
import sys

def _unpack_and_execute():
    encoded = """{encoded_data}"""
    try:
        compressed = base64.b64decode(encoded)
        marshaled = zlib.decompress(compressed)
        code_obj = marshal.loads(marshaled)
        exec(code_obj, globals())
    except Exception:
        sys.exit(1)

if __name__ == "__main__":
    _unpack_and_execute()
'''
        
        return loader_template.format(encoded_data=encoded)
        
    def obfuscate_bytecode_directly(self, bytecode):
        obfuscated = bytearray(bytecode)
        
        for i in range(len(obfuscated)):
            obfuscated[i] ^= (i * 0x9e) & 0xff
            obfuscated[i] = ((obfuscated[i] << 1) | (obfuscated[i] >> 7)) & 0xff
            
        return bytes(obfuscated)
        
    def create_polymorphic_code(self, source_code, variants=5):
        variants_list = []
        
        for variant in range(variants):
            tree = ast.parse(source_code)
            
            tree = self._add_junk_code(tree, variant)
            tree = self._reorder_functions(tree, variant)
            tree = self._modify_constants(tree, variant)
            
            variant_code = self._ast_to_code(tree)
            variants_list.append(variant_code)
            
        return variants_list
        
    def _add_junk_code(self, tree, variant):
        junk_statements = []
        for i in range(variant + 1):
            junk_var = f"_junk_{variant}_{i}"
            junk_statements.append(
                ast.Assign(
                    targets=[ast.Name(id=junk_var, ctx=ast.Store())],
                    value=ast.BinOp(
                        left=ast.Num(n=i * 17),
                        op=ast.Add(),
                        right=ast.Num(n=variant * 23)
                    )
                )
            )
            
        if hasattr(tree, 'body'):
            tree.body = junk_statements + tree.body
            
        return tree
        
    def _reorder_functions(self, tree, variant):
        if hasattr(tree, 'body'):
            functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
            non_functions = [node for node in tree.body if not isinstance(node, ast.FunctionDef)]
            
            if len(functions) > 1:
                import random
                random.seed(variant)
                random.shuffle(functions)
                
            tree.body = non_functions + functions
            
        return tree
        
    def _modify_constants(self, tree, variant):
        class ConstantModifier(ast.NodeTransformer):
            def __init__(self, variant):
                self.variant = variant
                
            def visit_Num(self, node):
                if isinstance(node.n, int):
                    modifier = self.variant * 7
                    new_value = ast.BinOp(
                        left=ast.Num(n=node.n + modifier),
                        op=ast.Sub(),
                        right=ast.Num(n=modifier)
                    )
                    return new_value
                return node
                
        return ConstantModifier(variant).visit(tree)

import json
from collections import namedtuple
from typing import Any, Dict, List, Union

PARSER_STATUS_TEXT = 0
PARSER_STATUS_EXPRESSION_SIMPLE = 1
PARSER_STATUS_EXPRESSION_COMPLEX = 2

def is_identifier_char(char):
    char_code = ord(char)
    return ((char_code >= 97 and char_code <= 122) or
            (char_code >= 65 and char_code <= 90) or
            (char_code >= 48 and char_code <= 57) or
            char_code == 95)

INTERPOLATION_CHAR = '$'
INTERPOLATION_EXPRESSION_START = '{'
INTERPOLATION_EXPRESSION_END = '}'

def parse_interpolation_impl(template, start, length):
    templates = []
    values = []
    current_template = ''
    current_value = ''
    expression_complex_depth = 0
    status = PARSER_STATUS_TEXT
    end = start + length - 1
    
    i = start
    while i <= end:
        if status == PARSER_STATUS_TEXT:
            next_interpolation_char = template.find(INTERPOLATION_CHAR, i)
            if next_interpolation_char < 0 or next_interpolation_char >= end:
                current_template += template[i:end + 1]
                break
            current_template += template[i:next_interpolation_char]
            next_char = template[next_interpolation_char + 1]
            i = next_interpolation_char
            if next_char == INTERPOLATION_CHAR:
                current_template += INTERPOLATION_CHAR
                i += 1
                continue
            if next_char == INTERPOLATION_EXPRESSION_START:
                templates.append(current_template)
                current_template = ''
                status = PARSER_STATUS_EXPRESSION_COMPLEX
                expression_complex_depth = 1
                i += 1
                continue
            if is_identifier_char(next_char):
                templates.append(current_template)
                current_template = ''
                current_value = next_char
                status = PARSER_STATUS_EXPRESSION_SIMPLE
                i += 1
                continue
            current_template += INTERPOLATION_CHAR
            continue
        
        char = template[i]
        if status == PARSER_STATUS_EXPRESSION_SIMPLE:
            if is_identifier_char(char):
                current_value += char
                i += 1
                continue
            values.append(current_value)
            current_value = ''
            status = PARSER_STATUS_TEXT
            continue
        
        if status == PARSER_STATUS_EXPRESSION_COMPLEX:
            if char == INTERPOLATION_EXPRESSION_START:
                expression_complex_depth += 1
            elif char == INTERPOLATION_EXPRESSION_END:
                expression_complex_depth -= 1
                if expression_complex_depth == 0:
                    values.append(current_value.strip())
                    current_value = ''
                    status = PARSER_STATUS_TEXT
                    i += 1
                    continue
            current_value += char
            i += 1
            continue
    
    if status == PARSER_STATUS_TEXT:
        templates.append(current_template)
    elif status == PARSER_STATUS_EXPRESSION_SIMPLE:
        values.append(current_value)
        templates.append('')
    else:
        raise ValueError('Unexpected end of input')
    
    return {
        'type': 'interpolation',
        'templates': templates,
        'values': values,
    }
    
# 是否为 ArrayBuffer
def is_array_buffer(value: Any) -> bool:
    return isinstance(value, (memoryview, bytearray))

# 是否为 Error
def is_error(value: Any) -> bool:
    return isinstance(value, Exception)


def parse_template(template: str) -> Any:
    if not template:
        return ''
    if template.startswith('='):
        return {
            'type': 'formula',
            'value': template[1:].strip(),
        }
    if template.startswith('$'):
        result = parse_interpolation_impl(template, 1, len(template)-1)
        if len(result['templates']) == 0:
            return result['templates'][0]
        return result        
    return template
# KNOWN_ERRORS = [EvalError, RangeError, ReferenceError, SyntaxError, TypeError, URIError]

# 模板序列号
seq = 0

# 创建模板
class TemplateCompiler:
    def __init__(self, template: Any, options: Dict[str, Any]):
        self.template = template
        self.options = options
        self.params = {}
        self.copyable = []

    # 构建求值
    def build_eval(self, expression: str, type_: str) -> str:
        evaluator = self.options['evaluator']
        if 'evaluator' not in self.params:
            self.params['evaluator'] = evaluator.get('inject',None)
        return evaluator['compile'](expression, type_)

    # 构建字符串
    def build_string(self, str_: str) -> Union[str, bool]:
        parsed = parse_template(str_)
        if isinstance(parsed, str):
            return json.dumps(parsed), False
        if parsed['type'] == 'formula':
            return self.build_eval(parsed['value'], parsed['type']), True
        result = ''
        for i in range(len(parsed['templates'])):
            if parsed['templates'][i]:
                result += (result and '+' or '') + json.dumps(parsed['templates'][i])
            if i < len(parsed['values']):
                if not result:
                    result = '""'
                result += '+' + self.build_eval(parsed['values'][i], parsed['type'])
        return result, True

    # 构建 Error
    def build_error(self, err: Exception) -> str:
        constructor="Error"
        if err.__class__.__name__ == constructor:
            return f'new {constructor}({self.build_string(err.message)[0]})'
        return f'Object.assign(new {constructor}({self.build_string(err.message)[0]}), {{name: {self.build_string(err.name)[0]}}})'

    # 构建数组
    def build_array(self, arr: List[Any]) -> str:
        return f'[{", ".join(self.build_value(v) for v in arr)}]'

    # 构建 ArrayBuffer
    def build_array_buffer(self, buffer: Union[memoryview, bytearray]) -> str:
        self.copyable.append(buffer[:])
        return f'copyable[{len(self.copyable) - 1}][:]'

    # 构建 ArrayBufferView
    def build_array_buffer_view(self, view: memoryview) -> str:
        self.copyable.append(view.tobytes())
        return f'new {view.__class__.__name__}(copyable[{len(self.copyable) - 1}][:])'

    # 构建对象
    def build_object(self, obj: Dict[str, Any]) -> str:
        result = ''
        for key, value in obj.items():
            if result:
                result += ',\n'
            if self.options['objectKeyMode'] == 'ignore':
                result += json.dumps(key)
            else:
                e, is_expression = self.build_string(key)
                if is_expression:
                    result += f'[{e}]'
                else:
                    result += e
            result += ':'
            result += self.build_value(value)
        return '{' + result + '}'

    # 构建值
    def build_value(self, value: Any) -> str:
        if value is None:
            return 'null'
        if value is True:
            return 'true'
        if value is False:
            return 'false'
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, str):
            return self.build_string(value)[0]
        if isinstance(value, Exception):
            return self.build_error(value)
        if isinstance(value, list):
            return self.build_array(value)
        if is_array_buffer(value):
            return self.build_array_buffer(value)
        if isinstance(value, memoryview):
            return self.build_array_buffer_view(value)
        if isinstance(value, dict):
            return self.build_object(value)
        raise ValueError(f'Unsupported value: {type(value)}')

    # 构建模板
    def build(self) -> Any:
        global seq
        source = self.build_value(self.template)
        if self.copyable:
            self.params['copyable'] = self.copyable
        params = list(self.params.items())
        try:
            result = eval(f'lambda context: ({source})')
            result.source = source
            return result
        except Exception as e:
            raise ValueError(f'Failed to compile template: {source}\n{str(e)}')



def template(templates,options={}):
    def compile_template(expression, type):
        if type == 'formula':
            return f'context[{json.dumps(expression)}]'
        elif type == 'interpolation':
            return f"context[{json.dumps(expression)}] ?? ''"
        raise ValueError(f'Unsupported type: {type}')
    opt = {
        'objectKeyMode': 'template',
        'evaluator':{
            'compile':compile_template
        },
        **options
    }
    return TemplateCompiler(templates, opt).build()



if __name__ == "__main__":
    
    message =[1, 1, {'component_load_5_无功功率': [0], 'component_load_5_有功功率': [0], 'time': ['placeholder']}, {'data': {'title': '负荷5功率(kW)', 'traces': [{'name': '有功功率', 'type': 'scatter', 'x': '=time', 'y': '=component_load_5_有功功率'}, {'name': '无功功率', 'type': 'scatter', 'x': '=time', 'y': '=component_load_5_无功功率'}], 'xAxis': {'title': 'time'}, 'yAxis': {'title': '功率(kW)'}}, 'key': '/component_load_5_功率(kW)', 'type': 'plot', 'verb': 'append', 'version': 1}]
    id =message[0]
    
    templates=message[3:]
    
    x= template(templates)
    
    values=[1, 1, {'component_load_5_无功功率': [5.44544554016478], 'component_load_5_有功功率': [16.3363363363363], 'time': ['2021-08-19 09:00:00']}]
    
    print(x)
    
    data= values[2]
    s=x(data)
    
    print(s)
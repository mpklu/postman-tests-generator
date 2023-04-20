# Author: Kun Lu
#         
# Created on 2023-04-17 10:33:20

import json
import sys

# generate utility functions
def gen_utils():
    return '''
// utilities
function nullOrNumber(value) {
    return value === null || typeof value === 'number';      
}

function nullOrString(value) {
    return value === null || typeof value === 'string';      
}

function nullOrObject(value) {
    return value === null || typeof value === 'object';      
}

function nullOrDate(value) {
    if (value === null || typeof value === 'number') {
        if (value !== null) {
            const date = new Date(value);
            pm.expect(date).to.not.be.NaN;
        }  
        return true;
    } else {
        return false;
    }
}
    '''

# generate 200 OK test
def test_status():
    return '''
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});
    '''
def isDateField(key):
    return key.endswith('On') or key.endswith('Date') or key.endswith('Until')

def isNumberField(key):
    return key.endswith('Id') or key.endswith('id') or key.endswith('By') or key.endswith('Amount') or key.endswith('Total')

def generate_test_case(data, name, indentation):
    indentation += '\t'
    test_case = ''
    if isinstance(data, list):
        test_case += f'{indentation}pm.expect({name}).to.be.an("array");\n'
        test_case += f'{indentation}{name}.forEach((obj) => {{\n'   
        if len(data) > 0:
            test_case += generate_test_case(data[0], 'obj', indentation)
        test_case += f'{indentation}}});\n'
    elif isinstance(data, dict):
        for key, value in data.items():            
            if isinstance(value, dict):
                test_case += f'{indentation}pm.test("{name}.{key} is an object", function () {{\n'
                test_case += generate_test_case(value, f'{name}.{key}', indentation)
                test_case += f'{indentation}}});\n'
            elif isinstance(value, list):
                test_case += generate_test_case(value, f'{name}.{key}', indentation)
            else:
                if value is None:
                    if isDateField(key):
                        test_case += f'{indentation}pm.expect({name}.{key}, "{name}.{key} should be a date or null").to.satisfy((value) => {{ return nullOrDate(value); }});\n'
                    elif isNumberField(key):
                        test_case += f'{indentation}pm.expect({name}.{key}, "{name}.{key} should be a number or null").to.satisfy((value) => {{ return nullOrNumber(value); }});\n'  
                    else: # Assume it's an object otherwise
                        test_case += f'{indentation}pm.expect({name}.{key}, "{name}.{key} should be an object or null").to.satisfy((value) => {{ return nullOrObject(value); }});\n'  
                elif isinstance(value, str):
                    test_case += f'{indentation}pm.expect({name}.{key}, "{name}.{key} should be a string or null").to.satisfy((value) => {{ return nullOrString(value); }});\n'
                elif isinstance(value, bool):
                    test_case += f'{indentation}pm.expect({name}.{key}, "{name}.{key} should be a boolean").to.be.a("boolean");\n'
                elif isinstance(value, int):
                    if key == "id":
                        test_case += f'{indentation}pm.expect({name}.{key}).to.be.a("number");\n'
                    elif isDateField(key):
                        test_case += f'{indentation}pm.expect({name}.{key}, "{name}.{key} should be a date or null").to.satisfy((value) => {{ return nullOrDate(value); }});\n'
                    else:
                        test_case += f'{indentation}pm.expect({name}.{key}, "{name}.{key} should be a number or null").to.satisfy((value) => {{ return nullOrNumber(value); }});\n'                
                elif isinstance(value, dict):
                    test_case += f'{indentation}pm.expect({name}.{key}, "{name}.{key} should be an object or null").to.satisfy((value) => {{ return nullOrObject(value); }});\n'
    return test_case

def build_test_cases(data):
    test_case = gen_utils()
    test_case += test_status()
    test_case += f'\npm.test("Each object in the response has the required fields and data types", () => {{\n'
    test_case += '\tconst response = pm.response.json();\n'
    test_case += generate_test_case(data, 'response', '')
    test_case += '});\n'
    return test_case

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python gen_pm_test.py <path/to/response/json/file>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        json_data = json.load(f)

    test_cases = build_test_cases(json_data)
    print(test_cases)

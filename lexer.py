
ATTR_LIST =[
    'LE_OP','GE_OP','EQ_OP','NE_OP','AND_OP','OR_OP',
    'MUL_ASSIGN','DIV_ASSIGN','MOD_ASSIGN','ADD_ASSIGN','SUB_ASSIGN',
    'INT','CHAR','VOID','IF','ELSE','WHILE','FOR','CONTINUE','BREAK','RETURN',
    'ID','CONST','STRING_LITERAL'
]

CATEGORY_LIST = {
    '<=':256,
    '>=':257,
    '==':258,
    '!=':259,
    '&&':260,
    '||':261,
    '*=':262,
    '/=':263,
    '%=':264,
    '+=':265,
    '-=':266,
    'int':267,
    'char':268,
    'void':269,
    'if':270,
    'else':271,
    'while':272,
    'for':273,
    'continue':274,
    'break':275,
    'return':276
}

ID = 277
CONST = 278
STRING_LITERAL =279

current_line = 0
current_row = -1
input_str = []

def getchar():
    global current_row
    global current_line
    current_row += 1
    if current_row == len(input_str[current_line]):
        current_line += 1
        current_row = 0
    if current_line == len(input_str):
        return 'SCANEOF'
    return input_str[current_line][current_row]

def ungetc():
    global current_row
    global current_line
    current_row -= 1
    if current_row < 0:
        current_line -= 1
        current_row = len(input_str[current_line]) - 1
    return input_str[current_line][current_row]

def read_source_file(file):
    global input_str
    with open(file, 'r') as f:
        input_str = f.readlines()

def lexical_error(msg,line=None,row=None):
    if line is None:
        line = current_line + 1
    if row is None:
        row = current_row + 1
    print(str(line)+':'+str(row)+ 'Lexical error: '+msg)

def scanner():
    current_char = getchar()
    if current_char == 'SCANEOF':
        return ('SCANEOF',ord('$'),'')
    while current_char.strip() == '':
        current_char = getchar()
    if current_char.isdigit():
        int_value = 0
        while current_char.isdigit():
            int_value = int_value * 10 + int(current_char)
            current_char = getchar()
        ungetc()
        return (str(int_value),CONST,int_value)
    if current_char.isalpha() or current_char == '_':
        string = ''
        while current_char.isalnum() or current_char == '_':
            string += current_char
            current_char = getchar()
            if current_char == 'SCANEOF':
                break
        ungetc()
        if string in CATEGORY_LIST.keys():
            return (string,CATEGORY_LIST[string],'')
        else:
            return (string,ID,'')
    if current_char == '\"':
        str_literal = ''
        current_char = getchar()
        while current_char != '\"':
            str_literal += current_char
            current_char = getchar()
        return (str_literal,STRING_LITERAL,'')
    if current_char in ['+','-','*','/','%','<','>','=','!']:
        op = current_char
        current_char = getchar()
        if current_char == '=':
            op += current_char
            return (op, CATEGORY_LIST[op],'')
        else :
            ungetc()
            return (op,ord(op),'')
    if current_char in ['&','|']:
        op = current_char
        current_char = getchar()
        if current_char == op:
            op += current_char
            return (op,CATEGORY_LIST[op],'')
        else:
            ungetc()
            return (op,ord(op),'')
    if current_char == "\'":
        current_char = getchar()
        next_char = getchar()
        if next_char != "\'":
            lexical_error("\' can only include a character")
            while next_char !="\'":
                next_char = getchar()
        return (current_char,CONST,'')
    return (current_char,ord(current_char),'')

def main():
    read_source_file('test.c')
    with open('first.txt','w') as f:
        s = '%16s%16s%16s\n' %('STRING','ATTR','OTHER')
        f.write(s)
        while True:
            result = scanner()
            if result[0] == 'SCANEOF':
                break
            if result is not None:
                s = '%16s%16s%16s\n' %(result[0],chr(result[1])if result[1]<256 else ATTR_LIST[result[1]-256],result[2])
                f.write(s)

if __name__ == '__main__':
    main()

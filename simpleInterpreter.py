'''
变量创建/使用 & 加减乘除的简单运算

expr：term((PLUS|MINUS)term)*

term：factor((MUL|DIV)factor)*

factor：INTEGER
'''


def error(msg='警告：错误的输入内容！'):  # 定义提示错误的方法
    raise Exception(msg)  # 抛出异常


class TokenType:
    INTEGER = 1
    STR = 2
    PLUS = 3
    PEQ = 4
    MINUS = 5
    MEQ = 6
    MUL = 7
    MULEQ = 8
    DIV = 9
    DEQ = 10
    ASS = 11
    VAR = 12
    VAL = 13
    LPAREN = 14
    RPAREN = 15
    EOF = 16

    OPERATORS = {"+": PLUS,
                 "+=": PEQ,
                 "-": MINUS,
                 "-=": MEQ,
                 "/": DIV,
                 "/=": DEQ,
                 "*": MUL,
                 "*=": MULEQ,
                 "=": ASS}

    @classmethod
    def toType(cls, token):
        if token in cls.OPERATORS:
            return cls.OPERATORS[token.value]


class Token:  # 定义记号类
    def __init__(self, value_type, value):  # 定义构造方法
        self.value_type = value_type  # 记号中值的类型
        self.value = value  # 记号中的值

    def __str__(self):  # 重写查看记号内容的方法
        return 'Token({value_type},{value})'.format(value_type=self.value_type, value=self.value)

    def __repr__(self):  # 也可以写成 __repr__=__str__
        return self.__str__()


class AST:
    pass


class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right


class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value


class UnaryOp(AST):
    def __init__(self, op, expr):
        self.token = self.op = op
        self.expr = expr


class Lexer:
    def __init__(self, text):
        self.text = text  # 用户输入的表达式
        self.position = 0  # 获取表达式中每一个字符时的位置
        self.current_char = self.text[self.position]

    @classmethod
    def error(cls, msg='警告：错误的输入内容！'):  # 定义提示错误的方法
        raise Exception(msg)  # 抛出异常

    def advance(self):  # 定义获取下一个字符的方法
        self.position += 1  # 获取字符的位置自增
        if self.position >= len(self.text):  # 如果位置到达字符串的末尾
            self.current_char = None  # 设置当前字符为None值
        else:  # 否则
            self.current_char = self.text[self.position]  # 设置当前字符为指定位置的字符

    def skip_whitespace(self):  # 定义跳过空格的方法
        while self.current_char is not None and self.current_char.isspace():  # 如果当前字符不是None值并且当前字符是空格
            self.advance()  # 获取下一个字符

    def string(self):  # 读取一个字符串
        result = ''
        strSymbol = self.current_char
        self.advance()  # skip ' or "
        closed = False
        while self.current_char is not None and \
                not self.current_char.isspace() \
                and self.current_char not in TokenType.OPERATORS:  # 如果当前字符不是None值并且当前字符不是空格且不是运算符号

            if closed:
                self.error()  # 不能在单引号或者双引号后面再写其他字符

            if self.current_char in ('\'', '"'):
                closed = True

            result += self.current_char
            self.advance()  # 获取下一个字符

        if result[-1] != strSymbol:  # 如何最后一个字符不是单引号或者双引号，或者单双混合就报错
            self.error()

        return result[:-1]

    def integer(self):  # 获取多位数字
        result = ''
        while self.current_char is not None and self.current_char.isdigit():  # 如果当前字符不是None值并且当前字符是数字
            result += self.current_char  # 连接数字
            self.advance()  # 获取下一个字符
        return int(result)  # 返回数字

    def variable(self):  # 获取多位数字
        result = ''
        while self.current_char \
                and not self.current_char.isspace() \
                and self.current_char not in ('\'', '"') \
                and self.current_char not in TokenType.OPERATORS:  # 如果当前字符不是None值并且不是空格
            result += self.current_char  # 连接字符
            self.advance()  # 获取下一个字符
        return result

    def operator(self):
        result = ''
        while self.current_char in TokenType.OPERATORS:
            if result and self.current_char != '=':
                return result
            result += self.current_char
            self.advance()
        return result

    def get_next_token(self):  # 定义获取记号的方法
        while self.current_char is not None:  # 如果当前字符不是None值
            current = self.current_char
            if current.isspace():  # 如果当前字符是空格
                self.skip_whitespace()  # 跳过所有空格
                continue

            if current in ('\'', '"'):  # 如果当前字符是字符串
                return Token(TokenType.VAL, self.string())  # 获取完整的字符串创建记号对象并返回

            if current.isdigit():  # 如果当前字符是整数
                return Token(TokenType.VAL, self.integer())  # 获取完整的数字创建记号对象并返回

            if current.isalpha():  # 如果不是字符串但是以字母开头，那就是一个变量
                return Token(TokenType.VAR, self.variable())

            if current == '(':
                self.advance()
                return Token(TokenType.LPAREN, '(')

            if current == ')':
                self.advance()
                return Token(TokenType.RPAREN, ')')

            if current in TokenType.OPERATORS:  # 如果当前字符是运算符号
                operator = self.operator()
                return Token(TokenType.OPERATORS[operator], operator)  # 创建记号对象并返回

            self.error()  # 如果以上都不是，则抛出异常。
        return Token(TokenType.EOF, None)  # 遍历结束返回结束标识创建的记号对象


class Parser:
    def __init__(self, lexer):  # 定义构造方法获取用户输入的表达式
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def _eat(self, *token_types):  # 判断如果记号中的值类型符合运算要求
        if isinstance(token_types[0], dict):
            if self.current_token.value not in token_types[0]:
                error()
            else:
                self.current_token = self.lexer.get_next_token()
        else:
            if self.current_token.value_type not in token_types:
                error()  # 抛出异常
            else:
                self.current_token = self.lexer.get_next_token()

    def _term(self):
        """
        term : factor ((MUL | DIV) factor)*
        """
        result = self._factor()  # 获取第1个整数（factor）
        while self.current_token.value_type in (TokenType.MUL, TokenType.DIV):
            operator = self.current_token
            self._eat(TokenType.OPERATORS)
            result = BinOp(result, operator, self._factor())
        return result

    def _factor(self):
        token = self.current_token
        if token.value_type in (TokenType.VAR, TokenType.VAL):
            self._eat(TokenType.VAR, TokenType.VAL)  # 调用验证方法传入运算要求的类型
            return Num(token)
        elif token.value_type == TokenType.LPAREN:  # 处理括号内表达式
            self._eat(TokenType.LPAREN)  # 验证左括号
            result = self._expr()  # 计算括号内的表达式
            self._eat(TokenType.RPAREN)  # 验证右括号
            return result  # 返回括号内表达式的值
        elif token.value_type in (TokenType.PLUS, TokenType.MINUS):
            self._eat(TokenType.OPERATORS)
            return UnaryOp(token, self._factor())

    def _expr(self):  # 定义验证运算结构并计算结果的方法
        result = self._term()  # 获取第一段乘除或者第一数字
        while self.current_token.value_type in (TokenType.PLUS,
                                                TokenType.PEQ,
                                                TokenType.MINUS,
                                                TokenType.MEQ,
                                                TokenType.MULEQ,
                                                TokenType.DEQ,
                                                TokenType.ASS):
            operator = self.current_token
            self._eat(TokenType.OPERATORS)

            if operator.value_type in (TokenType.PLUS, TokenType.MINUS):
                # 先算term, 也就是先乘除
                result = BinOp(result, operator, self._term())
            else:
                # 如果有赋值操作, 递归完成
                result = BinOp(result, operator, self._expr())

        return result  # 返回计算结果

    def parse(self):
        return self._expr()


class Interpreter:  # 定义解释器类
    VARIABLES = {}  # 变量表

    # 运算算法lambda
    OPERATION = {TokenType.PLUS: lambda a, b: Interpreter.getVal(a) + Interpreter.getVal(b),
                 TokenType.PEQ: lambda a, b: Interpreter.assignToVar(a, Interpreter.getVal(a) + Interpreter.getVal(b)),
                 TokenType.MINUS: lambda a, b: Interpreter.getVal(a) - Interpreter.getVal(b),
                 TokenType.MEQ: lambda a, b: Interpreter.assignToVar(a, Interpreter.getVal(a) - Interpreter.getVal(b)),
                 TokenType.DIV: lambda a, b: Interpreter.getVal(a) / Interpreter.getVal(b),
                 TokenType.DEQ: lambda a, b: Interpreter.assignToVar(a, Interpreter.getVal(a) / Interpreter.getVal(b)),
                 TokenType.MUL: lambda a, b: Interpreter.getVal(a) * Interpreter.getVal(b),
                 TokenType.MULEQ: lambda a, b: Interpreter.assignToVar(a,
                                                                       Interpreter.getVal(a) * Interpreter.getVal(b)),
                 TokenType.ASS: lambda a, b: Interpreter.assignToVar(a, Interpreter.getVal(b))}

    def __init__(self, parser):
        self.parser = parser

    @classmethod
    def assignToVar(cls, var, value):  # 变量赋值
        cls.VARIABLES[var.value] = value
        return value

    @classmethod
    def getVal(cls, token):  # 如果是变量, 就取出它的值。 否则直接返回
        if isinstance(token, Token):
            if token.value_type == TokenType.VAR:
                try:
                    return cls.VARIABLES[token.value]
                except:
                    error(f"变量 {token.value} 不存在！")

            return token.value
        else:
            return token

    def visit(self, node):
        # 获取节点类型名称组成访问器方法名（子类Interpreter中方法的名称）
        method_name = 'visit_' + type(node).__name__
        # 获取访问器对象，找不到访问器时获取“generic_visit”
        try:
            visitor = getattr(self, method_name, self.generic_visit)
            return visitor(node)
        except:
            return node.token.value

    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))

    def visit_BinOp(self, node):  # 访问二元运算符类型节点的方法
        return self.OPERATION[node.token.value_type](self.visit(node.left),
                                                     self.visit(node.right))

    def visit_UnaryOp(self, node):
        op = node.op.value_type
        if op == TokenType.PLUS:
            return self.visit(node.expr)
        elif op == TokenType.MINUS:
            return -self.visit(node.expr)

    def interpret(self):  # 执行解释的方法
        tree = self.parser.parse()  # 获取语法分析器分析后的树对象
        return self.getVal(self.visit(tree))  # 返回访问语法树最终的遍历结果


def main():
    while True:  # 循环获取输入
        try:
            text = input('>>>')  # 获取用户输入
        except EOFError:  # 捕获到末端错误时退出
            break
        if not text:  # 如果未输入时继续提示输入
            continue
        lexer = Lexer(text)
        parser = Parser(lexer)
        interpreter = Interpreter(parser)  # 实例化解释器对象
        result = interpreter.interpret()  # 执行运算方法获取运算结果
        if result is not None:
            print(result)  #


if __name__ == '__main__':
    main()

class Production:

    def __init__(self,left,right,point_position=0):
        self.left = left
        self.right = right
        self.point_position = point_position
        self.peek_chars = set()
        self.is_scaned = False

    def add_peek_char(self,peek_char):
        if isinstance(peek_char,set):
            for c in peek_char:
                self.peek_chars.add(c)
        else:
            self.peek_chars.add(peek_char)

    def __str__(self):
        string = self.left + ' ::= '
        for before in self.right[:self.point_position]:
            string += before
        string += '.'
        for after in self.right[self.point_position:]:
            string += after
        string += '\t\t,'
        for c in self.peek_chars:
            string += c + '/'
        return string.strip('/')

class Symbol:

    def __init__(self,symbol,sym_type='N',first_set=None,follow_set=None):
        self.symbol = symbol
        self.sym_type = sym_type
        self.first_set = first_set
        self.follow_set = follow_set
        self.is_nullable = False

    def is_terminal(self):
        return self.sym_type == 'T'

    def __str__(self):
        string = self.symbol
        if self.is_terminal():
            return string
        else:
            string += '\t\tFIRST' + str(self.first_set) + '\t\tFOLLOW' + str(self.follow_set)
            return string

class ProductionGroup:

    def __init__(self,number):
        self.productions=[]
        self.target={}
        self.number=number
        self.is_scaned = False

    def add_production(self,production):
        self.productions.append(production)

    def set_target(self,source,target):
        self.target[source]=target

    def find_production(self,left,right,position):
        for p in self.productions:
            if p.left == left and p.right == right and p.point_position == position:
                return p
        return False

    def __str__(self):
        string ='GROUP_STATE_NUMBER: '+str(self.number) + '\n'
        for production in self.productions:
            string += str(production) + '\n'
        for key in self.target.keys():
            string += 'TARGET [' + key + '] = ' + str(self.target[key]) + '\n'
        return string.strip('\n')

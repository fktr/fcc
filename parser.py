from lexer import scanner, ATTR_LIST, read_source_file
from util import Production,Symbol,ProductionGroup

TERMINAL_SET = set()
NON_TERMINAL_SET = set()
PRODUCTION_LIST = []
SYMBOL_DICT = {}
PRODUCTION_DICT={}
PRODUCTION_GROUP_LIST=[]
ACTION_TABLE = {}
GOTO_TABLE ={}

def prepare_symbols_and_productions():
    with open('grammer.txt','r') as f:
        lines = f.readlines()
        terminal = False
        production = False
        for line in lines:
            if line.strip() == '*terminals':
                terminal = True
                production = False
                continue
            if line.strip() == '*productions':
                terminal = False
                production = True
                continue
            if line.strip() == '*end':
                break
            if terminal:
                TERMINAL_SET.add(line.strip())
            if production:
                left = line.split('::=')[0].strip()
                NON_TERMINAL_SET.add(left)
                try:
                    right = line.split('::=')[1].strip()
                    if right == '':
                        raise IndexError
                    p = Production(left,right.split(' '))
                except IndexError:
                    p = Production(left,['null'])
                PRODUCTION_LIST.append(p)
        for s in TERMINAL_SET:
            sym = Symbol(s,sym_type='T')
            SYMBOL_DICT[s] = sym
        for s in NON_TERMINAL_SET:
            sym = Symbol(s,sym_type='N')
            SYMBOL_DICT[s] = sym

def get_nullable():
    changes = True
    while changes:
        changes = False
        for p in PRODUCTION_LIST:
            if not SYMBOL_DICT[p.left].is_nullable:
                if p.right[0] == 'null':
                    SYMBOL_DICT[p.left].is_nullable = True
                    changes = True
                    continue
                else:
                    right_is_nullable = True
                    for r in p.right:
                        if SYMBOL_DICT[r].is_nullable == False:
                            right_is_nullable = False
                            break
                    if right_is_nullable:
                        changes = True
                        SYMBOL_DICT[p.left].is_nullable = True

def get_first():
    for s in TERMINAL_SET:
        sym = SYMBOL_DICT[s]
        sym.first_set = set([s])
    for s in NON_TERMINAL_SET:
        sym = SYMBOL_DICT[s]
        if sym.is_nullable:
            sym.first_set = set(['null'])
        else:
            sym.first_set = set()
    while True:
        first_set_is_stable = True
        for p in PRODUCTION_LIST:
            sym_left = SYMBOL_DICT[p.left]
            if p.right[0] == "null":
                continue
            previous_first_set = set(sym_left.first_set)
            for s in p.right:
                sym_right = SYMBOL_DICT[s]
                sym_left.first_set.update(sym_right.first_set.difference(set(['null'])))
                if sym_right.is_nullable:
                    continue
                else:
                    break
            if previous_first_set != sym_left.first_set:
                first_set_is_stable = False
        if first_set_is_stable:
            break

def get_follow():
    for s in NON_TERMINAL_SET:
        sym = SYMBOL_DICT[s]
        sym.follow_set = set()
    SYMBOL_DICT['<s>'].follow_set.add('$')
    TERMINAL_SET.add('$')
    while True:
        follow_set_is_stable = True
        for p in PRODUCTION_LIST:
            sym_left = SYMBOL_DICT[p.left]
            for s in p.right:
                if s == 'null':
                    continue
                if SYMBOL_DICT[s].is_terminal():
                    continue
                current_sym = SYMBOL_DICT[s]
                previous_follow_set = set(current_sym.follow_set)
                next_is_nullable = True
                for s2 in p.right[p.right.index(s)+1:]:
                    next_sym = SYMBOL_DICT[s2]
                    current_sym.follow_set.update(next_sym.first_set.difference(set(['null'])))
                    if next_sym.is_nullable:
                        continue
                    else:
                        next_is_nullable = False
                        break
                if next_is_nullable:
                    current_sym.follow_set.update(sym_left.follow_set)
                if current_sym.follow_set != previous_follow_set:
                    follow_set_is_stable = False
        if follow_set_is_stable:
            break

def init():
    prepare_symbols_and_productions()
    get_nullable()
    get_first()
    get_follow()

def get_closure(group):
    more_nt_sym = []
    while True:
        for p in group.productions:
            if p.is_scaned:
                continue
            if p.point_position == len(p.right):
                continue
            if p.right[0] == "null":
                p.point_position = 1
                continue
            sym = SYMBOL_DICT[p.right[p.point_position]]
            if not sym.is_terminal():
                next_is_nullable = True
                after_sym_chars=set()
                for s in p.right[p.point_position+1:]:
                    if SYMBOL_DICT[s].is_terminal():
                        after_sym_chars.add(s)
                        next_is_nullable = False
                        break
                    else:
                        for c in SYMBOL_DICT[s].first_set.difference(set(['null'])):
                            after_sym_chars.add(c)
                        if not SYMBOL_DICT[s].is_nullable:
                            next_is_nullable = False
                            break
                        #else:
                         #   for f in SYMBOL_DICT[s].follow_set:
                          #      after_sym_chars.add(f)
                if len(after_sym_chars) == 0 or next_is_nullable:
                    for c in p.peek_chars:
                        after_sym_chars.add(c)
                item = [sym.symbol,after_sym_chars]
                if item not in more_nt_sym:
                    more_nt_sym.append(item)
            p.is_scaned = True
        if len(more_nt_sym) != 0:
            while len(more_nt_sym):
                item = more_nt_sym.pop()
                for s in PRODUCTION_DICT[item[0]]:
                    p = group.find_production(item[0],s,0)
                    if p == False:
                        p = Production(item[0],s)
                        group.add_production(p)
                    else:
                        p.is_scaned = False
                    p.add_peek_char(item[1])
        else:
            break
    for p in group.productions:
        if p.point_position < len(p.right):
            group.target[p.right[p.point_position]]=0
    PRODUCTION_GROUP_LIST.append(group)

def find_productions_in_grouplist(productions):
    for group in PRODUCTION_GROUP_LIST:
        find = True
        for p in productions:
            find_p = group.find_production(p.left,p.right,p.point_position)
            if find_p == False:
                find = False
                break
            elif find_p.peek_chars != p.peek_chars:
                find = False
                break
        if find:
            return group
    return False

def get_lr_dfa():
    add_production = Production("<s'>",['<s>'])
    PRODUCTION_LIST.append(add_production)
    for p in PRODUCTION_LIST:
        if p.left not in PRODUCTION_DICT.keys():
            PRODUCTION_DICT[p.left]=[]
            PRODUCTION_DICT[p.left].append(p.right)
        else:
            PRODUCTION_DICT[p.left].append(p.right)
    state_number = 0
    first_group = ProductionGroup(state_number)
    add_production.point_position = 0
    add_production.add_peek_char('$')
    first_group.add_production(add_production)
    get_closure(first_group)
    while True:
        grouplist_is_stable = True
        for group in PRODUCTION_GROUP_LIST:
            if group.is_scaned:
                continue
            for c in group.target.keys():
                if group.target[c] == 0:
                    productions = []
                    for p in group.productions:
                        if p.point_position == len(p.right):
                            continue
                        if p.right[p.point_position] == c:
                            new_p = Production(p.left,p.right,p.point_position+1)
                            new_p.add_peek_char(p.peek_chars)
                            productions.append(new_p)
                    g = find_productions_in_grouplist(productions)
                    if g == False:
                        state_number += 1
                        g = ProductionGroup(state_number)
                        g.productions = productions
                        get_closure(g)
                        grouplist_is_stable = False
                    #else:
                     #   for new_p in productions:
                      #      find_p = g.find_production(new_p.left,new_p.right,new_p.point_position)
                       #     find_p.add_peek_char(new_p.peek_chars)
                        #g.is_scaned = False
                    group.target[c] = g.number
            group.is_scaned = True
        if grouplist_is_stable:
            break

def find_production_in_productionlist(production):
    for p in PRODUCTION_LIST:
        if p.left == production.left and p.right == production.right:
            return PRODUCTION_LIST.index(p)
    return False

def set_action_and_goto():
    for group in PRODUCTION_GROUP_LIST:
        for nt in NON_TERMINAL_SET:
            if nt in group.target.keys():
                GOTO_TABLE[(group.number,nt)]=group.target[nt]
            else:
                GOTO_TABLE[(group.number,nt)]="ERR"
        for t in TERMINAL_SET:
            if t in group.target.keys():
                ACTION_TABLE[(group.number,t)]='s'+str(group.target[t])
            else:
                ACTION_TABLE[(group.number, t)] = "ERR"
                for p in group.productions:
                    if p.point_position == len(p.right) and t in p.peek_chars:
                        if p.right[0] == '<s>' and t == '$':
                            ACTION_TABLE[(group.number,t)] = "ACC"
                        else:
                            ACTION_TABLE[(group.number,t)] = 'r'+str(find_production_in_productionlist(p))
                        break

def print_debug_reference(p_action_and_goto=False,p_productions=False,p_groups=False,p_null_nt=False,p_first_and_follow=False):
    with open('debug.txt','w') as f:
        if p_action_and_goto:
            f.write("TABLE ACTION AND GOTO\n\n")
            string = '%-30s' %("state")
            for i in range(len(PRODUCTION_GROUP_LIST)):
                string += '%4s' %(str(i))
            f.write(string+'\n')
            for t in TERMINAL_SET:
                string = '%-30s' %(t)
                for i in range(len(PRODUCTION_GROUP_LIST)):
                    string += '%4s' %(ACTION_TABLE[(i,t)])
                f.write(string+'\n')
            for nt in NON_TERMINAL_SET:
                string = '%-30s' %(nt)
                for i in range(len(PRODUCTION_GROUP_LIST)):
                    string += '%4s' %(GOTO_TABLE[(i,nt)])
                f.write(string+'\n')
        if p_productions:
            f.write('\n\nPRODUCTIONS\n\n')
            index = 0
            for p in PRODUCTION_LIST:
                string = '%-4s' %(str(index))
                string += str(p)
                f.write(string + '\n')
                index += 1
        if p_groups:
            f.write('\n\nPRODUCTION GROUPS\n\n')
            for g in PRODUCTION_GROUP_LIST:
                f.write(str(g)+'\n')
        if p_null_nt:
            f.write('\n\nNULLABLE NT\n\n')
            string = ''
            for nt in NON_TERMINAL_SET:
                if SYMBOL_DICT[nt].is_nullable:
                    string += nt + '\t'
            f.write(string+'\n')
        if p_first_and_follow:
            f.write("\n\nSET FIRST AND FOLLOW\n\n")
            for nt in NON_TERMINAL_SET:
                f.write(str(SYMBOL_DICT[nt])+'\n')

def do_parsing():
    init()
    get_lr_dfa()
    set_action_and_goto()
    state_stack = [0]
    print_debug_reference(p_action_and_goto=True,p_productions=True,p_groups=True,p_null_nt=True,p_first_and_follow=True)
    read_source_file('test.c')
    is_last_reduce = False
    token = None
    string = ''
    while True:
        if not is_last_reduce:
            result = scanner()
            token = chr(result[1]) if result[1] < 256 else ATTR_LIST[result[1] - 256]
        action = ACTION_TABLE[(state_stack[len(state_stack)-1],token)]
        print(action)
        string += action + '\n'
        if action[0] == 's':
            state_stack.append(int(action[1:]))
            is_last_reduce = False
        elif action[0] == 'r':
            p = PRODUCTION_LIST[int(action[1:])]
            print(p)
            string += str(p) + '\n'
            if p.right[0] == "null":
                time = 0
            else:
                time = len(p.right)
            while time:
                state_stack.pop()
                time -= 1
            print(state_stack)
            string += str(state_stack) + '\n'
            state_stack.append(GOTO_TABLE[(state_stack[len(state_stack)-1],p.left)])
            print('s'+str(state_stack[len(state_stack)-1]))
            string += 's'+str(state_stack[len(state_stack)-1]) + '\n'
            is_last_reduce = True
        elif action == "ERR":
            group = PRODUCTION_GROUP_LIST[state_stack[len(state_stack)-1]]
            print('CURRENT_TOKEN: '+token)
            print(str(group))
            print("ERROR")
            string += 'CURRENT_TOKEN: '+token +'\n'+str(group)+'\n'+"ERROR"+'\n'
            break
        elif action == "ACC":
            print("ACCEPT")
            string += 'ACCEPT'+'\n'
            break
    with open('second.txt','w') as f:
        f.write(string)

if __name__ == '__main__':
    do_parsing()

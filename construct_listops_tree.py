from collections import namedtuple
from IPython import embed
import listops.load_listops_data as listops
import json

Node = namedtuple('Node', 'tag id left right')
T_SHIFT = 0
T_REDUCE = 1

def spans(transitions, tokens):
    n = (len(transitions) + 1) // 2
    stack = []
    buf = [ Node(tokens[i], i, None, None) for i in range(n)]
    i2n = {}
    for i in range(n):
        i2n[i] = buf[i]
    buf = list(reversed(buf))
    nodes = []
    i = n

    def SHIFT(item):
        nodes.append(item)
        return item

    def REDUCE(i, l, r):
        tag = ""
        new_stack_item = Node(tag=tag, id=i, left=l.id, right=r.id)
        i2n[i] = new_stack_item
        nodes.append(new_stack_item)
        return new_stack_item

    for t in transitions:
        if t == 0:
            stack.append(SHIFT(buf.pop()))
        elif t == 1:
            r, l = stack.pop(), stack.pop()
            stack.append(REDUCE(i, l, r))
            i+=1

    return nodes, i2n

def construct_object(root, i2n):
    obj = {}
    obj['label'] = root.tag
    obj['i'] = root.id
    left,right = None,None
    if root.left in i2n:
        left = i2n[root.left]
    if root.right in i2n:
        right = i2n[root.right]

    obj['children'] = []
    if left:
        obj['children'].append( construct_object(left, i2n) )
    if right:
        obj['children'].append( construct_object(right, i2n) )
    return obj

def construct_json_string(root, i2n):
    return json.dumps(construct_object(root, i2n))

def ConvertBinaryBracketedSeq(seq):
    tokens, transitions = [], []
    for item in seq:
        if item != "(":
            if item != ")":
                tokens.append(item)
            transitions.append(T_REDUCE if item == ")" else T_SHIFT)
    return tokens, transitions

def parse_single_data(line):
    line = line.strip()
    label, seq = line.split('\t')
    tokens, transitions = ConvertBinaryBracketedSeq(seq.split(' '))

    # example = {}
    # example["label"] = label
    # example["sentence"] = seq
    # example["tokens"] = tokens
    # example["transitions"] = transitions

    nodes, i2n = spans(transitions, tokens)
    return construct_json_string(nodes[-1], i2n)



if __name__ == '__main__':
    examples = listops.load_data("listops/test_d20s.tsv")

    e = examples[3]

    nodes, i2n = spans(e['transitions'], e['tokens'])

    obj = construct_object(nodes[-1], i2n)

    print(json.dumps(obj))

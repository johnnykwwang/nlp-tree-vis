from collections import namedtuple

# With loaded embedding matrix, the padding vector will be initialized to zero
# and will not be trained. Hopefully this isn't a problem. It seems better than
# random initialization...
PADDING_TOKEN = "_PAD"

# Temporary hack: Map UNK to "_" when loading pretrained embedding matrices:
# it's a common token that is pretrained, but shouldn't look like any
# content words.
UNK_TOKEN = "_"

T_SHIFT = 0
T_REDUCE = 1
T_SKIP = 2
SENTENCE_PADDING_SYMBOL = 0

CORE_VOCABULARY = {PADDING_TOKEN: 0,
                   UNK_TOKEN: 1}


def ConvertBinaryBracketedSeq(seq):
    tokens, transitions = [], []
    for item in seq:
        if item != "(":
            if item != ")":
                tokens.append(item)
            transitions.append(T_REDUCE if item == ")" else T_SHIFT)
    return tokens, transitions

SENTENCE_PAIR_DATA = False
OUTPUTS = list(range(10))
LABEL_MAP = {str(x): i for i, x in enumerate(OUTPUTS)}

Node = namedtuple('Node', 'tag span')

def spans(transitions, tokens=None):
    n = (len(transitions) + 1) // 2
    stack = []
    buf = [Node("leaf", (l, r)) for l, r in zip(list(range(n)), list(range(1, n + 1)))]
    buf = list(reversed(buf))

    nodes = []
    reduced = [False] * n

    def SHIFT(item):
        nodes.append(item)
        return item

    def REDUCE(l, r):
        tag = None
        i = r.span[1] - 1
        if tokens is not None and tokens[i] == ']' and not reduced[i]:
            reduced[i] = True
            tag = "struct"
        new_stack_item = Node(tag=tag, span=(l.span[0], r.span[1]))
        nodes.append(new_stack_item)
        return new_stack_item

    for t in transitions:
        if t == 0:
            stack.append(SHIFT(buf.pop()))
        elif t == 1:
            r, l = stack.pop(), stack.pop()
            stack.append(REDUCE(l, r))

    return nodes

def load_data(path):
    examples = []
    with open(path) as f:
        for example_id, line in enumerate(f):
            line = line.strip()
            label, seq = line.split('\t')
            if len(seq) <= 1:
                continue

            tokens, transitions = ConvertBinaryBracketedSeq(
                seq.split(' '))

            example = {}
            example["label"] = label
            example["sentence"] = seq
            example["tokens"] = tokens
            example["transitions"] = transitions
            example["example_id"] = str(example_id)

            examples.append(example)
    return examples

from collections import deque
from shunyard import CharWrapper, shunting_yard, augmented_regexp
from regexpconv import verbose_regexp


class Node:
    def __init__(self, value, left=None, right=None) -> None:
        self.value = value
        self.left = left
        self.right = right
        self.nullable = False
        self.firstpos = {}
        self.lastpos = {}
        self.position = 0

    def __str__(self) -> str:
        return str(self.value)

    def __hash__(self) -> int:
        return hash(str(self.value))

    def __eq__(self, __value: object) -> bool:
        return hash(str(self) == hash(str(__value)))


def build_syntax_tree(rpn_augmented_regexp):
    position = 1
    stack = deque()
    for char in rpn_augmented_regexp:
        if char == "*":
            child = stack.pop()
            node = Node(char, child)
            stack.append(node)
        elif char in (".", "|"):
            right = stack.pop()
            left = stack.pop()
            node = Node(char, left, right)
            stack.append(node)
        else:
            node = Node(char)
            node.position = position
            stack.append(node)
            position += 1
    return stack.pop()


class SyntaxTreeInfo:
    def __init__(self, root: Node) -> None:
        self.root: Node = root
        self.final_state_pos = 0
        SyntaxTreeInfo.nullable(root)
        SyntaxTreeInfo.firstpos(root)
        SyntaxTreeInfo.lastpos(root)
        self.alphabets = self.find_alphabets()
        self.positions = self.find_positions()
        self.followsets = SyntaxTreeInfo.followpos(root)

    @staticmethod
    def postorder(node):
        if node:
            yield from SyntaxTreeInfo.postorder(node.left)
            yield from SyntaxTreeInfo.postorder(node.right)
            yield node

    @staticmethod
    def followpos(root):
        follow = {}
        for node in SyntaxTreeInfo.postorder(root):
            if node.value == ".":
                for pos in node.left.lastpos:
                    if pos not in follow:
                        follow[pos] = set()
                    follow[pos].update(node.right.firstpos)
            elif node.value == "*":
                for pos in node.lastpos:
                    if pos not in follow:
                        follow[pos] = set()
                    follow[pos].update(node.firstpos)
        return follow

    @staticmethod
    def nullable(root):
        for node in SyntaxTreeInfo.postorder(root):
            if node.value == "|":
                node.nullable = node.left.nullable or node.right.nullable
            elif node.value == ".":
                node.nullable = node.left.nullable and node.right.nullable
            elif node.value == "*":
                node.nullable = True
            else:
                node.nullable = False

    @staticmethod
    def firstpos(root):
        for node in SyntaxTreeInfo.postorder(root):
            if node.value == "|":
                node.firstpos = node.left.firstpos.union(node.right.firstpos)
            elif node.value == ".":
                if node.left.nullable:
                    node.firstpos = node.left.firstpos.union(node.right.firstpos)
                else:
                    node.firstpos = node.left.firstpos
            elif node.value == "*":
                node.firstpos = node.left.firstpos
            else:
                node.firstpos = {node.position}

    @staticmethod
    def lastpos(root):
        for node in SyntaxTreeInfo.postorder(root):
            if node.value == "|":
                node.lastpos = node.left.lastpos.union(node.right.lastpos)
            elif node.value == ".":
                if node.right.nullable:
                    node.lastpos = node.left.lastpos.union(node.right.lastpos)
                else:
                    node.lastpos = node.right.lastpos
            elif node.value == "*":
                node.lastpos = node.left.lastpos
            else:
                node.lastpos = {node.position}

    def find_alphabets(self):
        alphabets = set()
        for node in SyntaxTreeInfo.postorder(self.root):
            if not node.left and not node.right:
                if not node.value == "#":
                    alphabets.add(node.value)
        return alphabets

    def find_positions(self):
        positions = {k: set() for k in self.alphabets}
        for node in SyntaxTreeInfo.postorder(self.root):
            if node in self.alphabets:
                positions[node].add(node.position)
            if node.value == "#":
                self.final_state_pos = node.position
        return positions


class DFA:
    def __init__(self, info: SyntaxTreeInfo) -> None:
        self.info = info
        self.alphabets = info.alphabets
        self.start_state = [frozenset(info.root.firstpos)]
        self.final_states = set()
        self.transitions: dict[frozenset, dict[CharWrapper, frozenset]] = {}

    def re2dfa(self):
        self.transitions = {frozenset(self.info.root.firstpos): {}}
        unmarked = deque([frozenset(self.info.root.firstpos)])
        while unmarked:
            state = unmarked.pop()
            for alphabet in self.alphabets:
                next_state = set()
                for position in self.info.positions[alphabet]:
                    if position in state:
                        next_state.update(self.info.followsets[position])
                next_state = frozenset(next_state)
                if next_state not in self.transitions:
                    self.transitions[next_state] = {}
                    unmarked.append(next_state)

                self.transitions[state][alphabet] = next_state
                if self.info.final_state_pos in state:
                    self.final_states.add(state)
        return self.transitions


if __name__ == "__main__":
    text = r"(a|b)*abb"  # You can test wth different regexps here.
    root = build_syntax_tree(shunting_yard(augmented_regexp(verbose_regexp(text))))

    syntree = SyntaxTreeInfo(root)
    dfa = DFA(syntree)
    s = dfa.re2dfa()

    print(dfa.alphabets)
    print(dfa.start_state)
    print(dfa.final_states)
    print(dfa.transitions)

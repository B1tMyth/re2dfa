import regexpconv
from collections import deque
from queue import Queue


def augmented_regexp(verbose_regexp):
    output = []
    for idx, elem in enumerate(verbose_regexp):
        if (isinstance(elem, regexpconv.CharWrapper) or elem == "*") and (
            idx + 1 < len(verbose_regexp) and verbose_regexp[idx + 1] not in ("|", ")")
        ):
            output.append(elem)
            output.append(".")
        else:
            output.append(elem)
    output.append(".")
    output.append("#")
    return output


def shunting_yard(
    verbose_regexp: list[regexpconv.CharWrapper | str],
) -> list[regexpconv.CharWrapper | str]:
    precedence = {"*": 3, ".": 2, "|": 1, "(": 0}
    output_queue = Queue()
    operator_stack = deque()
    for char in verbose_regexp:
        if char == "(":
            operator_stack.append(char)
        elif char == ")":
            while operator_stack[-1] != "(":
                output_queue.put(operator_stack.pop())
            operator_stack.pop()
        elif char in ("*", "|", "."):
            while operator_stack and precedence[char] <= precedence.get(
                operator_stack[-1], 0
            ):
                output_queue.put(operator_stack.pop())
            operator_stack.append(char)
        else:
            output_queue.put(char)
    while operator_stack:
        output_queue.put(operator_stack.pop())

    rpn = list(output_queue.queue)
    return rpn

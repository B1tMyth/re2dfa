import string
class CharWrapper:
    def __init__(self, char: str) -> None:
        self.char = char

    def __str__(self) -> str:
        return str(self.char)

    def __repr__(self) -> str:
        return str(self)

    def __hash__(self) -> int:
        return hash(self.char)
    
    def __eq__(self, __value: object) -> bool:
        return hash(str(self.char)) == hash(str(__value))


def textbook_notation(regexp: list) -> list:
    buffer: list[CharWrapper | str] = []
    buffer.append("(")
    for idx, char in enumerate(regexp, 1):
        buffer.append(char)
        if not idx == len(regexp):
            buffer.append("|")
    buffer.append(")")
    return buffer


def handle_quantifier(output: list, quantifier=None):
    if not quantifier:
        return output
    if quantifier == "+":
        output.extend(output)
        output.append("*")
    elif quantifier == "?":
        buffer = ["("]
        buffer.extend(output)
        buffer.extend(["|", CharWrapper("epsilon"), ")"])
        output = buffer
    elif quantifier == "*":
        output.append("*")
    else:
        raise (ValueError)
    return output


def handle_backslash(char):
    output: list[CharWrapper | str] = []
    if char == 'd':
        output = [CharWrapper(str(elem)) for elem in range(10)]
    elif char == 'w':
        lower_alpha = [
            CharWrapper(chr(char_code)) for char_code in range(ord("a"), ord("z") + 1)
        ]
        upper_alpha = [
            CharWrapper(chr(char_code)) for char_code in range(ord("A"), ord("Z") + 1)
        ]
        digits = [CharWrapper(str(dig)) for dig in range(10)]
        upper_alpha.extend(digits)
        lower_alpha.extend(upper_alpha)
        output.extend(lower_alpha)
    elif char == 's':
        output = [CharWrapper(repr(char)) for char in string.whitespace]
    else:
        output = [CharWrapper(char)]
    return output


def handle_char_class(subregexp):
    buffer: list[CharWrapper | str] = []
    i = 0
    while i < len(subregexp):
        if subregexp[i] == "\\":
            buffer.extend(handle_backslash(subregexp[i + 1]))
            i += 2
            continue

        elif subregexp[i] == "-":
            if i - 1 < 0 or i + 1 == len(subregexp):
                buffer.append(CharWrapper("-"))
                i += 1
            elif subregexp[i - 1].isalnum() and subregexp[i + 1].isalnum():
                buffer.pop()
                for char_code in range(
                    ord(subregexp[i - 1]), ord(subregexp[i + 1]) + 1
                ):
                    buffer.append(CharWrapper(chr(char_code)))
                i += 2
            else:
                buffer.append(CharWrapper("-"))
                i += 1
            continue
        buffer.append(CharWrapper(subregexp[i]))
        i += 1
    return buffer


def verbose_regexp(regexp):
    output: list[CharWrapper | str] = []
    i = 0
    while i < len(regexp):
        if regexp[i] == "\\":
            quantifier = (
                regexp[i + 2]
                if i + 2 < len(regexp) and regexp[i + 2] in "*+?"
                else None
            )
            temp = handle_backslash(regexp[i + 1])
            if not len(temp) == 1:
                output.extend(
                    handle_quantifier(
                        textbook_notation(handle_backslash(regexp[i + 1])), quantifier
                    )
                )
            else:
                output.extend(handle_quantifier(temp, quantifier))
            i += 2 if not quantifier else 3
            continue

        elif regexp[i] == "(":
            j = i + 1
            while regexp[j] != ")":
                j += 1
            quantifier = (
                regexp[j + 1]
                if j + 1 < len(regexp) and regexp[j + 1] in "*+?"
                else None
            )
            buffer = []
            buffer.append("(")
            for elem in verbose_regexp(regexp[i + 1 : j]):
                buffer.append(elem)
            buffer.append(")")
            output.extend(handle_quantifier(buffer, quantifier))
            i = j + 1 if not quantifier else j + 2
            continue

        elif regexp[i] == "[":
            j = i + 1
            while regexp[j] != "]":
                j += 1
            quantifier = (
                regexp[j + 1]
                if j + 1 < len(regexp) and regexp[j + 1] in "*+?"
                else None
            )
            output.extend(
                handle_quantifier(
                    textbook_notation(handle_char_class(regexp[i + 1 : j])), quantifier
                )
            )
            i = j + 1 if not quantifier else j + 2
            continue

        elif regexp[i] == "+":
            output.append(CharWrapper(regexp[i - 1]))
            output.append("*")
        elif regexp[i] == "?":
            output.extend(["(", output.pop(), "|", CharWrapper("epsilon"), ")"])
        elif regexp[i] == "*":
            output.append("*")
        elif regexp[i] == "|":
            output.append("|")
        else:
            output.append(CharWrapper(regexp[i]))
        i += 1
    return output

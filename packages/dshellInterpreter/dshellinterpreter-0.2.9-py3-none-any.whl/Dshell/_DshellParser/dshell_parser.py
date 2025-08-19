__all__ = [
    "parse",
    "parser_inline",
    "to_postfix",
    "parse_postfix_expression",
    "print_ast",
    "ast_to_dict",
]

from typing import Union

from .ast_nodes import (ASTNode,
                        CommandNode,
                        IfNode,
                        LoopNode,
                        ElseNode,
                        ArgsCommandNode,
                        ElifNode,
                        VarNode,
                        EndNode,
                        SleepNode,
                        IdentOperationNode,
                        EmbedNode,
                        FieldEmbedNode,
                        PermissionNode,
                        ParamNode,
                        StartNode)
from .._DshellTokenizer import dshell_operators
from .._DshellTokenizer.dshell_token_type import DshellTokenType as DTT
from .._DshellTokenizer.dshell_token_type import Token


def parse(token_lines: list[list[Token]], start_node: ASTNode) -> tuple[list[ASTNode], int]:
    """
    Parse the list of tokens and return a list of AST nodes.
    :param token_lines: table of tokens
    :param start_node: the node where to start the parsing
    """
    pointeur = 0  # pointeur sur les listes de tokens pour savoir ou parser
    blocks: list[Union[ASTNode, EndNode]] = [start_node]  # liste d'imbrication des blocks pour gérer l'imbrication
    len_token_lines = len(token_lines)

    while pointeur < len_token_lines:

        tokens_by_line = token_lines[pointeur]  # on récupère la liste de token par rapport au pointeur
        first_token_line = tokens_by_line[0]  # on récupère le premier token de la ligne
        last_block = blocks[-1]

        if first_token_line.type == DTT.COMMAND:  # si le token est une comande
            body = tokens_by_line[1:]  # on récupère ses arguments
            last_block.body.append(CommandNode(first_token_line.value,
                                               ArgsCommandNode(body)))  # on ajoute la commande au body du dernier bloc

        ############################## DSHELL KEYWORDS ##############################

        elif first_token_line.type == DTT.KEYWORD:  # si c'est un mot clé

            if first_token_line.value == 'if':  # si c'est une condition
                if_node = IfNode(condition=tokens_by_line[1:],
                                 body=[])  # on crée la node avec les arguments de condition du if
                last_block.body.append(if_node)
                _, p = parse(token_lines[pointeur + 1:],
                             if_node)  # on parse le reste du code avec la node if_node comme commancement du nouveau parsing
                pointeur += p + 1  # essentielle pour ne pas parser les lignes déjà faite

            elif first_token_line.value == '#if':
                if not isinstance(last_block, (IfNode, ElseNode, ElifNode)):
                    raise SyntaxError(f'[#IF] No conditional bloc open on line {first_token_line.position} !')

                if isinstance(last_block, (ElifNode, ElseNode)):

                    while isinstance(last_block, (ElifNode, ElseNode)):
                        blocks.pop()
                        last_block = blocks[-1]
                blocks.pop()
                return blocks, pointeur

            elif first_token_line.value == 'elif':
                if not isinstance(last_block, (IfNode, ElifNode)):
                    raise SyntaxError(f'[ELIF] No conditional bloc open on line {first_token_line.position} !')
                elif_node = ElifNode(condition=tokens_by_line[1:], body=[],
                                     parent=last_block if isinstance(last_block, IfNode) else last_block.parent)

                if isinstance(last_block, ElifNode):
                    last_block.parent.elif_nodes.append(elif_node)
                else:
                    if last_block.elif_nodes is None:
                        last_block.elif_nodes = [elif_node]
                    else:
                        last_block.elif_nodes.append(elif_node)

                blocks.append(elif_node)

            elif first_token_line.value == 'else':
                if not isinstance(last_block, (IfNode, ElifNode)):
                    raise SyntaxError(f'[ELSE] No conditional bloc open on line {first_token_line.position} !')

                if isinstance(last_block, ElseNode) and last_block.else_body is not None:
                    raise SyntaxError(f'[ELSE] already define !')

                else_node = ElseNode(body=[])

                if isinstance(last_block, ElifNode):  # si le dernier bloc est un elif
                    last_block.parent.else_body = else_node  # on ajoute le bloc else à son parent (qui est le dernier if)
                else:
                    last_block.else_body = else_node  # une fois le parsing fini, on l'ajoute au dernier bloc
                blocks.append(else_node)

            elif first_token_line.value == 'loop':
                loop_node = LoopNode(VarNode(tokens_by_line[1], to_postfix(tokens_by_line[2:])), body=[])
                last_block.body.append(loop_node)
                _, p = parse(token_lines[pointeur + 1:],
                             loop_node)  # on parse tous ce qu'il y a après l'instruction loop
                pointeur += p + 1

            elif first_token_line.value == '#loop':  # si rencontré
                if not isinstance(last_block, LoopNode):
                    raise SyntaxError(f'[#LOOP] No loop open on line {first_token_line.position} !')
                blocks.pop()
                return blocks, pointeur  # on renvoie les informations parsé à la dernière loop ouverte

            elif first_token_line.value == 'var':
                var_node = VarNode(name=token_lines[pointeur][1], body=[])
                last_block.body.append(var_node)
                result, status = parser_inline(tokens_by_line[
                                               2:])  # on fait en sorte de mettre les tokens de la ligne séparé par des retour à la ligne à chaque condition/else
                if status:
                    parse(result, var_node)  # on parse le tout dans la variable
                else:
                    # var_node.body = parse(result, StartNode([]))[0][0].body
                    var_node.body = result[0]

            elif first_token_line.value == 'sleep':
                sleep_node = SleepNode(tokens_by_line[1:])
                last_block.body.append(sleep_node)

            elif first_token_line.value == 'param':
                param_node = ParamNode(body=[])
                last_block.body.append(param_node)
                _, p = parse(token_lines[pointeur + 1:], param_node)
                pointeur += p + 1  # on avance le pointeur de la ligne suivante

            elif first_token_line.value == '#param':
                if not isinstance(last_block, ParamNode):
                    raise SyntaxError(f'[#PARAM] No parameters open on line {first_token_line.position} !')
                blocks.pop()  # on supprime le dernier bloc (le paramètre)
                return blocks, pointeur  # on renvoie les informations parsé à la dernière paramètre ouverte

            elif first_token_line.value == '#end':  # node pour arrêter le programme si elle est rencontré
                end_node = EndNode()
                last_block.body.append(end_node)

        ############################## DISCORD KEYWORDS ##############################

        elif first_token_line.type == DTT.DISCORD_KEYWORD:

            if first_token_line.value == 'embed':
                embed_node = EmbedNode(body=[], fields=[])
                var_node = VarNode(tokens_by_line[1], body=[embed_node])
                last_block.body.append(var_node)
                _, p = parse(token_lines[pointeur + 1:], embed_node)
                pointeur += p + 1

            elif first_token_line.value == '#embed':
                if not isinstance(last_block, EmbedNode):
                    raise SyntaxError(f'[#EMBED] No embed open on line {first_token_line.position} !')
                blocks.pop()
                return blocks, pointeur

            elif first_token_line.value == 'field':
                if not isinstance(last_block, EmbedNode):
                    raise SyntaxError(f'[FIELD] No embed open on line {first_token_line.position} !')
                last_block.fields.append(FieldEmbedNode(tokens_by_line[1:]))

            elif first_token_line.value in ('perm', 'permission'):
                perm_node = PermissionNode(body=[])
                var_node = VarNode(tokens_by_line[1], body=[perm_node])
                last_block.body.append(var_node)
                _, p = parse(token_lines[pointeur + 1:], perm_node)
                pointeur += p + 1

            elif first_token_line.value in ('#perm', '#permission'):
                if not isinstance(last_block, PermissionNode):
                    raise SyntaxError(f'[#PERM] No permission open on line {first_token_line.position} !')
                blocks.pop()
                return blocks, pointeur

        ############################## AUTRE ##############################

        elif first_token_line.type == DTT.IDENT:
            if len(tokens_by_line) == 1:
                last_block.body.append(CommandNode(name='sm', body=ArgsCommandNode([first_token_line])))

            else:
                last_block.body += parse_postfix_expression(to_postfix(tokens_by_line))

        elif first_token_line.type == DTT.STR:
            last_block.body.append(CommandNode(name='sm', body=ArgsCommandNode([first_token_line])))


        else:
            last_block.body += tokens_by_line

        pointeur += 1

    return blocks, pointeur


"""
elif first_token_line.type == DTT.LIST: # si le token est une liste (qui comporte une liste python avec des Tokens)
    list_node = ListNode(first_token_line.value) # le .value est une liste python
    last_block.body.append(list_node)
    """


def ast_to_dict(obj):
    if isinstance(obj, list):
        return [ast_to_dict(item) for item in obj]
    elif hasattr(obj, "to_dict"):
        return obj.to_dict()
    else:
        return obj  # fallback for primitives or tokens


def dict_to_ast(data):
    """
    Convertit un dictionnaire en une structure AST.
    :param data: le dictionnaire à convertir
    :return: la structure AST correspondante
    """
    if isinstance(data, list):
        return [dict_to_ast(item) for item in data]
    elif isinstance(data, dict):
        pass


def parser_inline(tokens: list[Token]) -> tuple[list[list[Token]], bool]:
    """
    Transforme une ligne avec un if/else inline en structure multilignes
    """
    result: list[list[Token]] = []

    try:
        if_index = next(i for i, tok in enumerate(tokens) if tok.value == 'if')
        else_index = next(i for i, tok in enumerate(tokens) if tok.value == 'else')
    except StopIteration:
        return [tokens], False  # ligne normale

    value_tokens = tokens[:if_index]
    condition_tokens = tokens[if_index + 1:else_index]
    else_tokens = tokens[else_index + 1:]

    # On génère :
    result.append([tokens[if_index]] + condition_tokens)  # ligne "if cond"
    result.append(value_tokens)  # body du if
    result.append([tokens[else_index]])  # ligne "else"
    result.append(else_tokens)  # body du else
    return result, True


def to_postfix(expression):
    """
    Transforme l'expression en notation postfixée (RPN)
    :param expression: l'expression donné par le tokenizer
    :return: l'expression en notation postfixée
    """
    output = []
    operators: list[Token] = []

    for token in expression:
        if token.type in (DTT.IDENT, DTT.CALL_ARGS, DTT.INT, DTT.FLOAT, DTT.LIST, DTT.STR, DTT.BOOL):  # Si c'est un ident
            output.append(token)
        elif token.value in dshell_operators:
            while (operators and operators[-1].value in dshell_operators and
                   dshell_operators[operators[-1].value][1] >= dshell_operators[token.value][1]):
                output.append(operators.pop())
            operators.append(token)
        else:
            raise ValueError(f"Token inconnu : {token}")

    while operators:
        output.append(operators.pop())

    return output


def parse_postfix_expression(postfix_tokens: list[Token]) -> list[IdentOperationNode]:
    stack = []

    for tok in postfix_tokens:

        if tok.type in (DTT.IDENT, DTT.CALL_ARGS, DTT.INT, DTT.STR, DTT.LIST, DTT.FLOAT, DTT.BOOL):
            stack.append(tok)

        elif tok.type == DTT.MATHS_OPERATOR:
            if tok.value == '.':
                args = stack.pop()
                func = stack.pop()
                base = stack.pop()
                node = IdentOperationNode(ident=base, function=func, args=args)
                stack.append(node)

            elif tok.value == '->':
                value = stack.pop()
                base = stack.pop()
                fake_func = Token(DTT.IDENT, 'at', tok.position)
                fake_args = Token(DTT.CALL_ARGS, value.value, value.position)
                node = IdentOperationNode(ident=base, function=fake_func, args=fake_args)
                stack.append(node)

            else:
                raise SyntaxError(f"Opérateur non supporté dans les appels : {tok.value}")

        else:
            raise SyntaxError(f"Token inattendu : {tok}")

    if len(stack) != 1:
        raise SyntaxError("Expression mal formée ou incomplète")

    return stack


def print_ast(ast: list[ASTNode], decalage: int = 0):
    for i in ast:

        if isinstance(i, StartNode):
            print_ast(i.body, decalage)

        if isinstance(i, LoopNode):
            print(f"{' ' * decalage}LOOP -> {i.variable.name} : {i.variable.body}")
            print_ast(i, decalage + 5)

        elif isinstance(i, IfNode):
            print(f"{' ' * decalage}IF -> {i.condition}")
            print_ast(i, decalage + 5)

            if i.elif_nodes is not None:
                for elif_body in i.elif_nodes:
                    print(f"{' ' * decalage}ELIF -> {elif_body.condition}")
                    print_ast(elif_body, decalage + 5)

            if i.else_body is not None:
                print(f"{' ' * decalage}ELSE -> ...")
                print_ast(i.else_body, decalage + 5)

        elif isinstance(i, IdentOperationNode):
            print(f"{' ' * decalage}IDENT_OPERATION -> {i.ident}.{i.function}({i.args})")

        elif isinstance(i, CommandNode):
            print(f"{' ' * decalage}COMMAND -> {i.name} : {i.body}")

        elif isinstance(i, VarNode):
            print(f"{' ' * decalage}VAR -> {i.name} : {i.body}")

        elif isinstance(i, EmbedNode):
            print(f"{' ' * decalage}EMBED :")
            print_ast(i.fields, decalage + 5)

        elif isinstance(i, FieldEmbedNode):
            for field in i.body:
                print(f"{' ' * decalage}FIELD -> {field.value}")

        elif isinstance(i, PermissionNode):
            print(f"{' ' * decalage}PERMISSION -> {i.body}")

        elif isinstance(i, ParamNode):
            print(f"{' ' * decalage}PARAM -> {i.body}")

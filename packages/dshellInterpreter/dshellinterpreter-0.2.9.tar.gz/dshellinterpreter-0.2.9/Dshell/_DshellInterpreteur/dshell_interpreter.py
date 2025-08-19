from asyncio import sleep
from re import findall
from typing import TypeVar, Union, Any, Optional, Callable

from discord import AutoShardedBot, Embed, Colour, PermissionOverwrite, Permissions, Guild, Member, Role, Message
from discord.abc import PrivateChannel

from .._DshellParser.ast_nodes import *
from .._DshellParser.dshell_parser import parse
from .._DshellParser.dshell_parser import to_postfix, print_ast
from .._DshellTokenizer.dshell_keywords import *
from .._DshellTokenizer.dshell_token_type import DshellTokenType as DTT
from .._DshellTokenizer.dshell_token_type import Token
from .._DshellTokenizer.dshell_tokenizer import DshellTokenizer

All_nodes = TypeVar('All_nodes', IfNode, LoopNode, ElseNode, ElifNode, ArgsCommandNode, VarNode, IdentOperationNode)
context = TypeVar('context', AutoShardedBot, Message, PrivateChannel)


class DshellInterpreteur:
    """
    Discord Dshell interpreter.
    Make what you want with Dshell code to interact with Discord !
    """

    def __init__(self, code: str, ctx: context, debug: bool = False, vars: Optional[str] = None):
        """
        Interpreter Dshell code
        :param code: The code to interpret. Each line must end with a newline character, except SEPARATOR and SUB_SEPARATOR tokens.
        :param ctx: The context in which the code is executed. It can be a Discord bot, a message, or a channel.
        :param debug: If True, prints the AST of the code.
        :param vars: Optional dictionary of variables to initialize in the interpreter's environment.
        """
        self.ast: list[ASTNode] = parse(DshellTokenizer(code).start(), StartNode([]))[0]
        self.env: dict[str, Any] = {
            '__ret__': None,  # environment variables, '__ret__' is used to store the return value of commands
            '__guild__': ctx.channel.guild.name,
            '__channel__': ctx.channel.name,
            '__author__': ctx.author.name,
            '__author_display_name__': ctx.author.display_name,
            '__author_avatar__': ctx.author.display_avatar.url if ctx.author.display_avatar else None,
            '__author_discriminator__': ctx.author.discriminator,
            '__author_bot__': ctx.author.bot,
            '__author_nick__': ctx.author.nick if hasattr(ctx.author, 'nick') else None,
            '__author_id__': ctx.author.id,
            '__message__': ctx.content,
            '__message_id__': ctx.id,
            '__channel_name__': ctx.channel.name,
            '__channel_type__': ctx.channel.type.name if hasattr(ctx.channel, 'type') else None,
            '__channel_id__': ctx.channel.id,
            '__private_channel__': isinstance(ctx.channel, PrivateChannel),
        } if ctx is not None else {}
        self.vars = vars if vars is not None else ''
        self.ctx: context = ctx
        if debug:
            print_ast(self.ast)

    async def execute(self, ast: Optional[list[All_nodes]] = None):
        """
        Executes the abstract syntax tree (AST) generated from the Dshell code.

        This asynchronous method traverses and interprets each node in the AST, executing commands,
        handling control flow structures (such as if, elif, else, and loops), managing variables,
        and interacting with Discord through the provided context. It supports command execution,
        variable assignment, sleep operations, and permission handling, among other features.

        :param ast: Optional list of AST nodes to execute. If None, uses the interpreter's main AST.
        :raises RuntimeError: If an EndNode is encountered, indicating execution should be stopped.
        :raises Exception: If sleep duration is out of allowed bounds.
        """
        if ast is None:
            ast = self.ast

        for node in ast:

            if isinstance(node, StartNode):
                await self.execute(node.body)

            if isinstance(node, CommandNode):
                self.env['__ret__'] = await call_function(dshell_commands[node.name], node.body, self)

            elif isinstance(node, ParamNode):
                params = get_params(node, self)
                self.env.update(params)  # update the environment

            elif isinstance(node, IfNode):
                elif_valid = False
                if eval_expression(node.condition, self):
                    await self.execute(node.body)
                    continue
                elif node.elif_nodes:

                    for i in node.elif_nodes:
                        if eval_expression(i.condition, self):
                            await self.execute(i.body)
                            elif_valid = True
                            break

                if not elif_valid and node.else_body is not None:
                    await self.execute(node.else_body.body)

            elif isinstance(node, LoopNode):
                self.env[node.variable.name.value] = 0
                for i in DshellIterator(eval_expression(node.variable.body, self)):
                    self.env[node.variable.name.value] = i
                    await self.execute(node.body)

            elif isinstance(node, VarNode):

                first_node = node.body[0]
                if isinstance(first_node, IfNode):
                    self.env[node.name.value] = eval_expression_inline(first_node, self)

                elif isinstance(first_node, EmbedNode):
                    self.env[node.name.value] = build_embed(first_node.body, first_node.fields, self)

                elif isinstance(first_node, PermissionNode):
                    self.env[node.name.value] = build_permission(first_node.body, self)

                else:
                    self.env[node.name.value] = eval_expression(node.body, self)

            elif isinstance(node, IdentOperationNode):
                function = self.eval_data_token(node.function)
                listNode = self.eval_data_token(node.ident)
                if hasattr(listNode, function):
                    getattr(listNode, function)(self.eval_data_token(node.args))

            elif isinstance(node, SleepNode):
                sleep_time = eval_expression(node.body, self)
                if sleep_time > 3600:
                    raise Exception(f"Sleep time is too long! ({sleep_time} seconds) - maximum is 3600 seconds)")
                elif sleep_time < 1:
                    raise Exception(f"Sleep time is too short! ({sleep_time} seconds) - minimum is 1 second)")

                await sleep(sleep_time)


            elif isinstance(node, EndNode):
                raise RuntimeError("Execution stopped - EndNode encountered")

    def eval_data_token(self, token: Token):
        """
        Eval a data token and returns its value in Python.
        :param token: The token to evaluate.
        """

        if not hasattr(token, 'type'):
            return token

        if token.type in (DTT.INT, DTT.MENTION):
            return int(token.value)
        elif token.type == DTT.FLOAT:
            return float(token.value)
        elif token.type == DTT.BOOL:
            return token.value.lower() == "true"
        elif token.type == DTT.NONE:
            return None
        elif token.type == DTT.LIST:
            return ListNode(
                [self.eval_data_token(tok) for tok in token.value])  # token.value contient déjà une liste de Token
        elif token.type == DTT.IDENT:
            if token.value in self.env.keys():
                return self.env[token.value]
            return token.value
        elif token.type == DTT.CALL_ARGS:
            return (self.eval_data_token(tok) for tok in token.value)
        elif token.type == DTT.STR:
            for match in findall(rf"\$({'|'.join(self.env.keys())})", token.value):
                token.value = token.value.replace('$' + match, str(self.env[match]))
            return token.value
        else:
            return token.value  # fallback


def get_params(node: ParamNode, interpreter: DshellInterpreteur) -> dict[str, Any]:
    """
    Get the parameters from a ParamNode.
    :param node: The ParamNode to get the parameters from.
    :param interpreter: The Dshell interpreter instance.
    :return: A dictionary of parameters.
    """
    regrouped_args: dict[str, list] = regroupe_commandes(node.body, interpreter)[
        0]  # just regroup the commands, no need to do anything else
    regrouped_args.pop('*', ())
    englobe_args = regrouped_args.pop('--*', {})  # get the arguments that are not mandatory
    obligate = [i for i in regrouped_args.keys() if regrouped_args[i] == '*']  # get the obligatory parameters

    g: list[list[Token]] = DshellTokenizer(interpreter.vars).start()
    env_give_variables = regroupe_commandes(g[0], interpreter)[0] if g else {}

    gived_variables = env_give_variables.pop('*', ())  # get the variables given in the environment
    englobe_gived_variables: dict = env_give_variables.pop('--*',
                                                           {})  # get the variables given in the environment that are not mandatory

    for key, value in zip(regrouped_args.keys(), gived_variables):
        regrouped_args[key] = value
        gived_variables.pop(0)

    if len(gived_variables) > 0:
        for key in englobe_args.keys():
            regrouped_args[key] = ' '.join([str(i) for i in gived_variables])
            del englobe_args[key]
            break

    for key, englobe_gived_key, englobe_gived_value in zip(englobe_args.keys(), englobe_gived_variables.keys(),
                                                           englobe_gived_variables.values()):
        if key == englobe_gived_key:
            regrouped_args[key] = englobe_gived_value

    regrouped_args.update(englobe_args)  # add the englobe args to the regrouped args

    for key, value in env_give_variables.items():
        if key in regrouped_args:
            regrouped_args[key] = value  # update the regrouped args with the env variables
        else:
            raise Exception(f"'{key}' is not a valid parameter, but was given in the environment.")

    for key in obligate:
        if regrouped_args[key] == '*':
            raise Exception(f"'{key}' is an obligatory parameter, but no value was given for it.")

    return regrouped_args


def eval_expression_inline(if_node: IfNode, interpreter: DshellInterpreteur) -> Token:
    """
    Eval a conditional expression inline.
    :param if_node: The IfNode to evaluate.
    :param interpreter: The Dshell interpreter instance.
    """
    if eval_expression(if_node.condition, interpreter):
        return eval_expression(if_node.body, interpreter)
    else:
        return eval_expression(if_node.else_body.body, interpreter)


def eval_expression(tokens: list[Token], interpreter: DshellInterpreteur) -> Any:
    """
    Evaluates an arithmetic and logical expression.
    :param tokens: A list of tokens representing the expression.
    :param interpreter: The Dshell interpreter instance.
    """
    postfix = to_postfix(tokens)
    stack = []

    for token in postfix:

        if token.type in {DTT.INT, DTT.FLOAT, DTT.BOOL, DTT.STR, DTT.LIST, DTT.IDENT}:
            stack.append(interpreter.eval_data_token(token))

        elif token.type in (DTT.MATHS_OPERATOR, DTT.LOGIC_OPERATOR, DTT.LOGIC_WORD_OPERATOR):
            op = token.value

            if op == "not":
                a = stack.pop()
                result = dshell_operators[op][0](a)

            else:
                b = stack.pop()
                try:
                    a = stack.pop()
                except IndexError:
                    if op == "-":
                        a = 0
                    else:
                        raise SyntaxError(f"Invalid expression: {op} operator requires two operands, but only one was found.")

                result = dshell_operators[op][0](a, b)

            stack.append(result)

        else:
            raise SyntaxError(f"Unexpected token type: {token.type} - {token.value}")

    if len(stack) != 1:
        raise SyntaxError("Invalid expression: stack should contain exactly one element after evaluation.")

    return stack[0]


async def call_function(function: Callable, args: ArgsCommandNode, interpreter: DshellInterpreteur):
    """
    Call the function with the given arguments.
    It can be an async function !
    :param function: The function to call.
    :param args: The arguments to pass to the function.
    :param interpreter: The Dshell interpreter instance.
    """
    reformatted = regroupe_commandes(args.body, interpreter)[0]

    # conversion des args en valeurs Python
    absolute_args = reformatted.pop('*', list())
    englobe_args = reformatted.pop('--*', list())

    reformatted: dict[str, Token]

    absolute_args.insert(0, interpreter.ctx)
    keyword_args = reformatted.copy()
    keyword_args.update(englobe_args)
    return await function(*absolute_args, **keyword_args)


def regroupe_commandes(body: list[Token], interpreter: DshellInterpreteur) -> list[dict[str, list[Any]]]:
    """
    Groups the command arguments in the form of a python dictionary.
    Note that you can specify the parameter you wish to pass via -- followed by the parameter name. But this is not mandatory!
    Non-mandatory parameters will be stored in a list in the form of tokens with the key ‘*’.
    The others, having been specified via a separator, will be in the form of a list of tokens with the IDENT token as key, following the separator for each argument.
    If two parameters have the same name, the last one will overwrite the previous one.
    To accept duplicates, use the SUB_SEPARATOR (~~) to create a sub-dictionary for parameters with the same name (sub-dictionary is added to the list returned).

    :param body: The list of tokens to group.
    :param interpreter: The Dshell interpreter instance.
    """
    tokens = {'*': [],
              '--*': {}}  # tokens to return
    current_arg = '*'  # the argument keys are the types they belong to. '*' is for all arguments not explicitly specified by a separator and an IDENT
    n = len(body)
    list_tokens: list[dict] = [tokens]

    i = 0
    while i < n:

        if body[i].type == DTT.SEPARATOR and body[
            i + 1].type == DTT.IDENT:  # Check if it's a separator and if the next token is an IDENT
            current_arg = body[i + 1].value  # change the current argument. It will be impossible to return to '*'
            tokens[current_arg] = ''  # create a key/value pair for it
            i += 2  # skip the IDENT after the separator since it has just been processed

        elif body[
            i].type == DTT.SUB_SEPARATOR:  # allows to delimit parameters and to have several with the same name
            list_tokens += regroupe_commandes(
                [Token(
                    type_=DTT.SEPARATOR, value=body[i].value, position=body[i].position)
                ] + body[i + 1:], interpreter
            )  # add a sub-dictionary for sub-commands
            # return list_tokens

        elif (body[i].type == DTT.SEPARATOR and
              (body[i + 1].type == DTT.MATHS_OPERATOR and body[i + 1].value == '*') and
              body[i + 2].type == DTT.IDENT and
              body[i + 3].type == DTT.ENGLOBE_SEPARATOR):
            current_arg = body[i + 2].value  # change the current argument
            tokens['--*'][current_arg] = body[i + 3].value
            i += 4

        else:
            if current_arg == '*':
                tokens[current_arg].append(interpreter.eval_data_token(body[i]))
            else:
                tokens[current_arg] = interpreter.eval_data_token(body[i])  # add the token to the current argument
            i += 1

    return list_tokens


def build_embed(body: list[Token], fields: list[FieldEmbedNode], interpreter: DshellInterpreteur) -> Embed:
    """
    Builds an embed from the command information.
    """
    args_main_embed: dict[str, list[Any]] = regroupe_commandes(body, interpreter)[0]
    args_main_embed.pop('*')  # remove unspecified parameters for the embed
    args_main_embed.pop('--*')
    args_main_embed: dict[str, Token]  # specify what it contains from now on

    args_fields: list[dict[str, Token]] = []
    for field in fields:  # do the same for the fields
        a = regroupe_commandes(field.body, interpreter)[0]
        a.pop('*')
        a.pop('--*')
        a: dict[str, Token]
        args_fields.append(a)

    if 'color' in args_main_embed:
        args_main_embed['color'] = build_colour(args_main_embed['color'])  # convert color to Colour object or int

    embed = Embed(**args_main_embed)  # build the main embed
    for field in args_fields:
        embed.add_field(**field)  # add all fields

    return embed

def build_colour(color: Union[int, ListNode]) -> Union[Colour, int]:
    """
    Builds a Colour object from an integer or a ListNode.
    :param color: The color to build.
    :return: A Colour object.
    """
    if isinstance(color, int):
        return color
    elif isinstance(color, (ListNode, list)):
        if not len(color) == 3:
            raise ValueError(f"Color must be a list of 3 integers, not {len(color)} elements !")
        return Colour.from_rgb(*color)
    else:
        raise TypeError(f"Color must be an integer or a ListNode, not {type(color)} !")


def build_permission(body: list[Token], interpreter: DshellInterpreteur) -> dict[
    Union[Member, Role], PermissionOverwrite]:
    """
    Builds a dictionary of PermissionOverwrite objects from the command information.
    """
    args_permissions: list[dict[str, list[Any]]] = regroupe_commandes(body, interpreter)
    permissions: dict[Union[Member, Role], PermissionOverwrite] = {}

    for i in args_permissions:
        i.pop('*')
        i.pop('--*')
        permissions.update(DshellPermissions(i).get_permission_overwrite(interpreter.ctx.channel.guild))

    return permissions


class DshellIterator:
    """
    Used to transform anything into an iterable
    """

    def __init__(self, data):
        self.data = data if isinstance(data, (str, list, ListNode)) else range(int(data))
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= len(self.data):
            self.current = 0
            raise StopIteration

        value = self.data[self.current]
        self.current += 1
        return value


class DshellPermissions:

    def __init__(self, target: dict[str, list[int]]):
        """
        Creates a Dshell permissions object.
        :param target: A dictionary containing parameters and their values.
        Expected parameters: “allow”, “deny”, ‘members’, “roles”.
        For “members” and “roles”, values must be ID ListNodes.
        """
        self.target: dict[str, Union[ListNode, int]] = target

    @staticmethod
    def get_instance(guild: Guild, target_id: int) -> Union[Member, Role]:
        """
        Returns the instance corresponding to the given id. Only a Member or Role.
        :param guild: The Discord server in which to search
        :param target_id: The ID of the member or role
        :return: An instance of Member or Role
        """
        try:
            member = DshellPermissions.get_member(guild, target_id)
        except ValueError:
            member = None

        try:
            role = DshellPermissions.get_role(guild, target_id)
        except ValueError:
            role = None

        if member is not None:
            return member

        elif role is not None:
            return role

        else:
            raise ValueError(f"No member or role found with ID {target_id} in guild {guild.name}.")

    @staticmethod
    def get_member(guild: Guild, target_id: int) -> Member:
        """
        Returns the Member instance corresponding to the given id.
        :param guild: The Discord server to search
        :param target_id: The member ID
        :return: A Member instance
        """
        member = guild.get_member(target_id)
        if member is not None:
            return member

        raise ValueError(f"No member found with ID {target_id} in guild {guild.name}.")

    @staticmethod
    def get_role(guild: Guild, target_id: int) -> Role:
        """
        Returns the Role instance corresponding to the given id.
        :param guild: The Discord server to search
        :param target_id: The role ID
        :return: A Role instance
        """
        role = guild.get_role(target_id)
        if role is not None:
            return role

        raise ValueError(f"No role found with ID {target_id} in guild {guild.name}.")

    def get_permission_overwrite(self, guild: Guild) -> dict[Union[Member, Role], PermissionOverwrite]:
        """
        Returns a PermissionOverwrite object with member and role permissions.
        If no members or roles are specified, it returns a PermissionOverwrite with None key.
        :param guild: The Discord server
        :return: A dictionary of PermissionOverwrite objects with members and roles as keys
        """
        permissions: dict[Union[Member, Role, None], PermissionOverwrite] = {}
        target_keys = self.target.keys()

        if 'members' in target_keys:
            for member_id in (
                    self.target['members'] if isinstance(self.target['members'], ListNode) else [
                        self.target['members']]):  # allow a single ID
                member = self.get_member(guild, member_id)
                permissions[member] = PermissionOverwrite.from_pair(
                    allow=Permissions(permissions=self.target.get('allow', 0)),
                    deny=Permissions(permissions=self.target.get('deny', 0))
                )

        elif 'roles' in target_keys:
            for role_id in (
                    self.target['roles'] if isinstance(self.target['roles'], ListNode) else [
                        self.target['roles']]):  # allow a single ID
                role = self.get_role(guild, role_id)
                permissions[role] = PermissionOverwrite.from_pair(
                    allow=Permissions(permissions=self.target.get('allow', 0)),
                    deny=Permissions(permissions=self.target.get('deny', 0))
                )
        else:
            permissions[None] = PermissionOverwrite.from_pair(
                allow=Permissions(permissions=self.target.get('allow', 0)),
                deny=Permissions(permissions=self.target.get('deny', 0))
            )

        return permissions

# pegomancy

Yet another parsing thingy

## Usage

### As a tool

Pegomancy provides `pegomant` executable that can be used to generate Python code to parse data according to a given grammar.

```
usage: pegomant [-h] grammar_file

positional arguments:
  grammar_file

optional arguments:
  -h, --help    show this help message and exit
```

### As a library

The `pegomancy` module can be used as a library to fully control grammars and how code is generated.

## Grammar syntax

Pegomancy grammars look like regular PEG grammars, with a dash of sugar syntax. Here is an example grammar that can be used to parse arithmetic expressions:

```
integer: r"[0-9]+"

expr: left:expr op:'+' right:term
    | left:expr op:'-' right:term
    | term

term: left:term op:'*' right:atom
    | left:term op:'/' right:atom
    | atom

atom: integer | '(' expr ')'
```

In case the syntax isn't familiar, let's provide a bit of information.

### Rules

A grammar is made of one or several rules. Each rule is specified with the following syntax:

```
rule_name: expression
```

In the grammar above, `integer`, `expr`, `term` and `atom` are the rules.

### Expressions

#### Atoms

Atoms are the most primitive constructs used in an expression: they match a simple portion of the source text.

In the example grammar given above, we have different kinds of atoms:
- `'('`, `')'`, `'+'` (and others), each matching a raw string of text
- `r"[0-9]+"`, matching a regular expression
- `integer` (in the `atom` rule), matching what the `integer` rule matches

#### Items

Items are more complex expressions and introduce modifiers to repeat or make expressions optional:
- the `*` operator can be used to allow repeating an expression zero or more times
- the `+` operator can be used to allow repeating an expression one or more times
- the `?` operator can be used to make an expression optional

Items are unnamed by default, but can be named using the `:` operator, as in `op:'+'`, which gives the name
`op` to the `'+'` atom.

Note that atoms can be concatenated: `'(' expr ')'` will match an opening parenthesis, then what the `expr` rule
matches, then a closing parenthesis.

#### Alternatives

Some rules might allow multiple possibilities: for example, the `atom` rule in the above grammar can match either
an integer or a parenthesized expression.
The notion of alternative is expressed in the grammar using the `|` operator.

## Parse results

### Default AST

By default, parsers generated with `pegomant` will produce AST nodes that are either:
- a single value, if the matched expression has only one component
- a list, if the matched expression has multiple components
- a dictionary, if the matched expression has named items (unnamed items are discarded from the result)

### Customizing the AST

The default AST can be enough, but in some cases it is useful to transform it into a custom data structure.
Pegomancy grammars can specify a class whose methods will be invoked when a rule matches some input.

That class can be specified using the `@rule_handler <ClassName>` directive.

Here is a possible rule handler for the example grammar given in previous sections.

```
class RuleHandler:
    def integer(self, node):
        return int(node)

    def expr(self, node):
        if isinstance(node, dict):
            if node["op"] == "+":
                return node["left"] + node["right"]
            else:
                return node["left"] - node["right"]
        else:
            return node

    def term(self, node):
        if isinstance(node, dict):
            if node["op"] == "*":
                return node["left"] * node["right"]
            else:
                return node["left"] / node["right"]
        else:
            return node

    def atom(self, node):
        if isinstance(node, list):
            return node[1]
        return node
```

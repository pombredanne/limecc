class Grammar:
    """Represents a set of production rules.
    
    A rule is an object with the members
     * `left`, which must be hashable,
     * `right`, which must ba an iterable of hashable objects, and
     * `action`.

    Typically, the `Rule` class is used to represent a rule.
    The rules are supplied during construction.
    
    >>> from .rule import Rule
    >>> g = Grammar(
    ...     Rule('list', ()),
    ...     Rule('list', ('list', 'item')))
    >>> print(g)
    'list' = ;
    'list' = 'list', 'item';
    
    Grammars expose their rules using the standard list interface.
    
    >>> g[0]
    Rule('list', ())
    >>> len(g)
    2
    >>> for rule in g: print(rule)
    'list' = ;
    'list' = 'list', 'item';
    
    Symbols are considered non-terminal (with respect to a grammar) if
    they stand on the left side of some rule. All other symbols are considered terminal.
    A grammar can test a symbol for its terminality. It also exposes a list of
    all non-terminals and a list of all referenced symbols.
    
    >>> g = Grammar(
    ...     Rule('list', ()),
    ...     Rule('list', ('list', 'item')),
    ...     Rule('root', ('list',)))
    >>> [g.is_terminal(symbol) for symbol in ('list', 'root', 'item', 'unreferenced')]
    [False, False, True, True]
    >>> sorted(list(g.symbols()))
    ['item', 'list', 'root']
    >>> sorted(list(g.nonterms()))
    ['list', 'root']
    
    The grammar also allows fast access to a set of rules with a given symbol on the left.
    
    >>> for rule in g.rules('list'): print(rule)
    'list' = ;
    'list' = 'list', 'item';
    >>> for rule in g.rules('unreferenced'): print(rule)
    >>> for rule in g.rules('root'): print(rule)
    'root' = 'list';
    """
    def __init__(self, *rules, **kw):
        if any((opt != 'symbols' for opt in kw)):
            raise AttributeError('Unknown argument')

        self._rules = rules
        self._nonterms = frozenset((rule.left for rule in self._rules))

        symbols = []
        for rule in self._rules:
            symbols.append(rule.left)
            symbols.extend(rule.right)

        if 'symbols' in kw:
            symbols.extend(kw['symbols'])

        self._symbols = frozenset(symbols)

        self._rule_cache = {}
        for left in self._nonterms:
            self._rule_cache[left] = tuple([rule for rule in self._rules if rule.left == left])

    def __getitem__(self, index):
        return self._rules[index]
        
    def __len__(self):
        return len(self._rules)
        
    def __iter__(self):
        return iter(self._rules)
        
    def __str__(self):
        """
        >>> from .rule import Rule
        >>> print(Grammar(Rule('a', ('b', 'c')), Rule('a', ('c', 'b'))))
        'a' = 'b', 'c';
        'a' = 'c', 'b';
        """
        return '\n'.join(str(rule) for rule in self._rules)
    
    def __repr__(self):
        """
        >>> from .rule import Rule
        >>> print(repr(Grammar(Rule('a', ('b', 'c')), Rule('a', ('c', 'b')))))
        Grammar(Rule('a', ('b', 'c')), Rule('a', ('c', 'b')))
        """
        return 'Grammar(%s)' % ', '.join(repr(rule) for rule in self._rules)
        
    def rules(self, left):
        """Retrieves the set of rules with a given non-terminal on the left.
        
        >>> from .rule import Rule
        >>> g = Grammar(Rule('a', ('b',)), Rule('b', ('c',)), Rule('b', ('d',)))
        >>> for rule in g.rules('a'): print(rule)
        'a' = 'b';
        >>> for rule in g.rules('c'): print(rule)
        >>> for rule in g.rules('b'): print(rule)
        'b' = 'c';
        'b' = 'd';
        """
        return self._rule_cache.get(left, ())
    
    def is_terminal(self, token):
        """Tests the symbol for terminality.
        
        All non-terminal symbols are considered terminal,
        regardless of whether they are referenced by the grammar.
        
        >>> from .rule import Rule
        >>> g = Grammar(Rule('a', ('b',)), Rule('b', ('c',)))
        >>> tuple(g.is_terminal(sym) for sym in 'abcd')
        (False, False, True, True)
        """
        return token not in self._nonterms

    def nonterms(self):
        """Returns an iterable representing the set of all non-terminal symbols."""
        return self._nonterms

    def symbols(self):
        """Returns an iterable representing the current set of all referenced symbols."""
        return self._symbols

    def terminals(self):
        """Returns an iterable representing the current set of all terminal symbols."""
        return self._symbols - self._nonterms

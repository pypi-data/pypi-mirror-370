class Style(dict):
    def __init__(self, d) -> None:
        super().__init__(d)

    def set(self, element: str, property: str, value: str) -> None:
        if element not in self:
            self[element] = {}
        self[element][property] = value

    def __str__(self) -> str:
        s = ''
        for k, v in self.items():
            s += k + ' {\n'
            for k_, v_ in v.items():
                s += f'  {k_}: {v_};\n'
            s += '}\n'
        return s[:-1]

    def __iadd__(self, other):
        if not isinstance(other, Style):
            raise TypeError(f'Unsupported operand types for +: Style and {type(other).__name__}')
        for k, v in other.items():
            if k in self:
                self[k] |= v
            else:
                self[k] = v
        return self

    @classmethod
    def default(cls):
        """Default style.
        """
        return cls({
            ':root': {
                '--text-primary': '#1f2328',
                '--text-link': '#008ab8',
                '--border-primary': '#aeb7c0',
                '--surface-primary': '#eaedef',
                '--surface-secondary': '#47515b',
            },
            'body': {
                'margin': '20px',
                'color': 'var(--text-primary)',
                'font-family': '\'Verdana\', \'BIZ UDGothic\', sans-serif',
                'font-size': '90%',
                'line-height': '1.3',
                'letter-spacing': '0.02em',
            },
            'label': {
                'cursor': 'pointer',
                'user-select': 'none',
            },
            'table': {
                'border-collapse': 'collapse',
                'margin': '1.0em 0',
            },
            'th, td': {
                'border': '1px solid var(--border-primary)',
                'padding': '0.2em 0.4em',
                'text-align': 'left',
            },
            'th': {
                'background': 'var(--surface-primary)',
            },
        })

    @classmethod
    def scrollable_table(cls):
        """Styles for a scrollable table within a container. 

        Notes:
            The header row and the leftmost column are sticky.
            Wrap the table in <div class="scrollable-table-container"></div>.
        """
        return cls({
            '.scrollable-table-container table th, .scrollable-table-container table td': {
                'border': '0',
            },
            '.scrollable-table-container': {
                'overflow': 'auto',
                'white-space': 'nowrap',
                'max-height': '300px',
                'margin-bottom': '1.0em',
            },
            '.scrollable-table-container table': {
                'margin': '0',
                'border-collapse': 'separate',
                'border-spacing': '0',
                'width': '100%',
            },
            '.scrollable-table-container thead th': {
                'border-top': '1px solid var(--border-primary)',
                'border-bottom': '1px solid var(--border-primary)',
                'padding-right': '0.5em',
                'text-align': 'left',
                'position': 'sticky',
                'top': '0',
                'z-index': '2',
            },
            '.scrollable-table-container thead th:first-child': {
                'left': '0',
                'z-index': '3',
            },
            '.scrollable-table-container tbody td, .scrollable-table-container tbody th': {
                'border-bottom': '1px solid var(--border-primary)',
                'padding-right': '0.5em',
            },
            (
                '.scrollable-table-container tbody td:first-child,'
                '.scrollable-table-container tbody th:first-child'
            ): {
                'position': 'sticky',
                'left': '0',
                'z-index': '1',
            },
            '.scrollable-table-container tbody td:first-child': {
                'background': '#ffffff',
            },
        })

    def add_scrollable_table(self):
        self += Style.scrollable_table()

    @classmethod
    def tab_label(cls):
        return cls({
            'label.tab-label': {
                'display': 'inline-block',
                'border': '1px solid var(--text-primary)',
                'padding': '0.2em 0.4em',
                'margin-bottom': '1.0em',
                'background': 'var(--surface-primary)',
            }
        })

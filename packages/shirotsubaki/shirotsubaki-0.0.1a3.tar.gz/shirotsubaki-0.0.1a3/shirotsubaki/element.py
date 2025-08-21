class Element:
    def __init__(self, tagname: str, content=None) -> None:
        self.tagname = tagname
        self.attrs = {}
        self.inner = [content] if content else []

    def set_attr(self, key: str, value: str) -> 'Element':
        self.attrs[key] = value
        return self

    def append(self, elm) -> None:
        self.inner.append(elm)

    def __str__(self) -> str:
        attrs_str = ''.join([f' {k}="{v}"' for k, v in self.attrs.items()])
        s = f'<{self.tagname}{attrs_str}>\n'
        for elm in self.inner:
            if isinstance(elm, str):
                s += elm + '\n'
            else:
                s += str(elm)
        s += f'</{self.tagname}>\n'
        return s

    @classmethod
    def table_from_rows(cls, rows, header=False, index=False, scrollable=False):
        table = cls('table')
        cursor = 0

        if header:
            thead = cls('thead')
            thead.append(cls('tr'))
            for v in rows[0]:
                thead.inner[-1].append(cls('th', f'{v}'))
            table.append(thead)
            cursor = 1

        tbody = cls('tbody')
        for row in rows[cursor:]:
            tbody.append(cls('tr'))
            for i_col, v in enumerate(row):
                tag = 'th' if index and (i_col == 0) else 'td'
                tbody.inner[-1].append(cls(tag, f'{v}'))
        table.append(tbody)

        if scrollable:
            return cls('div', table).set_attr('class', 'scrollable-table-container')
        return table

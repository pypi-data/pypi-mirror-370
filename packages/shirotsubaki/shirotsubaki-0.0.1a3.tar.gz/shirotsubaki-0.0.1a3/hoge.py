import shirotsubaki.report
from shirotsubaki.element import Element as Elm

def example_3():
    rp = shirotsubaki.report.Report(title='Fruits')
    rp.append(Elm('h1', 'Apple'))
    rp.append_as_minitabs('001', {
        'Taro': 'Taro Taro',
        'Jiro': 'Jiro Jiro',
        'Saburo': 'Saburo Saburo',
    })
    rp.append_as_minitabs('002', {
        'Shiro': 'Shiro Shiro',
        'Goro': 'Goro Goro',
        'Rokuro': 'Rokuro Rokuro',
    })
    rp.output('docs/example_3.html')

def example_2():
    rp = shirotsubaki.report.Report(title='Fruits')
    rp.append(Elm('h1', 'Apple'))
    rp.append_as_toggle('001', 'This message will be collapsed inside the toggle.')
    rp.output('docs/example_2.html')

def example_1():
    rp = shirotsubaki.report.ReportWithTabs()
    rp.set('title', 'Fruits Fruits Fruits')
    rp.style.add_scrollable_table()

    rp.add_tab('apple')
    rp.append(Elm.table_from_rows([['apple'] * 10] * 20, header=True, index=True, scrollable=True))

    rp.add_tab('banana')
    rp.append(Elm.table_from_rows([['banana'] * 10] * 20, header=True, index=False, scrollable=True))

    rp.add_tab('cherry')
    rp.append(Elm.table_from_rows([['cherry'] * 10] * 20, header=False, index=False, scrollable=True))

    rp.output('docs/example_1.html')



if False:
    if False:

        import shirotsubaki.report
        from shirotsubaki.element import Element as Elm

        rp = shirotsubaki.report.Report(title='Fruits')
        rp.style.set('h1', 'color', 'steelblue')
        rp.append(Elm('h1', 'Fruits Fruits'))
        rp.append('Fruits Fruits Fruits')
        rp.output('docs/example_report.html')

if True:
    example_3()

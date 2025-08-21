import shirotsubaki.report
import shirotsubaki.utils
from shirotsubaki.style import Style
from shirotsubaki.element import Element as Elm
import os


remove_output = False


def output(rp, out_html):
    if os.path.isfile(out_html):
        os.remove(out_html)
    rp.output(out_html)
    assert os.path.isfile(out_html)
    if remove_output:
        os.remove(out_html)


def create_table():
    return Elm.table_from_rows(
        [['apple', 'banana', 'cherry'] * 10] * 20, header=True, index=True, scrollable=True,
    )


def test_lighten_color():
    color = shirotsubaki.utils.lighten_color('#336699')
    assert color == '#99B2CC'


def test_report():
    rp = shirotsubaki.report.Report(title='Fruits')
    rp.style.set('h1', 'color', 'steelblue')
    rp.style.add_scrollable_table()
    rp.style.set('.scrollable-table-container', 'max-height', '200px')

    rp.append(Elm('h1', 'Fruits'))
    rp.append(create_table())
    rp.append_as_toggle('001', 'This message will be collapsed inside the toggle.')
    rp.append_as_minitabs('001', {
        'Taro': 'Taro Taro',
        'Jiro': 'Jiro Jiro',
        'Saburo': 'Saburo Saburo',
    })
    for header in [False, True]:
        for index in [False, True]:
            rp.append(Elm.table_from_rows(
                rows=[
                    ['Taro', 'Sato'],
                    ['Jiro', 'Suzuki'],
                ],
                header=header,
                index=index,
            ))

    assert rp.style['body']['margin'] == '20px'
    assert rp.style['h1']['color'] == 'steelblue'
    assert rp.style['.scrollable-table-container']['max-height'] == '200px'
    assert rp._data['content'][0].tagname == 'h1'
    assert rp._data['content'][1].tagname == 'div'

    out_html = 'tests/my_report.html'
    output(rp, out_html)


def test_report_with_tabs():
    rp = shirotsubaki.report.ReportWithTabs()
    rp.set('title', 'Fruits Fruits Fruits')

    rp.add_tab('apple')
    rp.append_as_toggle('001', 'This message will be collapsed inside the toggle.')
    rp.append_as_minitabs('001', {
        'Taro': 'Taro Taro',
        'Jiro': 'Jiro Jiro',
        'Saburo': 'Saburo Saburo',
    })

    rp.add_tab('banana', 'banana banana')

    rp.add_tab('cherry')
    for _ in range(3):
        rp.append(Elm('h3', 'table'))
        rp.append(create_table())
    rp.style.add_scrollable_table()

    assert rp._data['title'] == 'Fruits Fruits Fruits'
    assert 'apple' in rp.tabs
    assert 'banana' in rp.tabs
    assert 'cherry' in rp.tabs

    out_html = 'tests/my_report_with_tabs.html'
    output(rp, out_html)


def test_style():
    sty0 = Style({'body': {'color': 'red'}})
    sty1 = Style({'body': {'background': 'pink'}})
    sty2 = Style({'body': {'color': 'blue'}})

    sty0 += sty1
    assert sty0['body']['color'] == 'red'
    assert sty0['body']['background'] == 'pink'

    sty0 += sty2
    assert sty0['body']['color'] == 'blue'
    assert sty0['body']['background'] == 'pink'

    sty0.add_scrollable_table()
    assert sty0['.scrollable-table-container']['overflow'] == 'auto'


def test_report_hoge():
    rp = shirotsubaki.report.Report(title='Fruits')
    out_html = 'tests/my_report_hoge.html'
    output(rp, out_html)

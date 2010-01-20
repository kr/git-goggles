from gitgoggles.utils import force_unicode, force_str, console, colored, abbreviate, terminal_width

class AsciiCell(object):
    def __init__(self, value, color=None, background=None, reverse=False,
                 abbreviate=abbreviate, abbreviate_min_width=0):
        self.value = force_unicode(value)
        self.color = color
        self.background = background
        self.attrs = reverse and ['reverse'] or []
        self.width = len(self.value)
        self.abbreviate = abbreviate
        self.abbreviate_min_width = abbreviate_min_width

class AsciiTable(object):
    def __init__(self, headers):
        self.headers = [ isinstance(x, AsciiCell) and x or AsciiCell(x) for x in headers ]
        self.data = []
        self._widths = [ x.width for x in self.headers ]
        self.spacing = 1
        self.width_limit = terminal_width()

    def add_row(self, data):
        if len(data) != len(self.headers):
            raise Exception('The number of columns in a row must be equal to the header column count.')
        self.data.append([ isinstance(x, AsciiCell) and x or AsciiCell(x) for x in data ])

    def __str__(self):
        self.__unicode__()

    def __unicode__(self):
        self._print()

    def _print_horizontal_rule(self):
        bits = []
        first_column = True
        for column, width in zip(self.headers, self._widths):
            if not first_column: console(u'-' * self.spacing)
            first_column = False
            console(u'-' * width)
        console(u'\n')

    def _print_headers(self):
        self._print_row(self.headers)

    def _print_data(self):
        for row in self.data:
            self._print_row(row)

    def _print_row(self, row):
        bits = []
        first_column = True
        for column, cell, width in zip(self.headers, row, self._widths):
            if not first_column: console(u' ' * self.spacing)
            first_column = False
            padded_value = column.abbreviate(cell.value.ljust(width), limit=width)
            console(colored(padded_value, cell.color, cell.background, attrs=cell.attrs))
        console(u'\n')

    def render(self):
        self._calculate_widths()

        self._print_horizontal_rule()
        self._print_headers()
        self._print_horizontal_rule()
        self._print_data()
        self._print_horizontal_rule()

    def _calculate_widths(self):
        for data in self.data:
            for column, cell in enumerate(data):
                self._widths[column] = max(self._widths[column], cell.width)

        # Now alter the column widths so that rows do not wrap. Proceed from
        # right to left, shortening each column only as much as possible, but
        # no more than necessary, stopping when the table is narrow enough to
        # fit.
        for i in range(len(self.headers) - 1, -1, -1):
            row_width = sum(self._widths) + self.spacing * (len(self.headers) - 1)
            if self.width_limit >= row_width:
                break

            over = row_width - self.width_limit
            fit = self._widths[i] - over
            col_min = min(self._widths[i], self.headers[i].abbreviate_min_width)
            self._widths[i] = max(fit, col_min)

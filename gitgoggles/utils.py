import copy
import sys
import os
import unicodedata

def disable_colored_func(text, *args, **kwargs):
    return text

try:
    from termcolor import colored as colored_func
except ImportError:
    print 'You should run "pip install termcolor" to fully utilize these utilities.'
    colored_func = disable_colored_func

class Colored(object):
    disabled = False
    def __call__(self, *args, **kwargs):
        if self.disabled:
            return disable_colored_func(*args, **kwargs)
        return colored_func(*args, **kwargs)

colored = Colored()

def force_unicode(obj, encoding='utf-8'):
    if isinstance(obj, basestring):
        if not isinstance(obj, unicode):
            obj = unicode(obj, encoding)
        # Normalize the unicode data to have characters that in NFKD format would be represented by 2 characters, instead of 1.
        obj = unicodedata.normalize('NFKC', obj)
    return obj

def force_str(obj, encoding='utf-8'):
    if isinstance(obj, basestring):
        if not isinstance(obj, str):
            obj = obj.encode(encoding)
    return obj

def console(obj):
    sys.stdout.write(force_str(obj))

class AccumulatorDict(dict):
    def __init__(self, default, *args, **kwargs):
        self.__default = default

    def __getitem__(self, key):
        if key not in self:
            self[key] = copy.copy(self.__default)
        return super(AccumulatorDict, self).__getitem__(key)

def memoize(func):
    def _(self, *args, **kwargs):
        if not hasattr(self, '__memoize_cache'):
            self.__memoize_cache = AccumulatorDict(AccumulatorDict({}))
        key = tuple([ tuple(args), tuple([ tuple([x, y]) for x, y in kwargs.items() ]) ])
        if key not in self.__memoize_cache[func]:
            self.__memoize_cache[func][key] = func(self, *args, **kwargs)
        return self.__memoize_cache[func][key]
    return _

def abbreviate(s, limit=None, ellipsis=u'...'):
    if limit is None: return s
    if limit >= len(s): return s
    top = limit - len(ellipsis)
    return s[:top] + ellipsis

def abbreviate_ref_name(name, limit=None, part_min_len=1, ellipsis=u'...'):
    if limit is None: return name
    name, limit = unicode(name), int(limit)
    parts = name.split(u'/')
    i, current_len = 0, len('/'.join(parts))
    while i < len(parts) and current_len > limit:
        # Can it possibly be made shorter?
        if len(parts[i]) > part_min_len + len(ellipsis):
            over = current_len + len(ellipsis) - limit
            parts[i] = parts[i][:max(part_min_len, len(parts[i]) - over)] + ellipsis
        i, current_len = i + 1, len('/'.join(parts))
    return '/'.join(parts)

def terminal_width():
    # This probably does not work on windows, but it should work just about
    # everywhere else.
    rows, columns = os.popen('stty size', 'r').read().split()
    return int(columns)

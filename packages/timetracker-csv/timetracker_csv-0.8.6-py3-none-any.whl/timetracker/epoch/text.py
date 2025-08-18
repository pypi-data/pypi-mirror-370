"""Get timetracker data formatted for a report"""

__copyright__ = 'Copyright (C) 2025-present, DV Klopfenstein, PhD. All rights reserved.'
__author__ = "DV Klopfenstein, PhD"

from collections import namedtuple
from datetime import timedelta
from logging import debug
from timetracker.epoch.calc import str_td


# ---------------------------------------------------------------------
def get_data_formatted(timedata, pnum=None):
    """Get timetracker data formatted for a report"""
    has_activity, has_tags = _has_activity_tags(timedata)
    nto = _get_nto(has_activity, has_tags, pnum)
    return FUNCS[(pnum is not None, has_activity, has_tags)](nto, timedata)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def _has_activity_tags(timedata):
    has_activity = False
    has_tags = False
    for ntd in timedata:
        if not has_activity and ntd.activity != '':
            has_activity = True
        if not has_tags and ntd.tags != '':
            has_tags = True
        if has_activity and has_tags:
            break
    return has_activity, has_tags

def _get_nto(has_activity, has_tags, pnum):
    flds = _get_nto_fieldnames(has_activity, has_tags, pnum)
    debug('REPORT FIELDS: %s', flds)
    return namedtuple('TimeText', flds)

def get_fstr(has_activity, has_tags, pnum):
    """Get formatting for printing to stdout"""
    lst = ['{Day:3}', '{Date:10}', '{Start:8}', '{Span:>5}', '{Total:5}']
    if pnum:
        lst.append('{Sum:5}')
    if has_activity:
        lst.append('{Activity:12}')
    lst.append('{Description:60}')
    if has_tags:
        lst.append('{Tags:20}')
    return ' '.join(lst)

def _get_nto_fieldnames(has_activity, has_tags, pnum):
    lst = ['Day', 'Date', 'Start', 'Span', 'Total']
    if pnum:
        lst.append('Sum')
    if has_activity:
        lst.append('Activity')
    lst.append('Description')
    if has_tags:
        lst.append('Tags')
    return lst


def _get_dfmttd_at100(nto, nts, pho=350):
    # pylint: disable=protected-access
    debug('timetext: _get_dfmttd_at100')
    tot = timedelta()
    return [nto._make(_nttxt(ntd) +
        (str_td(tot:=tot+ntd.duration), f'{pho/3600*tot.total_seconds():0.0f}', ntd.message))
        for ntd in nts]

def _get_dfmttd_at000(nto, nts):
    # pylint: disable=protected-access
    debug('timetext: _get_dfmttd_at000')
    tot = timedelta()
    return [nto._make(_nttxt(ntd) +
        (str_td(tot:=tot+ntd.duration), ntd.message))
        for ntd in nts]

def _get_dfmttd_at010(nto, nts):
    # pylint: disable=protected-access
    debug('timetext: _get_dfmttd_at010')
    tot = timedelta()
    return [nto._make(_nttxt(ntd) +
        (str_td(tot:=tot+ntd.duration),
         ntd.activity, ntd.message))
        for ntd in nts]

def _get_dfmttd_at001(nto, nts):
    # pylint: disable=protected-access
    debug('timetext: _get_dfmttd_at001')
    tot = timedelta()
    return [nto._make(_nttxt(ntd) +
        (str_td(tot:=tot+ntd.duration), ntd.message, ntd.tags))
        for ntd in nts]

def _get_dfmttd_at011(nto, nts):
    # pylint: disable=protected-access
    debug('timetext: _get_dfmttd_at011')
    tot = timedelta()
    return [nto._make(_nttxt(ntd) +
        (str_td(tot:=tot+ntd.duration), ntd.activity, ntd.message, ntd.tags))
        for ntd in nts]

def _nttxt(ntd):
    return (ntd.start_datetime.strftime('%a'),       # weekday
            ntd.start_datetime.strftime('%Y-%m-%d'), # FMTDT12HM
            ntd.start_datetime.strftime('%I:%M %p'),
            f'{str_td(ntd.duration)}')               # span (HH:MM)

FUNCS = {
    ( True, False, False): _get_dfmttd_at100,
    (False, False, False): _get_dfmttd_at000,
    (False, False, True) : _get_dfmttd_at001,
    (False,  True, False): _get_dfmttd_at010,
    (False,  True, True) : _get_dfmttd_at011,
}


# Copyright (C) 2025-present, DV Klopfenstein, PhD. All rights reserved.

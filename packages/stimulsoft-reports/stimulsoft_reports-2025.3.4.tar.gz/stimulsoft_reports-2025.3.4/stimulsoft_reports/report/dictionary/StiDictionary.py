from __future__ import annotations

import typing

from ...classes.StiElement import StiElement
from .StiVariable import StiVariable

if typing.TYPE_CHECKING:
    from ..StiReport import StiReport


class StiDictionary(StiElement):

### Properties

    report: StiReport = None
    variables: list[StiVariable] = None


### HTML

    def getHtml(self):
        result: str = ''
        for variable in self.variables:
            result += variable.getHtml()
            result += f'{self.report.id}.dictionary.variables.add({variable.id});\n'

        return super().getHtml() + result


### Constructor

    def __init__(self, report: StiReport):
        self.report = report
        self.variables = []

from stimulsoft_reports.classes.StiFileResult import StiFileResult
from stimulsoft_reports.resources.StiResourcesHelper import StiResourcesHelper as StiReportResourcesHelper

from .scripts.StiScriptResource import StiScriptResource


class StiResourcesHelper:

### Public
    
    def getResult(name: str) -> StiFileResult:
        if len(name or '') == 0:
            return StiFileResult.getError('Resource name not specified.')
        
        if (name.endswith('.js') and name.startswith('stimulsoft.dashboards')):
            return StiScriptResource.getResult(name)
        
        return StiReportResourcesHelper.getResult(name)
    
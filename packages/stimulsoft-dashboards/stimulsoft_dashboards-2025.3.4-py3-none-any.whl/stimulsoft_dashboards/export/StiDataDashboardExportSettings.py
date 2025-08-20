from stimulsoft_reports.export.enums import StiDataType

from ..export.enums import StiDashboardExportFormat
from .StiDashboardExportSettings import StiDashboardExportSettings


class StiDataDashboardExportSettings(StiDashboardExportSettings):

### Properties

    dataType: StiDataType = StiDataType.CSV
    """[enum] Specifies the type of the data."""


### Helpers

    def getExportFormat(self):
        return StiDashboardExportFormat.DATA

from ..export.enums import StiDashboardExportFormat, StiDashboardScaleMode
from .StiDashboardExportSettings import StiDashboardExportSettings


class StiExcelDashboardExportSettings(StiDashboardExportSettings):

### Properties

    scaleMode: StiDashboardScaleMode = StiDashboardScaleMode.VIEW_SIZE
    """[enum] Specifies the scaling mode of the dashboard content."""

    imageQuality: int = 200
    """The image quality of images which will be exported to a result file."""

    exportDataOnly: bool = False
    """Specifies that only data will be exported."""


### Helpers

    def getExportFormat(self):
        return StiDashboardExportFormat.EXCEL
from stimulsoft_reports.export.enums import StiImageType

from ..export.enums import StiDashboardExportFormat, StiDashboardScaleMode
from .StiDashboardExportSettings import StiDashboardExportSettings


class StiImageDashboardExportSettings(StiDashboardExportSettings):

### Properties

    scaleMode: StiDashboardScaleMode = StiDashboardScaleMode.VIEW_SIZE
    """[enum] Specifies the scaling mode of the dashboard content."""

    imageType: StiImageType = StiImageType.SVG
    """[enum] Specifies the type of exported images."""

    scale: int = 100
    """The scale of an exported document."""

    renderSinglePage: bool = True
    """Export only the first page if elements require multiple pages to be rendered."""


### Helpers

    def getExportFormat(self):
        return StiDashboardExportFormat.IMAGE
    
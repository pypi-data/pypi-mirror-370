from ..export.enums import StiDashboardExportFormat, StiDashboardScaleMode
from .StiDashboardExportSettings import StiDashboardExportSettings


class StiHtmlDashboardExportSettings(StiDashboardExportSettings):

### Properties

    scaleMode: StiDashboardScaleMode = StiDashboardScaleMode.VIEW_SIZE
    """[enum] Specifies the scaling mode of the dashboard content."""

    imageQuality: int = 200
    """The image quality of images which will be exported to a result file."""

    scale: int = 100
    """The scale of an exported document."""

    enableAnimation: bool = True
    """Enables or disables animation of dashboard elements in the exported HTML file."""


### Helpers

    def getExportFormat(self):
        return StiDashboardExportFormat.HTML
    
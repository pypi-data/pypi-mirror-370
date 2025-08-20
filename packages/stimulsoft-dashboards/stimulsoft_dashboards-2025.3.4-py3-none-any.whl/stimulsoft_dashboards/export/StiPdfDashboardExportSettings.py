from stimulsoft_reports.enums import PaperKind
from stimulsoft_reports.report.enums import StiPageOrientation

from ..export.enums import StiDashboardExportFormat, StiDashboardScaleMode
from .StiDashboardExportSettings import StiDashboardExportSettings


class StiPdfDashboardExportSettings(StiDashboardExportSettings):

### Properties

    scaleMode: StiDashboardScaleMode = StiDashboardScaleMode.VIEW_SIZE
    """[enum] Specifies the scaling mode of the dashboard content."""

    autoPrint = False
    """Indicates that an exported document will start printing after opening."""

    imageQuality: int = 200
    """The image quality of images which will be exported to a result file."""

    paperSize: PaperKind = PaperKind.A4
    """[enum] The page size of a resulting document."""

    orientation: StiPageOrientation = StiPageOrientation.LANDSCAPE
    """[enum] The page orientation of a resulting document."""


### Helpers

    def getExportFormat(self):
        return StiDashboardExportFormat.PDF
    
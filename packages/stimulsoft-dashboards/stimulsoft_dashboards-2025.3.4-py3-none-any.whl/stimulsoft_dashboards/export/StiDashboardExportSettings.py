from stimulsoft_reports.export.StiExportSettings import StiExportSettings


class StiDashboardExportSettings(StiExportSettings):

### Properties

    renderBorders: bool = True
    """Enables or disables rendering of the defined element borders."""

    renderSingleElement: bool = False
    """Enables or disables exporting a single dashboard element to the entire page."""

    renderSinglePage: bool = False
    """Enables or disables exporting only the first page if elements require multiple pages to be rendered."""

    applyDefaultFilters: bool = False
    """Applies default filters to dashboard elements."""

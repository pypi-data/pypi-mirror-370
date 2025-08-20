class WorkToolMCPError(Exception):
    """Base exception for Work Tool MCP errors."""
    pass

class WorkbookError(WorkToolMCPError):
    """Raised when workbook operations fail."""
    pass

class SheetError(WorkToolMCPError):
    """Raised when sheet operations fail."""
    pass

class DataError(WorkToolMCPError):
    """Raised when data operations fail."""
    pass

class ValidationError(WorkToolMCPError):
    """Raised when validation fails."""
    pass

class FormattingError(WorkToolMCPError):
    """Raised when formatting operations fail."""
    pass

class CalculationError(WorkToolMCPError):
    """Raised when formula calculations fail."""
    pass

class PivotError(WorkToolMCPError):
    """Raised when pivot table operations fail."""
    pass

class ChartError(WorkToolMCPError):
    """Raised when chart operations fail."""
    pass

class PDFError(WorkToolMCPError):
    """Raised when PDF operations fail."""
    pass

class PDFParsingError(PDFError):
    """Raised when PDF parsing fails."""
    pass

class PDFProcessingError(PDFError):
    """Raised when PDF processing fails."""
    pass

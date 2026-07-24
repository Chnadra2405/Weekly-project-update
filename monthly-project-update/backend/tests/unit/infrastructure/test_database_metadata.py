from sqlalchemy.dialects import mssql
from sqlalchemy.schema import CreateTable

from app.infrastructure.database import AttachmentModel, ProjectUpdateModel


def test_models_compile_to_sql_server_types_and_constraints() -> None:
    dialect = mssql.dialect()
    project_sql = str(CreateTable(ProjectUpdateModel.__table__).compile(dialect=dialect))
    attachment_sql = str(CreateTable(AttachmentModel.__table__).compile(dialect=dialect))

    assert "UNIQUEIDENTIFIER" in project_sql
    assert "reporting_month DATE NOT NULL" in project_sql
    assert "achievements NVARCHAR(max) NOT NULL" in project_sql
    assert "created_at DATETIMEOFFSET NOT NULL" in project_sql
    assert "DAY(reporting_month) = 1" in project_sql
    assert "DEFAULT 'PENDING'" in project_sql
    assert "project_update_id UNIQUEIDENTIFIER NOT NULL" in attachment_sql
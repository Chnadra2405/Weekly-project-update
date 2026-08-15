from sqlalchemy.dialects import mssql
from sqlalchemy.schema import CreateTable

from app.infrastructure.database import ProjectUpdateModel


def test_models_compile_to_sql_server_types_and_constraints() -> None:
    dialect = mssql.dialect()
    project_sql = str(CreateTable(ProjectUpdateModel.__table__).compile(dialect=dialect))

    assert "UNIQUEIDENTIFIER" in project_sql
    assert "start_of_week DATE NOT NULL" in project_sql
    assert "end_of_week DATE NOT NULL" in project_sql
    assert "achievements NVARCHAR(max) NOT NULL" in project_sql
    assert "created_at DATETIMEOFFSET NOT NULL" in project_sql
    assert "end_of_week = DATEADD(day, 6, start_of_week)" in project_sql
    assert "reporting_month" not in project_sql
    assert "delivery_status" not in project_sql
from data_pipeline_helper_vi.data_pipeline_helper.sql_builder import build_select_query, build_insert_query

def test_build_select_query():
    query = build_select_query(
        table="my_table",
        columns=["col1", "col2"],
        where_clause="col1 > 10"
    )
    assert query == "SELECT col1, col2 FROM my_table WHERE col1 > 10"


def test_build_insert_query():
    query = build_insert_query(
        table="my_table",
        columns=["col1", "col2"],
        values=[1, 2]
    )
    assert query == "INSERT INTO my_table (col1, col2) VALUES (1, 2)"

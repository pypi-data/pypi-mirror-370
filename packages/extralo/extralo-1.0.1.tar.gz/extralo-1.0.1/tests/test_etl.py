# ETL:

# before validator deve validar todos as Keys q saíram do source e deve retornar
# trasnformer deve aceitar como input as mesmas Keys do sources.
# destinations deve aceitar como input as mesmas Keys exportadas do trasnformer

from typing import TypedDict
from unittest.mock import MagicMock, Mock

import pandas as pd
import pandera as pa
import pytest

from extralo.etl import ETL, IncompatibleStepsError


@pytest.fixture
def mock_data():
    return MagicMock(spec=pd.DataFrame)


@pytest.fixture
def mock_source(mock_data):
    class SourceStub:
        def extract(self):
            return mock_data

    return SourceStub()


@pytest.fixture
def mock_trans():
    class TransStub:
        def transform(self, source):
            return {"source_trans": source["source"]}

    return TransStub()


@pytest.fixture
def mock_dest():
    class DestStub:
        def load(self, data):
            return

    return DestStub()


@pytest.fixture
def mock_before_schema(mock_data):
    schema = MagicMock(spec=pa.DataFrameModel)
    schema.validate = Mock(return_value=mock_data)
    return schema


@pytest.fixture
def mock_after_schema(mock_data):
    schema = MagicMock(spec=pa.DataFrameModel)
    schema.validate = Mock(return_value=mock_data)
    return schema


def test_etl_delegates_to_components(mock_source, mock_trans, mock_dest, mock_before_schema, mock_after_schema):
    etl = ETL(
        sources={"source": mock_source},
        transformer=mock_trans,
        destinations={"source_trans": [mock_dest]},
        before_schemas={"source": mock_before_schema},
        after_schemas={"source_trans": mock_after_schema},
    )

    etl.execute()

    assert True


def test_etl_works_without_transformer(mock_source, mock_dest, mock_before_schema):
    etl = ETL(
        sources={"source": mock_source},
        destinations={"source": [mock_dest]},
        before_schemas={"source": mock_before_schema},
    )

    etl.execute()

    assert True


def test_etl_works_without_before_schema(mock_source, mock_trans, mock_dest, mock_before_schema, mock_after_schema):
    etl = ETL(
        sources={"source": mock_source},
        transformer=mock_trans,
        destinations={"source_trans": [mock_dest]},
        after_schemas={"source_trans": mock_after_schema},
    )

    etl.execute()

    assert True


def test_etl_works_without_after_schema(mock_source, mock_trans, mock_dest, mock_before_schema, mock_after_schema):
    etl = ETL(
        sources={"source": mock_source},
        transformer=mock_trans,
        destinations={"source_trans": [mock_dest]},
        before_schemas={"source": mock_before_schema},
    )

    etl.execute()

    assert True


def test_etl_fails_when_source_and_before_validator_are_incompatible(
    mock_source, mock_trans, mock_dest, mock_before_schema, mock_after_schema
):
    with pytest.raises(IncompatibleStepsError, match="extract"):
        ETL(
            sources={"source": mock_source},
            transformer=mock_trans,
            destinations={"source_trans": [mock_dest]},
            before_schemas={"not_source": mock_before_schema},
            after_schemas={"source_trans": mock_after_schema},
        )


def test_etl_fails_when_transformer_and_after_validator_are_incompatible(
    mock_source, mock_trans, mock_dest, mock_before_schema, mock_after_schema
):
    etl = ETL(
        sources={"source": mock_source},
        transformer=mock_trans,
        destinations={"source_trans": [mock_dest]},
        before_schemas={"source": mock_before_schema},
        after_schemas={"not_source_trans": mock_after_schema},
    )
    with pytest.raises(IncompatibleStepsError, match="transform"):
        etl.execute()


def test_etl_fails_when_transformer_and_destination_are_incompatible(
    mock_source, mock_trans, mock_dest, mock_before_schema, mock_after_schema
):
    etl = ETL(
        sources={"source": mock_source},
        transformer=mock_trans,
        destinations={"not_source_trans": [mock_dest]},
        before_schemas={"source": mock_before_schema},
        after_schemas={"source_trans": mock_after_schema},
    )
    with pytest.raises(IncompatibleStepsError, match="load"):
        etl.execute()


def test_etl_fails_on_init_when_transformer_and_destination_are_incompatible_and_transformer_output_is_a_typed_dict(
    mock_source, mock_dest, mock_before_schema, mock_after_schema
):
    class TransformerOutputStub(TypedDict):
        source_trans: pd.DataFrame

    class TransformerStub:
        def transform(self, source) -> TransformerOutputStub:
            return source

    with pytest.raises(IncompatibleStepsError, match="load"):
        ETL(
            sources={"source": mock_source},
            transformer=TransformerStub(),
            destinations={"not_source_trans": [mock_dest]},
            before_schemas={"source": mock_before_schema},
            after_schemas={"source_trans": mock_after_schema},
        )


def test_etl_fails_on_init_when_transformer_and_after_validator_are_incompatible_and_transformer_output_is_a_typed_dict(
    mock_source, mock_dest, mock_before_schema, mock_after_schema
):
    class TransformerOutputStub(TypedDict):
        source_trans: pd.DataFrame

    class TransformerStub:
        def transform(self, source) -> TransformerOutputStub:
            return source

    with pytest.raises(IncompatibleStepsError, match="transform"):
        ETL(
            sources={"source": mock_source},
            transformer=TransformerStub(),
            destinations={"source_trans": [mock_dest]},
            before_schemas={"source": mock_before_schema},
            after_schemas={"not_source_trans": mock_after_schema},
        )


def test_etl_fails_when_source_and_transformer_are_incompatible(
    mock_source, mock_dest, mock_before_schema, mock_after_schema
):
    class TransformerStub:
        def transform(self, not_source):
            return not_source

    with pytest.raises(IncompatibleStepsError, match="transform"):
        ETL(
            sources={"source": mock_source},
            transformer=TransformerStub(),
            destinations={"source_trans": [mock_dest]},
            before_schemas={"source": mock_before_schema},
            after_schemas={"source_trans": mock_after_schema},
        )

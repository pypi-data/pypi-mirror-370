import pytest
from unittest.mock import patch, MagicMock, mock_open
import pandas as pd
import networkx as nx

from pyntegritydb.cli import main

@patch('pyntegritydb.cli.report')
@patch('pyntegritydb.cli.metrics')
@patch('pyntegritydb.cli.schema')
@patch('pyntegritydb.cli.connect')
@patch('argparse.ArgumentParser.parse_args')
def test_main_cli_flow(
    mock_parse_args, mock_connect, mock_schema, mock_metrics, mock_report
):
    """
    Prueba el flujo completo de la CLI, simulando cada módulo.
    """
    # 1. Configuración de los mocks
    # Simular argumentos de línea de comandos
    mock_parse_args.return_value = MagicMock(
        db_uri="sqlite:///test.db", 
        format="cli",
        config=None,
        visualize=False
    )
    
    # Simular un grafo y un dataframe de resultados
    mock_graph = nx.DiGraph()
    mock_graph.add_edge("table_a", "table_b")
    mock_df = pd.DataFrame({
        'referencing_table': ['table_a'],
        'validity_rate': [0.99]
    })

    # Asignar los valores de retorno a los módulos simulados
    mock_connect.create_db_engine.return_value = MagicMock()
    mock_schema.get_schema_graph.return_value = mock_graph
    mock_metrics.analyze_database_completeness.return_value = mock_df
    mock_report.generate_report.return_value = "Reporte de prueba"

    # 2. Ejecutar la función principal
    main()

    # 3. Verificaciones
    # Verificar que cada módulo fue llamado en el orden correcto
    mock_connect.create_db_engine.assert_called_once_with("sqlite:///test.db")
    mock_schema.get_schema_graph.assert_called_once()
    mock_metrics.analyze_database_completeness.assert_called_once()
    mock_report.generate_report.assert_called_once()
    args, kwargs = mock_report.generate_report.call_args
    assert kwargs['report_format'] == 'cli'
    pd.testing.assert_frame_equal(kwargs['completeness_df'], mock_df)
    assert 'consistency_df' in kwargs # Verifica que el otro argumento también esté presente


@patch('pyntegritydb.cli.connect.create_db_engine')
@patch('argparse.ArgumentParser.parse_args')
def test_main_cli_handles_connection_error(mock_parse_args, mock_create_engine):
    """
    Prueba que la CLI maneja correctamente un error de conexión.
    """
    # Simular argumentos
    mock_parse_args.return_value = MagicMock(
        db_uri="invalid_uri", 
        format="cli",
        config=None
    )
    
    # Simular que la conexión falla
    mock_create_engine.side_effect = ValueError("Conexión fallida")

    # Ejecutar main y verificar que no se lance una excepción no controlada
    main()

    # Verificar que se intentó conectar
    mock_create_engine.assert_called_once_with("invalid_uri")


@patch('pyntegritydb.cli.report')
@patch('pyntegritydb.cli.metrics')
@patch('pyntegritydb.cli.schema')
@patch('pyntegritydb.cli.connect')
@patch('pyntegritydb.cli.config')
@patch('pyntegritydb.cli.alerts')
@patch('argparse.ArgumentParser.parse_args')
def test_main_cli_flow_with_config(
    mock_parse_args,
    mock_alerts,
    mock_config, 
    mock_connect, mock_schema, 
    mock_metrics, 
    mock_report
):
    """
    Prueba el flujo completo de la CLI cuando se proporciona un archivo de configuración.
    """
    # 1. Configuración de Mocks
    # Simular argumentos, incluyendo --config
    mock_parse_args.return_value = MagicMock(
        db_uri="sqlite:///test.db", 
        format="cli",
        alerts="[]",
        config="config.yml",
        visualize=False
    )
    
    # Simular datos de retorno
    mock_config.load_config.return_value = {"thresholds": {}, "consistency_checks": {}}
    mock_alerts.check_thresholds.return_value = []

    mock_completeness_df = pd.DataFrame({
        'referencing_table': ['orders'],
        'validity_rate': [0.99]
    })
    mock_consistency_df = pd.DataFrame({
        'referencing_table': ['orders'],
        'referencing_attribute': ['customer_name'],
        'consistency_rate': [0.95]
    })
    mock_metrics.analyze_database_completeness.return_value = mock_completeness_df
    mock_metrics.analyze_attribute_consistency.return_value = mock_consistency_df
    
    # Simular un grafo CON relaciones
    mock_graph = nx.DiGraph()
    mock_graph.add_edge("orders", "users")
    mock_schema.get_schema_graph.return_value = mock_graph

    # 2. Ejecución
    main()

    # 3. Verificaciones
    # Verificar que se cargó la configuración
    mock_config.load_config.assert_called_once_with("config.yml")
    
    # Verificar que se llamaron AMBOS análisis
    mock_metrics.analyze_database_completeness.assert_called_once()
    mock_metrics.analyze_attribute_consistency.assert_called_once()

    # Verificar que el módulo de alertas fue llamado correctamente
    mock_alerts.check_thresholds.assert_called_once()
    
    # Verificar que el reporte se genera con ambos DataFrames
    mock_report.generate_report.assert_called_once()
    args, kwargs = mock_report.generate_report.call_args
    assert 'completeness_df' in kwargs
    assert 'consistency_df' in kwargs
    assert not kwargs['completeness_df'].empty
    assert not kwargs['consistency_df'].empty


@patch('pyntegritydb.cli.report')
@patch('pyntegritydb.cli.metrics')
@patch('pyntegritydb.cli.schema')
@patch('pyntegritydb.cli.connect')
@patch('pyntegritydb.cli.config')
@patch('pyntegritydb.cli.alerts')
@patch('argparse.ArgumentParser.parse_args')
@patch('pyntegritydb.cli.sys.exit')
def test_main_cli_exits_with_error_on_alerts(
    mock_exit, mock_parse_args, mock_alerts, mock_config, mock_connect, mock_schema, mock_metrics, mock_report
):
    """Prueba que la CLI sale con código 1 si se encuentran alertas."""
    # Configurar mocks para un flujo completo
    mock_parse_args.return_value = MagicMock(
        db_uri="sqlite:///test.db",
        format="cli",
        config="config.yml",
        visualize=False,       
        output_image=None,     
        output_file=None       
    )
    mock_config.load_config.return_value = {"thresholds": {}}
    mock_metrics.analyze_database_completeness.return_value = pd.DataFrame()
    mock_metrics.analyze_attribute_consistency.return_value = pd.DataFrame()
    
    # Simular que se encontraron alertas
    mock_alerts.check_thresholds.return_value = ["ALERTA: Algo salió mal"]

    # Simula un grafo con al menos una relación
    mock_schema.get_schema_graph.return_value = nx.DiGraph([("a", "b")])

    # Ejecutar la función principal
    main()

    # Verificar que se llamó a sys.exit con el código de error 1
    mock_alerts.check_thresholds.assert_called_once()
    mock_exit.assert_called_once_with(1)


@patch('pyntegritydb.cli.visualize')
@patch('pyntegritydb.cli.report')
@patch('pyntegritydb.cli.metrics')
@patch('pyntegritydb.cli.schema')
@patch('pyntegritydb.cli.connect')
@patch('pyntegritydb.cli.config')
@patch('pyntegritydb.cli.alerts')
@patch('argparse.ArgumentParser.parse_args')
def test_main_cli_with_visualize_flag(
    mock_parse_args, mock_alerts, mock_config, mock_connect, 
    mock_schema, mock_metrics, mock_report, mock_visualize
):
    """Prueba que el módulo de visualización es llamado con el flag --visualize."""
    mock_parse_args.return_value = MagicMock(
        db_uri="sqlite:///test.db",
        format="cli",
        config=None,
        visualize=True, # Simula que el flag está activado
        output_image="test_graph.png"
    )
    
    # Simular datos de retorno necesarios para el flujo
    mock_graph = nx.DiGraph()
    mock_graph.add_edge("table_a", "table_b")
    
    mock_df = pd.DataFrame({
        'referencing_table': ['table_a'],
        'validity_rate': [0.99]
    })
    mock_schema.get_schema_graph.return_value = mock_graph
    mock_metrics.analyze_database_completeness.return_value = mock_df

    main()

    # Verificar que la función de visualización fue llamada con los argumentos correctos
    mock_visualize.visualize_schema_graph.assert_called_once_with(
        graph=mock_graph,
        metrics_df=mock_df,
        output_path="test_graph.png"
    )


@patch('builtins.open', new_callable=mock_open)
@patch('pyntegritydb.cli.report')
@patch('pyntegritydb.cli.metrics')
@patch('pyntegritydb.cli.schema')
@patch('pyntegritydb.cli.connect')
@patch('pyntegritydb.cli.config')
@patch('pyntegritydb.cli.alerts')
@patch('argparse.ArgumentParser.parse_args')
def test_main_cli_writes_to_output_file(
    mock_parse_args, mock_alerts, mock_config, mock_connect,
    mock_schema, mock_metrics, mock_report, mock_open_file
):
    """Prueba que el reporte se escriba en un archivo con --output-file."""
    # Simular argumentos
    mock_parse_args.return_value = MagicMock(
        db_uri="sqlite:///test.db",
        format="json",
        config=None,
        visualize=False,
        output_image=None,
        output_file="report.json"
    )

    # Simula un grafo CON relaciones para que el programa no termine antes.
    mock_graph = nx.DiGraph([("table_a", "table_b")])
    mock_schema.get_schema_graph.return_value = mock_graph
    
    # Simular un flujo simple
    # mock_schema.get_schema_graph.return_value = nx.DiGraph()
    mock_report.generate_report.return_value = "{'report': 'test'}"

    main()

    # Verificar que se intentó abrir el archivo correcto en modo escritura
    mock_open_file.assert_called_once_with("report.json", "w")
    # Verificar que se escribió el contenido del reporte en el archivo
    mock_open_file().write.assert_called_once_with("{'report': 'test'}")



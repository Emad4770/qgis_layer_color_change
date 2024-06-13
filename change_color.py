from PyQt5.QtGui import QColor
from qgis._core import QgsRuleBasedRenderer
from qgis.core import (
    QgsApplication,
    QgsProject,
    QgsSymbol,
)
import sys
import docker


def initialize_qgis(prefix_path=''):
    try:
        QgsApplication.setPrefixPath(prefix_path, True)
        qgs = QgsApplication([], False)
        qgs.initQgis()
        return qgs
    except Exception as e:
        print(f"Error initializing QGIS: {e}")
        sys.exit(1)


def load_project_from_postgis(uri):
    try:
        project = QgsProject.instance()
        project.read(uri)
        return project
    except Exception as e:
        print(f"Error loading project from PostGIS: {e}")
        sys.exit(1)


def find_layer(project, layer_name):
    try:
        for layer in project.mapLayers().values():
            if layer.name() == layer_name:
                print('Layer found!')
                return layer
        print('Layer not found!')
        return None
    except Exception as e:
        print(f"Error finding layer: {e}")
        sys.exit(1)

def modify_layer_colors_based_on_attribute(layer, attribute_name):
    try:
        # Define the rules and their expressions
        rules = [
            {"label": "Low Leakage (0 - 40%)", "expression": f'"{attribute_name}" >= 0 AND "{attribute_name}" < 0.40',
             "color": QColor.fromRgb(0, 0, 255), "width": 0.75},
            {"label": "Medium Leakage (40% - 60%)",
             "expression": f'"{attribute_name}" >= 0.40 AND "{attribute_name}" < 0.60',
             "color": QColor.fromRgb(255, 255, 0),"width": 0.75},
            {"label": "High Leakage (60% - 100%)", "expression": f'"{attribute_name}" >= 0.60 AND "{attribute_name}" <= 1',
             "color": QColor.fromRgb(255, 0, 0),"width": 0.75},
        ]

        # Create the root rule
        root_rule = QgsRuleBasedRenderer.Rule(None)

        # Create rules and add them to the root rule
        for rule in rules:
            # Create a new symbol
            symbol = QgsSymbol.defaultSymbol(layer.geometryType())
            symbol.setColor(rule["color"])
            symbol.symbolLayer(0).setWidth(rule["width"])


            # Create the rule
            new_rule = QgsRuleBasedRenderer.Rule(symbol)
            new_rule.setLabel(rule["label"])
            new_rule.setFilterExpression(rule["expression"])

            # Add the rule to the root rule
            root_rule.appendChild(new_rule)

        # Create the rule-based renderer
        rule_based_renderer = QgsRuleBasedRenderer(root_rule)

        # Apply the new renderer to the layer
        layer.setRenderer(rule_based_renderer)

        # Refresh the layer to apply changes
        layer.triggerRepaint()

        print("Rule-based symbology applied successfully.")
        return True
    except Exception as e:
        print(f"Error modifying layer colors: {e}")
        return False


def save_project_to_postgis(project, uri):
    try:
        project.write(uri)
    except Exception as e:
        print(f"Error saving project to PostGIS: {e}")
        sys.exit(1)
        
        
def reload_qgis_server():
    # Connect to Docker daemon
    client = docker.from_env()

    # Specify your project name and the service (container) name to restart
    project_name = 'qwc-docker'
    service_name = 'qwc-qgis-server'

    # Restart the specific service
    try:
        client.compose.restart(project=project_name, services=[service_name])
        print(f"Successfully restarted service '{service_name}' in Docker Compose project '{project_name}'.")
    except docker.errors.APIError as e:
        print(f"Failed to restart service '{service_name}' in Docker Compose project '{project_name}': {e}")
    


def main():
    qgs = initialize_qgis()

    # PostGIS database connection parameters
    db_params = {
        'dbname': 'qwc_services',
        'host': 'localhost',
        'port': '5432',
        'user': 'postgres',
        'password': 'admin',
        'schema': 'qgs_projects',
        'project': 'testproject'
    }

    # Define the URI for the PostGIS database

    uri = (f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}?sslmode=disable&dbname={db_params['dbname']}&schema={db_params['schema']}"
           f"&project={db_params['project']}")

    project = load_project_from_postgis(uri)

    layer_name = "pipes"
    attribute_name = "leakage_prob"  # Replace with your attribute name
    the_layer = find_layer(project, layer_name)

    if the_layer:
        success = modify_layer_colors_based_on_attribute(the_layer, attribute_name)
        if success:
            save_project_to_postgis(project, uri)
            print("Successfully changed pipe layer colors based on attribute in PostGIS project")
    else:
        print("Layer modification skipped due to missing layer")

    qgs.exitQgis()


if __name__ == "__main__":
    main()

"""translate module contains the implmentation for the `app2run translate` command.
"""

from typing import Dict, List
import click
import yaml
from app2run.config.feature_config_loader import InputType, FeatureConfig,\
    get_feature_config
from app2run.commands.translation_rules.scaling import translate_scaling_features

@click.command(short_help="Translate an app.yaml to migrate to Cloud Run.")
@click.option('-a', '--appyaml', default='app.yaml', show_default=True,
              help='Path to the app.yaml of the app.', type=click.File())
def translate(appyaml) -> None:
    """Translate command translates app.yaml to eqauivalant gcloud command to migrate the \
        GAE App to Cloud Run."""
    input_data = yaml.safe_load(appyaml.read())
    if input_data is None:
        click.echo(f'{appyaml.name} is empty.')
        return

    flags: List[str] = _get_cloud_run_flags(input_data, InputType.APP_YAML)
    service_name = _get_service_name(input_data)
    _generate_output(service_name, flags)

def _get_cloud_run_flags(input_data: Dict, input_type: InputType):
    feature_config : FeatureConfig = get_feature_config()
    return translate_scaling_features(input_data, input_type, feature_config)

def _get_service_name(input_data: Dict):
    if 'service' in input_data:
        custom_service_name = input_data['service'].strip()
        if len(custom_service_name) > 0:
            return custom_service_name
    return 'default'

def _generate_output(service_name: str, flags: List[str]):
    """
    example output:
    gcloud run deploy default \
      --cpu=1GB \
      --memory=2GB \
      --timeout=10m
    """
    click.echo("""Warning:not all configuration could be translated,
for more info use app2run list–incompatible-features.""")
    first_line_ending_char = '' if flags is None or len(flags) == 0 else '\\'
    output = f"""
gcloud run deploy {service_name} {first_line_ending_char}
"""
    if flags is not None:
        for i, flag in enumerate(flags):
            # The last flag does not have tailing \
            output += '  '
            output += flag + ' \\' if i < len(flags) - 1 else flag
            output += '\n'
    click.echo(output)
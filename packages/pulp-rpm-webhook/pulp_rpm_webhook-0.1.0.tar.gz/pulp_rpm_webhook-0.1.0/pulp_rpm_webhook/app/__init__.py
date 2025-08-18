from pulpcore.plugin import PulpPluginAppConfig

class PulpRpmWebhookPluginAppConfig(PulpPluginAppConfig):
  """
  AppConfig for the pulp_rpm_webhook plugin.
  """
  name = "pulp_rpm_webhook.app"
  label = "rpm_webhook"
  version = "0.1.0"
  python_package_name = "pulp_rpm_webhook"
  domain_compatible = True

  def ready(self):
    super().ready()
    from . import signals  # noqa

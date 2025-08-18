# Pulp RPM Webhook Plugin
This plugin extends Pulp's RPM functionality by adding webhook notifications when RPM packages are published or uploaded.

## Features
- Triggers webhooks on RPM package publications
- Provides detailed package information in webhook payloads
- Supports authentication via secret tokens
- Configurable webhook endpoint URL

## Installation
```bash
pip install pulp-rpm-webhook
```

## Configuration
Add the following to your Pulp settings:

```python
# Webhook endpoint URL
RPM_WEBHOOK_URL = "https://your-webhook-endpoint.com"

# Optional secret token for authentication (adds header X-PulpRPM-Token)
RPM_WEBHOOK_SECRET = "your-secret-token"
```

## Usage
Create an RPM repository:
```bash
pulp rpm repository create --name my-rpm-repo
```
2. Create a distribution:
```bash
pulp rpm distribution create --name my-dist --base-path my-dist --repository my-rpm-repo
```
3. Upload or sync RPM packages to the repository. The plugin will automatically trigger webhooks when packages are published.

## Webhook Payload Structure
The webhook payload includes:
- Event type ("rpm.published")
- Repository name
- Publication details
- List of added packages with:
  - Package metadata (name, version, release, etc.)
  - Distribution URLs
  - Upstream URLs (if synced from a remote)

## Contributing
Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License
This project is licensed under the GNU General Public License v2.0 - see the [LICENSE](LICENSE) file for details.

## Links
* [https://github.com/cz-guardian/pulp_rpm_webhook](https://github.com/cz-guardian/pulp_rpm_webhook)
* [https://pypi.org/project/pulp-rpm-webhook/](https://pypi.org/project/pulp-rpm-webhook/)

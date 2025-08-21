# Certbot DNS Micetro Plugin

A certbot plugin for automating DNS-01 challenges using the BlueCat Micetro DNS management system.

## Features

- Automatic DNS TXT record creation and cleanup for ACME challenges
- Support for wildcard certificates
- Secure credential management via INI files
- Preference for external DNS zones over internal zones
- Comprehensive logging and error handling

## Installation

### From PyPI

```bash
pip install certbot-dns-micetro
```

### From Source

```bash
git clone https://github.com/cedarville-university/certbot-dns-micetro.git
cd certbot-dns-micetro
pip install .
```

## Configuration

Create a credentials INI file with your Micetro API details:

```ini
# micetro.ini
# Micetro API credentials for certbot DNS authentication
# Save this file with restricted permissions: chmod 600 micetro.ini

# Username for your Micetro account
certbot_dns_micetro:dns_micetro_username = your_micetro_username

# Password for your Micetro account  
certbot_dns_micetro:dns_micetro_password = your_micetro_password

# Micetro API base URL (include the protocol and port if needed)
# Example: https://ipam.yourcompany.com/mmws/api/v2
certbot_dns_micetro:dns_micetro_url = https://your-micetro-server/mmws/api/v2
```

**Important:** Secure your credentials file:
```bash
chmod 600 micetro.ini
```

## Usage

### Obtain a certificate

```bash
certbot certonly \
  --authenticator certbot-dns-micetro:dns-micetro \
  --certbot-dns-micetro:dns-micetro-credentials /path/to/micetro.ini \
  -d example.com
```

### Obtain a wildcard certificate

```bash
certbot certonly \
  --authenticator certbot-dns-micetro:dns-micetro \
  --certbot-dns-micetro:dns-micetro-credentials /path/to/micetro.ini \
  -d example.com \
  -d "*.example.com"
```

### Certificate renewal

Certificates obtained with this plugin will be automatically renewed by certbot using the same DNS challenge method.

## API Requirements

This plugin requires:
- Micetro DNS management system with API access
- Valid user account with DNS zone management permissions
- Network connectivity to the Micetro API endpoint

The plugin authenticates using username/password credentials and obtains a session token from the `/sessions` endpoint.

## Zone Selection

When multiple DNS zones exist for the same domain (e.g., internal and external views), this plugin will:
1. Prefer external zones over internal zones
2. Use the first available zone if no external zone is found

## Troubleshooting

### Authentication Issues

- Verify your credentials in the INI file
- Ensure the Micetro API URL is correct and accessible
- Check that your user account has appropriate permissions

### DNS Issues

- Verify that the domain's DNS zone is managed by Micetro
- Ensure the zone allows dynamic DNS updates
- Check network connectivity to the Micetro server

### Debugging

Enable debug logging to troubleshoot issues:

```bash
certbot certonly \
  --authenticator certbot-dns-micetro:dns-micetro \
  --certbot-dns-micetro:dns-micetro-credentials /path/to/micetro.ini \
  -d example.com \
  --debug
```

## Development

### Setting up development environment

```bash
git clone https://github.com/cedarville-university/certbot-dns-micetro.git
cd certbot-dns-micetro
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
pip install -r requirements.txt
```

### Running tests

```bash
python -m pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built on the [certbot](https://certbot.eff.org/) framework
- Designed for [BlueCat Micetro](https://www.bluecatnetworks.com/) DNS management
- Inspired by other certbot DNS plugins

## Support

For issues and questions:
- Open an issue on [GitHub](https://github.com/cedarville-university/certbot-dns-micetro/issues)
- Check the certbot documentation for general SSL certificate help
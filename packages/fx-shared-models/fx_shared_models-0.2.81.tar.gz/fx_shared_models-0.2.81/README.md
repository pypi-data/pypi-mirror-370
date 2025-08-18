# FX Shared Models

A Django package containing shared models and configurations for the FX Backend system. This package provides base models for customers and system settings that can be extended using proxy models in your Django applications.

## Features

- Customer Models
  - Base customer model with essential fields
  - Customer settings and details
  - Customer authentication
  - Flexible proxy model support

- System Settings Models
  - Email configuration management
  - System-wide settings
  - Extensible settings framework

## Installation

You can install the package using pip:

```bash
pip install fx-shared-models
```

For development, you can install from source:

```bash
git clone https://github.com/yourusername/fx-shared-models.git
cd fx-shared-models
pip install -e .
```

## Quick Start

1. Add the shared models to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    ...
    'shared_models.customers.apps.CustomersConfig',  # Base models
    'shared_models.system_settings.apps.SystemSettingsConfig',  # Base system settings
    ...
]
```

2. Create proxy models in your app:

```python
# your_app/models.py
from shared_models.customers.models import Customer as BaseCustomer

class Customer(BaseCustomer):
    class Meta:
        proxy = True
        
    # Add your custom methods here
```

## Usage Examples

### Customer Models

```python
# Using base customer model
from shared_models.customers.models import Customer

# Create a new customer
customer = Customer.objects.create(
    email='customer@example.com',
    first_name='John',
    last_name='Doe'
)

# Using proxy model in your app
from your_app.models import Customer

# Your custom methods will be available
customer = Customer.objects.create_customer(
    email='customer@example.com',
    first_name='John',
    last_name='Doe'
)
```

### System Settings

```python
from shared_models.system_settings.models import EmailConfiguration

# Create email configuration
email_config = EmailConfiguration.objects.create(
    name='SMTP Config',
    provider='smtp',
    from_email='noreply@example.com'
)
```

## Model Structure

### Customer Models

- `Customer`: Base customer model with essential fields
  - Personal information (name, email, phone)
  - Status fields (is_funded, is_client, is_ib)
  - KYC status tracking
  - IB relationship management

### System Settings Models

- `SystemSetting`: Base settings model
  - Configuration management
  - Status tracking
  - Metadata storage

- `EmailConfiguration`: Email provider settings
  - SMTP configuration
  - Provider management
  - Email templates

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Requirements

- Python >= 3.8
- Django >= 3.0
- django-environ >= 0.10.0

## Support

For support, please open an issue in the GitHub repository or contact the development team. 
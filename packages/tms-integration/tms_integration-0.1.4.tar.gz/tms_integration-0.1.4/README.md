# F-ONE Group TMS Integration

Welcome to the F-ONE Group TMS Integration package! This Python library is designed to streamline the integration process with various Transportation Management Systems (TMS). It provides robust tools and utilities to facilitate seamless communication and data exchange between your systems and supported TMS platforms.

## Features
- **Lis Winsped Integration**: Comprehensive support for integrating with the Lis Winsped TMS, including models and utilities for handling various data types.
- **Carlo Integration**: (Coming soon) Future support for the Carlo TMS platform.
- **Utilities**: Includes XML handling and SFTP utilities to simplify data transfer and processing.

## Installation
To install the library, use pip:

```bash
pip install fone-tms-integration
```

## Usage
Here is a quick example to get started:

```python
from tms_integration.lis_winsped import lis_winsped

# Example usage
response = lis_winsped.some_function()
print(response)
```

For detailed usage instructions, please refer to the documentation provided in the respective modules.

## Documentation
The library is organized into the following modules:

### Lis Winsped
- Models for handling various data types such as orders, ADR, and more.
- Utilities for interacting with the Lis Winsped TMS API.

### Carlo (Coming Soon)
- Planned support for Carlo TMS integration.

### Utilities
- XML handling utilities.
- SFTP utilities for secure file transfers.

## Contributing
We welcome contributions to enhance the functionality of this library. To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix (`git checkout -b feature-branch`).
3. Commit your changes with clear and concise messages (`git commit -am 'Add new feature'`).
4. Push your branch to your fork (`git push origin feature-branch`).
5. Submit a pull request for review.

## License
This project is licensed under the Apache 2.0 License. See the LICENSE file for more details.

## Support
For any issues or questions, please open an issue on the GitHub repository or contact the maintainers directly.
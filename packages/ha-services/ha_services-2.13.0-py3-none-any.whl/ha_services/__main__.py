"""
    Allow ha_services to be executable
    through `python -m ha_services`.
"""

from ha_services.cli_app import main


if __name__ == '__main__':
    main()

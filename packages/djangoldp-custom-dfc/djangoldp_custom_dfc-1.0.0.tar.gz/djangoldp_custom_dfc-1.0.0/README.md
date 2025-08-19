# DjangoLDP Custom DFC (CQCM)

[![pypi](https://img.shields.io/pypi/v/djangoldp-custom-dfc)](https://pypi.org/project/djangoldp-custom-dfc/)

## Description

This packages is a Django package, based on DjangoLDP, that provides models requires by CQCM Map.

## Installation

This package is intended to be used as a dependency within a Django project that uses `djangoldp`.

### Install the package

```bash
pip install djangoldp-custom-dfc
```

### Configure your server

Add to `settings.yml`

Within your Django project's `settings.yml` file, add `djangoldp-custom-dfc` to the `dependencies` list and the wanted individual model packages to the `ldppackages` list. The order in `ldppackages` matters, so maintain the order shown below.

```yaml
dependencies:
  - djangoldp-custom-dfc

ldppackages:
  - djangoldp_custom_dfc
```

If you do not have a settings.yml file, you should follow the djangoldp server installation guide.

### Run migrations

```bash
./manage.py migrate
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

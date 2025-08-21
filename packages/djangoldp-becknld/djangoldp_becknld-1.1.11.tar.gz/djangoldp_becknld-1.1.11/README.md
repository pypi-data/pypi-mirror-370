# DjangoLDP Beckn-LD Draft Implementation

[![pypi](https://img.shields.io/pypi/v/djangoldp-becknld)](https://pypi.org/project/djangoldp-becknld/)

## Description

This packages is a Django package, based on DjangoLDP, that provides models required for Beckn-LD Specifications Draft implementations.

## Installation

This package is intended to be used as a dependency within a Django project that uses `djangoldp`.

### Install the package

```bash
pip install djangoldp-becknld
```

### Configure your server

Add to `settings.yml`

Within your Django project's `settings.yml` file, add `djangoldp-becknld` to the `dependencies` list and the wanted individual model packages to the `ldppackages` list. The order in `ldppackages` matters, so maintain the order shown below.

```yaml
dependencies:
  - djangoldp-becknld

ldppackages:
  - djangoldp_becknld
  # - djangoldp_becknld_bap
  # - djangoldp_becknld_bpp
```

If you do not have a settings.yml file, you should follow the djangoldp server installation guide.

### Run migrations

```bash
./manage.py migrate
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

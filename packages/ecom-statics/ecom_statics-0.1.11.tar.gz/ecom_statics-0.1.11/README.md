## Versión

- Python 3.12.3

## Limpiar

``` shell
Remove-Item -Recurse -Force build, dist, ecom_statics.egg-info
```

## Actualizar

``` shell
python setup.py sdist bdist_wheel
```

## Publicar en producción

``` shell
twine upload dist/*
```

## Instalar

``` shell
pip install ecom-statics
```

## Actualizar a la ultima versión

``` shell
pip install --upgrade --no-cache-dir ecom-statics
```

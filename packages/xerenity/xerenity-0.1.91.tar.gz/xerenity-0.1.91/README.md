# Xerenity & Python

Xerenity tiene una biblioteca para acceder a todos nuestros datos, series e incluso interactuar con nuestros modelos de precios de préstamos.


## Registrarse en Xerenity

Para utilizar nuestra plataforma, visita nuestra página web y crea una cuenta para ti o para tu empresa.

El proceso de registro se puede completar en [Xerenity](https://xerenity.vercel.app/), visita la página y luego crea una cuenta.


## Utilizar la libreria de python

Python es un lenguaje de programación muy accesible y utilizado en el mundo financiero, por eso lo elegimos para acceder a nuestra plataforma.

Aquí te mostramos los pasos para utilizar la biblioteca.



### Instalacion

Nuestra libreria se encuentra disponible en PyPI, [PyPI](https://pypi.org/project/xerenity/)

```commandline
pip install xerenity
```

### Autenticacion

La biblioteca utilizará usuario y contraseña, los cuales son los que utilizaste en el registro.

### Ejecucion

Una vez instalada, solo tienes que importarla en tu programa de Python. Aquí te mostramos un simple ejemplo para leer el IBR de 3 años.

```python

from xerenity import Xerenity
import pandas as pd
import os

# Almacena el usuario y contrasena de xerenity de forma segura, puede ser en una variable de entorno
username = os.environ.get('XERENITY_USERNAME')
password = os.environ.get('XERENITY_PASSWORD')

# Crea la clase principal de xerenity, con esta tienes acceso a todas nuestras series
data = Xerenity(username, password)

# En la funcion search, da el nombre de la serie que necesitas los datos
# En este caso vamos a lerr los datos del ibr de 3 anos
ibr_3y = data.series.search(ticker='3d9f4cdbc81a0e04d61b6c9601f3a049')

# Puedes utilizar librearias como pandas, para analizar tus datos
ibr_3y_df = pd.DataFrame(ibr_3y)

print(ibr_3y_df)


```

La salida del anterio ejemplo seria algo como

```commandline

           time   value
0    2023-01-04  10.780
1    2023-01-10  11.020
2    2023-01-11  10.890
3    2023-01-13  10.600
4    2023-01-17  10.460
..          ...     ...
217  2024-05-21   8.095
218  2024-05-22   8.145
219  2024-05-24   8.320
220  2024-05-28   8.365
221  2024-05-29   8.485

[222 rows x 2 columns]

```





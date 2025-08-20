
# ***Librería Propósito y uso General***
Esta es una librería, uso general.
Contiene Funciones o clases, para uso pantalla (posición, color, etc.)

## ***Inicio***
Instalar / actualiza usando :
~~~
pip3 install libPy2023 --upgrade
~~~
>Puede buscar la librería en [pypi](https://pypi.org/search/?q=libPy2023).


A continuación encontrara una lista de las distintas funciones y clases, publicadas y algunos ejemplo de uso y su respectiva salida.

---
## ***ClearCrt***
Limpia la pantalla o Terminal.

##### ***Parámetros***:
~~~ python
none
~~~
##### ***Uso / Ejemplo***
~~~ Python
  from libPy2023 import ClearCrt
  ClearCrt()
~~~
---
## ***CleanText( xTexto:`str` ):***
Limpia un texto pasado con `xTexto`, de lo caracteres de control o especiales.

##### ***Parámetros***:
~~~ python
xTexto --> string
~~~
##### ***Uso / Ejemplo***
~~~python
  from libPy2023 import CleanText
  TextoInicial='╔╩╦Texto╠═╬'
  print(CleanText(TextoInicial))
~~~
>Salida:<br>
``
Texto
``
---
## ***class Color***
Esta es una clase que permite pasar los colores a usar en un texto mostrado por pantalla o terminal.
Al pasar un color se debe indicar si se usara para el fondo o primer plano y luego se pasa el color
>

##### ***Parámetros***:
~~~ python
None
~~~
##### ***Uso / Ejemplo***
~~~python
  print(f"{Color.Foreground+Color.Rojo}Mi Texto{Color.Fin}")
~~~

---
## ***class logs( NombreArchivoLogs : `string`)***
Logs es una clase que permite crear un objeto que mantiene las salidas tanto an el archivo indicado en el parámetro como en la Terminal.

###### **Puede usar**:
- logs(Archivo)
- logs.Texto('Texto de Salida con y sin formato')
- logs.Fin()

##### ***Parámetros***:
~~~ python
NombreArchivoLogs --> string
~~~
##### ***Uso / Ejemplo***
~~~python
  from libPy2023 import logs
  MiLogs=logs(r'c:\temp\logs.log')
  MiLogs.Texto('Calculando la cantidad de registros...')
  MiLogs.Fin()
~~~
>Salida:<br>
``
Archivo logs, en el direectorio indicado en el parametro NombreArchivo.
``
---
## ***ProgressBar***
Esta es una clase que permite pasar los colores a usar en un texto mostrado por pantalla o terminal.
Al pasar un color se debe indicar si se usara para el fondo o primer plano y luego se pasa el color
> print(f"{Color.Foreground+Color.Rojo}Mi Texto{Color.Fin}")

##### ***Parámetros***:
~~~ python
xTexto --> string
~~~
##### ***Uso / Ejemplo***
~~~python
  from libPy2023 import CleanText
  TextoInicial='╔╩╦Texto╠═╬'
  print(CleanText(TextoInicial))
~~~
>Salida:<br>
``
Texto
``
---
## ***Table***
Esta es una clase que permite pasar los colores a usar en un texto mostrado por pantalla o terminal.
Al pasar un color se debe indicar si se usara para el fondo o primer plano y luego se pasa el color
> print(f"{Color.Foreground+Color.Rojo}Mi Texto{Color.Fin}")

##### ***Parámetros***:
~~~ python
xTexto --> string
~~~
##### ***Uso / Ejemplo***
~~~python
  from libPy2023 import CleanText
  TextoInicial='╔╩╦Texto╠═╬'
  print(CleanText(TextoInicial))
~~~
>Salida:<br>
``
Texto
``
---
## ***DiaSemana***
Esta es una clase que permite pasar los colores a usar en un texto mostrado por pantalla o terminal.
Al pasar un color se debe indicar si se usara para el fondo o primer plano y luego se pasa el color
> print(f"{Color.Foreground+Color.Rojo}Mi Texto{Color.Fin}")

##### ***Parámetros***:
~~~ python
xTexto --> string
~~~
##### ***Uso / Ejemplo***
~~~python
  from libPy2023 import CleanText
  TextoInicial='╔╩╦Texto╠═╬'
  print(CleanText(TextoInicial))
~~~
>Salida:<br>
``
Texto
``
---
## ***PrintError***
Esta es una clase que permite pasar los colores a usar en un texto mostrado por pantalla o terminal.
Al pasar un color se debe indicar si se usara para el fondo o primer plano y luego se pasa el color
> print(f"{Color.Foreground+Color.Rojo}Mi Texto{Color.Fin}")

##### ***Parámetros***:
~~~ python
xTexto --> string
~~~
##### ***Uso / Ejemplo***
~~~python
  from libPy2023 import CleanText
  TextoInicial='╔╩╦Texto╠═╬'
  print(CleanText(TextoInicial))
~~~
>Salida:<br>
``
Texto
``
---
## ***Cronometro***
Esta es una clase que permite pasar los colores a usar en un texto mostrado por pantalla o terminal.
Al pasar un color se debe indicar si se usara para el fondo o primer plano y luego se pasa el color
> print(f"{Color.Foreground+Color.Rojo}Mi Texto{Color.Fin}")

##### ***Parámetros***:
~~~ python
xTexto --> string
~~~
##### ***Uso / Ejemplo***
~~~python
  from libPy2023 import CleanText
  TextoInicial='╔╩╦Texto╠═╬'
  print(CleanText(TextoInicial))
~~~
>Salida:<br>
``
Texto
``
---
## ***ImportarHojasXLSX***
Esta es una clase que permite pasar los colores a usar en un texto mostrado por pantalla o terminal.
Al pasar un color se debe indicar si se usara para el fondo o primer plano y luego se pasa el color
> print(f"{Color.Foreground+Color.Rojo}Mi Texto{Color.Fin}")

##### ***Parámetros***:
~~~ python
xTexto --> string
~~~
##### ***Uso / Ejemplo***
~~~python
  from libPy2023 import CleanText
  TextoInicial='╔╩╦Texto╠═╬'
  print(CleanText(TextoInicial))
~~~
>Salida:<br>
``
Texto
``
---
## ***EnviarCorreoAdjunto***
Esta es una clase que permite pasar los colores a usar en un texto mostrado por pantalla o terminal.
Al pasar un color se debe indicar si se usara para el fondo o primer plano y luego se pasa el color
> print(f"{Color.Foreground+Color.Rojo}Mi Texto{Color.Fin}")

##### ***Parámetros***:
~~~ python
xTexto --> string
~~~
##### ***Uso / Ejemplo***
~~~python
  from libPy2023 import CleanText
  TextoInicial='╔╩╦Texto╠═╬'
  print(CleanText(TextoInicial))
~~~
>Salida:<br>
``
Texto
``
---
## ***emailSender***
Esta es una clase que permite pasar los colores a usar en un texto mostrado por pantalla o terminal.
Al pasar un color se debe indicar si se usara para el fondo o primer plano y luego se pasa el color
> print(f"{Color.Foreground+Color.Rojo}Mi Texto{Color.Fin}")

##### ***Parámetros***:
~~~ python
xTexto --> string
~~~
##### ***Uso / Ejemplo***
~~~python
  from libPy2023 import CleanText
  TextoInicial='╔╩╦Texto╠═╬'
  print(CleanText(TextoInicial))
~~~
>Salida:<br>
``
Texto
``
---
## ***Box***
Esta es una clase que permite pasar los colores a usar en un texto mostrado por pantalla o terminal.
Al pasar un color se debe indicar si se usara para el fondo o primer plano y luego se pasa el color
> print(f"{Color.Foreground+Color.Rojo}Mi Texto{Color.Fin}")

##### ***Parámetros***:
~~~ python
xTexto --> string
~~~
##### ***Uso / Ejemplo***
~~~python
  from libPy2023 import CleanText
  TextoInicial='╔╩╦Texto╠═╬'
  print(CleanText(TextoInicial))
~~~
>Salida:<br>
``
Texto
``
---
## ***toVars***
Esta es una clase que permite pasar los colores a usar en un texto mostrado por pantalla o terminal.
Al pasar un color se debe indicar si se usara para el fondo o primer plano y luego se pasa el color
> print(f"{Color.Foreground+Color.Rojo}Mi Texto{Color.Fin}")

##### ***Parámetros***:
~~~ python
xTexto --> string
~~~
##### ***Uso / Ejemplo***
~~~python
  from libPy2023 import CleanText
  TextoInicial='╔╩╦Texto╠═╬'
  print(CleanText(TextoInicial))
~~~
>Salida:<br>
``
Texto
``
---
## ***GenerateQuery***
Esta es una clase que permite pasar los colores a usar en un texto mostrado por pantalla o terminal.
Al pasar un color se debe indicar si se usara para el fondo o primer plano y luego se pasa el color
> print(f"{Color.Foreground+Color.Rojo}Mi Texto{Color.Fin}")

##### ***Parámetros***:
~~~ python
xTexto --> string
~~~
##### ***Uso / Ejemplo***
~~~python
  from libPy2023 import CleanText
  TextoInicial='╔╩╦Texto╠═╬'
  print(CleanText(TextoInicial))
~~~
>Salida:<br>
``
Texto
``
---
## ***MessageBox***
Esta es una clase que permite pasar los colores a usar en un texto mostrado por pantalla o terminal.
Al pasar un color se debe indicar si se usara para el fondo o primer plano y luego se pasa el color
> print(f"{Color.Foreground+Color.Rojo}Mi Texto{Color.Fin}")

##### ***Parámetros***:
~~~ python
xTexto --> string
~~~
##### ***Uso / Ejemplo***
~~~python
  from libPy2023 import CleanText
  TextoInicial='╔╩╦Texto╠═╬'
  print(CleanText(TextoInicial))
~~~
>Salida:<br>
``
Texto
``
---

# Clismo

## Índice

- [Objetivos](https://github.com/jmorgadov/clismo#objetivos)
- [Instalación](https://github.com/jmorgadov/clismo#instalaci%C3%B3n)
- [Lenguaje](https://github.com/jmorgadov/clismo#lenguaje)
  - [Características básicas](https://github.com/jmorgadov/clismo#caracter%C3%ADsticas-b%C3%A1sicas)
    - [Declaración y uso de variables](https://github.com/jmorgadov/clismo#declaraci%C3%B3n-y-uso-de-variables)
    - [Condicionales](https://github.com/jmorgadov/clismo#condicionales)
    - [Ciclos](https://github.com/jmorgadov/clismo#cliclos)
  - [Estructuras principales](https://github.com/jmorgadov/clismo#estructuras-principales)
  - [Atributos y funciones especiales](https://github.com/jmorgadov/clismo#atributos-y-funciones-especiales)
    - [Client](https://github.com/jmorgadov/clismo#client)
    - [Server](https://github.com/jmorgadov/clismo#server)
    - [Step](https://github.com/jmorgadov/clismo#step)
    - [Simulation](https://github.com/jmorgadov/clismo#simulation)
  - [General](https://github.com/jmorgadov/clismo#general)
  - [Funciones built-in](https://github.com/jmorgadov/clismo#funciones-built-in)
- [Implementación](https://github.com/jmorgadov/clismo#implementaci%C3%B3n)
  - [Autómatas](https://github.com/jmorgadov/clismo#aut%C3%B3matas)
  - [Motor de expresiones regulares](https://github.com/jmorgadov/clismo#motor-de-expresiones-regulares)
  - [Tokenizador](https://github.com/jmorgadov/clismo#tokenizador)
  - [Gramáticas](https://github.com/jmorgadov/clismo#gram%C3%A1ticas)
  - [Árbol de Sintaxis Abstracta (AST)](https://github.com/jmorgadov/clismo#%C3%A1rbol-de-sintaxis-abstracta-ast)
  - [Parser](https://github.com/jmorgadov/clismo#parser)
  - [Visitors](https://github.com/jmorgadov/clismo#visitors)
  - [Ejecución](https://github.com/jmorgadov/clismo#ejecuci%C3%B3n)
    - [Reconocimiento de las estructuras declaradas](https://github.com/jmorgadov/clismo#reconocimiento-de-las-estructuras-declaradas)
    - [Chequeo semántico](https://github.com/jmorgadov/clismo#chequeo-sem%C3%A1ntico)
    - [Evaluación](https://github.com/jmorgadov/clismo#evaluaci%C3%B3n)
- [Ejemplo](https://github.com/jmorgadov/clismo#ejemplo)

## Objetivos

El objetivo de este proyecto es crear un lenguaje de programación
(específicamente un DCL) que permita la creación, ejecución y optmización de
modelos de simulación de eventos discretos de tipo cliente-servidor. De esta
forma, los usuarios pueden enfocarse más en la estructura de los modelos y no
en la implementación interna de los mismos.

El lenguaje ofrece además la posibilidad de optimizar los modelos creados bajo
criterios que el mismo usuario puede especificar.

## Instalación

```bash
pip install clismo
```

Para más información sobre el uso del programa:

```bash
clismo --help
```

## Lenguaje

**Clismo** es un lenguaje no orientado a objetos, y a pesar de ser un lenguaje
de programación imperativo, el mismo tiene características funcionales. El
tipado es estático, aunque no es necesario declarar los tipos en la sintaxis
(son inferidos automáticamente).

Al ser un lenguaje dedicado a la creación de modelos de simulación del tipo
cliente-servidor, posee cuatro estructuras básicas: `client`, `server`, `step`
y `simulation`. Las relaciones entre estas estructuras son:

- Los servidores atienden a los clientes.
- Un `step` contiene una serie de servidores (indica que están en paralelo).
- Un `simulation` contiene una serie de steps (indica que están en secuencia).

Cada una de estas estructuras puede contener atributos y/o funciones especiales
que definen el comportamiento del sistema que serán analizados en futuras
secciones.

### Características básicas

A continuación se presentan ejemplos de código que muestran las características
básicas del lenguaje.

#### Declaración y uso de variables

```text
var name = "John"
var is_elder = False
var count = 10
count = count + 3
```

#### Condicionales

```text
if count == 10:
    ...
else:
    ...
```

> Con indentaciones similar a Python.

#### Cliclos

- Ciclo infinito

    ```text
    loop:
        ...
    ```

    > Dentro de los loops se pueden usar las palabras claves `endloop` o `nextloop`
    > para terminar el loop o saltar a la siguiente iteración respectivamente.

- Ciclo infinito con variable

    ```text
    loop i:
        ...
    ```

- Ciclo infinito con variable y comienzo

    ```text
    loop i from 5:
        ...
    ```

- Ciclo con comienzo y fin

    ```text
    loop i from 5 to 10:
        ...
    ```

- Ciclo con comienzo, fin y paso

    ```text
    loop i from 5 to 10 by 2:
        ...
    ```

### Estructuras principales

Las estructuras principales (`client`, `server`, `step` y `simulation`) se
crean de la siguiente forma:

```text
<struct_type> <name>:
    <attr_name> = <attr_value>
    ...

    <func_name>(<specifications>):
        <func_body>
        ...
```

> Los <specifications> no representan parámetros que se pasan a la función,
> sino que son, como su nombre lo indica, especificaciones.

Por ejemplo, para crear un servidor:

```text
server server1:
    my_own_attr = 10

    attend_client():
        return norm() + 10
```

> `attend_client` es una función especial que deben definir los servidores para
> indicar el tiempo que tardará en atender a un cliente.

### Atributos y funciones especiales

Algunas estructuras requieren de atributos y funciones especiales para
ser poder definidas. (Como en el ejemplo anterior `attend_client`, no
se puede crear un servidor si no se define esta función en el cuerpo
del mismo).

#### Client

Los clientes no requieren de atributos especiales, pero si pueden definir
opcionalmente una función `on_server_out` que será llamada cuando el cliente
sale del servidor. Esta función no debe devolver ningun valor, se usa
generalemente para indicar modificar attributos del cliente.

> Más adelante se explicará como se pueden obtener y modificar los atributos
> de una estructura.

#### Server

Los servidores requieren la implementación de la función `attend_client`.
Esta función debe devolver el tiempo que tardará en atender a un cliente.
Dentro de ella se puede acceder al cliente actual mediante la variable
`current_client`.

#### Step

Los steps no requieren ninguna función especial pero si la declaración del
atributo `servers`, una lista de servidores que se encargarán de atender a los
clientes.

```text
step step1:
    servers = [server1, server2]
```

#### Simulation

Las simulaciones requieren la declaración de los siguientes atributos:

- `steps`: una lista de steps que representan los servidores en serie.
- `time_limit` o `client_limit`: una cantidad de tiempo o cantidad de clientes que se desea simular. Solo es necesario uno de los dos (aunque se pueden indicar ambas)
- `arrive(<client_type>)`: una función que devuelve el tiempo que tardará en llegar un cliente de un tipo determinado. Ejemplo:
    
    ```text
    arrive(DefaultClient):
        return norm() + 10
    ```

    > `DefaultClient` es un tipo de cliente que se usa por defecto. Cada simulación
    > puede definir más funciones `arrive` con clientes de distintos tipos. También
    > se puede definir una misma función `arrive` para varios tipos de clientes,
    > por ejemplo `arrive(ClientType1, ClientType2)`.

Opcionalemente, se puede definit el modo de ejecución de la simulación con el
atributo `mode`. El mismo puede ser `"run"` (por defecto) o `"optimize"`. Estos
indican si se quiere ejecutar la simulación u optimizar el modelo.

En caso de que se quiera optimizar el modelo, se debe definir la función
`minimize()` que devuelve el valor que se desea minimizar.

Para la configuración del algoritmo genético utilizado para la optimización,
se pueden especificar los atributos:

- `pop_size`: cantidad de individuos en la población. Por defecto es 10.
- `max_iter`: cantidad máxima de iteraciones. Por defecto es 5.
- `mut_prob`: probabilidad de mutación. Por defecto es 0.1.
- `best_sel`: cantidad de individuos que se seleccionan para la siguiente generación. Por defecto es 3.
- `new_rand`: cantidad de nuevos individuos que se generan al final de cada iteración. Por defecto es 2.

### General

Cada estructura puede definir una función `possible(<attr_name>)`. Esta función
debe devolver un posible valor (aleatorio) para el atributo especificado.

Estas funciones se utlizarán para crear el vector de posibles valores para los
diferentes atributos. Con ello se pueden crear diferentes versiones de un mismo
modelo y es lo que el algoritmo genético utilizará para optimizar el mismo.

Adicionalemente, en cualquier función se puede acceder a las variables globales
`time` y `clients` que representan el tiempo actual se la simulación y la
cantidad de clientes que han salido del sistema.

### Funciones built-in

Dentro de la implementación de las funciones especiales se pueden usar diversas
funciones built-in. Dos de las funciones principales son: `get` y `set`. Con
estas funciones se pueden obtener y modificar los atributos de una estructura.
Por ejemplo:

```text
server S1:
    mean = 10
    total = 0

    attend_client():
        set(self, "total", get(self, "total") + 1)
        return nomr() + get(self, "mean")
```

> `self` es una referencia a la instancia de la estructura actual

Como el lenguaje no es orintado a objetos, existen diversas funciones que
permiten realizar todo tipo de acciones:

- `get_at(<list>, <index>)`: devuelve el valor del elemento en la posición especificada de la lista.
- `set_at(<list>, <index>, <value>)`: modifica el valor del elemento en la posición especificada de la lista.
- `append(<list>, <value>)`: agrega un elemento al final de la lista.
- `rand()`: devuelve un valor aleatorio entre 0 y 1.
- `norm()`: devuelve un valor aleatorio entre 0 y 1 con distribución normal.
- `randint(<min>, <max>)`: devuelve un valor aleatorio entre `min` y `max`.
- `startswith(<string>, <substring>)`: devuelve `True` si `string` empieza con `substring`.
- `lower(<string>)`: devuelve `string` en minúsculas.
- `upper(<string>)`: devuelve `string` en mayúsculas.
- `sqrt(<number>)`: devuelve la raíz cuadrada de `number`.
- `abs(<number>)`: devuelve el valor absoluto de `number`.
- `round(<number>, <decimals>)`: devuelve `number` redondeado a `decimals` decimales.

Entre muchas otras similares a las funciones de python.

## Implementación

**Clismo** es un lenguaje evaluado escrito en Python. A continuación se
exponen las características principales de la implementación de cada etapa.

### Autómatas

Para la creación de las algunas de las proximas funcionalidades, se realizaó
una implementación de un tipo `Automata` que permite simular una
máquina de estados de forma genérica. A los mismos se le pueden agregar
estados así como transiciones entre los mismos. Cada autómata tiene un estado
inicial y uno o varios estados finales.

La ejecución de una máquina de estados realizada con un autómata es bastante
simple. Dado una entrada iterable, se comienza en el estado inicial y se va
ejecutando cada transición hasta llegar a un estado final. En caso de llegar a
un estado en el que ninguna transición es válida, se termina la ejecución y la
entrada no es válida. En caso de terminar de recorrer la entrada se clasifica
la entrada como válida o inválida en dependencia de si se llegó a un estado
final o no respectivamente.

Los autómatas pueden tener transiciones **épsilon** entre estados, en este
caso, la ejecución se bifurca y la maquina de estados se mueve por todos los
estaos posibles al mismo timepo. Esto da la posibliadad de ejecutar autómatas
no deterministas.

Se implementó además, utilizando el algoritmo visto en clase (calculando los
**goto** y **epsilon clausuras**) la opción de convertir un autómata no
determinista (NFA) a un autómata determinista (DFA).

### Motor de expresiones regulares

Las principales funcionalidades implementadas son:

- Operador `*`: Matchea cero o más veces la expresión anterior.
- Operador `|`: Mathcea la expresión anterior o la siguiente.
- Operador `^`: Matchea cualquier expresion excepto la expresión que le prosigue.
- Caracter `.`: Matchea cualquier caracter (ASCII).
- Caracter `\`: Inicio de un caracter especial.
- Caracter `\d`: Matchea un dígito.
- Caracter `\a`: Matchea una letra minúscula.
- Caracter `\A`: Matchea una letra mayúscula.
- Parentesis `(` y `)`: Agrupan una expresión regular.

> Cualquier operador o caracter especal puede ser escapado con `\`.

Para la realización del motor de expresiones regulares se utilizó la clase
`Automata`. Para cada expresión regular se construye un autómata finito no
determinista (NFA) usando el algoritmo de Thompson y luego el mismo se
convierte a un DFA utlizando el método `to_dfa` de la clase `Automata`.

Se ofrecen además dos funciones para el matcheo de cadenas segun una expresión
regular: `match` (la cual tiene un comportamiento similar a `re.match`) y
`compile_patt` (la cual tiene un comportamiento similar a `re.compile`). La
ventaja principal de usar `compile_patt` es que se no es necesario crear un
autómata para cada vez que se desea matchear una cadena (ya que el autómata es
construido una sola vez).

### Tokenizador

Para la implementación del tokenizador se creó una clase `Tokenizer`. Esta
clase se encarga de tomar un texto y dividirlo en diferentes tipos de tokens.
Cada patrón que se agrega está definido por un nombre (tipo del token) y una
expresión regular (se hace uso del motor de expresiones regulares
implementado).

```python
tknz = Tokenizer()
tknz.add_pattern("NUMBER", r"\d\d*|\d\d*\.\d\d*")
```

Al tokenizar un texto, se revisan los patrones comenzando por el primero (en el
mismo orden en el que fueron agregados) y el primero que matchee con un prefijo
de la cadena se establece como un token nuevo (se toma como lexema la subcadena
que matcheó con la expresión regular). Luego se vuelve a realizar esta
operación con el resto de la cadena, así sucesivamente hasta terminar la misma.
Si en algún punto no se encuentra un token que matchee con el inicio de la
cadena, se considera que la cadena no se puede tokenizar (con los tipos de
tokens establecidos).

Cada vez que se agrega un patrón al tokenizador se puede establecer una
función que se aplicará al lexema antes de guardar su valor en el token.

Por ejemplo, para quitar las comillas al tokenizar un **string**:

```python
tknz.add_pattern("STRING", r"'((^')|(\\'))*(^\\)'", lambda t: t[1:-1])
```

Esta función tambien puede ser utilizada para indicar que se quiere ignorar
los tokens de un tipo determinado. En tal caso basta con que la función devuelva
`None`:

```python
tknz.add_pattern("SPACE", r"( | \t)( |\t)*", lambda t: None)
```

Se ofrece también la opción de agregar `keywords` (palabras claves) para una
mayor comodidad. Esto se hace mediante el método `add_keywords()` el cual recibe
una lista de palabras. En el proceso de tokenización, si el prefijo matcheado
conicide con alguna de las palabras clave, entonces el tipo del token se
establece como `KEYWORD`.

En caso de que se quiera aplicar una función para procesar todos los tokens
obtenidos, se puede usar el decorador `process_tokens` de la clase `Tokenizer`.
Este debe ser usado en una función que reciba un solo argumento (la lista de
tokens) y devuelva una lista de tokens procesados.

```python
@tknz.process_tokens
def process_tokens(tokens):
    # ...
    return tokens
```

Finalmente, para obtener los tokens de un texto basta con usar la función
`tokenize`:

```python
tokens = tknz.tokenize("some text")
```

### Gramáticas

Se implementaron las clases `Grammar`, `NonTerminal`, `Terminal` y `Production`
las cuales son usadas para la representación de una gramática general. Se
implementó además un parser de gramáticas con el cual es posible crear
gramáticas dado un formato, esto permite definir la gramática del lenguaje en
un archivo y poder cambiarla fácilmente. Dado la sencillez del formato (el
lenguaje de las gramáticas), se implementó un sencillo parser recursivo
descendente para la creación de las mismas.

El formato especificado es el siguiente:

```
expression: production_1 | production_2 | ... | production_n
```

De forma equivalente, para mayor legibilidad:

```
expression:
    | production_1 
    | production_2
    | ...
    | production_n
```

Ejemplo:

```
ExprAB:
    | 'a' ExprAB 'b'
    | EPS
```

> EPS es un elemento especial en las gramáticas para representar *epsilon*

Las gramáticas luego pueden ser cargadas como se muestra a continuación:

```python
from grammar im port Grammar
gm = Grammar.open("expr_ab.gm")
```

Las gramáticas están compuestas por una lista de expresiones (no terminales).
Cada no terminal de la gramática, contiene una lista de producciones. Cada
producción contiene una lista de elementos (terminales o no terminales).

### Árbol de Sintaxis Abstracta (AST)

Para la creación de un AST se creó la clase abstracta `AST`. De esta clase
heredan todos las clases que representan los nodos del árbol de sintaxis 
abstracta del lenguaje. En la clase se implementa también un método `dump`
que permite mostrar el árbol de forma legible. Este método usa el
atributo `__slots__` mediante el cual se definen los atributos que se
quieren mostrar.

Para definir cómo se construye cada nodo del AST se pueden asignar los
constructores a cada producción de la gramática usando la función
`assign_builders`. Esta función recibe un diccionario donde las llaves son la
representación textual de la producción y los valores son funciones que reciben
como argumentos los elementos de la producción. En caso de que el símbolo sea
un terminal la función recibirá dicho terminal, en caso de ser un no terminal,
la función recibirá el resultado de la ejecución algunas de las funciones
constructoras de las producciones que tengan como cabeza a dicho no terminal.

Por ejemplo, a continuación se muestran algunos de los constructores para
la gramática de **Clismo**:

```python
builders = {
    # -------------------------------------------------------------------------
    "program -> obj_def program": lambda s, p: ast.Program([s] + p.stmts),
    "program -> NEWLINE program": lambda n, p: p,
    "program -> EPS": lambda: ast.Program([]),
    # -------------------------------------------------------------------------
    "obj_def -> client_def": lambda c: c,
    "obj_def -> server_def": lambda s: s,
    "obj_def -> step_def": lambda s: s,
    "obj_def -> sim_def": lambda s: s,
    # -------------------------------------------------------------------------
    # ...
    # ...
```

### Parser

Para la implementación del parser principal del lenguaje se creó la clase
abstacta `Parser`. Usando esta clase como base se creó una clase `LR1Parser`,
la cual implementa un parser LR(1).

Para la realización del parser LR(1) fue necesario implementar las clases
`LR1Item` y `LR1Table`. La primera de estas clases representa un item del
parser, el cual contiene: la producción que lo genera, la posición del punto
(dot) en la producción y el terminal que le debe proseguir (lookahead).

La segunda clase (`LR1Table`) representa la tabla de transición del parser.
Cada posición de la tabla puede contener tres tipos de elementos: un **string**
`"OK"`, que indica que el estado de aceptación; un valór numérico entero, que
indica cual es el siguiente estado; o un no terminal de la gramática, el cual
representa que hay que realizar una reducción. Para no tener que recalcular la
tabla cada vez que se va a parsear un texto, la misma puede ser serializada y
luego cargada.

La construcción de la tabla se realizó siguiendo el algoritmo visto en las
conferencias de la asignatura (calculando los **goto** y las **clausuras** de
los estados).

En el proceso de parsing, al realizar una acción de reducción, es donde se
utilizan las funciones constructoras vistas en la sección anterior. En
dependencia de la producción que se está reduciendo, se llama a la función
constructora correspondiente.

Para una mayor comodidad se implementó también la clase `ParserManager`. Esta
clase ofrece, dado una gramática, un tokenizador (opcional) y un parser
(opcional, por defecto LR(1)), métodos como: `parse_file` (para parsear un
archivo), `parse` (para parsear un texto) y `parse_tokens` (para parsear una
lista de tokens directamete). Estas funciones devuelven el AST resultante del
proceso de parsing.

### Visitors

Una vez obtenido el AST de un programa es necesario realizar recorridos sobre
él. Para ello se implmentó una clase `Visitor` la cual contiene dos decoradores
`@visitor` y `@callback`. Por cada **visitor** que se quiera implementar para
el AST, se debe implementar una nueva clase que tenga como atributo de clase
una instancia de la clase `Visitor`. Luego, cada método de la clase que tenga
el decorador `@visitor`, se establecerá como una sobrecarga. Es por ello que
todos estos métodos deben tener sus argumentos tipados (esta es la forma en la
que el **visitor** sabe cual de los métodos de la clase debe llamar).

Por ejemplo:

```python
from clismo.lang.visitor import Visitor

class EvalVisitor:
    visitor_dec = Visitor().visitor

    @visitor_dec
    def eval(self, node: ast.Program):
        for stmt in node.stmts:
            stmt.eval(self)

    @visitor_dec
    def eval(self, node: ast.ClientDef): ...

    # ...
```

El decorador `@callback` se utiliza para definir funciones que se van a llamar
cada vez que se llame a una función marcada como **visitor**.

### Ejecución

El proceso de ejecución se divide en 3 partes:

1. Reconocimiento de las estructuras declaradas.
2. Chequeo semántico.
3. Ejecución.

#### Reconocimiento de las estructuras declaradas

En este paso se recorre el AST con un visitor el cual analiza las estructuras
declaradas. Esta información es utilizada luego en el checqueo semántico. Esto
permite usar dentro de las estructuras referencias a otras que por el orden del
código no han sido definidas aún.

#### Chequeo semántico

En esta etapa se realiza una verificación a cada estructura declarado
(igualmente con otro visitor). Se asegura que las estructuras declaradas tengan
los atributos y funciones necesarias para su correcta ejecución.

Además se realiza un chequeo de tipos de los atributos y cuerpos de las
funciones. De esta forma se asegura que cada función devuelva un valor de
tipo correcto.

#### Evaluación

Finalmente, un último vísitor se encarga de recorrer el AST configurando la
simulación según las estructuras declaradas para luego ejecutar (u optimizar)
el modelo definido.

## Ejemplo

En el script [clismo_example.csm](./clismo_example.csm) se muestra un ejemplo
de un programa.

```text
client Normal:
    test_val = 5

    possible(test_val):
        return randint(2, 10)

server S1:
    total = 0

    attend_client():
        var t = 1 * get(current_client, "test_val")
        set(self, "total", get(self, "total") + t)
        return t

server S2:
    total = 0

    attend_client():
        var t = 3 * get(current_client, "test_val")
        set(self, "total", get(self, "total") + t)
        return t

step P1:
    servers = [S2, S2, S1]

    possible(servers):
        var s = [S1, S2]
        var count = len(get(self, "servers"))
        var new_servers = list("server")
        loop _ from 0 to count:
            var r = randint(0, 1)
            new_servers = append(new_servers, get_at(s, r))
        return new_servers

simulation Test:
    mode = "optimize"
    steps = [P1]
    client_limit = 50

    max_iter = 20
    pop_size = 3
    mut_prob = 0.4
    new_rand = 10

    arrive(Normal):
        return 5
    
    minimize():
        var servers = get(get_at(get(self, "steps"), 0), "servers")
        var count = len(servers)
        var total = 0
        loop i from 0 to count:
            total = total + get(get_at(servers, i), "total")
        return total
```

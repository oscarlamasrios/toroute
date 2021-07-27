## PRÁCTICA PROGRAMACIÓN INTEGRATIVA

**Autores:**

   - Óscar Lamas Ríos (oslamasri@gmail.com)
   - Lois Soto López (loissotolopez@gmail.com) 

**IMPORTANTE:**
	
   - Probar aplicación con el navegador "Mozilla Firefox", otros como "Google Chrome" pueden dar algun problema en relación al contenido
     html.
   - Se puede dar el caso de que caduque la clave de la API de Google que utilizamos. En teoría caduca diariamente, aunque nosotros hemos   	
     utilizado la misma a lo largo de varios días sin problema. Si surge algún tipo de problema con esto, estaremos atentos al correo por
     si nos solicitáos una nueva clave.

**Docker:**
    
   docker pull loissotolopez/touroute 
   docker run -p 8000:8000 -i -t loissotolopez/touroute /bin/bash
   python3 manage.py runserver 0.0.0.0:8000 


**Vista principal de nuestra aplicación:**
	
   http://0.0.0.0:8000/index/

**Aspectos a tener en cuenta respecto lo indicado en la propuesta inicial:**

   1. En el mapa mostrado por nuestra aplicación, el punto marcado en ROJO es el origen (punto de partida). Los lugares que se visitarán están 	     marcados en color AZUL.

   2. Con respecto a los lugares de interés, hemos decidido incluír "Museos" y "Galerías de Arte". 
      En cada búsqueda se podrá seleccionar uno de estos tipos de lugares.

   3. Hemos utilizado Pandas para almacenar los distintos parámetros de los lugares en un dataframe, además de realizar una ordenación por uno 	     de ellos (Distancia).	
      **Distancia**: valor de la longitud de la recta entre dos puntos en el mapa.

   4. Integración con otros lenguajes:
	- Hemos creado una librería en C, que nos calcula la distancia mencionada en el punto 3, dados dos pares de coordenadas.                	Le hemos dado el nombre de "distmod" y la incluímos en el directorio de nuestra aplicación.
  - Se utilizó SWIG.

   5. Con respecto a los tweets, en lugar de publicar un tweet con la ruta que nos ha proporcionado la aplicación, decidimos realizar una 
      búsqueda sobre todos los lugares correspondientes a cada ruta, y enseñar un tweet de cada uno de ellos.
      Si el tweet contiene alguna URL, este será "clickable" y accederás a dicha URL.

   6. Se han controlado las distintas respuestas que nos pueden dar las APIs utilizadas. 
	- Puede que no existan "Museos" o "Galerías de Arte" en una ubicación y rango de búsqueda especificados.
	- Puede que no existan tweets sobre un determinado lugar de interés.
	- Puede que se produzca algún tipo de error en el momento de calcular la ruta por parte de la API.
   
   7. En relación a la utilización de las APIs, el funcionamiento de nuestra aplicación es el siguiente:
  - Búsqueda del punto origen (Places API).
  - Búsqueda de lugares de interés (Places API). 
	- Para la construcción de los mapas que enseñamos (Maps Static API).
	- Para calcular las rutas (Directions API). Realmente esta API nos devuelve una serie de puntos o "polyline" que representan la ruta 
	  exacta a seguir, esta información se envía a "Maps Static API" para realizar la construcción del mapa.
	  Es necesario utilizar esta API pues, con "Maps Static API", sólo se calculan rutas en línea recta, sin tener en cuenta las distintas
	  calles ... etc.

Los archivos probando.txt y probando2.txt son versiones cortas de los .csv generados para cada estación y procesadas con la GHI relativa ya sacada (falta eso).

Las 4 primeras columnas representan segundos, año, día y hora local. La 5ª columna, GHI relativa.

Falta crear un json para que nsamples, ntime, predictiont y offset se puedan cambiar más fácilmente.



	La idea del programa (nts.py, viene de ntimesamples pero más corto, que resulta más cómodo) es que proporcionando cuántas muestras queremos tomar, cada cuantos segundos, qué offset, a partir de qué tiempo y qué estaciones considerar (como hay 2 .txt tomaría los 2 pero la idea es introducirlo en el json), genere una matriz X con todos los GHI's relativos desde t - d (siendo d = nsamples * ntime + offset) hasta predictiont (de esto último no estoy completamente seguro).
	Finalmente queda una matriz donde la 1ª columna son las ghi's desde t-d hasta t (comprobar esto, tampoco estoy seguro) en la primera estación, la segunda columna las ghi's desde t-(d-1) hasta t, etc y la última (de la 1ª estación), desde t-1 hasta t (o hasta más, creo que sería lo suyo). Después se hace lo mismo con las de la segunda estación.
	Faltaría crear la matriz Y con los targets y, de forma opcional, meter azimuth y tal.

Al acabar el programa guarda todo en un .csv.

=======
History
=======

*******************
0.10.1 (2026-08-07)
*******************

* se arego location headers a elastic retrive model
* se agrego get actions para las pruebas

*******************
0.10.0 (2026-08-07)
*******************

* nueva operacion de migracion para reindexar Elasticsearch_reindex
* nueva operacion de migracion para ejecutar funciones Elasticsearch_run_python
* nueva operacion de migracion para eliminar indices Elasticsearch_delete_index
* nueva operacion de migracion para bloquar la escritura Elasticsearch_block_write
* nueva vista de solo lectura Elastic_read_only_model_viewset

******************
0.9.0 (2026-08-05)
******************

* se agrego que soporte donkeys con . en las migraciones de los new fields
  para los campos internos del modelo

******************
0.8.0 (2026-07-30)
******************

* se agrego la migracion para nuevos fields
* nueva vista de only list de elastic
* se agrego fields_read_only para los serializadores de elastic

******************
0.7.0 (2026-07-29)
******************

* se agrego la funcionalidad de read_only_field a los serializadores de elastic
* se agrego vista de only list para elastic
* nueva migracion para campos de elastic

******************
0.7.0 (2026-07-28)
******************

* se agregaron mas helper para las pruebas
* correcion con el content type para el view 404

******************
0.6.0 (2026-07-17)
******************

* se agrega el serializador para modelos de elasticsearch
* mejoras con las excepciones 404

#### DUDAS QUE VAN SURGUIENDO PARA MIRAR Y RESOLVER

- Tenemos varios objetos de los cuales no podemos obtener el initiator de forma "directa":
    - Initiator de tipo parser (que devuelve una url, se podría asociar a un targetID pero no a un evento,
    a no ser que se utilice el timestamp y el orden de eventos)
    + Con el evento Target.getTargets, podemos obtener todos los targets y por lo tanto mapear cada una de
    las URLs con sus respectivos Targets ID, en caso de no ser ninguno de los que esta, se mantendría la URL.
    - El primer script que no tiene ni origen ni initiator, unicamente executionContextID
    


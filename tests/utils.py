import json


def get_list_proyectos_by_constructora(handler, constructora):
    lista_proyectos = handler(
        {
            "service": "get_list_proyectos_by_constructora",
            "data": {
                "nombre": constructora,
            },
        },
        None,
    )

    return json.loads(lista_proyectos)

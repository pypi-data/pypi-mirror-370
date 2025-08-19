class BgFlowGes:
    class AccionesMonitorizadas:
        _tbl = 'WAccionesMonitorizadas'
        id = 'id'
        nom_trigger = 'NomTrigger'
        id_flujo = 'id_flujo'
        empresa = 'Empresa'
        bd = 'BD'
        tabla = 'Tabla'
        segmentos_clave = 'SegmentosClave'
        alta = 'Alta'
        baja = 'Baja'
        modificacion = 'Modificacion'
  

    class Alertas:
        _tbl = 'WAlertas'
        id = 'id'
        fecha = 'Fecha'
        periodicidad = 'Periodicidad'
        para = 'Para'
        mensaje = 'Mensaje'


    class Datos:
        _tbl = 'WDatos'
        id = 'id'
        id_Forms = 'id_forms'
        nombre = 'Nombre'
        tipo = 'Tipo'
        longitud = 'Longitud'
        decimales = 'Decimales'
        lista = 'Lista'
        imprescindible = 'Imprescindible'


    class DatosValores:
        _tbl = 'WDatos_valores'
        id = 'id'
        id_datos = 'id_datos'
        id_transiciones_valores = 'id_transiciones_valores'
        valor = 'valor'


    class Flows:
        _tbl = 'WFlows'
        id = 'id'
        concepto = 'Concepto'
        descripcion = 'Descripcion'
        version = 'Version'
        activo = 'Activo'
        valor_inicial = 'ValorInicial'
        sociedades = 'Sociedades'
        solo_mostrar_iniciados = 'SoloMostrarIniciados'


    class FlowsValores:
        _tbl = 'WFlows_valores'
        id = 'id'
        id_flows = 'id_flows'
        creado_por = 'CreadoPor'
        empresa = 'Empresa'
        clave = 'Clave'
        fecha_creacion = 'Fecha_creacion'
        fecha_finalizacion = 'Fecha_finalizacion'
        fase = 'Fase'
        id_transicion_actual = 'id__TransicionActual'
        nombre_transicion_actual = 'NombreTransicionActual'
        email = 'Email'


    class Forms:
        _tbl = 'WForms'
        id = 'id'
        id_flows = 'id_flows'
        nombre = 'Nombre'


    class Preferencias:
        _tbl = 'WPreferencias'
        id = 'id'
        exportar_omitir_usuarios = 'exportar_omitir_usuarios'
        exportar_omitir_notificaciones = 'exportar_omitir_notificaciones'
        max_registros_consulta_work_flows = 'max_registros_consulta_workflows'
        email_host = 'email_host'
        email_usuario = 'email_usuario'
        email_pwd = 'email_password'
        eesplegar_transiciones_vinculadas = 'Desplegar_Transiciones_Vinculadas'


    class RegistroAcciones:
        _tbl = 'WRegistroAcciones'
        id = 'id'
        bd = 'BD'
        tabla = 'Tabla'
        clave = 'Clave'
        accion = 'Accion'
        empresa = 'Empresa'
        clave_anterior = 'ClaveAnterior'


    class Transiciones:
        _tbl = 'WTransiciones'
        id = 'id'
        id_flows = 'id_flows'
        id_padre = 'id_padre'
        forms_nombre = 'Forms_nombre'
        nombre = 'Nombre'
        is_recursivo = 'is_recursivo'
        usuario = 'usuario'
        rol = 'rol'
        concepto = 'Concepto'
        descripcion = 'Descripcion'
        version = 'Version'
        bloquear_registro_gestion = 'BloquearRegistroGestion'


    class TransicionesEventos:
        _tbl = 'WTransiciones_eventos'
        id = 'id'
        arg_1 = 'Arg1'
        arg_2 = 'Arg2'


    class TransicionesPermisos:
        _tbl = 'WTransiciones_permisos'
        id = 'id'
        id_transiciones = 'id_transiciones'
        clase = 'clase'
        nombre = 'Nombre'


    class TransicionesValores:
        _tbl = 'WTransiciones_valores'
        id = 'id'
        id_transiciones = 'id_transiciones'
        id_flows_valores = 'id_flows_valores'
        id_forms = 'id_forms'
        unic_id = 'Unicid'
        usuario = 'Usuario'
        fecha_atencion = 'Fecha_atencion'
        id_padre_virtual = 'id_padre_virtual'
        id_flows_valores_vinculado = 'id_flowsValores_Vinculado'
        num_seguimiento = 'NumSeguimiento'
  
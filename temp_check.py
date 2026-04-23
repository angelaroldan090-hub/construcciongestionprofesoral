import psycopg2, json

conn = psycopg2.connect(host='localhost', port=5432, dbname='mapaConocimiento', user='postgres', password='adminsanny')
cur = conn.cursor()

# Crear tabla docentes_estudios si no existe y migrar datos
cur.execute("""
    CREATE TABLE IF NOT EXISTS docentes_estudios (
        docente  INTEGER NOT NULL REFERENCES docente(cedula),
        estudio  INTEGER NOT NULL REFERENCES estudios_realizados(id),
        PRIMARY KEY (docente, estudio)
    );
""")

# Migrar relaciones existentes desde estudios_realizados.docente
cur.execute("""
    INSERT INTO docentes_estudios (docente, estudio)
    SELECT docente, id FROM estudios_realizados
    WHERE docente IS NOT NULL
    ON CONFLICT DO NOTHING;
""")

conn.commit()

# Verificar migración
cur.execute("SELECT COUNT(*) FROM docentes_estudios")
print("Registros en docentes_estudios:", cur.fetchone()[0])

# Probar todas las funciones
for sp, args in [
    ("sp_crud_docente_departamento", ('LISTAR',)),
    ("sp_crud_docentes_estudios", ('LISTAR',)),
    ("sp_crud_estudio_ac", ('LISTAR',)),
    ("sp_crud_red_docente", ('LISTAR',)),
]:
    cur.execute(f"SELECT * FROM {sp}(%s)", args)
    r = cur.fetchone()
    resultado = r[0] if r else None
    if isinstance(resultado, list):
        print(f"OK {sp}: {len(resultado)} registros")
    elif isinstance(resultado, dict) and 'error' in resultado:
        print(f"ERROR {sp}: {resultado['error']}")
    else:
        print(f"OK {sp}: {resultado}")

cur.close()
conn.close()


# Corregir sp_crud_docente_departamento (ORDER BY dentro de jsonb_agg)
cur.execute("""
CREATE OR REPLACE FUNCTION public.sp_crud_docente_departamento(
    p_operacion character varying,
    p_docente integer DEFAULT NULL,
    p_departamento integer DEFAULT NULL,
    p_dedicacion character varying DEFAULT NULL,
    p_modalidad character varying DEFAULT NULL,
    p_fecha_ingreso date DEFAULT NULL,
    p_fecha_salida date DEFAULT NULL,
    OUT p_resultado jsonb
)
RETURNS jsonb LANGUAGE plpgsql AS $function$
DECLARE v_record RECORD;
BEGIN
    IF p_operacion = 'LISTAR' THEN
        SELECT jsonb_agg(
            jsonb_build_object(
                'docente', dd.docente,
                'departamento', dd.departamento,
                'dedicacion', dd.dedicacion,
                'modalidad', dd.modalidad,
                'fecha_ingreso', dd.fecha_ingreso,
                'fecha_salida', dd.fecha_salida,
                'docente_nombre', d.nombres || ' ' || d.apellidos,
                'departamento_nombre', p.nombre
            ) ORDER BY d.apellidos, d.nombres
        ) INTO p_resultado
        FROM docente_departamento dd
        LEFT JOIN docente d ON d.cedula = dd.docente
        LEFT JOIN programa p ON p.id = dd.departamento;
        IF p_resultado IS NULL THEN p_resultado = jsonb_build_array(); END IF;
        RETURN;
    ELSIF p_operacion = 'INSERT' THEN
        IF EXISTS (SELECT 1 FROM docente_departamento WHERE docente = p_docente AND departamento = p_departamento) THEN
            p_resultado = jsonb_build_object('error', 'El docente ya está asignado a este departamento'); RETURN;
        END IF;
        INSERT INTO docente_departamento (docente, departamento, dedicacion, modalidad, fecha_ingreso, fecha_salida)
        VALUES (p_docente, p_departamento, p_dedicacion, p_modalidad, p_fecha_ingreso, p_fecha_salida);
        p_resultado = jsonb_build_object('mensaje', 'Relación docente-departamento creada exitosamente', 'docente', p_docente, 'departamento', p_departamento);
        RETURN;
    ELSIF p_operacion = 'UPDATE' THEN
        UPDATE docente_departamento
        SET dedicacion = COALESCE(p_dedicacion, dedicacion),
            modalidad = COALESCE(p_modalidad, modalidad),
            fecha_ingreso = COALESCE(p_fecha_ingreso, fecha_ingreso),
            fecha_salida = COALESCE(p_fecha_salida, fecha_salida)
        WHERE docente = p_docente AND departamento = p_departamento;
        IF FOUND THEN p_resultado = jsonb_build_object('mensaje', 'Relación docente-departamento actualizada exitosamente');
        ELSE p_resultado = jsonb_build_object('error', 'Relación docente-departamento no encontrada'); END IF;
        RETURN;
    ELSIF p_operacion = 'DELETE' THEN
        DELETE FROM docente_departamento WHERE docente = p_docente AND departamento = p_departamento;
        IF FOUND THEN p_resultado = jsonb_build_object('mensaje', 'Relación docente-departamento eliminada exitosamente');
        ELSE p_resultado = jsonb_build_object('error', 'Relación docente-departamento no encontrada'); END IF;
        RETURN;
    ELSE
        p_resultado = jsonb_build_object('error', 'Operación no válida. Use: LISTAR, INSERT, UPDATE, DELETE');
    END IF;
EXCEPTION WHEN OTHERS THEN
    p_resultado = jsonb_build_object('error', SQLERRM);
END;
$function$
""")

# Corregir sp_crud_estudio_ac (ORDER BY dentro de jsonb_agg)
cur.execute("""
CREATE OR REPLACE FUNCTION public.sp_crud_estudio_ac(
    p_operacion character varying,
    p_estudio integer DEFAULT NULL,
    p_area_conocimiento integer DEFAULT NULL,
    OUT p_resultado jsonb
)
RETURNS jsonb LANGUAGE plpgsql AS $function$
BEGIN
    IF p_operacion = 'LISTAR' THEN
        SELECT jsonb_agg(
            jsonb_build_object(
                'estudio', ea.estudio,
                'area_conocimiento', ea.area_conocimiento,
                'estudio_titulo', e.titulo,
                'area_nombre', a.area,
                'gran_area', a.gran_area,
                'disciplina', a.disciplina
            ) ORDER BY e.titulo, a.area
        ) INTO p_resultado
        FROM estudio_ac ea
        LEFT JOIN estudios_realizados e ON e.id = ea.estudio
        LEFT JOIN area_conocimiento a ON a.id = ea.area_conocimiento;
        IF p_resultado IS NULL THEN p_resultado = jsonb_build_array(); END IF;
        RETURN;
    ELSIF p_operacion = 'LISTAR_POR_ESTUDIO' THEN
        SELECT jsonb_agg(jsonb_build_object('id', a.id, 'gran_area', a.gran_area, 'area', a.area, 'disciplina', a.disciplina))
        INTO p_resultado
        FROM estudio_ac ea
        LEFT JOIN area_conocimiento a ON a.id = ea.area_conocimiento
        WHERE ea.estudio = p_estudio;
        IF p_resultado IS NULL THEN p_resultado = jsonb_build_array(); END IF;
        RETURN;
    ELSIF p_operacion = 'INSERT' THEN
        IF EXISTS (SELECT 1 FROM estudio_ac WHERE estudio = p_estudio AND area_conocimiento = p_area_conocimiento) THEN
            p_resultado = jsonb_build_object('error', 'El estudio ya tiene esta área de conocimiento'); RETURN;
        END IF;
        INSERT INTO estudio_ac (estudio, area_conocimiento) VALUES (p_estudio, p_area_conocimiento);
        p_resultado = jsonb_build_object('mensaje', 'Relación estudio-área creada exitosamente', 'estudio', p_estudio, 'area_conocimiento', p_area_conocimiento);
        RETURN;
    ELSIF p_operacion = 'DELETE' THEN
        DELETE FROM estudio_ac WHERE estudio = p_estudio AND area_conocimiento = p_area_conocimiento;
        IF FOUND THEN p_resultado = jsonb_build_object('mensaje', 'Relación estudio-área eliminada exitosamente');
        ELSE p_resultado = jsonb_build_object('error', 'Relación estudio-área no encontrada'); END IF;
        RETURN;
    ELSE
        p_resultado = jsonb_build_object('error', 'Operación no válida. Use: LISTAR, LISTAR_POR_ESTUDIO, INSERT, DELETE');
    END IF;
EXCEPTION WHEN OTHERS THEN
    p_resultado = jsonb_build_object('error', SQLERRM);
END;
$function$
""")

# Corregir sp_crud_intereses_futuros (ORDER BY dentro de jsonb_agg)
cur.execute("""
CREATE OR REPLACE FUNCTION public.sp_crud_intereses_futuros(
    p_operacion character varying,
    p_docente integer DEFAULT NULL,
    p_termino_clave character varying DEFAULT NULL,
    OUT p_resultado jsonb
)
RETURNS jsonb LANGUAGE plpgsql AS $function$
BEGIN
    IF p_operacion = 'LISTAR' THEN
        SELECT jsonb_agg(
            jsonb_build_object(
                'docente', i.docente,
                'termino_clave', i.termino_clave,
                'docente_nombre', d.nombres || ' ' || d.apellidos,
                'termino_ingles', t.termino_ingles
            ) ORDER BY d.apellidos, i.termino_clave
        ) INTO p_resultado
        FROM intereses_futuros i
        LEFT JOIN docente d ON d.cedula = i.docente
        LEFT JOIN termino_clave t ON t.termino = i.termino_clave;
        IF p_resultado IS NULL THEN p_resultado = jsonb_build_array(); END IF;
        RETURN;
    ELSIF p_operacion = 'LISTAR_POR_DOCENTE' THEN
        SELECT jsonb_agg(jsonb_build_object('termino', t.termino, 'termino_ingles', t.termino_ingles))
        INTO p_resultado
        FROM intereses_futuros i
        LEFT JOIN termino_clave t ON t.termino = i.termino_clave
        WHERE i.docente = p_docente;
        IF p_resultado IS NULL THEN p_resultado = jsonb_build_array(); END IF;
        RETURN;
    ELSIF p_operacion = 'INSERT' THEN
        IF EXISTS (SELECT 1 FROM intereses_futuros WHERE docente = p_docente AND termino_clave = p_termino_clave) THEN
            p_resultado = jsonb_build_object('error', 'El docente ya tiene este interés'); RETURN;
        END IF;
        INSERT INTO intereses_futuros (docente, termino_clave) VALUES (p_docente, p_termino_clave);
        p_resultado = jsonb_build_object('mensaje', 'Interés futuro asignado exitosamente', 'docente', p_docente, 'termino_clave', p_termino_clave);
        RETURN;
    ELSIF p_operacion = 'DELETE' THEN
        DELETE FROM intereses_futuros WHERE docente = p_docente AND termino_clave = p_termino_clave;
        IF FOUND THEN p_resultado = jsonb_build_object('mensaje', 'Interés futuro eliminado exitosamente');
        ELSE p_resultado = jsonb_build_object('error', 'Relación no encontrada'); END IF;
        RETURN;
    ELSE
        p_resultado = jsonb_build_object('error', 'Operación no válida. Use: LISTAR, LISTAR_POR_DOCENTE, INSERT, DELETE');
    END IF;
EXCEPTION WHEN OTHERS THEN
    p_resultado = jsonb_build_object('error', SQLERRM);
END;
$function$
""")

# Corregir sp_crud_red_docente (ORDER BY dentro de jsonb_agg)
cur.execute("""
CREATE OR REPLACE FUNCTION public.sp_crud_red_docente(
    p_operacion character varying,
    p_red integer DEFAULT NULL,
    p_docente integer DEFAULT NULL,
    p_fecha_inicio date DEFAULT NULL,
    p_fecha_fin character varying DEFAULT NULL,
    p_act_destacadas text DEFAULT NULL,
    OUT p_resultado jsonb
)
RETURNS jsonb LANGUAGE plpgsql AS $function$
BEGIN
    IF p_operacion = 'LISTAR' THEN
        SELECT jsonb_agg(
            jsonb_build_object(
                'red', rd.red,
                'docente', rd.docente,
                'fecha_inicio', rd.fecha_inicio,
                'fecha_fin', rd.fecha_fin,
                'act_destacadas', rd.act_destacadas,
                'red_nombre', r.nombre,
                'docente_nombre', d.nombres || ' ' || d.apellidos
            ) ORDER BY r.nombre, d.apellidos
        ) INTO p_resultado
        FROM red_docente rd
        LEFT JOIN red r ON r.idr = rd.red
        LEFT JOIN docente d ON d.cedula = rd.docente;
        IF p_resultado IS NULL THEN p_resultado = jsonb_build_array(); END IF;
        RETURN;
    ELSIF p_operacion = 'INSERT' THEN
        IF EXISTS (SELECT 1 FROM red_docente WHERE red = p_red AND docente = p_docente) THEN
            p_resultado = jsonb_build_object('error', 'El docente ya está en esta red'); RETURN;
        END IF;
        INSERT INTO red_docente (red, docente, fecha_inicio, fecha_fin, act_destacadas)
        VALUES (p_red, p_docente, p_fecha_inicio, p_fecha_fin, p_act_destacadas);
        p_resultado = jsonb_build_object('mensaje', 'Relación red-docente creada exitosamente', 'red', p_red, 'docente', p_docente);
        RETURN;
    ELSIF p_operacion = 'UPDATE' THEN
        UPDATE red_docente
        SET fecha_inicio = COALESCE(p_fecha_inicio, fecha_inicio),
            fecha_fin = COALESCE(p_fecha_fin, fecha_fin),
            act_destacadas = COALESCE(p_act_destacadas, act_destacadas)
        WHERE red = p_red AND docente = p_docente;
        IF FOUND THEN p_resultado = jsonb_build_object('mensaje', 'Relación red-docente actualizada exitosamente');
        ELSE p_resultado = jsonb_build_object('error', 'Relación red-docente no encontrada'); END IF;
        RETURN;
    ELSIF p_operacion = 'DELETE' THEN
        DELETE FROM red_docente WHERE red = p_red AND docente = p_docente;
        IF FOUND THEN p_resultado = jsonb_build_object('mensaje', 'Relación red-docente eliminada exitosamente');
        ELSE p_resultado = jsonb_build_object('error', 'Relación red-docente no encontrada'); END IF;
        RETURN;
    ELSE
        p_resultado = jsonb_build_object('error', 'Operación no válida. Use: LISTAR, INSERT, UPDATE, DELETE');
    END IF;
EXCEPTION WHEN OTHERS THEN
    p_resultado = jsonb_build_object('error', SQLERRM);
END;
$function$
""")

conn.commit()
print("Funciones corregidas exitosamente.")

# Probar LISTAR de cada una
import json
for sp, args in [
    ("sp_crud_docente_departamento", ('LISTAR',)),
    ("sp_crud_docentes_estudios", ('LISTAR',)),
    ("sp_crud_estudio_ac", ('LISTAR',)),
    ("sp_crud_red_docente", ('LISTAR',)),
]:
    cur.execute(f"SELECT * FROM {sp}(%s)", args)
    r = cur.fetchone()
    resultado = r[0] if r else None
    if isinstance(resultado, list):
        print(f"OK {sp}: {len(resultado)} registros")
    elif isinstance(resultado, dict) and 'error' in resultado:
        print(f"ERROR {sp}: {resultado['error']}")
    else:
        print(f"OK {sp}: {resultado}")

cur.close()
conn.close()

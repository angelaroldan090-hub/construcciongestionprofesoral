-- Fix para sp_listar_docentes_y_estudios
-- Corrige error de ORDER BY fuera del contexto de agregacion.

CREATE OR REPLACE FUNCTION public.sp_listar_docentes_y_estudios(OUT p_resultado jsonb)
RETURNS jsonb
LANGUAGE plpgsql
AS $function$
BEGIN
    SELECT COALESCE(
        jsonb_agg(registro ORDER BY cedula_orden),
        '[]'::jsonb
    )
    INTO p_resultado
    FROM (
        SELECT
            d.cedula AS cedula_orden,
            jsonb_build_object(
                'cedula', d.cedula,
                'nombres', d.nombres,
                'apellidos', d.apellidos,
                'genero', d.genero,
                'cargo', d.cargo,
                'correo', d.correo,
                'telefono', d.telefono,
                'escalafon', d.escalafon,
                'nacionalidad', d.nacionalidad,
                'estudios', COALESCE(
                    (
                        SELECT jsonb_agg(
                            jsonb_build_object(
                                'id', e.id,
                                'titulo', e.titulo,
                                'universidad', e.universidad,
                                'fecha', e.fecha,
                                'tipo', e.tipo,
                                'ciudad', e.ciudad,
                                'pais', e.pais,
                                'metodologia', e.metodologia,
                                'ins_acreditada', e.ins_acreditada,
                                'perfil_egresado', e.perfil_egresado
                            )
                            ORDER BY e.fecha DESC NULLS LAST, e.id DESC
                        )
                        FROM public.estudios_realizados e
                        WHERE e.docente = d.cedula
                    ),
                    '[]'::jsonb
                )
            ) AS registro
        FROM public.docente d
    ) x;
END;
$function$;

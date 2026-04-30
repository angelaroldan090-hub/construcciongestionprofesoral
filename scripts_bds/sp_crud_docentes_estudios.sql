-- SP CRUD para la tabla intermedia docentes_estudios
-- Maneja las operaciones LISTAR, INSERT y DELETE de la relación docente-estudio.
-- Patrón idéntico a sp_crud_docente_departamento.

CREATE OR REPLACE FUNCTION public.sp_crud_docentes_estudios(
    p_accion  TEXT,
    p_docente BIGINT DEFAULT NULL,
    p_estudio INT    DEFAULT NULL
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
    v_resultado JSONB;
BEGIN
    -- ── LISTAR ────────────────────────────────────────────────────────────────
    IF p_accion = 'LISTAR' THEN
        SELECT COALESCE(
            jsonb_agg(
                jsonb_build_object(
                    'docente', docente,
                    'estudio', estudio
                )
                ORDER BY docente, estudio
            ),
            '[]'::jsonb
        )
        INTO v_resultado
        FROM public.docentes_estudios;

    -- ── INSERT ────────────────────────────────────────────────────────────────
    ELSIF p_accion = 'INSERT' THEN
        IF p_docente IS NULL OR p_estudio IS NULL THEN
            RETURN jsonb_build_object('error', 'Se requieren docente y estudio para INSERT.');
        END IF;

        INSERT INTO public.docentes_estudios (docente, estudio)
        VALUES (p_docente, p_estudio)
        ON CONFLICT DO NOTHING;

        v_resultado := jsonb_build_object('mensaje', 'Asignación creada correctamente.');

    -- ── DELETE ────────────────────────────────────────────────────────────────
    ELSIF p_accion = 'DELETE' THEN
        IF p_docente IS NULL OR p_estudio IS NULL THEN
            RETURN jsonb_build_object('error', 'Se requieren docente y estudio para DELETE.');
        END IF;

        DELETE FROM public.docentes_estudios
        WHERE docente = p_docente
          AND estudio = p_estudio;

        v_resultado := jsonb_build_object('mensaje', 'Asignación eliminada correctamente.');

    -- ── ACCIÓN NO RECONOCIDA ──────────────────────────────────────────────────
    ELSE
        RETURN jsonb_build_object('error', 'Acción no reconocida: ' || COALESCE(p_accion, 'NULL'));
    END IF;

    RETURN v_resultado;
END;
$$;

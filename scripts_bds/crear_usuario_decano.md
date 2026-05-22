# Crear usuario Decano en Swagger

## Paso 1: Consultar ID del rol DECANO
GET /api/rol
Buscar el id del rol con nombre "DECANO"

## Paso 2: Crear usuario
POST /api/usuario?camposEncriptar=password

{
  "username": "test_decano",
  "password": "Decano123",
  "email": "test_decano@test.com",
  "nombre_completo": "Decano Test",
  "activo": true
}

## Paso 3: Consultar ID del usuario recién creado
GET /api/usuario
Buscar el id del usuario test_decano

## Paso 4: Asignar rol DECANO al usuario
POST /api/rol_usuario

{
  "usuario_id": ID_DEL_USUARIO,
  "rol_id": ID_DEL_ROL_DECANO
}
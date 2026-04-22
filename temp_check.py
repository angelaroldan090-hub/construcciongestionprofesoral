import requests
r=requests.get('http://localhost:5035/api/docente_departamento')
print('Status:', r.status_code)
data=r.json()
print('Registros existentes:')
for reg in data['datos']:
    print(f'  docente={reg["docente"]}, departamento={reg["departamento"]}')
# Cobranova 360 para Windows

Programa de la oficina. Nuitka lo convierte en `Cobranova.exe` e Inno Setup arma `Cobranova360-Setup.exe`.

La cartera queda en SQLite, en `%LOCALAPPDATA%\Cobranova\libro.db`. El programa abre el navegador en `http://127.0.0.1:8787` y también escucha en la red, para que el cobrador entre por ZeroTier.

## Descargar el instalador

1. Abre **Actions** en este repositorio.
2. Entra a la corrida **Instalador Windows**.
3. Descarga el artefacto `Cobranova360-Setup`.
4. Ejecuta el `.exe` en la computadora de la oficina.

En el teléfono del cobrador, con ZeroTier activo, la app abre `http://IP-ZEROTIER:8787`.

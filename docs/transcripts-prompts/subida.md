Tarea mecánica: subir 3 archivos locales a Google Drive con las herramientas MCP de Google Drive (si no están cargadas: ToolSearch "select:mcp__Google_Drive__create_file,mcp__Google_Drive__search_files"). No traduzcas, no edites ni reformatees nada, no toques git ni otros archivos.

Carpeta padre en Drive (año 2019): 1QStnJngv2OC16AzM26Lfs3nqTv4cbtd0

Pasos:
1. search_files con query `parentId = '1QStnJngv2OC16AzM26Lfs3nqTv4cbtd0' and title contains '<NNN>'`. Si ya existe alguna carpeta cuyo nombre empiece por "<NNN> ", PARA y repórtalo sin crear nada.
2. create_file con title = nombre de carpeta indicado, contentMimeType "application/vnd.google-apps.folder", parentId = la carpeta padre.
3. Para cada uno de los 3 archivos de la carpeta local (.txt → "text/plain"; .json y _es.json → "application/json"): léelo con `cat` y súbelo con create_file: parentId = carpeta nueva, title = nombre del archivo, textContent = contenido EXACTO byte a byte (incluido el salto de línea final, comillas tipográficas, líneas en blanco dobles entre turnos, espacios dobles), disableConversionToGoogleType = true.
4. Compara el fileSize de cada create_file con `wc -c` local. Si alguno no coincide, NO borres nada: repórtalo.

Devuelve solo: id de la carpeta creada y, por archivo, nombre, tamaño local y tamaño en Drive.

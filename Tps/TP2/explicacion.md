# COMPUTACION II - TP2
Fecha de entrega: 14/11/2023

## Descripción del Trabajo

El presente trabajo práctico tiene como objetivo el procesamiento de imágenes utilizando Python, haciendo uso de bibliotecas especializadas en el tratamiento de imágenes. El escenario planteado implica el envío de imágenes a un servidor HTTP concurrente para su procesamiento y posterior retorno al cliente. A continuación, se detallan los principales aspectos abordados en este trabajo:

### Problema

#### A
Se requiere implementar un sistema que permita el procesamiento de imágenes mediante un servidor HTTP concurrente. El servidor debe generar un hijo encargado de llevar a cabo un servicio no concurrente que convierta las imágenes recibidas del cliente a escala de grises. Para lograr esto, es esencial implementar un mecanismo de IPC que permita al servidor HTTP solicitar el procesamiento de imágenes. Además, se debe establecer un mecanismo de sincronización para que el servidor HTTP espere la finalización de la conversión de la imagen antes de enviarla al cliente y cerrar la conexión.

#### B
El servidor HTTP debe establecer comunicación con otro servidor en el mismo host. Este segundo servidor tiene la responsabilidad de reducir el tamaño de la imagen, utilizando un factor de escala proporcionado por el primer servidor.

#### C
Los servicios del servidor de escalado deben ser accesibles desde el cliente a través del primer servidor.

### Requerimientos

* La aplicación debe contener al menos 3 funciones.
* El servidor HTTP debe ser capaz de atender solicitudes tanto de direcciones IPv4 como IPv6 indistintamente.
* Se deben procesar las opciones mediante getopt (con la adición de una opción de ayuda) o con argparse.
* La aplicación debe manejar adecuadamente los errores.

### Necesario

#### Pasos
```bash
1) pip install -r requirements.txt
2) cd /compu2/Tps/TP2
3) Usos:

IPv4:
# server_a.py
python3 server_a.py -i 0.0.0.0 -p 8080

# server_b.py
python3 server_b.py -i 0.0.0.0 -p 8000 -s 0.5

IPv6:
# server_a.py
python3 server_a.py -i :: -p 8080 

# server_b.py
python3 server_b.py -i :: -p 8000 -s 0.5

# Enviar las imagenes:

curl -X POST -H "Content-Type: image/jpeg" --data-binary "@foto.jpg" http://localhost:8080

curl -X POST -H "Content-Type: image/jpeg" --data-binary "@compu.jpg" http://localhost:8080


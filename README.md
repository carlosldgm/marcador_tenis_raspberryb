# marcador_tenis_raspberryb

Marcador de tenis en la raspberry

pasos para ejecutarlo

1- desde mi notebook conectarme por ssh a la raspberry
ssh cldeg@192.168.1.58
pass: chaca 2 veces

2- dentro de la raspberry
cd rpi-rgb-led-matrix/mis_ejs/marcador_tenis_archivos/

3- Levantar servidor (Flask)
sudo python3 server.py 

4- desde mi notebook llamar a los servicios por postman (el json para importar en postmand estan en la carpeta del proyecto Marcador Tenis.postman_collection.json)

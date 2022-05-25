# Microservice LQN-CREDIFAMILIA

Lambda to connect to LQN with Web Service from Credifamilia.

### Requirements

1. AWS cli
2. Python environment:

```shell script
pip install -r requirements.txt
pip install -r requirements_dev.txt
```

### Build lambda package

1. Compilar una imagen para python 3.8 lambda.

```
docker build .
```

2. Obtener el id de la imagen. Debe ser la última creada.

```
docker images
```

3. Creamos un container con la imagen. No importa si falla al iniciar, solo importa crearlo.

```
docker run <id_imagen>
```

4. Obtener el id del container. Debe ser el último creado.

```
docker ps -a
```

5. Obtenemos el `lambda.zip` del container.

```
docker cp <id_container>:/var/task/lambda.zip .
```

### Upload lambda.zip

En AWS en la sección lambda, debe seleccionar la lambda respectiva.
Una vez dentro de la lambda en la tab de `Code` debe seleccionarse la opción `Upload from` -> `Zip file`.
Por último selecciona el archivo y espera a que actualice.

### Generar certificado

keytool -keystore credifamilia.p12 -genkey -alias [ALIAS] -keyalg RSA -keysize 2048 -sigalg SHA256withRSA -validity 365

keytool -export -alias [Alias] -keystore [P12_path_file] -file [Public_cert_file]

<!-- ### VPCs and IP addresses
#### Production:
- ip: 44.228.48.56
- vcp: vpc-0ef39cbcffc075d5b

#### Development:
- ip: 44.226.241.43
- vcp: vpc-08ad393e6de0f4c30


### Deploy lambdas
Configuration files are: `config_dev.yaml` and `config_prd.yaml`.

#### Production:
```shell script
 lambda deploy --preserve-vpc --config-file config_prd.yaml
```
#### Development:
```shell script
 lambda deploy --preserve-vpc --config-file config_dev.yaml
``` -->

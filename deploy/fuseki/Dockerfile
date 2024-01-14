# # FROM stain/jena-fuseki
# FROM d1egoprog/jena-fuseki:4.9.0-web

# # Set environment variables
# ENV ADMIN_PASSWORD=ADM01u
# ENV ENABLE_DATA_WRITE=true
# ENV ENABLE_UPDATE=true
# ENV ENABLE_UPLOAD=true
# ENV QUERY_TIMEOUT=100
# ENV FUSEKI_PORT=80

# # Expose the default port
#  EXPOSE 3030

# # Set the volume for data persistence


# CMD ["/jena-fuseki/fuseki-server"]

#FROM ubuntu:latest
FROM alpine:latest


ENV ADMIN_PASSWORD=ADM01u
ENV ENABLE_DATA_WRITE=true
ENV ENABLE_UPDATE=true
ENV ENABLE_UPLOAD=true
ENV QUERY_TIMEOUT=100
# ENV FUSEKI_BASE=/opt/fuseki/apache-jena-fuseki-4.10.0/fuseki-base

# Mise à jour des paquets et installation d'OpenJDK 8
RUN apk update && \
    apk add openjdk11 wget && \
    rm -rf /var/lib/apk/lists/*

# Téléchargement et extraction d'Apache Jena Fuseki
WORKDIR /opt/fuseki

RUN wget https://dlcdn.apache.org/jena/binaries/apache-jena-fuseki-4.10.0.tar.gz && \
    tar -xvzf apache-jena-fuseki-4.10.0.tar.gz && \
    rm apache-jena-fuseki-4.10.0.tar.gz && \
    cd apache-jena-fuseki-4.10.0 && \
    export FUSEKI_BASE=$(pwd)

EXPOSE 3030

WORKDIR /

COPY ./shiro.ini /opt/fuseki/apache-jena-fuseki-4.10.0/run/shiro.ini
ADD ./databases /opt/fuseki/apache-jena-fuseki-4.10.0/run/databases/
ADD ./configuration /opt/fuseki/apache-jena-fuseki-4.10.0/run/configuration/

# VOLUME ["${FUSEKI_BASE}/databases"]

# Définition du répertoire de travail
WORKDIR /opt/fuseki/apache-jena-fuseki-4.10.0

ENV JAVA_OPTIONS="-Xmx1048m -Xms1048m"

# Exécution du serveur Fuseki lors du démarrage du conteneur
CMD ["sh", "-c", "./fuseki-server --port=$PORT"]
#CMD ["sh", "-c", "while true; do echo 'This is an infinite loop'; sleep 1; done"]

FROM stain/jena-fuseki

# # Set environment variables
ENV ADMIN_PASSWORD=ADM01u
ENV ENABLE_DATA_WRITE=true
ENV ENABLE_UPDATE=true
ENV ENABLE_UPLOAD=true
ENV QUERY_TIMEOUT=100

EXPOSE 3030

# Set the volume for data persistence
VOLUME ["/fuseki-base/databases"]

COPY shiro.ini /jena-fuseki/run/shiro.ini

# Exécution du serveur Fuseki lors du démarrage du conteneur
CMD ["sh", "-c", "/jena-fuseki/fuseki-server --port=$PORT"]

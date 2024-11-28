FROM docker.elastic.co/elasticsearch/elasticsearch:8.6.2

# Set environment variables
ENV discovery.type=single-node
ENV xpack.security.enabled=false
ENV ES_JAVA_OPTS="-Xms1g -Xmx1g"

# Expose port 8080
EXPOSE 8080

# Command to start Elasticsearch
CMD [ "elasticsearch", "-Ehttp.port=8080" ]

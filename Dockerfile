FROM divio/base:1.0-py3.9-slim-buster
RUN apt update
RUN apt install --yes nginx
CMD ["nginx", "-g", "daemon off;"]

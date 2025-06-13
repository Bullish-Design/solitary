FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends git \
 && rm -rf /var/lib/apt/lists/*                 # installs Git 

WORKDIR /projects

# Install uv
RUN pip install uv

# Copy script
COPY ./scripts /projects/scripts
RUN chmod +x /projects/scripts/*.py /projects/scripts/*.sh

CMD ["/projects/scripts/entrypoint.sh"]

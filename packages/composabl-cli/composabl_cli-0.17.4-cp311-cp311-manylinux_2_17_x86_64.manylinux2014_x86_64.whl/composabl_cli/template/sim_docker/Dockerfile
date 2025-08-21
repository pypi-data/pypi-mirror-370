######################################################
# Composabl Image
######################################################
FROM python:3.11-slim

# Set working directory
WORKDIR /opt/composabl

# ######################################################
# Install Dependencies
# ######################################################
RUN apt update; apt install -y unzip tree

# ######################################################
# Make `python3` available as `python`
# ######################################################
RUN ln -s /usr/bin/python3 /usr/bin/python

# ######################################################
# Install Composabl
# ######################################################
RUN pip install composabl-core

# ######################################################
# Install Python Module
# ######################################################
COPY module/ /opt/composabl/sim/
RUN pip install /opt/composabl/sim/

# ######################################################
# Install Composabl Code and Docker scripts
# ######################################################
# Copy over the scripts
COPY docker /docker
RUN chmod +x /docker/*.sh

# Copy over the main startup file
# this file takes care of starting the Composabl server
COPY *.py /opt/composabl/

# ######################################################
# Define run
# ######################################################
EXPOSE 1337
CMD ["/docker/sim-start.sh", "/opt/composabl/sim"]

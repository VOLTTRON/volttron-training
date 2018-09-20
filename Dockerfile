FROM debian:jessie

SHELL [ "bash", "-c" ]

ENV VOLTTRON_GIT_BRANCH=feature/notebook_improvements
ENV VOLTTRON_APPLICATIONS_GIT_BRANCH=feature/simulation_fixes
ENV VOLTTRON_USER_HOME=/home/volttron
#ENV VOLTTRON_HOME=${VOLTTRON_USER_HOME}/.volttron
ENV VOLTTRON_ROOT=/code/volttron
ENV VOLTTRON_USER=volttron

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python-dev \
    openssl \
    libssl-dev \
    libevent-dev \
    python-pip \
    git \
    gnupg \
    sqlite3 \
    libsqlite3-dev \
    dirmngr \
    && pip install PyYAML \
    && rm -rf /var/lib/apt/lists/*

# Install additional libraries that are used by Jupyter notebooks and VOLTTRON agents
RUN python -m pip install --upgrade pip
RUN pip install jupyter==1.0.0 \
    && pip install matplotlib==2.2.3 \
    && pip install numpy==1.15.0 \
    && pip install isodate==0.6.0 \
    && pip install SQLAlchemy==1.1.4 \
    && pip install signxml==2.4

# add gosu for easy step-down from root
ENV GOSU_VERSION 1.7
RUN set -x \
	&& apt-get update && apt-get install -y --no-install-recommends ca-certificates wget && rm -rf /var/lib/apt/lists/* \
	&& wget -O /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$(dpkg --print-architecture)" \
	&& wget -O /usr/local/bin/gosu.asc "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$(dpkg --print-architecture).asc" \
	&& export GNUPGHOME="$(mktemp -d)" \
	&& gpg --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys B42F6819007F00F88E364FD4036A9C25BF357DD4 \
	&& gpg --batch --verify /usr/local/bin/gosu.asc /usr/local/bin/gosu \
	&& rm -rf "$GNUPGHOME" /usr/local/bin/gosu.asc \
	&& chmod +x /usr/local/bin/gosu \
	&& gosu nobody true \
&& apt-get purge -y --auto-remove wget

RUN adduser --disabled-password --gecos "" $VOLTTRON_USER

RUN mkdir /code && chown $VOLTTRON_USER.$VOLTTRON_USER /code

USER $VOLTTRON_USER
WORKDIR /code
RUN git clone https://github.com/ChargePoint/volttron -b ${VOLTTRON_GIT_BRANCH}
RUN git clone https://github.com/ChargePoint/volttron-applications -b ${VOLTTRON_APPLICATIONS_GIT_BRANCH}
WORKDIR ${VOLTTRON_ROOT}
RUN ln -s ../volttron-applications applications
RUN ls -la
RUN python bootstrap.py
RUN echo "source /code/volttron/env/bin/activate">${VOLTTRON_USER_HOME}/.bashrc
USER root

RUN pwd

# now we need to setup so we are always in the volttron python context
RUN echo "source /code/volttron/env/bin/activate">/home/${VOLTTRON_USER}/.bashrc

WORKDIR ${VOLTTRON_USER_HOME}

COPY . ${VOLTTRON_USER_HOME}
RUN chmod +x entrypoint.sh
RUN chmod +x bootstart.sh
RUN chmod +x start_jupyter.sh
RUN chmod +x -R volttron
RUN chmod +x -R .jupyter

RUN chown -R $VOLTTRON_USER: start_jupyter.sh
RUN chown -R $VOLTTRON_USER: volttron
RUN chown -R $VOLTTRON_USER: .jupyter
USER $VOLTTRON_USER
RUN chmod +x start_jupyter.sh
RUN chmod +x -R volttron
RUN chmod +x -R .jupyter

# Give the volttron group write permission on some files that can get overwritten by notebooks.
RUN chmod 664 ${VOLTTRON_ROOT}/applications/kisensum/Simulation/SimulationAgent/simulation/custom_setpoint.py
RUN chmod 664 ${VOLTTRON_ROOT}/applications/kisensum/Simulation/SimulationAgent/simulation/meter_target.py

# Allow notebooks files to be updated by containers
RUN chmod 664 ${VOLTTRON_ROOT}/examples/JupyterNotebooks/*
# Allow notebook checkpoint files to be written by containers
RUN chmod 774 ${VOLTTRON_ROOT}/examples/JupyterNotebooks

USER root
EXPOSE 22916

ENTRYPOINT ["./entrypoint.sh"]
CMD ["./bootstart.sh"]

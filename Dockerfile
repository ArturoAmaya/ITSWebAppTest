# TODO: For local dev, execute docker login repository.ucsd.edu and enter your UCSD email and AD password when prompted
# FROM v-its-ciap-docker.repository.ucsd.edu/rhel/minimal/8.x/python/3.9/webapp:v153
# FROM http://registry.access.redhat.com/ubi8/ubi-minimal/minimal/8.x/python/3.9/
FROM python:3.10.12-bookworm

# TODO: Probably remove this once a better local dev setup is worked out
EXPOSE 8080

# 
WORKDIR /code

# https://fastapi.tiangolo.com/deployment/docker/
# we first copy the file with the dependencies alone, not the rest of the code
COPY ./requirements.txt ./.env* /code/

# install python actually 
RUN apt-get -y update
# so the python xml wheel doesnt break, thanks to https://stackoverflow.com/questions/52378890/failed-building-wheel-for-xmlsec-mac
RUN apt-get -y install libxmlsec1
RUN apt-get -y install libxmlsec1-dev
RUN apt-get install pkg-config
#RUN apt-get -y install python3.10

#RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN pip install xmlsec
#RUN pip install greenlet
RUN python -m pip install --no-cache-dir --upgrade -r /code/requirements.txt

# install Julia
RUN wget https://julialang-s3.julialang.org/bin/linux/x64/1.7/julia-1.7.2-linux-x86_64.tar.gz
RUN tar zxvf julia-1.7.2-linux-x86_64.tar.gz

#RUN export PATH="$PATH:/code/julia-1.7.2/bin"
ENV PATH="${PATH}:/code/julia-1.7.2/bin"
# copy all the code. As this is what changes most frequently, we put it near the end, because almost always, anything after this step will not be able to use the cache.
COPY ./app /code/app

# setup Julia/Python stuff
RUN julia -e 'ENV["PYTHON"]="/usr/local/bin/python"'
RUN julia -e 'using Pkg; Pkg.add("PyCall")'
RUN python -c 'import julia;julia.install()'

# set up Julia environment, because it's weird
RUN julia -e 'using Pkg;Pkg.add(PackageSpec(name = "CurricularAnalytics", version="1.4.2"))'
RUN julia -e 'using Pkg;Pkg.add(url="https://github.com/ArturoAmaya/CurricularAnalyticsDiff.jl")'
RUN julia -e 'using Pkg;Pkg.add(PackageSpec(name = "DataFrames", version="0.21.8"))'
RUN julia -e 'using Pkg;Pkg.add(PackageSpec(name = "CSV", version="0.7.10"))'
RUN julia -e 'using Pkg;Pkg.add(PackageSpec(name = "SimpleWebsockets", version="0.1.4"))'
RUN julia -e 'using Pkg;Pkg.add(PackageSpec(name = "HTTP", version="0.8.19"))'
RUN julia -e 'using Pkg;Pkg.add(PackageSpec(name = "JSON", version="0.21.3"))'

# add option --proxy-headers if contaier behind load balancer like nginx
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers", "--forwarded-allow-ips", "*"]
#CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers", "--forwarded-allow-ips", "*", "--ssl-keyfile=./app/config/local-key.pem", "--ssl-certfile=./app/config/local-cert.pem"]

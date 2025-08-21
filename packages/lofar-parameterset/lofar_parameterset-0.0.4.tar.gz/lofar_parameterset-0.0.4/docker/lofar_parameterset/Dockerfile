# This dockerfile creates a minimal docker image that can run the project.
# It can copy the result of `tox -e build` from the host to the container
# or build from source inside the container.
# Set `docker build --build-arg BUILD_ENV=copy` to copy from the host, rebuild otherwise
# contrarily, to the ci image it does not contain any dependencies used for testing.
ARG BUILD_ENV=no_copy

# Build without copying from host inside docker
FROM python:3.13 AS build_no_copy
ADD ../../requirements.txt .
COPY ../.. /work
RUN rm -rf /work/dist
RUN python -m pip install --user tox
WORKDIR /work
RUN python -m tox -e build

# Copy build package from host `dist` directory
FROM python:3.13 AS build_copy
COPY dist /work/dist

# Dynamically set `build` from `build_no_copy` or `build_copy` depending on
# `BUILD_ENV` argument
FROM build_${BUILD_ENV} AS build

# Copy build stage files into final python slim image and install
FROM python:3.13-slim
COPY --from=build /work/dist /dist
RUN python -m pip install /dist/*.whl

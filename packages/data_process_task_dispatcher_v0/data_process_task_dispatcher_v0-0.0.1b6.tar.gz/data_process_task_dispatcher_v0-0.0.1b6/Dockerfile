FROM 172.22.121.50/gzhu/library/python:3.11-slim

COPY --from=172.22.121.50/gzhu/astral-sh/uv:latest /uv /uvx /bin/
ENV UV_SYSTEM_PYTHON=1
ENV UV_FROZEN=1
ENV UV_NO_CACHE=true

WORKDIR /workspace

ARG DEBIAN_FRONTEND=noninteractive

RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo 'Asia/Shanghai' >/etc/timezone

# hadolint ignore=DL3008
# Install what you need
# RUN apt-get clean && \
#     rm -rf /var/lib/apt/lists/* &&  \
#     rm -rf /etc/apt/sources.list.d && \
#     echo 'deb http://172.22.121.51:8081/repository/apt-aliyun//debian/ bookworm main' > /etc/apt/sources.list && \
#     echo 'deb http://172.22.121.51:8081/repository/apt-aliyun//debian-security/ bookworm-security main' >> /etc/apt/sources.list && \
#     echo 'deb http://172.22.121.51:8081/repository/apt-aliyun//debian/ bookworm-updates main' >> /etc/apt/sources.list && \
#     apt-get update && \
#     apt-get install -y --no-install-recommends \
#     curl && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/*

COPY README.md pyproject.toml uv.lock ./

RUN uv sync --no-install-project

COPY src src

RUN uv sync

ENTRYPOINT ["uv", "run", "endpoint"]

EXPOSE 10000

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from maleo.soma.dtos.configurations.middleware import CORSMiddlewareConfigurationDTO


def add_cors_middleware(
    app: FastAPI, *, configuration: CORSMiddlewareConfigurationDTO
) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=configuration.allow_origins,
        allow_methods=configuration.allow_methods,
        allow_headers=configuration.allow_headers,
        allow_credentials=configuration.allow_credentials,
        expose_headers=configuration.expose_headers,
    )

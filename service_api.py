#!/usr/bin/env python3

from helpers import (generic_error_message, make_invoice_model)
import json
import document_service
from fastapi import FastAPI, status, Body, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from Entity.models import EmailRequest
from Service.Data.caching import Caching


app = FastAPI(
    title="Document Service API",
    description="Document Service API.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


@app.get("/ping")
def pong():
    return "pong"


@app.get("/health")
def health_check():
    caching = Caching().get_instance()
    cache_status = caching.get("status").decode()
    if cache_status == "healthy":
        return {"status": "healthy"}
    return {"status": "unhealthy"}


@app.get("/get/")
def get_invoice(request: Request):
    """Fetch an invoice from DB."""
    try:
        api_service = document_service.Main()
        api_response = api_service.get_invoice(
            session_id=request.invoice_id
        )

        data = json.loads(api_response)

        the_invoice = make_invoice_model(data)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "success": True,
                "data": the_invoice,
                "response": [],
            },
        )
    except Exception as ex:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "data": generic_error_message,
                "response": ex,
            },
        )


@app.post("/email")
def send_email(req: EmailRequest = Body(...)):
    """Request an invoice be emailed to a user."""
    try:
        api_service = document_service.Main()
        api_service.email_via_rmq(
            recipient=req.recepient,
            body_text=req.body_text,
            subject_text=req.subject_text,
        )
    except Exception as ex:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "response": f"Exception: {ex}",
            },
        )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "success": True,
            "response": "OK",
        },
    )


### Exception Handlers ###
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status_code": exc.status_code,
            "success": False,
            "message": exc.detail,
            "response": [],
        },
    )

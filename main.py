from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

import os
import json
from datetime import datetime
from pydantic import BaseModel
from report_logger import logger
import ulid
from jinja2 import Environment, FileSystemLoader
from queue import Queue
from threading import Thread
import base64
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from utils import RecursiveNamespace, TemplateInstance
from constants import TEMPLATE_DIR, FONT_DIR, TRAYS_DIR


def get_available_templates():
    return [d[:-4] for d in os.listdir(TEMPLATE_DIR) if d.endswith('.tpl')] if not is_debug \
        else [d for d in os.listdir(TEMPLATE_DIR) if os.path.isdir(os.path.join(TEMPLATE_DIR, d))]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # @app.on_event("startup")
    logger.info("Starting up report generation API")
    for path in [FONT_DIR]:
        if not os.path.exists(path):
            logger.error(f"Required file not found: {path}")
            raise RuntimeError(f"Required file not found: {path}")
    if not get_available_templates():
        logger.error("No templates found in template directory")
        raise RuntimeError("No templates found")
    logger.info(f"Startup verification completed successfully - Available templates: {get_available_templates()}")
    yield
    # @app.on_event("shutdown")
    logger.info("Shutting down report generation API")

app = FastAPI(lifespan=lifespan)

# Jinja2 environment setup
template_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

class ReportData(BaseModel):
    content: dict
    template: str

class ReportStatus(BaseModel):
    status: str
    result: str = None

report_queue = Queue()
report_status = {}
worker_count = 1
is_debug = True

def worker():
    while True:
        request_id, data = report_queue.get()
        try:
            # Validate template
            available_templates = get_available_templates()
            if data.template not in available_templates:
                error_msg = f"Invalid template: {data.template}. Available templates: {available_templates}"
                logger.error(f"Template validation failed - Request ID: {request_id} - {error_msg}")
                raise ValueError(error_msg)

            # Load template content using TemplateInstance
            template_path = os.path.join(TEMPLATE_DIR, data.template) + (".tpl" if not is_debug else "")
            template_instance = TemplateInstance.load(template_path, debug=is_debug)
            if not template_instance or not template_instance.is_loaded():
                raise ValueError(f"Failed to load template: {data.template}")

            # Prepare template data
            template_data = {
                "date": datetime.now().strftime("%B %d, %Y"),
                "content": RecursiveNamespace(**data.content),
                "font_DIR": FONT_DIR
            }

            template_content = template_instance.render_content(template_data)
            html_content = template_content.html_content
            font_config = FontConfiguration()

            # Load CSS
            stylesheets = []
            if template_content.style_content:
                stylesheets.append(CSS(string=template_content.style_content, font_config=font_config))                  

            # Generate PDF
            output_path = os.path.join(TRAYS_DIR, f"report_{request_id}.pdf")
            
            logger.info(f"Generating PDF file: {output_path}")
            HTML(string=html_content).write_pdf(output_path, stylesheets=stylesheets, font_config=font_config, **(template_content.options or {}))

            if not os.path.exists(output_path):
                logger.error(f"PDF file was not created at: {output_path}")
                raise Exception("PDF generation failed")

            logger.info(f"Report generation successful - Request ID: {request_id}")
            report_status[request_id] = ReportStatus(status="success", result=output_path)

        except Exception as e:
            logger.error(f"Report generation failed - Request ID: {request_id} - Error: {str(e)}")
            report_status[request_id] = ReportStatus(status="failure", result=str(e))
        finally:
            report_queue.task_done()

for _ in range(worker_count):
    t = Thread(target=worker)
    t.daemon = True
    t.start()

@app.post("/queue/")
async def queue_report(data: ReportData):
    request_id = str(ulid.new())
    logger.info(f"New report request received - Request ID: {request_id}")
    report_status[request_id] = ReportStatus(status="in progress")
    report_queue.put((request_id, data))
    return {"request_id": request_id}

@app.get("/retrieve/{request_id}")
async def get_report(request_id: str):
    if request_id not in report_status:
        raise HTTPException(status_code=404, detail="Report not found")
    status = report_status[request_id]
    if status.status == "success" and status.result:
        pdf_path = status.result
        try:
            with open(pdf_path, "rb") as pdf_file:
                encoded_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
            os.remove(pdf_path)
            status.result = encoded_pdf
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to read or delete PDF file: {str(e)}")
    return status

@app.get("/status/")
async def queue_status():
    return {"queue_count": report_queue.qsize(), "worker_count": worker_count}

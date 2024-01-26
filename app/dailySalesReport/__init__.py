from flask import Flask, Blueprint
bp = Blueprint('dailysalesreport',__name__)


from app.dailysalesreport import routes
from flask import Flask, Blueprint
bp = Blueprint('stock',__name__)


from app.stock import routes
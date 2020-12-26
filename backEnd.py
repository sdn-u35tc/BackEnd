from flask import Flask, render_template, request
from flask_cors import CORS, cross_origin
import basicShell

app = Flask(__name__)
app.config['CORS_HEADERS']='Content-Type'
cors = CORS(app)

@app.route('/basictopo')
def getBasicTopo():
    return basicShell.basicTopoDisplay()
    

@app.route('/bestpath', methods=['get', 'post'])
@cross_origin()
def choice():
    
    bestPathGraph = basicShell.chooseBestPath()
    basicShell.dropFlows()
    basicShell.addFlows()

    return bestPathGraph


if __name__ == '__main__':
    app.run(host='127.0.0.1',port=5000)

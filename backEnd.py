from flask import Flask, render_template, request
from flask_cors import CORS, cross_origin
import basicShell

app = Flask(__name__)
app.config['CORS_HEADERS']='Content-Type'
cors = CORS(app)


@app.route('/basictopo', methods=['get', 'post'])
def getBasicTopo():
    
    return basicShell.basicTopoDisplay()
  

@app.route('/bestpath', methods=['get', 'post'])
@cross_origin()
def choice():

    if basicShell.deleteFlows() == 204 :
        basicShell.basicTopoDisplay()
        bestPathGraph = basicShell.chooseBestPath()
        basicShell.addFlows()
    else:
        return {"status":"Delete Flows Failed!"}

    return bestPathGraph


if __name__ == '__main__':
    app.run(host='192.168.28.129',port=5000)

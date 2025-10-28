# Mustafa Abdullah, Lucas Zheng, Eviss Wu
# London Metal Exchange
# SoftDev
# K20
# 2025-10-14t
# time spent: 0.5

from flask import Flask, render_template

app = Flask(__name__)

@app.route("/", methods=['GET','POST'])
def main():
    return render_template('index.html')
    print("does this work")

if __name__ == "__main__": #false if this file imported as module
    app.debug = True  #enable PSOD, auto-server-restart on code chg
    app.run()

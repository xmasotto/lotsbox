from flask import Flask, render_template

app = Flask(__name__)

@app.route('/signin')
def sign_in():
  return render_template('sign_in.html')

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0')
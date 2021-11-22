# install requirements
# %%bash
# pip install -qr https://raw.githubusercontent.com/ultralytics/yolov5/master/requirements.txt
import os
import shutil
from base64 import b64encode

import torch
from PIL import Image

from flask import Flask, send_file, jsonify
from flask import render_template
from flask import send_from_directory
from flask import request, redirect, url_for
from werkzeug.utils import secure_filename
#########################################
# model = torch.hub.load('pytorch/vision:v0.10.0', 'resnet18', pretrained=True)
# model.eval()
# from PIL import Image
# from torchvision import transforms
#########################################


UPLOAD_FOLDER = './uploads'
RESULTS_FOLDER = './runs/detect/exp'
DEL_RESULTS_FOLDER = './runs/detect'
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
MODEL = torch.hub.load('ultralytics/yolov5', 'yolov5x', pretrained=True)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULTS_FOLDER'] = RESULTS_FOLDER
app.config['DEL_RESULTS_FOLDER'] = DEL_RESULTS_FOLDER

@app.route('/')
def hello_world():
	return render_template('Home.html')

def allowed_file(filename):
	return '.' in filename and \
			filename.rsplit('.', 1)[-1] in ALLOWED_EXTENSIONS

@app.route('/',methods = ['GET','POST'])
def upload_file():
	if request.method =='POST':

		file = request.files['file']
		file.filename = file.filename.lower()
		if file and allowed_file(file.filename):

			#Deleting previous reuslts folders and result file
			try:
				shutil.rmtree(app.config['DEL_RESULTS_FOLDER'])
			except FileNotFoundError:
				pass

			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
			input_image = Image.open(os.path.join(app.config['UPLOAD_FOLDER'],filename))
			result = MODEL(input_image)
			result.save()

			# Deleting taken image from app.config['UPLOAD_FOLDER']
			img_dir = os.path.join(app.config['UPLOAD_FOLDER'],filename)
			os.remove(img_dir)

			#Taking result image and decoding it with b64
			with open(os.path.join(app.config['RESULTS_FOLDER'],filename[:-4]+'.jpg'), 'rb') as in_f:
				# so we read an image and decode it into utf-8 string and append it
				# to data:image/jpeg;base64 and then return it.
				img_b64 = b64encode(in_f.read()).decode('utf-8')

			return render_template('Results.html', image=img_b64)

			# return render_template('success.html')
	return render_template('wrong.html')

@app.route('/Results',methods = ['GET','POST'])
def return_home():
	if request.method =='POST':
		return render_template('Home.html')

if __name__ == '__main__':
	app.run()
import os
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from PIL import Image
import pytesseract
import pdf2image
from PyPDF2 import PdfFileMerger
import shutil

app = Flask(__name__)
# Clear Cache to avoid caching the Output File
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/')
def index():
   return render_template('index.html')
	
@app.route('/', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if there is a file in the request
        if 'file' not in request.files:
            return render_template('index.html', msg='No file selected')

        # Save Input file to directory
        input_file = request.files['file']
        input_file.save(secure_filename(input_file.filename))

        # OCR FILES
        pytesseract.pytesseract.tesseract_cmd = "C:\Program Files\Tesseract-OCR\Tesseract.exe"
        
        # Check whether PDF or Image File input 
        if input_file.filename[-3:] == "pdf" :
            ## Delete all the files in the "output" Directory
            # shutil.rmtree('./static/output')

            ## Create a new "output" directory
            try:
                # Search for directory if doesn't exist make a new
                os.mkdir('./static/output/temp/'+input_file.filename)
            except:
                # Pass if directory already exist
                pass

            ## Read a pdf file as image pages
            pages = pdf2image.convert_from_path(pdf_path=input_file.filename, dpi=200, size=(1654,2340))

            ## Save all pages as images
            for i in range(len(pages)):
                # pages[i].save('./static/output/temp_img_' + str(i) + '.jpg')
                pages[i].save('./static/output/temp/'+input_file.filename+'/temp_img_' + str(i) + '.jpg')

            ## Save all pages as multiple pdf
            for i in range(len(pages)):
                # Convert a page to hocr (page 2)
                content = pytesseract.image_to_pdf_or_hocr('./static/output/temp/'+input_file.filename+'/temp_img_' + str(i) + '.jpg', lang='eng+tel+urd', nice=0, extension='pdf')
                # Write content to a new file, owerwrite w or append a (b=binary)
                f = open('./static/output/temp/'+input_file.filename+'/temp_output_' + str(i) + '.pdf', 'w+b')
                f.write(bytearray(content))

            ## Merge all PDF to Single PDF
            location = './static/output/temp/'+input_file.filename
            x = [location+"\\"+a for a in os.listdir(location) if a.endswith(".pdf")]
            merger = PdfFileMerger()
            for pdf in x:
                merger.append(open(pdf, 'rb'))
            with open("./static/output/output.pdf", "wb") as fout:
                merger.write(fout)

            ## Delete the Input File
            os.remove(input_file.filename)
        else:
            # If the file is Image instead of PDF
            pdf = pytesseract.image_to_pdf_or_hocr(input_file.filename, extension='pdf', lang="eng+tel+urd")
            with open('./static/output/output.pdf', 'w+b') as f:
                f.write(pdf) # pdf type is bytes by default
                
            ## Delete the Input File
            os.remove(input_file.filename)

        ## extract the text and display it
        return render_template('index.html', extracted_text="Converted Successfully")

		
if __name__ == '__main__':
   app.run(debug = True)
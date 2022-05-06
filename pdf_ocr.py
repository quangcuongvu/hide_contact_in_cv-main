from paddleocr import PaddleOCR
from skimage import io
import re
import cv2
import os
from pdf2image import convert_from_path
import shutil
from subprocess import  Popen
from datetime import datetime
import docx
from subprocess import check_output
current_date_and_time= datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
### docx to pdf on linux
LIBRE_OFFICE = r"/usr/bin/lowriter"
def convert_to_pdf(input_docx, out_folder):
    p = Popen([LIBRE_OFFICE, '--headless', '--convert-to', 'pdf', '--outdir',
               out_folder, input_docx])
    print([LIBRE_OFFICE, '--convert-to', 'pdf', input_docx])
    p.communicate()

def get_num_pages(pdf_path):
    output = check_output(["pdfinfo", pdf_path]).decode()
    pages_line = [line for line in output.splitlines() if "Pages:" in line][0]
    num_pages = int(pages_line.split(":")[1])
    return num_pages

## use paddle detection text on image
ocr = PaddleOCR(use_angle_cls=True, lang='en') 

## merger images
def vconcat_resize_min(im_list, interpolation=cv2.INTER_CUBIC):
            w_min = min(im.shape[1] for im in im_list)
            im_list_resize = [cv2.resize(im, (w_min, int(im.shape[0] * w_min / im.shape[1])), interpolation=interpolation)
                              for im in im_list]
            return cv2.vconcat(im_list_resize)


def mask_cv(input_image):   ### che cv
    image = io.imread(input_image)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    result = ocr.ocr(image, cls=True)  
    for line in result:
        if(line[1][0].lower()=='timviec'):
          image[4:130,1402:1630] = 255,255,255
        patterns=['www.','\+84','[0-9]{4} [0-9]{3} [0-9]{3}','gma.','@','\S+\.com','\S+\.vn','\S+\:\/\S+','facebook.com','fb.com','\S+[0-9]{2}\.\S+','[0-9]{4}-[0-9]{3}-[0-9]{3}','[0-9]{6}[0-9]+','[0-9]{3}-[0-9]{3}-[0-9]{4}']
        for pattern in patterns:
            if(re.search(pattern,line[1][0])):
                x=line[0][0]
                y=line[0][2]
                image[int(x[1]):int(y[1]),int(x[0]):int(y[0])] = 255,255,255
    return image

def ocr_folder_image(input_image):
  list_image=[] 
  for file in os.listdir(input_image):
      print(file)  ### folder image
      input=input_image+'/'+file
      image=mask_cv(input)
      list_image.append(image)   
  image=vconcat_resize_min(list_image)
  return image

def create_folder_pdf(input_pdf):
    number_page=get_num_pages(input_pdf)
    if number_page<30:
      file=input_pdf.split('.pd')[0]
      if not os.path.exists(file):
        os.makedirs(file)
      pages=convert_from_path(input_pdf,200)
      counter=0
      for page in pages:
        myfile=file+'/'+str(counter)+'.png'
        page.save(myfile,'PNG')
        counter=counter+1
        if (counter>1):
          break
      return file
    else:
          print('error')

def ocr_image(input):
    name, extension = os.path.splitext(input)
    img_end=['.png','.jpg']
    doc_end=['.docx','.doc']
    input1=input.split('/')[0]
    input2=input.split('/')[1]
    folder_file=input1+'/'+input2
    if extension in img_end: ## if input is image
      if '/' in name:
        name=name.split('/')[-1]
      image=mask_cv(input)
      output=folder_file+'/'+name+'_'+str(current_date_and_time)+'.png'
      cv2.imwrite(output,image)
      os.remove(input)
      return output
    elif extension in doc_end: ## if input is doc,docx
      try:
        doc = docx.Document(input)  # Creating word reader object.
        data = ""
        fullText = []
        for para in doc.paragraphs:
            fullText.append(para.text)
            data = '\n'.join(fullText)
        if data == "":
          print('None')
          os.remove(input)
        if data!="":
          convert_to_pdf(input, folder_file)
          file=input.split('.doc')[0]
          if '/' in file:
            file_name=file.split('/')[-1]
          file_pdf=folder_file+'/'+file_name+'.pdf'
          input_image=create_folder_pdf(file_pdf)
          image_meger=ocr_folder_image(input_image)
          output=folder_file+'/'+file_name+'_'+str(current_date_and_time)+'.png'
          cv2.imwrite(output,image_meger)
          shutil.rmtree(input_image, ignore_errors=True)
          os.unlink(file_pdf)
          os.remove(input)
          return output
      except IOError:
          print('There was an error opening the file!')
    else:
      file=input.split('.pd')[0]
      if '/' in file:
        file_name=file.split('/')[-1]
        file_name=file.split('.pd')[0]
      input_image=create_folder_pdf(input)
      image_meger=ocr_folder_image(input_image)
      output=file_name+'_'+str(current_date_and_time)+'.png'
      cv2.imwrite(output,image_meger)
      shutil.rmtree(input_image, ignore_errors=True)
      os.unlink(input)
      return output
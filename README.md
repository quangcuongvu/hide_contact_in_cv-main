# hide_contact_in_cv
`Paddeocr + Flask api + opencv`


Dự án che số điện thoại và email trong CV sử dụng Paddleocr và flask để viết api.
------------------------------
Đầu vào:là file ảnh, pdf, doc hoặc docx


Đầu ra: là file ảnh định dạng png nằm trong thư mục static/result  


Sử dụng postman để nhận đầu vào. Đầu ra trả về địa chỉ hình ảnh sau khi che


#Hướng dẫn cài đặt
------------------------------

Sử dụng python 3.7 trên ubuntu. yêu cầu cần có libreoffice để chuyển đổi file docx sang pdf.


Trong quá trình chuyển đổi docx sang pdf ở ubuntu có thể sai chút định dạng so với file docx (do font chữ lạ hoặc định dạng khác thông thường)

1. Cài paddleocr (bản cpu)

python3 -m pip install paddlepaddle==2.0.0 -i https://mirror.baidu.com/pypi/simple


2. Cài đặt các thư viện ngoài lề phục vụ quá trình che số điện thoại và email

pip install -r requiremant.txt


3. chạy file app.py : python app.py 


4. chạy postman với câu lệnh:

 http://localhost:5000/api để chế độ POST với body >> form-data (với key: files[] và value: file gửi lên)

Cấu trúc thư mục
-----------------------------
```
MaskCV
├── ppocr                        // 
├── tools                       //   Thư mục của paddleocr để nhận diện chữ 
├── paddleocr.py               //          
│   
│   
│   
├── pdf_ocr.py                   // Code che số điện thoại và email trong cv theo yêu cầu bài toán  
│ 
│ 
│   
├── app.py                      // Flask viết api nhận gửi file và thực hiện che cv
├── __init__.py                //
│ 
│ 
├── static/result            // tự sinh ra khi bắt đầu chạy code để chứa file gửi lên từ api
│ 
├── requirement.txt        //  hướng dẫn cài đặt
```

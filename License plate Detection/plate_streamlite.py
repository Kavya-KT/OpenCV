#Importing Libraries
import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import cv2
import easyocr

# Load the Haar Cascade for number plate detection
number_cascade=cv2.CascadeClassifier('haarcascade_russian_plate_number.xml')

#create state code with corresponding state names
state={
    'AP':'Andhra Pradesh','AR':'Arunachal Pradesh','AS':'Assam','BR':'Bihar',
    'CG':'Chhattisgarh','GA':'Goa','GJ':'Gujarat','HR':'Haryana','HP':'Himanchal Pradesh',
    'JK':'Jammu and Kashmir','JH':'Jharkhand','KA':'Karnataka','KL':'Kerala',
    'MP':'Madhya Pradesh','MH':'Maharashtra','MN':'manipur','ML':'Meghalaya','MZ':'Mizoram',
    'NL':'Nagaland','OD':'Odisha','PB':'Panjab','RJ':'Rajasthan','SK':'sikkim',
    'TN':'Tamil Nadu','TS':'Telangana','TR':'Tripura','UP':'Uttar Pradesh','UK':'Uttarakhand',
    'WB':'West Bengal','DL':'Delhi','AN':'Andaman and Nicobar Islands','CH':'Chandigarh',
    'LD':'lakshadweep','PY':'Ponducherry'
}

st.write("<h1 style='text-align: center; color: violet;'>LICENCE PLATE DETECTION</h1>", unsafe_allow_html=True)
st.write('To identify the number plate and Using the number plate, get the details of the person too')

#Sidebar for File Upload
with st.sidebar:
    st.title('Upload')
    uploaded_file=st.file_uploader('upload an image',type=['png','jpeg','jpg'])

#Processing the Uploaded Image    
if uploaded_file is not None:
    img=Image.open(uploaded_file)    
    image_np=np.array(img)
    width=image_np.shape[1]*3
    height=image_np.shape[0]*3
    img=cv2.resize(image_np,(width,height))

    #Displaying the Image in Two Columns
    col1,col2=st.columns(2)
    with col1:
            st.image(img, caption='Uploaded Image')

    #Converting to Grayscale and Detecting License Plate
    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)   
    number_plate=number_cascade.detectMultiScale(gray,1.1,10)

    #Handling Detection Results    
    if len(number_plate)==0:
        st.write('No number plate detected')
    else:
       for (x,y,w,h) in number_plate:
        cv2.rectangle(image_np,(x,y),(x+w,y+h),(0,255,255),2)
        number_plate=gray[y:y+h,x:x+w]
        number_plate1=img[y:y+h,x:x+w]

        #Preprocess the number plate for better OCR accuracy
        _, number_plate = cv2.threshold(number_plate, 0, 255,cv2.THRESH_BINARY+  cv2.THRESH_OTSU)
        number_plate = cv2.GaussianBlur(number_plate, (5,5),0)
        
        #Performing OCR with EasyOCR
        reader = easyocr.Reader(['en'])
        number= reader.readtext(number_plate) 
        text=''.join(i.upper() for i in number[0][1] if i.isalnum())

        #Displaying the License Plate and Detected Text
        with col2:
                st.image(number_plate)
                st.write(f'Detected Licence Plate: <span style="color:blue;font-size:24px;"><i>{text}</i></span>', unsafe_allow_html=True)

        #Vehicle Details Lookup        
        statecode=text[0:2]
        if statecode in state:
           state_name=state[statecode]
        else:
            state_name="Unknown state"

        data={
            'VehicleNumber': ['MH04JM8765', 'MH20EJ0364', 'MH12DE1433', 'MH20EE7602', 'KL01BT1719',  'HR26DK8337', 'DL7C01939'],
            'Owner Name': ['John', 'Michael', 'Appu', 'Anju', 'Kerala State Government Insurance Department', 'Arjun','Anil'],
            'Phone Number': [2244556677, 9895140897, 7896541238,  9123456789, 8765432109, 9812345678, 9834567890]
            }
        df_vehicle_department = pd.DataFrame(data)
        def get_vehicle_details(text):
            row=df_vehicle_department[df_vehicle_department['VehicleNumber']==text]
            if not row.empty:
                return row.iloc[0]
            else:
                return None
        details=get_vehicle_details(text)
        
        #Displaying Vehicle Details
        with col2:
            if details is not None:
                name=details['Owner Name']
                number=details['Phone Number']
                if st.button('Get the details of the number plate'):
                        st.write(f'Vehicle belongs to:  <span style="font-size:24px;"><i>{ state_name.upper()}</i></span>', unsafe_allow_html=True)
                        st.write(f'Owner Name: <span style="font-size:24px;"><i>{name.upper()}</span></i>', unsafe_allow_html=True)
                        st.write(f'Phone Number: <span style="font-size:24px;"><i>{number}</span></i>', unsafe_allow_html=True)
                    
            else:

                st.write(f"No details found for vehicle number {text}")

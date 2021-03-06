# -*- coding: utf-8 -*-
"""

연세대학교 컴퓨터정보통신공학부
2021년 가을학기 - 인공지능
MNIST 실시간 인식(Tensorflow)
담당교수: 윤 한 얼

"""

#%%
# 참고자료
# Tensorflow
# https://www.tensorflow.org/tutorials/quickstart/beginner
# From_Anaconda_To_Tensorflow_Yonsei.pdf
# OpenCV
# https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_gui/py_video_display/py_video_display.html#display-video

#%%
import cv2 # conda install -c conda-forge opencv
import numpy as np
import tensorflow as tf # 2.1.0

#%%
# MNIST dataset
mnist = tf.keras.datasets.mnist

(X_train, y_train), (X_test, y_test) = mnist.load_data()

# Normalize
X_train = X_train.astype('float32')
X_train = X_train / 255.0
X_test = X_test.astype('float32')
X_test = X_test / 255.0

#%%
# MNIST shape
img_rows, img_cols = 28, 28

if tf.keras.backend.image_data_format() == 'channels_first':
    input_shape = (1, img_rows, img_cols)
    first_dim = 0
    second_dim = 1
else:
    input_shape = (img_rows, img_cols, 1)
    first_dim = 0
    second_dim = 3

X_train = np.expand_dims(X_train, second_dim)
X_test = np.expand_dims(X_test, second_dim)

#%%
# tensorflow.keras로 MNIST 인식 모델 구축
model = tf.keras.models.Sequential([
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(512, activation='relu'),
        tf.keras.layers.Dropout(0.2), # 512개의 노드 중 20%는 일부러 배제함(연산결과 0이 나오도록)->일반화 성능 up
        tf.keras.layers.Dense(10, activation='softmax')
        ])   # fill code
    
# 입력층과 출력층이 있음(입력층 노드수>출력층 노드수)
#한 층을 통과할때마다 노드의 개수는 점점 작아지는 방식으로
# 그리고 보통 중간 층의 노드개수는 2의 배수로 함

#%%
# MNIST 인식 모델 compile
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])   # fill code

# 계산된 예측결과와 정답결과를 비교할때,
# 정답결과를 one-hot-encoding하는 과정도 함수에 포함됨!
#%%
# MNIST 인식 모델 훈련
model.fit(X_train, y_train, epochs=5)   # fill code

#%%
# MNIST 인식 모델 정보 출력
model.summary()   # fill code

#%%
# MNIST 인식 모델 평가
model.evaluate(X_test, y_test)   # fill code

#%%
model.save_weights('./mnist_ffn/mnist_ffn_checkpoint')

#%%
font = cv2.FONT_HERSHEY_SIMPLEX

cp = cv2.VideoCapture(0)   # 여러개 카메라가 있을 시, 0번쨰 카메라 사용
cp.set(3, 5*128)
cp.set(4, 5*128)
SIZE = 28

#%%
def annotate(frame, label, location = (20,30)):
    #writes label on image#

    cv2.putText(frame, label, location, font,
                fontScale = 0.5,
                color = (255, 255, 0),
                thickness =  1,
                lineType =  cv2.LINE_AA)

def extract_digit(frame, rect, pad = 10):
    x, y, w, h = rect
    cropped_digit = final_img[y-pad:y+h+pad, x-pad:x+w+pad]
    cropped_digit = cropped_digit/255.0

    #only look at images that are somewhat big:
    if cropped_digit.shape[0] >= 32 and cropped_digit.shape[1] >= 32:
        cropped_digit = cv2.resize(cropped_digit, (SIZE, SIZE))
    else:
        return
    return cropped_digit

def img_to_mnist(frame, tresh = 90):
    gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_img = cv2.GaussianBlur(gray_img, (5, 5), 0)
    #adaptive here does better with variable lighting:
    gray_img = cv2.adaptiveThreshold(gray_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY_INV, blockSize = 321, C = 28)

    return gray_img

#%%
print("loading model")
model.load_weights('./mnist_ffn/mnist_ffn_checkpoint')

# 숫자 라벨 list 생성
num_label_list = ["zero", "one", "two", "three", "four",
                         "five", "six", "seven", "eight", "nine"]
labelz = dict(enumerate(num_label_list))

#%%
for i in range(1000):
    ret, frame = cp.read(0)

    final_img = img_to_mnist(frame)
    image_shown = frame
    contours, _ = cv2.findContours(final_img.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)

    rects = [cv2.boundingRect(contour) for contour in contours]
    rects = [rect for rect in rects if rect[2] >= 3 and rect[3] >= 8]

    #draw rectangles and predict:
    for rect in rects:

        x, y, w, h = rect

        if i >= 0:

            mnist_frame = extract_digit(frame, rect, pad = 15)

            if mnist_frame is not None: #and i % 25 == 0:
                mnist_frame = np.expand_dims(mnist_frame, first_dim) #needed for keras
                mnist_frame = np.expand_dims(mnist_frame, second_dim) #needed for keras

                class_prediction = model.predict_classes(mnist_frame, verbose = False)[0]
                prediction = np.around(np.max(model.predict(mnist_frame, verbose = False)), 2)
                label = str(prediction) # if you want probabilities

                cv2.rectangle(image_shown, (x - 15, y - 15), (x + 15 + w, y + 15 + h),
                              color = (255, 255, 0))

                label = labelz[class_prediction]

                annotate(image_shown, label, location = (rect[0], rect[1]))

    cv2.imshow('frame', image_shown)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break

#CSE574 | Project 4
#Description: TO implement a convolutional neural network to determine 
#whether the person in a portrait image is wearing glasses or not
#########################################################################

# import tensorflow as tf
import PIL.ImageOps
from PIL import Image
from sklearn import preprocessing
import numpy as np
from libs import *
import tensorflow as tf

filename = '../data/CelebA/Anno/list_attr_celeba.txt'
imagepath = '../data/CelebA/Img/img_align_celeba/'
celebData = 0
(celebData, labels, imageNames) = dataloader2(imagepath, filename)

#(celebData, labels, imageNames) = dataloader(imagepath, filename)
# celebData = celebData[0:100000,:,:,:]
# celebData = celebData[0:100000,:,:]
# labels = labels[0:100000,:]
# imageNames = imageNames[0:100000]
print("Celebdata dimension is ", celebData.shape)
print("labels dimension is ", labels.shape)
print("imageNames dimension is ", imageNames.shape)
#exit()
# # view_image(normalized_X[9999,:,:], train_images_label[9999])
# trains_images = celebData[0:20000,:,:,:]#getting the training sets
# test_images = celebData[20000:25000,:,:,:]#getting the training sets
# train_images_labels = labels[0:20000,:]
# test_images_labels = labels[20000:25000,:]
# # trains_images = trains_images.reshape([20000,2475*3])#flattening the input array
# test_images = test_images.reshape([5000,2475*3])

# view_image(normalized_X[9999,:,:], train_images_label[9999])
train_num = 21600 #80% of 70000
val_num = 2400
test_num = 6000

trains_images = celebData[0:train_num,:,:]#getting the training sets
train_images_labels = labels[0:train_num,:]

val_images = celebData[train_num:train_num+val_num,:,:]#getting the validation sets
val_images_labels = labels[train_num:train_num+val_num,:]

test_images = celebData[train_num+val_num:train_num+val_num+test_num,:,:]#getting the training sets
test_images_labels = labels[train_num+val_num:train_num+val_num+test_num,:]

#flattening the input array
# trains_images = trains_images.reshape([20000,2475*3])
trains_images = trains_images.reshape([train_num,784])
val_images = val_images.reshape([val_num,784])
test_images = test_images.reshape([test_num,784])

#standardizing the image data set with zero mean and unit standard deviation
trains_images = preprocessing.scale(trains_images)
val_images = preprocessing.scale(val_images)
test_images = preprocessing.scale(test_images)

#creating one-hot vectors for labels
train_images_labels_mat = np.zeros((train_num, 2), dtype=np.uint8)
train_images_labels_mat[np.arange(train_num), train_images_labels.T] = 1
train_images_labels = train_images_labels_mat
print(train_images_labels[51,:])

val_images_labels_mat = np.zeros((val_num, 2), dtype=np.uint8)
val_images_labels_mat[np.arange(val_num), val_images_labels.T] = 1
val_images_labels = val_images_labels_mat

test_images_labels_mat = np.zeros((test_num, 2), dtype=np.uint8)
test_images_labels_mat[np.arange(test_num), test_images_labels.T] = 1
test_images_labels = test_images_labels_mat

print("Train images shape: ", trains_images.shape)
print("Train labels shape: ", train_images_labels.shape)
print("Test images shape: ", val_images.shape)
print("Test labels shape: ", val_images_labels.shape)
print("Test images shape: ", test_images.shape)
print("Test labels shape: ", test_images_labels.shape)

#eyglasses at column 15+1
#Extract data

# for i in range(10):
# 	for file in os.listdir("../proj3_images/Numerals/"+str(i)+"/"):


#CNN model
#Create nodes for input images and target labels
tf.set_random_seed(2103)
x = tf.placeholder(tf.float32, shape = [None, 784]) 
actual_y = tf.placeholder(tf.float32, shape = [None, 2]) 
#dropout only during training to prevent overfitting, not during testing
no_drop_prob = tf.placeholder(tf.float32)  #probability of not dropping out the neurons output

logit_output = create_cnn_model(x, actual_y, no_drop_prob)

#-------Cross entropy loss function------
cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels = actual_y, logits = logit_output))

#training using optimizers: AdamOptimizer
train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)

#gives a boolean vector for whether the actual and predicted output match (1 if true, 0 if false)
right_prediction = tf.equal(tf.argmax(logit_output, 1), tf.argmax(actual_y, 1))

#get accuracy
accuracy = tf.reduce_mean(tf.cast(right_prediction, tf.float32))


#train and evaluate the model
with tf.Session() as sess:
	sess.run(tf.global_variables_initializer())
	# saver = tf.train.Saver()
	for i in range(100):
		for j in np.arange(0, train_num-10, 10):
			trainData = trains_images[j:j+10,:]
			trainLabels = train_images_labels[j:j+10,:]
			# print(i)
			if (i%10 == 0 and j == 0):
				train_accuracy = accuracy.eval(feed_dict={x: trainData, actual_y: trainLabels, no_drop_prob: 1.0})
				print("At step %d, training accuracy: %.2f" %(i, train_accuracy))
			train_step.run(feed_dict={x: trainData, actual_y: trainLabels, no_drop_prob: 0.5})
		print("Epoch ",i)
		if(i%2==0):
			print('cross_entropy loss is ', cross_entropy)
		
	#Run on validation data
	accuracy_val = accuracy.eval(feed_dict={x: val_images, actual_y: val_images_labels, no_drop_prob: 1.0})
	print("CelebA validation accuracy: %.2f" %(accuracy_val*100))

	#Run on test data
	accuracy_test = accuracy.eval(feed_dict={x: test_images, actual_y: test_images_labels, no_drop_prob: 1.0})
	print("CelebA test accuracy: %.2f" %(accuracy_test*100))

# test = Image.open("../data/CelebA/Img/img_align_celeba/"+imageNames[52])
# img_array = np.asarray(test)
# test.show()

#"../../CelebA/Anno/list_attr_celeba.txt"

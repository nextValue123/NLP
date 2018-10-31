import tensorflow as tf
import numpy as np

class TextCNN(object):
    def __init__(self, sequence_size, num_classes, vocab_size, embedding_size, filter_sizes, num_filters):

        #placeholders for input,output,dropout
        self.input_x = tf.placeholder(tf.int32, [None, sequence_size], name="input")
        self.input_y = tf.placeholder(tf.float32, [None, num_classes], name="output")
        self.dropout_keep_prob = tf.placeholder

        #keep track of l2 regularzation
        l2_loss = tf.constant(0.0)

        # Embedding layer
        with tf.device('/cpu:0'), tf.name_scope("embedding"):
            self.W = tf.Variable(
                tf.random_uniform([vocab_size, embedding_size], -1.0, 1.0),
                name="W")
            self.embedded_chars = tf.nn.embedding_lookup(self.W, self.input_x)
            #[batch_size, height, weight, input_channels] 其中batch_size为None
            self.embedded_chars_expanded = tf.expand_dims(self.embedded_chars, -1)

        #creating convolution + maxpool for ever layer
        pooled_outputs = []
        for i, filter_size in enumerate(filter_sizes):
            with tf.name_scope("conv-maxpool-%s" % filter_size):
                #convolution layers
                #[height, weight, input_channels, output_channels]第三个参数和输入的第四个参数一致
                filter_shape = [filter_size, embedding_size, 1, num_filters]
                W = tf.Variable(tf.truncated_normal(filter_shape, stddev=0.1), name="W")
                b = tf.Variable(tf.constant(0.1, [num_filters]), name="b")
                conv = tf.nn.conv2d(
                    self.embedded_chars_expanded,
                    W,
                    strides=[1, 1, 1, 1],
                    padding='VALID',
                    name="conv"
                )
                #卷积结果为：[None(batch_size), sequence_size - filter_size + 1, 1, num_filter]
                #apply nonlinearity
                h = tf.nn.relu(tf.nn.bias_add(conv, b), name="relu")
                #maxpooling layer
                pooled = tf.nn.max_pool(
                    h,
                    ksize=[1, sequence_size - filter_size + 1, 1, 1],
                    strides=[1, 1, 1, 1],
                    padding='VALID',
                    name="pool"
                )
                pooled_outputs.append(pooled)



"""
Created on Wed Sep 16 10:34:04 2020

@author: 九童
"""
#!/usr/bin/env python

import tensorflow as tf
import numpy as np

class attention(tf.keras.layers.Layer):
  def __init__(self, dim):
    super(attention, self).__init__()
    
    self.dim      = dim
    self.dense_s  = tf.keras.layers.Dense(self.dim)
    self.dense_h  = tf.keras.layers.Dense(self.dim)
    
  def call(self, inputs):
    #Split inputs into attentions vectors and inputs from the LSTM output
    s     = inputs[0]
    h     = inputs[1]
    
    #Linear FC
    s     = self.dense_s(s)
    h     = self.dense_h(h)
    
    #Linear blendning
    alpha = tf.keras.backend.expand_dims(s)
    alpha = tf.matmul(h, alpha)
    alpha = tf.keras.backend.squeeze(alpha, axis=-1)

    #softmax_vector
    softmaxed = tf.nn.softmax(alpha, axis=-1)
    softmaxed = tf.keras.backend.expand_dims(softmaxed, axis=-2)

    #Wheighted vector fetures
    c = tf.matmul(softmaxed, h)
    c = tf.keras.backend.squeeze(c, axis=-2)

    return c

class att_rnn( tf.keras.layers.Layer):
  def __init__(self, units,):
    super(att_rnn, self).__init__()
    self.units      = units
    self.state_size = [self.units, self.units]
    
    self.attention_context  = attention(self.units)
    self.rnn                = tf.keras.layers.LSTMCell(self.units)
    self.rnn2               = tf.keras.layers.LSTMCell(self.units)
    
  def call(self, inputs, states, constants):
    h       = tf.squeeze(constants, axis=0)

    s       = self.rnn(inputs=inputs, states=states)
    s       = self.rnn2(inputs=s[0], states=s[1])[1]

    c       = self.attention_context([s[0], h])
    out     = tf.keras.layers.concatenate([s[0], c], axis=-1)
    
    return out, [s[0], c]

class pBLSTM(tf.keras.layers.Layer):
  def __init__(self, dim):
    super(pBLSTM, self).__init__()
    
    self.dim        = dim
    self.LSTM       = tf.keras.layers.LSTM(self.dim, return_sequences=True)
    self.bidi_LSTM  = tf.keras.layers.Bidirectional(self.LSTM)
    
  @tf.function
  def call(self, inputs):
    y = self.bidi_LSTM(inputs)
    
    if( tf.shape(inputs)[1] % 2 == 1):
      y = tf.keras.layers.ZeroPadding1D(padding=(0, 1))(y)

    y = tf.keras.layers.Reshape(target_shape=(-1, int(self.dim*4)))(y)
    return y

def LAS(dim, f_1, no_tokens):
  input_1 = tf.keras.Input(shape=(None, f_1))
  input_2 = tf.keras.Input(shape=(None, no_tokens))
  
  #Listen; Lower resoultion by 8x
  x = pBLSTM( dim//2 )(input_1)
  x = pBLSTM( dim//2 )(x)
  x = pBLSTM( dim//2 )(x)
  
  #Attend
  x = tf.keras.layers.RNN(att_rnn(dim), return_sequences=True)(input_2, constants=x)
  
  #Spell
  x = tf.keras.layers.Dense(dim, activation="relu")(x)
  x = tf.keras.layers.Dense(no_tokens, activation="softmax")(x)

  model = tf.keras.Model(inputs=[input_1,input_2], outputs=x)
  return model
'''
调试中
model = LAS(256, 256, 16)
model.compile(loss="mse", optimizer="adam")

# x_1 should have shape (Batch-size, timesteps, f_1)
x_1 = np.random.random((1, 550, 256))

# x_2 should have shape (Batch-size, no_prev_tokens, No_tokens). The token vector should be one-hot encoded.
x_2 = np.zeros((1,12,16))
for n in range(12):
  x_2[0, n, np.random.randint(1, 16)] = 1

# By passing x_1 and x_2 the model will predict the 12th token 
# given by the spectogram and the prev predicted tokens

output = model.predict([x_1, x_2])
'''
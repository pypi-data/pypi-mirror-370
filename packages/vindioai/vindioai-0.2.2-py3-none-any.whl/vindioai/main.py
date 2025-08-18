# -*- coding: utf-8 -*-
"""

# **QUANTUM VISION THEORY - QV BLOCK**
"""

# Quantum Vision Theory in Deep Learning for Object Recognition
# Copyright (C) 2025 [Vindio AI Software Ltd. - https://vindioai.com / Cem Direkoglu and Melike Sah]
# AGPL-3.0 Licence

# Licensing Summary

# | Use Case                                   | Free? | Must Release Source Code?      | License Type           |
# |--------------------------------------------|-------|--------------------------------|------------------------|
# | Academic / research (non-commercial)       | Yes   |  Yes (if modified/distributed) | AGPL-3.0               |
# | Personal experiments / hobby projects      | Yes   |  Yes (if shared publicly)      | AGPL-3.0               |
# | Open-source commercial product             | Yes   |  Yes                           | AGPL-3.0               |
# | Closed-source commercial product           | No    |  No (with Enterprise License)  | Enterprise License     |

from tensorflow import keras
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten

import tensorflow as tf
import numpy as np

def QVBlock(momentum_magnitude, input_shape=(64, 64, 3), conv_layers=3, waves=128):
    input = layers.Input(shape=input_shape)

    momentum_magnitude = np.array(momentum_magnitude)

    if np.array_equal(momentum_magnitude, [1]) or np.array_equal(momentum_magnitude, [2]):
       print("##############\nMomentum magnitude of 1 or 2\n")

       shiftConv11 = Conv2D(
               3,
               (9,9),
               activation=None,
               padding='same',
               use_bias=True,
               bias_initializer='zeros',
               kernel_regularizer=None,
               bias_regularizer=None,
               activity_regularizer=None,
               kernel_constraint=None,
               bias_constraint=None,name=f"shiftConv11_{waves}")(input)

       shiftConv12 = Conv2D(waves, (3, 3), activation=None, padding='same',
              use_bias=False, bias_initializer='zeros',name='shiftConv12')(shiftConv11)
       x11 = tf.keras.activations.relu(shiftConv12, max_value=None, threshold=0.0)


       if conv_layers >= 2:
         shiftConv13 = Conv2D(waves, (3, 3), activation=None, padding='same',
              use_bias=False, bias_initializer='zeros',name='shiftConv13')(x11)
         x11 = tf.keras.activations.relu(shiftConv13, max_value=None, threshold=0.0)

       if conv_layers >= 3:
          shiftConv14 = Conv2D(waves, (3, 3), activation=None, padding='same',
              use_bias=False, bias_initializer='zeros',name='shiftConv14')(x11)
          x11 = tf.keras.activations.relu(shiftConv14, max_value=None, threshold=0.0)


       # shift2
       shiftConv21 = Conv2D(
               3,
               (9,9),
               activation=None,
               padding='same',
               use_bias=True,
               bias_initializer='zeros',
               kernel_regularizer=None,
               bias_regularizer=None,
               activity_regularizer=None,
               kernel_constraint=None,
               bias_constraint=None,name=f"shiftConv21_{waves}")(input)

       shiftConv22 = Conv2D(waves, (3, 3), activation=None, padding='same',
              use_bias=False, bias_initializer='zeros',name='shiftConv22')(shiftConv21)
       x21 = tf.keras.activations.relu(shiftConv22, max_value=None, threshold=0.0)

       if conv_layers >= 2:
          shiftConv23 = Conv2D(waves, (3, 3), activation=None, padding='same',
              use_bias=False, bias_initializer='zeros',name='shiftConv23')(x21)
          x21 = tf.keras.activations.relu(shiftConv23, max_value=None, threshold=0.0)

       if conv_layers >= 3:
          shiftConv24 = Conv2D(waves, (3, 3), activation=None, padding='same',
              use_bias=False, bias_initializer='zeros',name='shiftConv24')(x21)
          x21 = tf.keras.activations.relu(shiftConv24, max_value=None, threshold=0.0)


       # shift3
       shiftConv31 = Conv2D(
               3,
               (9,9),
               activation=None,
               padding='same',
               use_bias=True,
               bias_initializer='zeros',
               kernel_regularizer=None,
               bias_regularizer=None,
               activity_regularizer=None,
               kernel_constraint=None,
               bias_constraint=None, name=f"shiftConv31_{waves}")(input)

       shiftConv32 = Conv2D(waves, (3, 3), activation=None, padding='same',
                     use_bias=False, bias_initializer='zeros',name='shiftConv32')(shiftConv31)
       x31 = tf.keras.activations.relu(shiftConv32, max_value=None, threshold=0.0)

       if conv_layers >= 2:
          shiftConv33 = Conv2D(waves, (3, 3), activation=None, padding='same',
                     use_bias=False, bias_initializer='zeros',name='shiftConv33')(x31)
          x31 = tf.keras.activations.relu(shiftConv33, max_value=None, threshold=0.0)

       if conv_layers >= 3:
          shiftConv34 = Conv2D(waves, (3, 3), activation=None, padding='same',
                     use_bias=False, bias_initializer='zeros',name='shiftConv34')(x31)
          x31 = tf.keras.activations.relu(shiftConv34,  max_value=None, threshold=0.0)


       # shift4
       shiftConv41 = Conv2D(
               3,
               (9,9),
               activation=None,
               padding='same',
               use_bias=True,
               bias_initializer='zeros',
               kernel_regularizer=None,
               bias_regularizer=None,
               activity_regularizer=None,
               kernel_constraint=None,
               bias_constraint=None, name=f"shiftConv41_{waves}")(input)

       shiftConv42 = Conv2D(waves, (3, 3), activation=None, padding='same',
                     use_bias=False, bias_initializer='zeros',name='shiftConv42')(shiftConv41)
       x41 = tf.keras.activations.relu(shiftConv42, max_value=None, threshold=0.0)

       if conv_layers >= 2:
          shiftConv43 = Conv2D(waves, (3, 3), activation=None, padding='same',
                     use_bias=False, bias_initializer='zeros',name='shiftConv43')(x41)
          x41 = tf.keras.activations.relu(shiftConv43, max_value=None, threshold=0.0)

       if conv_layers >= 3:
          shiftConv44 = Conv2D(waves, (3, 3), activation=None, padding='same',
                     use_bias=False, bias_initializer='zeros',name='shiftConv44')(x41)
          x41 = tf.keras.activations.relu(shiftConv44, max_value=None, threshold=0.0)


       # ADDING INFORMATION WAVES
       # FOR A LIGHTER QV BLOCK, arelu13 or arelu12 etc. outputs can be added.
       addedlayers = tf.keras.layers.Add()([x11, x21, x31, x41])
       output = addedlayers


       return tf.keras.Model(inputs=input, outputs=output, name='QVblock')

# #######################################

    if np.array_equal(momentum_magnitude, [1, 2]) or np.array_equal(momentum_magnitude, [2, 4]):
       print("##############\nMomentum magnitude of [1, 2] or [2, 4]\n")

       shiftConv11 = Conv2D(
               3,
               (9,9),
               activation=None,
               padding='same',
               use_bias=True,
               bias_initializer='zeros',
               kernel_regularizer=None,
               bias_regularizer=None,
               activity_regularizer=None,
               kernel_constraint=None,
               bias_constraint=None,name=f"shiftConv11_{waves}")(input)

       shiftConv12 = Conv2D(waves, (3, 3), activation=None, padding='same',
              use_bias=False, bias_initializer='zeros',name='shiftConv12')(shiftConv11)
       x11 = tf.keras.activations.relu(shiftConv12, max_value=None, threshold=0.0)


       if conv_layers >= 2:
         shiftConv13 = Conv2D(waves, (3, 3), activation=None, padding='same',
              use_bias=False, bias_initializer='zeros',name='shiftConv13')(x11)
         x11 = tf.keras.activations.relu(shiftConv13, max_value=None, threshold=0.0)

       if conv_layers >= 3:
          shiftConv14 = Conv2D(waves, (3, 3), activation=None, padding='same',
              use_bias=False, bias_initializer='zeros',name='shiftConv14')(x11)
          x11 = tf.keras.activations.relu(shiftConv14, max_value=None, threshold=0.0)


       # shift2
       shiftConv21 = Conv2D(
               3,
               (9,9),
               activation=None,
               padding='same',
               use_bias=True,
               bias_initializer='zeros',
               kernel_regularizer=None,
               bias_regularizer=None,
               activity_regularizer=None,
               kernel_constraint=None,
               bias_constraint=None,name=f"shiftConv21_{waves}")(input)

       shiftConv22 = Conv2D(waves, (3, 3), activation=None, padding='same',
              use_bias=False, bias_initializer='zeros',name='shiftConv22')(shiftConv21)
       x21 = tf.keras.activations.relu(shiftConv22, max_value=None, threshold=0.0)

       if conv_layers >= 2:
          shiftConv23 = Conv2D(waves, (3, 3), activation=None, padding='same',
              use_bias=False, bias_initializer='zeros',name='shiftConv23')(x21)
          x21 = tf.keras.activations.relu(shiftConv23, max_value=None, threshold=0.0)

       if conv_layers >= 3:
          shiftConv24 = Conv2D(waves, (3, 3), activation=None, padding='same',
              use_bias=False, bias_initializer='zeros',name='shiftConv24')(x21)
          x21 = tf.keras.activations.relu(shiftConv24, max_value=None, threshold=0.0)


       # shift3
       shiftConv31 = Conv2D(
               3,
               (9,9),
               activation=None,
               padding='same',
               use_bias=True,
               bias_initializer='zeros',
               kernel_regularizer=None,
               bias_regularizer=None,
               activity_regularizer=None,
               kernel_constraint=None,
               bias_constraint=None, name=f"shiftConv31_{waves}")(input)

       shiftConv32 = Conv2D(waves, (3, 3), activation=None, padding='same',
                     use_bias=False, bias_initializer='zeros',name='shiftConv32')(shiftConv31)
       x31 = tf.keras.activations.relu(shiftConv32, max_value=None, threshold=0.0)

       if conv_layers >= 2:
          shiftConv33 = Conv2D(waves, (3, 3), activation=None, padding='same',
                     use_bias=False, bias_initializer='zeros',name='shiftConv33')(x31)
          x31 = tf.keras.activations.relu(shiftConv33, max_value=None, threshold=0.0)

       if conv_layers >= 3:
          shiftConv34 = Conv2D(waves, (3, 3), activation=None, padding='same',
                     use_bias=False, bias_initializer='zeros',name='shiftConv34')(x31)
          x31 = tf.keras.activations.relu(shiftConv34,  max_value=None, threshold=0.0)


       # shift4
       shiftConv41 = Conv2D(
               3,
               (9,9),
               activation=None,
               padding='same',
               use_bias=True,
               bias_initializer='zeros',
               kernel_regularizer=None,
               bias_regularizer=None,
               activity_regularizer=None,
               kernel_constraint=None,
               bias_constraint=None, name=f"shiftConv41_{waves}")(input)

       shiftConv42 = Conv2D(waves, (3, 3), activation=None, padding='same',
                     use_bias=False, bias_initializer='zeros',name='shiftConv42')(shiftConv41)
       x41 = tf.keras.activations.relu(shiftConv42, max_value=None, threshold=0.0)

       if conv_layers >= 2:
          shiftConv43 = Conv2D(waves, (3, 3), activation=None, padding='same',
                     use_bias=False, bias_initializer='zeros',name='shiftConv43')(x41)
          x41 = tf.keras.activations.relu(shiftConv43, max_value=None, threshold=0.0)

       if conv_layers >= 3:
          shiftConv44 = Conv2D(waves, (3, 3), activation=None, padding='same',
                     use_bias=False, bias_initializer='zeros',name='shiftConv44')(x41)
          x41 = tf.keras.activations.relu(shiftConv44, max_value=None, threshold=0.0)


       # shift5
       shiftConv51 = Conv2D(
               3,
               (9,9),
               activation=None,
               padding='same',
               use_bias=True,
               bias_initializer='zeros',
               kernel_regularizer=None,
               bias_regularizer=None,
               activity_regularizer=None,
               kernel_constraint=None,
               bias_constraint=None,name=f"shiftConv51_{waves}")(input)



       shiftConv52 = Conv2D(waves, (3, 3), activation=None, padding='same',
                     use_bias=False, bias_initializer='zeros',name='shiftConv52')(shiftConv51)
       x51 = tf.keras.activations.relu(shiftConv52, max_value=None, threshold=0.0)

       if conv_layers >= 2:
          shiftConv53 = Conv2D(waves, (3, 3), activation=None, padding='same',
                     use_bias=False, bias_initializer='zeros',name='shiftConv53')(x51)
          x51 = tf.keras.activations.relu(shiftConv53, max_value=None, threshold=0.0)

       if conv_layers >= 3:
          shiftConv54 = Conv2D(waves, (3, 3), activation=None, padding='same',
                     use_bias=False, bias_initializer='zeros',name='shiftConv54')(x51)
          x51 = tf.keras.activations.relu(shiftConv54, max_value=None, threshold=0.0)


       #shift6

       shiftConv61 = Conv2D(
               3,
               (9,9),
               activation=None,
               padding='same',
               use_bias=True,
               bias_initializer='zeros',
               kernel_regularizer=None,
               bias_regularizer=None,
               activity_regularizer=None,
               kernel_constraint=None,
               bias_constraint=None,name=f"shiftConv61_{waves}")(input)

       shiftConv62 = Conv2D(waves, (3, 3), activation=None, padding='same',
                     use_bias=False, bias_initializer='zeros',name='shiftConv62')(shiftConv61)
       x61 = tf.keras.activations.relu(shiftConv62, max_value=None, threshold=0.0)

       if conv_layers >= 2:
          shiftConv63 = Conv2D(waves, (3, 3), activation=None, padding='same',
                     use_bias=False, bias_initializer='zeros',name='shiftConv63')(x61)
          x61 = tf.keras.activations.relu(shiftConv63, max_value=None, threshold=0.0)

       if conv_layers >= 3:
          shiftConv64 = Conv2D(waves, (3, 3), activation=None, padding='same',
                     use_bias=False, bias_initializer='zeros',name='shiftConv64')(x61)
          x61 = tf.keras.activations.relu(shiftConv64, max_value=None, threshold=0.0)


       #shift7

       shiftConv71 = Conv2D(
               3,
               (9,9),
               activation=None,
               padding='same',
               use_bias=True,
               bias_initializer='zeros',
               kernel_regularizer=None,
               bias_regularizer=None,
               activity_regularizer=None,
               kernel_constraint=None,
               bias_constraint=None,name=f"shiftConv71_{waves}")(input)

       shiftConv72 = Conv2D(waves, (3, 3), activation=None, padding='same',
                     use_bias=False, bias_initializer='zeros',name='shiftConv72')(shiftConv71)
       x71 = tf.keras.activations.relu(shiftConv72, max_value=None, threshold=0.0)

       if conv_layers >= 2:
          shiftConv73 = Conv2D(waves, (3, 3), activation=None, padding='same',
                     use_bias=False, bias_initializer='zeros',name='shiftConv73')(x71)
          x71 = tf.keras.activations.relu(shiftConv73, max_value=None, threshold=0.0)

       if conv_layers >= 3:
          shiftConv74 = Conv2D(waves, (3, 3), activation=None, padding='same',
                     use_bias=False, bias_initializer='zeros',name='shiftConv74')(x71)
          x71 = tf.keras.activations.relu(shiftConv74, max_value=None, threshold=0.0)


       #shift8

       shiftConv81 = Conv2D(
               3,
               (9,9),
               activation=None,
               padding='same',
               use_bias=True,
               bias_initializer='zeros',
               kernel_regularizer=None,
               bias_regularizer=None,
               activity_regularizer=None,
               kernel_constraint=None,
               bias_constraint=None,name=f"shiftConv81_{waves}")(input)


       shiftConv82 = Conv2D(waves, (3, 3), activation=None, padding='same',
                     use_bias=False, bias_initializer='zeros',name='shiftConv82')(shiftConv81)
       x81 = tf.keras.activations.relu(shiftConv82, max_value=None, threshold=0.0)

       if conv_layers >= 2:
          shiftConv83 = Conv2D(waves, (3, 3), activation=None, padding='same',
                     use_bias=False, bias_initializer='zeros',name='shiftConv83')(x81)
          x81 = tf.keras.activations.relu(shiftConv83, max_value=None, threshold=0.0)

       if conv_layers >= 3:
          shiftConv84 = Conv2D(waves, (3, 3), activation=None, padding='same',
                     use_bias=False, bias_initializer='zeros',name='shiftConv84')(x81)
          x81 = tf.keras.activations.relu(shiftConv84, max_value=None, threshold=0.0)


       # ADDING INFORMATION WAVES
       # FOR A LIGHTER QV BLOCK, arelu13 or arelu12 etc. outputs can be added.
       addedlayers = tf.keras.layers.Add()([x11, x21, x31, x41, x51, x61, x71, x81])
       output = addedlayers

       return tf.keras.Model(inputs=input, outputs=output, name='QVblock')

    else:
        print("########################\nIncorrect momentum_magnitude parameter\n")

def Init_Freeze_ShiftSubtract_Layers(qvmodel, waves, momentum_magnitude):

####################################################################
# DEFINING FILTERS FOR SHIFT CONV LAYERS AND FREEZING WEIGHT LEARNING
####################################################################

#shiftConv11 Weight settings
   if f"shiftConv11_{waves}" in [layer.name for layer in qvmodel.layers]:
      weights_original2=qvmodel.get_layer(f"shiftConv11_{waves}").get_weights()[0];
      bias_original2=qvmodel.get_layer(f"shiftConv11_{waves}").get_weights()[1];

      shiftConv11_Weights=np.zeros((9, 9, 3, 3))

      if np.array_equal(momentum_magnitude, [1, 2]) or np.array_equal(momentum_magnitude, [1]):
        for mi in range(3):
          shiftConv11_Weights[4,4,mi,mi] = -1;
          shiftConv11_Weights[4,5,mi,mi] = 1;

      if np.array_equal(momentum_magnitude, [2]) or np.array_equal(momentum_magnitude, [2, 4]):
        for mi in range(3):
          shiftConv11_Weights[4,4,mi,mi] = -1;
          shiftConv11_Weights[4,6,mi,mi] = 1;

      # print("\nshiftConv11_Weights:")
      # print(shiftConv11_Weights)

      l2=[]
      l2.append(shiftConv11_Weights)
      l2.append(bias_original2)

      qvmodel.get_layer(f"shiftConv11_{waves}").set_weights(l2)

      #FREEZING LEARNING
      qvmodel.get_layer(f"shiftConv11_{waves}").trainable=False
      print(f"\nShiftConv11_{waves} layer filter weights are set and training is frozen\n")

#shiftConv21 Weight settings
   if f"shiftConv21_{waves}" in [layer.name for layer in qvmodel.layers]:
      weights_original3=qvmodel.get_layer(f"shiftConv21_{waves}").get_weights()[0]
      bias_original3=qvmodel.get_layer(f"shiftConv21_{waves}").get_weights()[1]

      shiftConv21_Weights=np.zeros((9, 9, 3, 3)) #index starts at 0

      if np.array_equal(momentum_magnitude, [1, 2]) or np.array_equal(momentum_magnitude, [1]):
        for mi in range(3):
          shiftConv21_Weights[4,4,mi,mi] = -1;
          shiftConv21_Weights[4,3,mi,mi] = 1;

      if np.array_equal(momentum_magnitude, [2]) or np.array_equal(momentum_magnitude, [2, 4]):
        for mi in range(3):
          shiftConv21_Weights[4,4,mi,mi] = -1;
          shiftConv21_Weights[4,2,mi,mi] = 1;

      # print("\nshiftConv21_Weights:")
      # print(shiftConv21_Weights)

      l3=[]
      l3.append(shiftConv21_Weights)
      l3.append(bias_original3)

      qvmodel.get_layer(f"shiftConv21_{waves}").set_weights(l3)

      #FREEZING LEARNING
      qvmodel.get_layer(f"shiftConv21_{waves}").trainable=False
      print(f"\nShiftConv21_{waves} layer filter weights are set and training is frozen\n")

#shiftConv31 Weight settings
   if f"shiftConv31_{waves}" in [layer.name for layer in qvmodel.layers]:
      weights_original4=qvmodel.get_layer(f"shiftConv31_{waves}").get_weights()[0]
      bias_original4=qvmodel.get_layer(f"shiftConv31_{waves}").get_weights()[1]

      shiftConv31_Weights=np.zeros((9, 9, 3, 3)) #index starts at 0

      if np.array_equal(momentum_magnitude, [1, 2]) or np.array_equal(momentum_magnitude, [1]):
        for mi in range(3):
          shiftConv31_Weights[4,4,mi,mi] = -1;
          shiftConv31_Weights[3,4,mi,mi] = 1;

      if np.array_equal(momentum_magnitude, [2]) or np.array_equal(momentum_magnitude, [2, 4]):
        for mi in range(3):
          shiftConv31_Weights[4,4,mi,mi] = -1;
          shiftConv31_Weights[2,4,mi,mi] = 1;

      # print("\nshiftConv31_Weights:")
      # print(shiftConv31_Weights)

      l4=[]
      l4.append(shiftConv31_Weights)
      l4.append(bias_original4)

      qvmodel.get_layer(f"shiftConv31_{waves}").set_weights(l4)

      #FREEZING LEARNING
      qvmodel.get_layer(f"shiftConv31_{waves}").trainable=False
      print(f"\nShiftConv31_{waves} layer filter weights are set and training is frozen\n")

#shiftConv41 Weight settings
   if f"shiftConv41_{waves}" in [layer.name for layer in qvmodel.layers]:
      weights_original5=qvmodel.get_layer(f"shiftConv41_{waves}").get_weights()[0]
      bias_original5=qvmodel.get_layer(f"shiftConv41_{waves}").get_weights()[1]

      shiftConv41_Weights=np.zeros((9, 9, 3, 3)) #index starts at 0

      if np.array_equal(momentum_magnitude, [1, 2]) or np.array_equal(momentum_magnitude, [1]):
        for mi in range(3):
          shiftConv41_Weights[4,4,mi,mi] = -1;
          shiftConv41_Weights[5,4,mi,mi] = 1;

      if np.array_equal(momentum_magnitude, [2]) or np.array_equal(momentum_magnitude, [2, 4]):
        for mi in range(3):
          shiftConv41_Weights[4,4,mi,mi] = -1;
          shiftConv41_Weights[6,4,mi,mi] = 1;

      # print("\nshiftConv41_Weights:")
      # print(shiftConv41_Weights)

      l5=[]
      l5.append(shiftConv41_Weights)
      l5.append(bias_original5)

      qvmodel.get_layer(f"shiftConv41_{waves}").set_weights(l5)

      #FREEZING LEARNING
      qvmodel.get_layer(f"shiftConv41_{waves}").trainable=False
      print(f"\nShiftConv41_{waves} layer filter weights are set and training is frozen\n")

#shiftConv51 Weight settings
   if f"shiftConv51_{waves}" in [layer.name for layer in qvmodel.layers]:
      weights_original6=qvmodel.get_layer(f"shiftConv51_{waves}").get_weights()[0]
      bias_original6=qvmodel.get_layer(f"shiftConv51_{waves}").get_weights()[1]

      shiftConv51_Weights=np.zeros((9, 9, 3, 3))

      if np.array_equal(momentum_magnitude, [1, 2]) or np.array_equal(momentum_magnitude, [1]):
        for mi in range(3):
          shiftConv51_Weights[4,4,mi,mi] = -1;
          shiftConv51_Weights[6,4,mi,mi] = 1;

      if np.array_equal(momentum_magnitude, [2]) or np.array_equal(momentum_magnitude, [2, 4]):
        for mi in range(3):
          shiftConv51_Weights[4,4,mi,mi] = -1;
          shiftConv51_Weights[8,4,mi,mi] = 1;

      # print("\nshiftConv51_Weights:")
      # print(shiftConv51_Weights)

      l6=[]
      l6.append(shiftConv51_Weights)
      l6.append(bias_original6)

      qvmodel.get_layer(f"shiftConv51_{waves}").set_weights(l6)

      #FREEZING LEARNING
      qvmodel.get_layer(f"shiftConv51_{waves}").trainable=False
      print(f"\nShiftConv51_{waves} layer filter weights are set and training is frozen\n")

#shiftConv61 Weight settings
   if f"shiftConv61_{waves}" in [layer.name for layer in qvmodel.layers]:
      weights_original7=qvmodel.get_layer(f"shiftConv61_{waves}").get_weights()[0]
      bias_original7=qvmodel.get_layer(f"shiftConv61_{waves}").get_weights()[1]

      shiftConv61_Weights=np.zeros((9, 9, 3, 3))

      if np.array_equal(momentum_magnitude, [1, 2]) or np.array_equal(momentum_magnitude, [1]):
        for mi in range(3):
          shiftConv61_Weights[4,4,mi,mi] = -1;
          shiftConv61_Weights[2,4,mi,mi] = 1;

      if np.array_equal(momentum_magnitude, [2]) or np.array_equal(momentum_magnitude, [2, 4]):
        for mi in range(3):
          shiftConv61_Weights[4,4,mi,mi] = -1;
          shiftConv61_Weights[0,4,mi,mi] = 1;

      # print("\nshiftConv61_Weights:")
      # print(shiftConv61_Weights)

      l7=[]
      l7.append(shiftConv61_Weights)
      l7.append(bias_original7)

      qvmodel.get_layer(f"shiftConv61_{waves}").set_weights(l7)

      #FREEZING LEARNING
      qvmodel.get_layer(f"shiftConv61_{waves}").trainable=False
      print(f"\nShiftConv61_{waves} layer filter weights are set and training is frozen\n")

#shiftConv71 Weight settings
   if f"shiftConv71_{waves}" in [layer.name for layer in qvmodel.layers]:

      weights_original8=qvmodel.get_layer(f"shiftConv71_{waves}").get_weights()[0]
      bias_original8=qvmodel.get_layer(f"shiftConv71_{waves}").get_weights()[1]

      shiftConv71_Weights=np.zeros((9, 9, 3, 3))

      if np.array_equal(momentum_magnitude, [1, 2]) or np.array_equal(momentum_magnitude, [1]):
        for mi in range(3):
          shiftConv71_Weights[4,4,mi,mi] = -1;
          shiftConv71_Weights[4,2,mi,mi] = 1;

      if np.array_equal(momentum_magnitude, [2]) or np.array_equal(momentum_magnitude, [2, 4]):
        for mi in range(3):
          shiftConv71_Weights[4,4,mi,mi] = -1;
          shiftConv71_Weights[4,0,mi,mi] = 1;

      # print("\nshiftConv71_Weights:")
      # print(shiftConv71_Weights)

      l8=[]
      l8.append(shiftConv71_Weights)
      l8.append(bias_original8)

      qvmodel.get_layer(f"shiftConv71_{waves}").set_weights(l8)

      #FREEZING LEARNING
      qvmodel.get_layer(f"shiftConv71_{waves}").trainable=False
      print(f"\nShiftConv71_{waves} layer filter weights are set and training is frozen\n")

#shiftConv81 Weight settings
   if f"shiftConv81_{waves}" in [layer.name for layer in qvmodel.layers]:
      weights_original9=qvmodel.get_layer(f"shiftConv81_{waves}").get_weights()[0];
      bias_original9=qvmodel.get_layer(f"shiftConv81_{waves}").get_weights()[1];

      shiftConv81_Weights=np.zeros((9, 9, 3, 3)) #index starts at 0

      if np.array_equal(momentum_magnitude, [1, 2]) or np.array_equal(momentum_magnitude, [1]):
        for mi in range(3):
          shiftConv81_Weights[4,4,mi,mi] = -1;
          shiftConv81_Weights[4,6,mi,mi] = 1;

      if np.array_equal(momentum_magnitude, [2]) or np.array_equal(momentum_magnitude, [2, 4]):
        for mi in range(3):
          shiftConv81_Weights[4,4,mi,mi] = -1;
          shiftConv81_Weights[4,8,mi,mi] = 1;

      # print("\nshiftConv81_Weights:")
      # print(shiftConv81_Weights)

      l9=[]
      l9.append(shiftConv81_Weights)
      l9.append(bias_original9)

      qvmodel.get_layer(f"shiftConv81_{waves}").set_weights(l9)

      #FREEZING LEARNING
      qvmodel.get_layer(f"shiftConv81_{waves}").trainable=False
      print(f"\nShiftConv81_{waves} layer filter weights are set and training is frozen\n")

   return qvmodel
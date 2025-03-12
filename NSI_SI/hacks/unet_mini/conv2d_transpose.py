from keras.engine import InputSpec
from keras.layers import Conv2D
from keras.utils.conv_utils import deconv_length
import keras.backend as K


class Conv2DTranspose(Conv2D):
    def __init__(
        self,
        filters,
        kernel_size,
        strides=(1, 1),
        padding='valid',
        output_shape=None,
        data_format=None,
        activation=None,
        use_bias=True,
        kernel_initializer='glorot_uniform',
        bias_initializer='zeros',
        kernel_regularizer=None,
        bias_regularizer=None,
        activity_regularizer=None,
        kernel_constraint=None,
        bias_constraint=None,
        **kwargs
    ):
        super().__init__(
            filters,
            kernel_size,
            strides=strides,
            padding=padding,
            data_format=data_format,
            activation=activation,
            use_bias=use_bias,
            kernel_initializer=kernel_initializer,
            bias_initializer=bias_initializer,
            kernel_regularizer=kernel_regularizer,
            bias_regularizer=bias_regularizer,
            activity_regularizer=activity_regularizer,
            kernel_constraint=kernel_constraint,
            bias_constraint=bias_constraint,
            **kwargs
        )
        self.input_spec = InputSpec(ndim=4)
        self._output_shape = tuple(output_shape) if output_shape is not None else None

    def build(self, input_shape):
        if len(input_shape) != 4:
            raise ValueError(f"Inputs should have rank 4; received shape: {input_shape}")
        channel_axis = 1 if self.data_format == 'channels_first' else -1

        if input_shape[channel_axis] is None:
            raise ValueError("The channel dimension of the inputs must be defined.")

        input_dim = input_shape[channel_axis]
        kernel_shape = self.kernel_size + (self.filters, input_dim)

        self.kernel = self.add_weight(
            shape=kernel_shape,
            initializer=self.kernel_initializer,
            name='kernel',
            regularizer=self.kernel_regularizer,
            constraint=self.kernel_constraint
        )
        self.bias = self.add_weight(
            shape=(self.filters,),
            initializer=self.bias_initializer,
            name='bias',
            regularizer=self.bias_regularizer,
            constraint=self.bias_constraint
        ) if self.use_bias else None

        self.input_spec = InputSpec(ndim=4, axes={channel_axis: input_dim})
        self.built = True

    def call(self, inputs):
        input_shape = K.shape(inputs)
        batch_size = input_shape[0]
        h_axis, w_axis = (2, 3) if self.data_format == 'channels_first' else (1, 2)

        height, width = input_shape[h_axis], input_shape[w_axis]
        kernel_h, kernel_w = self.kernel_size
        stride_h, stride_w = self.strides

        if self._output_shape is None:
            out_height = deconv_length(height, stride_h, kernel_h, self.padding)
            out_width = deconv_length(width, stride_w, kernel_w, self.padding)
            output_shape = (
                (batch_size, self.filters, out_height, out_width)
                if self.data_format == 'channels_first'
                else (batch_size, out_height, out_width, self.filters)
            )
        else:
            output_shape = (batch_size,) + self._output_shape

        outputs = K.conv2d_transpose(
            inputs, self.kernel, output_shape, self.strides,
            padding=self.padding, data_format=self.data_format
        )

        if self.bias is not None:
            outputs = K.bias_add(outputs, self.bias, data_format=self.data_format)

        return self.activation(outputs) if self.activation is not None else outputs

    def compute_output_shape(self, input_shape):
        output_shape = list(input_shape)
        c_axis, h_axis, w_axis = (1, 2, 3) if self.data_format == 'channels_first' else (3, 1, 2)

        kernel_h, kernel_w = self.kernel_size
        stride_h, stride_w = self.strides

        if self._output_shape is None:
            output_shape[c_axis] = self.filters
            output_shape[h_axis] = deconv_length(output_shape[h_axis], stride_h, kernel_h, self.padding)
            output_shape[w_axis] = deconv_length(output_shape[w_axis], stride_w, kernel_w, self.padding)
        else:
            output_shape[1:] = self._output_shape

        return tuple(output_shape)

    def get_config(self):
        config = super().get_config()
        config.pop('dilation_rate', None)  # Remove unused key
        config['output_shape'] = self._output_shape
        return config


from functools import partial

import numpy as np
import torch.nn as nn
import torch
import math
# from .model_utils import *
import math
import torch
from functools import partial
import torch.nn as nn
from einops import repeat, rearrange



class BlockLayer(nn.Module):
    def __init__(self, num_blcks, block_layer, planes_in, planes_out, kernel_size=3, first_layer=False,
                 input_size=None, norm_type='layer'):
        super(BlockLayer, self).__init__()

        self.blocks = nn.ModuleList()
        for i in range(num_blcks):
            if i == 0:
                self.blocks.append(block_layer(planes_in, planes_out, kernel_size=kernel_size, first_layer=first_layer,
                                               input_size=input_size, norm_type=norm_type))
            else:
                self.blocks.append(block_layer(planes_in, planes_out, kernel_size=kernel_size, first_layer=False,
                                               input_size=input_size, norm_type=norm_type))
            planes_in = planes_out

    def forward(self, x):
        for i, block in enumerate(self.blocks):
            x = block(x)
        return x


class ResidualBlock(nn.Module):
    def __init__(self, planes_in, planes_out, kernel_size=3, first_layer=False, input_size=128, norm_type='layer'):
        super(ResidualBlock, self).__init__()

        self.conv1 = ConvolutionalBlock(planes_in=planes_in, planes_out=planes_out, first_layer=first_layer,
                                        kernel_size=kernel_size, dilation=1,
                                        activation=nn.ELU, input_size=input_size, norm_type=norm_type)
        self.conv2 = ConvolutionalBlock(planes_in=planes_out, planes_out=planes_out, first_layer=False,
                                        kernel_size=1,
                                        dilation=1, activation=nn.ELU, input_size=input_size, norm_type=norm_type)
        if planes_in != planes_out:
            self.sample = nn.Conv3d(planes_in, planes_out, (1, 1, 1), stride=(1, 1, 1), dilation=(1, 1, 1),
                                    bias=True)  #
        else:
            self.sample = None

    def forward(self, x):
        identity = x.clone()

        x = self.conv1(x)
        x = self.conv2(x)

        if self.sample is not None:
            identity = self.sample(identity)

        x += identity

        return x


class UnetEncoder(nn.Module):
    def __init__(self, in_channel, base_inc_channel=8, layer=BlockLayer, block=None, layer_blocks=None,
                 downsampling_stride=None, feature_dilation=1.5, layer_widths=None, kernel_size=3,
                 norm_type='layer'):
        super(UnetEncoder, self).__init__()

        self.layers = nn.ModuleList()
        self.downsampling_convolutions = nn.ModuleList()
        self.attention_modules = nn.ModuleList()
        self.downsampling_zarib = []
        in_channel_layer = in_channel
        input_size = 192
        self._layers_with = []
        # self._layers_with.append(base_inc_channel)
        for i, num_blcks in enumerate(layer_blocks):
            if layer_widths is not None:
                out_channel_layer = layer_widths[i]
            else:
                out_channel_layer = base_inc_channel * int(feature_dilation ** (i + 1)) // 2

            if i == 0:
                first_layer = True
            else:
                first_layer = False
            self.layers.append(layer(num_blcks=num_blcks, block_layer=block,
                                     planes_in=in_channel_layer, planes_out=out_channel_layer,
                                     kernel_size=kernel_size,
                                     first_layer=first_layer, input_size=input_size,
                                     norm_type=norm_type))
            # self.attention_modules.append(Attention(out_channel_layer))
            if i != len(layer_blocks) - 1:
                # padding = kernel_size // 2  # constant size
                downsampling_conv = nn.Conv3d(out_channel_layer, out_channel_layer, (3, 3, 3), padding=3 // 2,
                                              stride=(downsampling_stride, downsampling_stride, downsampling_stride),
                                              bias=True)
                # downsampling_conv = nn.MaxPool3d(kernel_size=2, stride=2)

                self.downsampling_convolutions.append(downsampling_conv)

                input_size = input_size // 2
            print("Encoder {}:".format(i), in_channel_layer, out_channel_layer)
            self._layers_with.append(out_channel_layer)
            in_channel_layer = out_channel_layer
        self.out_channel_layer = in_channel_layer // 2
        self.last_downsampling_conv = nn.Conv3d(out_channel_layer, out_channel_layer, (3, 3, 3),
                                                padding=3 // 2,
                                                stride=(downsampling_stride, downsampling_stride, downsampling_stride),
                                                bias=True)
        self.output_size = input_size

    def forward(self, x):
        outputs = list()
        # outputs.insert(0, x)
        for layer, downsampling in zip(self.layers[:-1], self.downsampling_convolutions):
            x = layer(x)

            outputs.insert(0, x)

            x = downsampling(x)
        outputs.insert(0, x)
        x = self.layers[-1](x)
        x = self.last_downsampling_conv(x)
        #outputs.insert(0, x)  # bottle neck layer
        return x, outputs


class ConvolutionalBlock(nn.Module):
    def __init__(self, planes_in, planes_out, first_layer=False, kernel_size=3, dilation=1, activation=None,
                 input_size=None, norm_type='layer'):
        super(ConvolutionalBlock, self).__init__()
        if dilation == 1:
            padding = kernel_size // 2  # constant size
        else:
            # (In + 2*padding - dilation * (kernel_size - 1) - 1)/stride + 1
            if kernel_size == 3:
                if dilation == 2:
                    padding = 2
                elif dilation == 4:
                    padding = 4
                elif dilation == 3:
                    padding = 3
                else:
                    padding = None
            elif kernel_size == 1:
                padding = 0
        self.activation = None
        self.norm = None
        if first_layer:
            self.norm = nn.InstanceNorm3d(planes_in)
            self.activation = activation()
            self.conv = nn.Conv3d(planes_in, planes_out, (kernel_size, kernel_size, kernel_size),
                                  padding=padding, bias=True,
                                  dilation=(dilation, dilation, dilation))
        else:
            if activation is not None:
                if norm_type.lower() == 'layer':
                    self.norm = nn.LayerNorm([input_size, input_size, input_size])
                elif norm_type.lower() == 'group':
                    valid_num_groups = np.array([16, 8, 4, 2])
                    valid_num_groups = valid_num_groups[valid_num_groups < planes_in]
                    num_groups = None
                    for num_groups in valid_num_groups:
                        if planes_in % num_groups != 0:
                            break
                    if num_groups is None:
                        raise exit('Num groups can not be determined')
                    self.norm = nn.GroupNorm(num_groups=num_groups, num_channels=planes_in)
                elif norm_type.lower() == 'batch':
                    self.norm = nn.BatchNorm3d(planes_in)
                elif norm_type.lower() == 'instance':
                    self.norm = nn.InstanceNorm3d(planes_in)
                else:
                    self.norm = None

                self.activation = activation()
                self.conv = nn.Conv3d(planes_in, planes_out, (kernel_size, kernel_size, kernel_size),
                                      padding=padding, bias=True,
                                      dilation=(dilation, dilation, dilation))

            else:
                if norm_type.lower() == 'layer':
                    if input_size < 120:
                        self.norm = nn.LayerNorm([input_size, input_size, input_size])
                    else:
                        self.norm = nn.InstanceNorm3d(planes_in)
                elif norm_type.lower() == 'group':
                    valid_num_groups = [16, 8, 4, 2]
                    valid_num_groups = valid_num_groups[valid_num_groups < planes_in]
                    num_groups = None
                    for num_groups in valid_num_groups:
                        if planes_in % num_groups != 0:
                            break
                    if num_groups is None:
                        raise exit('Num groups can not be determined')
                    self.norm = nn.GroupNorm(num_groups=planes_in, num_channels=planes_in)
                elif norm_type.lower() == 'batch':
                    self.norm = nn.BatchNorm3d(planes_in)
                elif norm_type.lower() == 'instance':
                    self.norm = nn.InstanceNorm3d(planes_in)
                else:
                    self.norm = None

                self.conv = nn.Conv3d(planes_in, planes_out, (kernel_size, kernel_size, kernel_size),
                                      padding=padding, bias=True,
                                      dilation=(dilation, dilation, dilation))

    def forward(self, x):
        if self.norm is not None:
            x = self.norm(x)

        if self.activation is not None:
            x = self.activation(x)

        x = self.conv(x)

        return x


class UnetDecoder(nn.Module):
    def __init__(self, in_channel, base_inc_channel=64, layer=BlockLayer, block=None, layer_blocks=[1, 1, 1, 1],
                 feature_dilation=2, upsampling_stride=2, layer_widths=None, kernel_size=3,
                 upsampling_mode="trilinear", align_corners=False, use_transposed_convolutions=False,
                 last_cov_channels=256,
                 norm_type='layer'
                 ):
        super(UnetDecoder, self).__init__()
        self.layers = nn.ModuleList()

        self.upsampling_blocks = nn.ModuleList()

        self.attention_modules = nn.ModuleList()
        in_channel_layer = in_channel
        # input_size = 24
        input_size = 16

        for i, num_blcks in enumerate(layer_blocks):
            if layer_widths is not None:
                out_channel_layer = layer_widths[i]
            else:
                out_channel_layer = base_inc_channel // (feature_dilation ** (i))

            if i == 0:
                first_layer = True
                self.layers.append(layer(num_blcks=num_blcks, block_layer=block,
                                         planes_in=last_cov_channels, planes_out=out_channel_layer,
                                         kernel_size=kernel_size,
                                         first_layer=first_layer, input_size=input_size, norm_type=norm_type))
            else:
                first_layer = False

                self.layers.append(layer(num_blcks=num_blcks, block_layer=block,
                                         planes_in=in_channel_layer + layer_widths[i - 1], planes_out=out_channel_layer,
                                         kernel_size=kernel_size,
                                         first_layer=first_layer, input_size=input_size, norm_type=norm_type))


            # self.upsampling_blocks.append(nn.ConvTranspose3d(out_channel_layer, out_channel_layer, kernel_size=2,
            #                                                         stride=upsampling_stride, padding=0))
            self.upsampling_blocks.append(nn.Upsample(scale_factor=2, mode='trilinear'))

            input_size = input_size * 2
            last_cov_channels = in_channel_layer  # last_cov_channels//2
            print("Decoder {}:".format(i), in_channel_layer, out_channel_layer)
            in_channel_layer = out_channel_layer
        self.out_channel_layer = in_channel_layer

    def forward(self, y, x):
        i = 0
        outputs = list()
        #y = x[0]
        for up, lay in zip(self.upsampling_blocks, self.layers[:-1]):
            if i == 0:
                y = lay(y)
            else:
                y = lay(y)
            outputs.insert(0, y)
            y = up(y)
            y = torch.cat([y, x[i]], 1)

            # y = att(y)
            # y = torch.cat([y, x[i + 1]],1)
            i += 1
        outputs.insert(0, y)
        y = self.layers[-1](y)
        y = up(y)
        outputs.insert(0, y)
        return y, outputs


class Attention(nn.Module):
    def __init__(self, dim, heads=4, dim_head=16):
        super().__init__()
        self.scale = dim_head ** -0.5
        self.heads = heads
        hidden_dim = dim_head * heads

        self.to_qkv = nn.Conv3d(dim, hidden_dim * 3, 1, bias=False)
        self.to_out = nn.Conv3d(hidden_dim, dim // 2, 1)

    def forward(self, x, mask=None):
        b, c, h, w, z = x.shape
        qkv = self.to_qkv(x).chunk(3, dim=1)
        q, k, v = map(lambda t: rearrange(t, 'b (h c) x y z -> b h c (x y z)', h=self.heads), qkv)

        scaled_dot_prod = torch.einsum('... i d , ... j d -> ... i j', q, k) * self.scale
        attention = torch.softmax(scaled_dot_prod, dim=-1)
        v = v / (h * w * z)
        atv = torch.einsum('... i j , ... j d -> ... i d', attention, v)
        out = rearrange(atv, "b h c (x y z) -> b (h c) x y z", h=self.heads, x=h, y=w, z=z)
        return self.to_out(out)


class UnetGen(nn.Module):
    def __init__(self, base_inc_channel=8,
                 feature_dilation=2, downsampling_stride=2,
                 encoder_class=UnetEncoder, layer_widths=None, block=None,
                 kernel_size=3, interpolation_mode="trilinear", decoder_class=None,
                 use_transposed_convolutions=True, norm_type='layer', outChannels=3):
        super(UnetGen, self).__init__()

        use_transposed_convolutions = self.use_tr_conv
        inblock = 16
        base_inc_channel = inblock
        self.base_inc_channel = base_inc_channel

        # encoder_blocks = [1, 1, 1, 1, 1, 1]

        # decoder_blocks = [1,1,1,1, 1, 1]
        #encoder_blocks = [1, 1, 1]

        #decoder_blocks = [1, 1, 1]

        encoder_blocks = [1, 1, 1, 1, 1]

        decoder_blocks = [1, 1, 1, 1, 1]

        padding = kernel_size // 2  # constant size
        self.before_encoder = nn.Conv3d(1, inblock, kernel_size=(3, 3, 3),
                                        stride=(1, 1, 1), padding=3 // 2,
                                        bias=True)

        self.encoder = encoder_class(in_channel=inblock, base_inc_channel=base_inc_channel, layer_blocks=encoder_blocks,
                                     block=block,
                                     feature_dilation=feature_dilation, downsampling_stride=downsampling_stride,
                                     layer_widths=layer_widths, kernel_size=kernel_size,
                                     norm_type=norm_type)

        layer_widths = self.encoder._layers_with
        in_channel = layer_widths[-1]
        self.BottleNeck = BlockLayer(num_blcks=1, block_layer=block,
                                     planes_in=in_channel, planes_out=in_channel // 2,
                                     kernel_size=kernel_size,
                                     first_layer=False, input_size=self.encoder.output_size, norm_type=norm_type)

        # self.BottleNeck_att = Attention(in_channel)

        layer_widths = layer_widths[::-1]  # [1:]
        layer_widths[0] = layer_widths[0] // 2
        layer_widths[-1] = layer_widths[-2]

        in_channel = in_channel // 2
        self.decoder = decoder_class(in_channel=in_channel, base_inc_channel=base_inc_channel * 8,
                                     layer_blocks=decoder_blocks,
                                     block=block, last_cov_channels=self.encoder.out_channel_layer,
                                     upsampling_mode=interpolation_mode, layer_widths=layer_widths,
                                     use_transposed_convolutions=use_transposed_convolutions,
                                     kernel_size=kernel_size, norm_type=norm_type,
                                     )

        kernel_size = 3

        #self.last_convolution_rec = BlockLayer(num_blcks=1, block_layer=block,
        #                                       planes_in=inblock * 2, planes_out=inblock * 4,
        #                                       kernel_size=kernel_size,
        #                                       first_layer=False, input_size=192, norm_type=norm_type)

        """

        self.decoder2 = decoder_class(in_channel=in_channel, base_inc_channel=base_inc_channel*8, layer_blocks=decoder_blocks,
                                     block=block, last_cov_channels = self.encoder.out_channel_layer,
                                     upsampling_mode=interpolation_mode, layer_widths=layer_widths,
                                     use_transposed_convolutions=use_transposed_convolutions,
                                     kernel_size=kernel_size, norm_type=norm_type,
                                     )
        self.last_convolution_rec2 = BlockLayer(num_blcks=1, block_layer=block,
                                         planes_in=inblock*2, planes_out=inblock//2,
                                         kernel_size=kernel_size,
                                         first_layer=False, input_size=192, norm_type=norm_type)
        self.final_convolution_rec2 = nn.Conv3d(inblock//2, 1, kernel_size=(kernel_size, kernel_size, kernel_size),
                                           stride=(1, 1, 1), bias=True, padding=kernel_size // 2)
        """
        kernel_size = 1
        self.final_convolution_rec = nn.Conv3d(inblock * 3, outChannels, kernel_size=(kernel_size, kernel_size, kernel_size),
                                               stride=(1, 1, 1), bias=True, padding=kernel_size // 2)
        #self.seg_layer = nn.Conv3d(inblock * 3, outChannels, kernel_size=(kernel_size, kernel_size, kernel_size),
        #                                       stride=(1, 1, 1), bias=True, padding=kernel_size // 2)
        self.activation = nn.Softmax(dim=1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, y):
        y = self.before_encoder(y)

        y1, x = self.encoder(y)
        y1 = self.BottleNeck(y1)
        # x[0] = self.BottleNeck_att(x[0])

        x1, _ = self.decoder(y1, x)

        x1 = torch.cat([x1, y], 1)
        # x = (x * mask)
        #z1 = self.last_convolution_rec(x1)
        z1 = self.final_convolution_rec(x1)
        z2 = 0# self.seg_layer(x1)

        """

        x2, _ = self.decoder2(x)

        x2 = torch.cat([x2, y], 1)
        #x = (x * mask)
        z2 = self.last_convolution_rec2(x2)
        z2 = self.final_convolution_rec2(z2)
        """
        return z1, z2


class MGA_NET(UnetGen):
    def __init__(self, channels=3,  *args, encoder_class=UnetEncoder, **kwargs):
        self.use_tr_conv = False

        norm_type = "instance"
        super().__init__(encoder_class=encoder_class, decoder_class=UnetDecoder,
                         block=ResidualBlock, outChannels=channels, norm_type=norm_type, **kwargs)

        self.channels = channels
        self.netName = 'MGA_NET'

    def name(self):
        return 'MGA_NET'


class Segmentor(nn.Module):
    """
    Segmentor
    """

    def __init__(self,
                 channels=30):
        """

        """
        super().__init__()
        self.seg_model = MGA_NET(channels=channels)

    def forward(self, source, shape=None):
        pred_logits, pred_logits_seg = self.seg_model(source)

        return pred_logits, pred_logits_seg
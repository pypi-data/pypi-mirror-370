__AUTHOR__ = 'Bahram Jafrasteh'


import math
import torch
import torch.nn as nn

class BlockLayer(nn.Module):
    def __init__(self, num_blcks, block_layer, planes_in, planes_out, kernel_size=3, first_layer=False,
                 input_size=None, time_emb_dim=None, norm_type='layer'):
        super(BlockLayer, self).__init__()

        self.blocks = nn.ModuleList()
        for i in range(num_blcks):
            if i == 0:
                self.blocks.append(block_layer(planes_in, planes_out, kernel_size=kernel_size, first_layer=first_layer,
                                               input_size=input_size, time_emb_dim=time_emb_dim, norm_type=norm_type))
            else:
                self.blocks.append(block_layer(planes_in, planes_out, kernel_size=kernel_size, first_layer=False,
                                               input_size=input_size, time_emb_dim=time_emb_dim, norm_type=norm_type))
            planes_in = planes_out


    def forward(self, x, t=None):
        for i, block in enumerate(self.blocks):
            x = block(x, t)
        return x




class ResidualBlock(nn.Module):
    def __init__(self, planes_in, planes_out, time_emb_dim = None, kernel_size=3, first_layer=False, input_size=128, norm_type='layer'):
        super(ResidualBlock, self).__init__()
        if time_emb_dim is not None:
            if planes_in>planes_out:
                dim = planes_in*2
            else:
                dim = planes_in*2
            self.mlp = nn.Sequential(
                nn.SiLU(),
                nn.Linear(time_emb_dim, dim)
            )

        self.conv1 = ConvolutionalBlock(planes_in=planes_in, planes_out=planes_out, first_layer=first_layer,
                                        kernel_size=kernel_size, dilation=1,
                                        activation=nn.ReLU, input_size=input_size, norm_type= norm_type)
        self.conv2 = ConvolutionalBlock(planes_in=planes_out, planes_out=planes_out, first_layer=False,
                                        kernel_size=1,
                                        dilation=1, activation=nn.ReLU, input_size=input_size, norm_type=norm_type)
        if planes_in != planes_out:
            self.sample = nn.Conv3d(planes_in, planes_out, (1, 1, 1), stride=(1, 1, 1), dilation=(1, 1, 1),
                                    bias=True)  #
        else:
            self.sample = None

    def forward(self, x, time_emb= None):
        identity = x.clone()
        scale_shift = None
        if time_emb is not None:
            time_emb = self.mlp(time_emb)
            #time_emb = rearrange(time_emb, 'b c -> b c 1 1 1')
            time_emb = time_emb.unsqueeze(-1).unsqueeze(-1).unsqueeze(-1)
            #scale_shift = time_emb#.chunk(2, dim = 1)
            scale_shift = time_emb.chunk(2, dim=1)
        x = self.conv1(x, scale_shift= scale_shift)
        x = self.conv2(x, scale_shift=None)


        if self.sample is not None:
            identity = self.sample(identity)


        x += identity

        return x


class UnetEncoder(nn.Module):
    def __init__(self, in_channel, base_inc_channel=8, layer=BlockLayer, block=None,layer_blocks=None,
                 downsampling_stride=None,feature_dilation=1.5, layer_widths=None, kernel_size=3,
                 time_emb_dim=None, norm_type='layer'):
        super(UnetEncoder, self).__init__()

        self.layers = nn.ModuleList()
        self.downsampling_convolutions = nn.ModuleList()
        self.downsampling_zarib = []
        in_channel_layer = in_channel
        input_size = 192
        self._layers_with = []
        self._layers_with.append(base_inc_channel)
        for i, num_blcks in enumerate(layer_blocks):
            if layer_widths is not None:
                out_channel_layer = layer_widths[i]
            else:
                out_channel_layer = base_inc_channel * int(feature_dilation ** (i+1))//2
                #if out_channel_layer>128:
                #    out_channel_layer = 128 + out_channel_layer//int(2*feature_dilation)

            if i == 0:
                first_layer = True
            else:
                first_layer = False
            self.layers.append(layer(num_blcks=num_blcks, block_layer=block,
                                     planes_in=in_channel_layer, planes_out=out_channel_layer,
                                     kernel_size=kernel_size,
                                     first_layer=first_layer, input_size=input_size,
                                     time_emb_dim=time_emb_dim, norm_type=norm_type))
            if i != len(layer_blocks) - 1:

                padding = kernel_size // 2  # constant size
                #downsampling_conv = nn.Conv3d(out_channel_layer, out_channel_layer, (kernel_size, kernel_size, kernel_size), padding=padding,
                #              stride=(downsampling_stride,downsampling_stride,downsampling_stride),
                #                 bias=True)
                downsampling_conv = nn.MaxPool3d(kernel_size=2, stride=2)

                self.downsampling_convolutions.append(downsampling_conv)

                input_size = input_size // 2
            print("Encoder {}:".format(i), in_channel_layer, out_channel_layer)
            self._layers_with.append(out_channel_layer)
            in_channel_layer = out_channel_layer
        self.out_channel_layer = in_channel_layer
        self.output_size = input_size

    def forward(self, x, time=None):
        outputs = list()
        #outputs.insert(0, x)
        for layer, downsampling in zip(self.layers[:-1], self.downsampling_convolutions):
            x = layer(x, time)
            outputs.insert(0, x)
            x = downsampling(x)
        x = self.layers[-1](x, time)
        outputs.insert(0, x) #bottle neck layer
        return outputs

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
            self.activation = activation()
            self.conv = nn.Conv3d(planes_in, planes_out, (kernel_size, kernel_size, kernel_size),
                                                  padding=padding, bias=True,
                                                  dilation=(dilation, dilation, dilation))
        else:
            if activation is not None:
                if norm_type.lower()=='layer':
                    self.norm = nn.LayerNorm([input_size, input_size, input_size])
                elif norm_type.lower()=='group':
                    valid_num_groups = [16, 8, 4, 2]
                    num_groups = None
                    for num_groups in valid_num_groups:
                        if planes_in % num_groups != 0:
                            break
                    if num_groups is None:
                        raise exit('Num groups can not be determined')
                    self.norm = nn.GroupNorm(num_groups=num_groups, num_channels=planes_in)
                elif norm_type.lower()=='batch':
                    self.norm = nn.BatchNorm3d(planes_in)
                elif norm_type.lower() == 'instance':
                    self.norm = nn.InstanceNorm3d(planes_in)
                else:
                    self.norm= None

                self.activation = activation()
                self.conv = nn.Conv3d(planes_in, planes_out, (kernel_size, kernel_size, kernel_size),
                                                      padding=padding, bias=True,
                                                      dilation=(dilation, dilation, dilation))

            else:
                if norm_type.lower()=='layer':
                    if input_size<120:
                        self.norm = nn.LayerNorm([input_size, input_size, input_size])
                    else:
                        self.norm = nn.InstanceNorm3d(planes_in)
                elif norm_type.lower()=='group':
                    valid_num_groups = [16, 8, 4, 2]
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


    def forward(self, x, scale_shift=None):
        if self.norm is not None:
            x = self.norm(x)

        if scale_shift is not None:
            scale, shift = scale_shift
            #scale1, scale2 = scale.chunk(2, dim=0)
            #shift1, shift2 = scale.chunk(2, dim=0)
            #x = x * (scale1 + 1) + shift1 +  x * (scale2 + 1) + shift2
            x = x * (scale + 1) + shift

        if self.activation is not None:
            x = self.activation(x)

        x = self.conv(x)

        return x
class SinusoidalPosEmb(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.dim = dim

    def forward(self, x):
        device = x.device
        half_dim = self.dim // 2
        emb = math.log(10000) / (half_dim - 1)
        emb = torch.exp(torch.arange(half_dim, device=device) * -emb)
        emb = x[...,None]*emb[None,:]
        emb = torch.cat((emb.sin(), emb.cos()), dim=-1)
        if len(emb.shape)==3:
            emb = emb.view(emb.shape[0], emb.shape[1] * emb.shape[2])
        return emb



class UnetDecoder(nn.Module):
    def __init__(self, in_channel, base_inc_channel=64, layer=BlockLayer, block=None,layer_blocks=[1,1,1,1],
                 feature_dilation=2, upsampling_stride=2, layer_widths=None, kernel_size=3,
                 upsampling_mode="trilinear", align_corners=False, use_transposed_convolutions=False, last_cov_channels=256,
                 time_emb_dim=None, norm_type='layer'
                 ):
        super(UnetDecoder, self).__init__()
        self.layers = nn.ModuleList()
        if use_transposed_convolutions:
            self.upsampling_blocks = nn.ModuleList()
        else:
            self.upsampling_blocks = list()
        in_channel_layer = in_channel
        input_size = 24


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
                                         first_layer=first_layer, input_size=input_size, time_emb_dim=time_emb_dim, norm_type=norm_type))
            else:
                first_layer = False

                self.layers.append(layer(num_blcks=num_blcks, block_layer=block,
                                         planes_in=in_channel_layer+layer_widths[i-1], planes_out=out_channel_layer,
                                         kernel_size=kernel_size,
                                         first_layer=first_layer, input_size=input_size, time_emb_dim=time_emb_dim, norm_type=norm_type))
            if 2>1:#i != len(layer_blocks) - 1:

                if use_transposed_convolutions:

                    self.upsampling_blocks.append(nn.ConvTranspose3d(out_channel_layer, out_channel_layer, kernel_size=2,
                                                                     stride=upsampling_stride, padding=0))
                else:

                    self.upsampling_blocks.append(nn.Upsample(scale_factor=2, mode='nearest'))


                input_size = input_size *2
                last_cov_channels = in_channel_layer#last_cov_channels//2
            print("Decoder {}:".format(i), in_channel_layer, out_channel_layer)
            in_channel_layer = out_channel_layer
        self.out_channel_layer = in_channel_layer
    def forward(self, x, t):
        i = 0

        y = x[0]
        for up, lay in zip(self.upsampling_blocks, self.layers[:-1]):
            if i == 0:
                y = lay(y, t)
            else:
                y = lay(y,t)
            y = up(y)
            y = torch.cat([y, x[i + 1]],1)
            i += 1
        y = self.layers[-1](y,t)
        return y




class UnetGen(nn.Module):
    def __init__(self, base_inc_channel=8,
                 feature_dilation=2, downsampling_stride=2,
                 encoder_class=UnetEncoder, layer_widths=None, block=None,
                 kernel_size=3, interpolation_mode ="trilinear",decoder_class=None,
                 use_transposed_convolutions=True, time_embed = False, norm_type='layer'):
        super(UnetGen, self).__init__()
        time_embed = self.time_embed
        use_transposed_convolutions = self.use_tr_conv
        inblock = 16
        base_inc_channel = inblock
        self.base_inc_channel = base_inc_channel

        sinu_pos_emb = SinusoidalPosEmb(inblock)
        fourier_dim = inblock
        if self.spacing_embed:
            fourier_dim*=4

        # time embeddings

        time_dim = inblock * 4
        if time_embed:
            self.time_mlp = nn.Sequential(
                sinu_pos_emb,
                nn.Linear(fourier_dim, time_dim),
                nn.GELU(),
                nn.Linear(time_dim, time_dim)
            )
        else:
            time_dim = None

        #encoder_blocks = [1, 1, 1, 1, 1, 1]

        #decoder_blocks = [1,1,1,1, 1, 1]
        encoder_blocks = [1, 1, 1, 1]

        decoder_blocks = [1, 1, 1, 1]

        padding = kernel_size // 2  # constant size
        self.before_encoder = nn.Conv3d(1, inblock, kernel_size=(7, 7, 7),
                                        stride=(1, 1, 1), padding=7//2,
                                        bias=True)




        #self.before_encoder = nn.Sequential(*[cv])

        self.encoder = encoder_class(in_channel=inblock, base_inc_channel=base_inc_channel, layer_blocks=encoder_blocks,
                                     block=block,
                                     feature_dilation=feature_dilation, downsampling_stride=downsampling_stride,
                                     layer_widths=layer_widths, kernel_size=kernel_size,
                                     time_emb_dim=time_dim, norm_type=norm_type)

        layer_widths = self.encoder._layers_with
        in_channel = layer_widths[-1]
        self.BottleNeck = BlockLayer(num_blcks=1, block_layer=block,
                                         planes_in=in_channel, planes_out=in_channel,
                                         kernel_size=kernel_size,
                                         first_layer=False, input_size=self.encoder.output_size, time_emb_dim=time_dim, norm_type=norm_type)


        layer_widths = layer_widths[::-1][1:]


        self.decoder = decoder_class(in_channel=in_channel, base_inc_channel=base_inc_channel*8, layer_blocks=decoder_blocks,
                                     block=block, last_cov_channels = self.encoder.out_channel_layer,
                                     upsampling_mode=interpolation_mode, layer_widths=layer_widths,
                                     use_transposed_convolutions=use_transposed_convolutions,
                                     kernel_size=kernel_size, time_emb_dim=time_dim, norm_type=norm_type,
                                     )

        kernel_size = 3

        self.last_convolution = BlockLayer(num_blcks=1, block_layer=block,
                                         planes_in=inblock*2, planes_out=inblock,
                                         kernel_size=kernel_size,
                                         first_layer=False, input_size=192, time_emb_dim=time_dim, norm_type=norm_type)

        self.final_convolution = nn.Conv3d(inblock, 1, kernel_size=(kernel_size, kernel_size, kernel_size),
                                           stride=(1, 1, 1), bias=True, padding=kernel_size // 2)
        self.activation = nn.Softmax(dim=1)

    def forward(self, y, time, interp=False, I = None):

        y = self.before_encoder(y)
        if self.time_embed:
            if len(time.shape)==1:
                t = self.time_mlp(time)
            else:
                t = self.time_mlp(time)
        else:
            t = None
        x = self.encoder(y, t)
        x[0] = self.BottleNeck(x[0], t)

        x=self.decoder(x, t)
        x = torch.cat([x, y], 1)
        x = self.activation(x)
        x = self.last_convolution(x)
        x = self.final_convolution(x)
        return x


class Unet3D(UnetGen):
    def __init__(self, time_embed=False, spacing_embed=False, channels=1, *args, encoder_class=UnetEncoder, **kwargs):
        self.time_embed = time_embed
        self.spacing_embed = spacing_embed
        self.use_tr_conv = False#opt.use_tr_conv
        norm_type = 'instance'
        super().__init__(*args, encoder_class=encoder_class, decoder_class=UnetDecoder,
                         block=ResidualBlock, norm_type=norm_type, **kwargs)
        self.channels = channels
        self.netName = 'Unet3D'
    def name(self):
        return 'unet3d'







